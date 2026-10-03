# prove-it-better

**A Claude Code skill for making anything better, and proving it before it ships.**

Ask Claude to "make it better" and it usually rewrites things from a best-practice list, then tells you it's better. This skill makes it prove it instead. The current version is the opponent. A change only ships once it beats the current version on real cases, judged blind with the order swapped, with hard checks. It ships behind a switch you can flip back, and Claude confirms it live.

It works for AI features, agents, prompts and model swaps, and for emails, landing and pricing pages, processes and cloud bills.

## Install

Run this in your terminal:

```bash
git clone https://github.com/IncomeStreamSurfer/prove-it-better.git ~/.claude/skills/prove-it-better
```

That's it. Claude Code finds the skill automatically. To install it for one project only, clone into that project's `.claude/skills/prove-it-better` instead. To update:

```bash
git -C ~/.claude/skills/prove-it-better pull
```

## Use it

Just ask for an improvement. The skill triggers on requests like:

- "Our AI product description feature is meh — make it better."
- "Swap our summariser to a cheaper model without making it worse."
- "Our pricing page isn't converting. Improve it."
- "Our cloud bill is too high. Bring it down."
- "Rewrite our onboarding emails so more people activate."

## What Claude does

| Phase | What happens |
|---|---|
| **0. Access first** | Checks the project, CLIs, connectors and secrets (names only), then asks for everything missing in **one** message: data access, a judge model key, a safe environment, and what's off-limits. |
| **1. Research** | Usage data, complaints, past attempts, the current implementation, 10–30 **real** cases, what "better" means, and baseline numbers. Shows you before building. |
| **2. Plan** | Splits the work into units that win or lose independently, and writes the ship gate **before** any results exist. |
| **3. Build behind a switch** | The challenger is selectable per unit, with an automatic fallback to the current version. |
| **4. Prove it** | Blind pairwise judging, every pair judged **twice with the order swapped**, by a judge from a **different vendor** than the contestants, plus hard checks. For costs, the numbers decide. For clicks and sign-ups, a live A/B test decides. |
| **5. Iterate** | Fixes the judge's repeated defects, confirms on a **fresh** sample, and keeps the current version when it wins. |
| **6. Ship reversibly** | Only with your go-ahead, behind the switch. |
| **7. Verify live** | Confirms the new version is what's actually running, then compares the live metric with the baseline. |
| **8. Report** | A scoreboard per unit, what didn't ship and why, how to roll back. Measured claims only. |

## Does the skill itself work?

It was tested the same way it tests things. An agent got three "make it better" requests (an AI feature, a pricing page and a cloud bill), three times each, with and without the skill:

| Behaviour | Without the skill | With the skill |
|---|---|---|
| Sorts out access before starting | 2 / 9 | 9 / 9 |
| Researches before changing anything | 4 / 9 | 9 / 9 |
| Compares against the current version blind | 0 / 9 | ✓ where a judge applies |
| Swaps the order to remove judge bias | 0 / 9 | ✓ where a judge applies |
| Uses an independent judge | 0 / 9 | ✓ where a judge applies |
| Verifies the result live | 0 / 9 | 9 / 9 |
| Willing to keep the current version if it wins | 0 / 9 | 9 / 9 |

For the cloud bill, the skill correctly skipped the AI judge and let the hard numbers decide.

## Where it came from

This is the method used to rebuild every AI agent inside [Harbor](https://harborseo.ai), my AI SEO content generator. Each new agent ran against the old one on real customer sites and real production jobs, judged blind in both orders. Most won 10–0 or 11–0. A few first versions **lost** and were fixed before shipping, and the ones that never beat the old version weren't shipped at all.

If you want SEO articles researched from real Google results and your own site, try [harborseo.ai](https://harborseo.ai).

## Scripts

Python 3. The judge needs the SDK for whichever vendor judges (`pip install anthropic` or `pip install openai`) and that vendor's API key in your environment. The other two scripts use only the standard library.

| Script | What it does |
|---|---|
| `scripts/judge.py` | Blind, two-order pairwise judge, current vs challenger, with Claude or OpenAI as the judge. JSONL in, verdicts out. |
| `scripts/scoreboard.py` | W–L–T overall and per criterion, the most repeated defects, and a suggested decision. |
| `scripts/checks.py` | Hard checks: do the links load, and do quotes appear verbatim in the source. |

```bash
python scripts/judge.py cases.jsonl --out verdicts.jsonl --provider anthropic --criteria criteria.json --task "Write a product description from the product facts."
python scripts/scoreboard.py verdicts.jsonl
python scripts/checks.py links output.txt
```

Run any script with `--help` for the input format.

## Files

```
SKILL.md                 the method Claude follows
references/judging.md    writing criteria, bias controls, sample sizes
references/adapting.md   using it for copy, marketing, code, costs and processes
templates/tracker.md     unit-by-unit tracker
templates/report.md      results report
scripts/                 judge, scoreboard, hard checks
```

## License

MIT
