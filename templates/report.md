# <What was improved> — results

## Summary
One paragraph: what changed, how it was tested, what shipped, what did not.

## How it was tested
- Cases: <n> real <inputs> from <source> (label any synthetic cases).
- Judge: <model, vendor>, blind, every pair judged twice with the order swapped; a win counts only when both orders agree.
- Hard checks: <list>.

## Scoreboard (challenger vs current)
| Unit | W–L–T | Strongest criteria | Hard checks before → after | Decision |
|------|-------|--------------------|-----------------------------|----------|

## Not shipped, and why
| Unit | Result | Why it stays as is |

## Rollback
How to switch each unit back (flag / env var), and what falls back automatically.

## Live verification
What was checked after shipping, when, and what it showed. When the live metric will be compared again.
