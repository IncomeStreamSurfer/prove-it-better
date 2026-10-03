# Judging: criteria, prompt, bias, sample size

## Writing criteria

Criteria describe how well the output does its **job**, not how it sounds. Three to five, each one checkable by a careful reader with the context in front of them.

| Job | Good criteria | Weak criteria |
|---|---|---|
| Topic ideas for a business | Fits what the business actually sells; tied to real searches; no repeats | Creative; engaging |
| Landing page | Accurate (nothing invented); would convert the stated audience; follows the brief | Well written |
| Support reply | Resolves the issue; correct policy; tone fits the customer | Friendly |
| Statistics for an article | Relevant to the topic; from the right market; sourced and checkable | Interesting |

Write one sentence per criterion saying what a winner does. Include "nothing invented" whenever the output makes factual claims.

## The judge prompt (what `scripts/judge.py` sends)

- The task: one sentence on the job the output must do.
- The context the output was produced from (the real input, the source material).
- The criteria.
- Output A and Output B, unlabelled as old/new.
- Instructions: judge each criterion A / B / tie with a one-line reason; give an overall verdict; list concrete defects in each output; do not reward length; facts in the context beat claims in the output; trust any "AUTOMATED CHECK" line over your own impression.

## Bias controls

| Bias | Control |
|---|---|
| Position (prefers first or second) | Judge every pair twice with the order swapped; count only agreeing verdicts |
| Self-preference (a model favours its own family) | Judge from a different vendor than every contestant; otherwise hard checks only |
| Author bias (you built the challenger) | You never judge; you only read the judge's reasons |
| Length | Instruction not to reward length; check that winners are not just longer |
| Surface polish over substance | Hard checks for facts, links, numbers; put results in front of the judge |

## Sample size and reading results

- Fewer than ~8 cases: treat any result as a hint, not a verdict.
- 10–12 real cases with a lopsided result (10–0, 11–0) is strong evidence.
- Close results (6–4, 5–3–4) are noise until confirmed on more cases.
- Always confirm a win on a **fresh** sample before shipping; the first sample is the one you tuned on.
- Ties are information: many ties usually means the criteria do not separate the outputs — sharpen them.

## Reading the judge's reasons

The defect lists are the most valuable output. Group them across cases; the top two or three repeated defects are the next iteration. Fix those specifically, rerun, repeat.

## Choosing the judge model

Use the strongest model available from a vendor that did not produce either output. If the contestants are, say, an OpenAI model and a Google model, a Claude model can judge; if Claude is a contestant, use an OpenAI or Google judge. Pass `--provider anthropic|openai` and `--model` to `scripts/judge.py`.
