#!/usr/bin/env python3
"""Blind, two-order pairwise judge: current vs challenger.

Every case is judged twice — once with the current output as A, once with it as B.
A verdict (overall or per criterion) counts only when both orders agree; otherwise
it is a tie. Outputs are never labelled old/new.

Input: JSONL, one case per line:
  {"id": "case-1",
   "task": "one sentence: the job the output must do",        # or pass --task
   "criteria": [{"key": "accuracy", "description": "..."}],   # or pass --criteria FILE.json
   "context": "the real input / source material",
   "current": "output of the current version",
   "challenger": "output of the challenger",
   "current_check": "optional AUTOMATED CHECK result for current",
   "challenger_check": "optional AUTOMATED CHECK result for challenger"}

Output: JSONL verdicts (one per case) for scripts/scoreboard.py.

Judge must be a different vendor from both contestants:
  --provider anthropic  (needs ANTHROPIC_API_KEY; pip install anthropic)
  --provider openai     (needs OPENAI_API_KEY;   pip install openai)

Example:
  python judge.py cases.jsonl --out verdicts.jsonl --provider anthropic --model claude-opus-5-5
"""
import argparse, concurrent.futures as cf, json, os, sys

SYSTEM = (
    "You are an impartial expert evaluator. You compare two outputs, A and B, produced for the same job "
    "from the same context. Judge only how well each does the job described, using the criteria given. "
    "Do not reward length or polish over substance. Facts in the context outrank claims in the outputs. "
    "If an AUTOMATED CHECK line is given for an output, trust it over your own impression. "
    "When the outputs are equally good on a criterion, say tie. List concrete defects for each output: "
    "specific, checkable problems, not general impressions."
)


def build_schema(keys):
    crit = {
        k: {
            "type": "object",
            "properties": {"winner": {"type": "string", "enum": ["A", "B", "tie"]}, "reason": {"type": "string"}},
            "required": ["winner", "reason"],
            "additionalProperties": False,
        }
        for k in keys
    }
    return {
        "type": "object",
        "properties": {
            "criteria": {"type": "object", "properties": crit, "required": list(keys), "additionalProperties": False},
            "overall": {"type": "string", "enum": ["A", "B", "tie"]},
            "overall_reason": {"type": "string"},
            "defects_A": {"type": "array", "items": {"type": "string"}},
            "defects_B": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["criteria", "overall", "overall_reason", "defects_A", "defects_B"],
        "additionalProperties": False,
    }


def prompt_for(case, a, b, a_check, b_check):
    crit = "\n".join(f"- {c['key']}: {c['description']}" for c in case["criteria"])
    def block(label, out, check):
        head = f"=== OUTPUT {label} ===\n"
        if check:
            head += f"AUTOMATED CHECK: {check}\n\n"
        return head + out
    return (
        f"JOB: {case['task']}\n\nCRITERIA:\n{crit}\n\n=== CONTEXT ===\n{case.get('context', '')}\n\n"
        f"{block('A', a, a_check)}\n\n{block('B', b, b_check)}\n\n"
        "Judge each criterion, give an overall verdict, and list defects for A and B."
    )


def call_judge(args, case, a, b, a_check, b_check):
    keys = [c["key"] for c in case["criteria"]]
    schema = build_schema(keys)
    user = prompt_for(case, a, b, a_check, b_check)
    if args.provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        r = client.messages.create(
            model=args.model,
            max_tokens=12000,
            system=SYSTEM,
            thinking={"type": "adaptive"},
            output_config={"format": {"type": "json_schema", "schema": schema}},
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in r.content if b.type == "text")
        if not text:
            raise RuntimeError(f"judge returned no verdict (stop_reason={r.stop_reason})")
        return json.loads(text)
    import openai
    client = openai.OpenAI()
    r = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
        response_format={"type": "json_schema", "json_schema": {"name": "verdict", "schema": schema, "strict": True}},
    )
    return json.loads(r.choices[0].message.content)


def to_side(winner, current_is_a):
    if winner == "tie":
        return "tie"
    a_wins = winner == "A"
    return "current" if a_wins == current_is_a else "challenger"


def judge_case(args, case):
    if args.task and "task" not in case:
        case["task"] = args.task
    if args.criteria_list and "criteria" not in case:
        case["criteria"] = args.criteria_list
    cur, cha = case["current"], case["challenger"]
    cc, hc = case.get("current_check"), case.get("challenger_check")
    v1 = call_judge(args, case, cur, cha, cc, hc)   # current = A
    v2 = call_judge(args, case, cha, cur, hc, cc)   # current = B
    o1, o2 = to_side(v1["overall"], True), to_side(v2["overall"], False)
    overall = o1 if o1 == o2 else "tie"
    crit = {}
    for c in case["criteria"]:
        k = c["key"]
        s1 = to_side(v1["criteria"][k]["winner"], True)
        s2 = to_side(v2["criteria"][k]["winner"], False)
        crit[k] = s1 if s1 == s2 else "tie"
    return {
        "id": case.get("id"),
        "overall": overall,
        "consistent": o1 == o2,
        "criteria": crit,
        "challenger_defects": v1["defects_B"] + v2["defects_A"],
        "current_defects": v1["defects_A"] + v2["defects_B"],
        "reasons": [v1["overall_reason"], v2["overall_reason"]],
        "raw_orders": [o1, o2],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", help="JSONL file of cases")
    ap.add_argument("--out", required=True, help="JSONL file for verdicts")
    ap.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    ap.add_argument("--model", help="judge model (default for anthropic: claude-opus-5-5; required for openai)")
    ap.add_argument("--task", help="task sentence for cases that omit it")
    ap.add_argument("--criteria", help="JSON file with a criteria list for cases that omit it")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if not args.model:
        if args.provider == "openai":
            sys.exit("--model is required with --provider openai")
        args.model = "claude-opus-5-5"
    args.criteria_list = json.load(open(args.criteria)) if args.criteria else None
    cases = [json.loads(l) for l in open(args.cases) if l.strip()]

    results = []
    with cf.ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(judge_case, args, c): c for c in cases}
        for f in cf.as_completed(futs):
            c = futs[f]
            try:
                r = f.result()
            except Exception as e:  # keep going; a failed case is reported, not dropped silently
                r = {"id": c.get("id"), "error": str(e)[:300]}
            results.append(r)
            print(f"{r.get('id')}: {r.get('overall', 'ERROR ' + r.get('error', ''))}", file=sys.stderr)
    with open(args.out, "w") as fh:
        for r in results:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote {len(results)} verdicts to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
