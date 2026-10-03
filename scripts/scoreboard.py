#!/usr/bin/env python3
"""Tally verdicts from judge.py into a scoreboard and a suggested decision.

  python scoreboard.py verdicts.jsonl            # markdown summary
  python scoreboard.py verdicts.jsonl --json     # machine-readable

W–L–T is always challenger vs current. Decision follows the skill's verdict rules:
consistent wins >= 2x losses -> ship (after a fresh-sample confirm); fewer than 8
judged cases -> not enough evidence. Hard checks are judged separately — a worse
hard check blocks shipping regardless of this tally.
"""
import argparse, collections, json


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verdicts")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.verdicts) if l.strip()]
    ok = [r for r in rows if "overall" in r]
    errors = [r for r in rows if "error" in r]

    def wlt(values):
        c = collections.Counter(values)
        return c["challenger"], c["current"], c["tie"]

    w, l, t = wlt(r["overall"] for r in ok)
    per = {}
    for r in ok:
        for k, v in r["criteria"].items():
            per.setdefault(k, []).append(v)
    per_wlt = {k: wlt(v) for k, v in per.items()}

    defects = collections.Counter()
    for r in ok:
        for d in r.get("challenger_defects", []):
            defects[d.strip().rstrip(".")[:90]] += 1

    n = len(ok)
    if n < 8:
        decision = f"not enough evidence ({n} judged cases; get at least ~8, ideally 10+)"
    elif w >= 2 * max(l, 1) and w > l:
        decision = "ship candidate — confirm on a fresh sample, and only if no hard check got worse"
    elif w > l:
        decision = "leaning challenger but not decisive — iterate on the top defects, or add cases"
    else:
        decision = "keep current (or iterate on the top defects)"

    if args.json:
        print(json.dumps({"n": n, "errors": len(errors), "overall": [w, l, t], "criteria": per_wlt,
                          "top_challenger_defects": defects.most_common(10), "decision": decision}, indent=2))
        return

    print(f"# Scoreboard — challenger vs current\n\n**Overall: {w}–{l}–{t}** (W–L–T, {n} cases judged in both orders"
          + (f", {len(errors)} failed" if errors else "") + ")\n")
    print("| Criterion | W–L–T |\n|---|---|")
    for k, (a, b, c) in per_wlt.items():
        print(f"| {k} | {a}–{b}–{c} |")
    print(f"\n**Suggested decision:** {decision}\n")
    if defects:
        print("## Most repeated challenger defects (fix these next)\n")
        for d, cnt in defects.most_common(10):
            print(f"- ({cnt}×) {d}")
    losses = [r["id"] for r in ok if r["overall"] == "current"]
    if losses:
        print(f"\n## Cases the challenger lost\n\n{', '.join(map(str, losses))} — read the judge's reasons for each.")


if __name__ == "__main__":
    main()
