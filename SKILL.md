---
name: prove-it-better
description: Use when asked to make something better, improve quality, upgrade, migrate, swap models, rewrite prompts, optimise copy or conversions, or cut costs — an AI feature, agent, prompt, email, landing page, pricing page, process, or bill — and the change should beat what exists today before it ships.
---

# Prove It Better

## Overview

The current version is the opponent. A change ships only after it beats the current version on real cases, judged blind, with hard checks — and it ships in a way you can undo, then gets confirmed live. Everything below is in service of that one rule.

Work through the phases in order. Each phase ends with a required output; do not start the next phase until that output exists and the user has seen it where marked.

## Phase 0 — Access (always first, before reading code or proposing anything)

Run, in the terminal:
- `git status`, the project's stack and scripts, what environments exist (local / staging / production).
- Which CLIs are installed and logged in (`gh`, cloud CLIs, database / hosting / deploy CLIs).
- Which secrets exist — print names only, never values.
- Which connectors / MCP servers are available and authorised (analytics, payments, email, search console, docs, support inbox). Note any that are configured but need the user to authorise.

Then work out what the job needs and you do not have yet. Usually:
- read access to real usage / production data or exports,
- a judge model API key from a **different vendor** than the thing being judged,
- a safe place to run things (dev or staging),
- the rules: what is off-limits (production writes, sends, money), and who approves shipping.

Ask for everything missing in **one** message, saying what each item is for.

**Output — Access table:** item · have / missing / requested · what it is for.

## Phase 1 — Research (before changing anything)

- What is the thing's job, in one sentence? Who uses it, how much (real numbers from the data)?
- What do people complain about? What failed before? What was already tried, with what result?
- Read the current implementation end to end.
- Collect **real cases**: 10–30 real inputs from production, customers, or history. If real cases genuinely do not exist, build synthetic ones, label them synthetic in every report, and replace them with real ones as soon as possible.
- Define "better" as 3–5 criteria tied to the job (not to style), and list every **hard check** you can run without an opinion (links load, facts match the source, numbers add up, cost per run, latency, test suite, real conversion data).
- Measure the current version on the hard checks.

**Output — Research brief:** job · usage · known failures · case set · criteria · hard checks · baseline numbers. Show it to the user before building.

## Phase 2 — Plan

Split the work into units that can win or lose independently (one feature, one page, one cost line). Fill the tracker (`templates/tracker.md`): unit · current · challenger · eval · status.

Write the ship gate before any results exist: the challenger wins on consistent verdicts, no hard check gets worse, and its cost is acceptable.

## Phase 3 — Build the challenger behind a switch

Leave the current version intact. Make the challenger selectable per unit (flag / env var / config) and fall back to the current version on error, so either can run on the same input.

## Phase 4 — Prove it

1. Run current and challenger on the **same** cases.
2. Judge pairwise and blind: outputs are labelled A and B, never "old/new"; every pair is judged **twice with the order swapped**; a win counts only when both orders agree, otherwise it is a tie.
3. The judge is never the author. Use a model from a different vendor than the contestants (`scripts/judge.py --provider`). If every available judge shares a vendor with a contestant, decide on hard checks only.
4. Run every hard check (`scripts/checks.py`) and put the results in front of the judge as an "AUTOMATED CHECK" line.
5. Where the real outcome is human behaviour (opens, clicks, sign-ups, revenue), the blind judge is a pre-screen; a live A/B test or the live metric decides.
6. Where every criterion is a hard number (cost, latency, error rate, test pass rate), the hard checks are the verdict and no judge is needed.
7. Tally with `scripts/scoreboard.py`.

## Phase 5 — Iterate on defects

Read the judge's reasons for every loss and tie. Fix the specific defects, rerun on the same cases, then confirm on a **fresh** sample before calling it a win. When stuck, change one thing at a time to find what actually helps. After 3–5 rounds with no consistent win, keep the current version and record why — that is a result, not a failure.

## Phase 6 — Ship reversibly

Get the owner's explicit go. Ship behind the per-unit switch with the fallback in place. Never ship during another risky operation (a send, a migration, an incident).

## Phase 7 — Verify live

Confirm the new version is what is actually running (deployed version / function signature / build id), watch logs for the new path and for fallbacks, run one real case in production, and after enough time compare the live metric with the baseline.

## Phase 8 — Report

Use `templates/report.md`: per-unit scoreboard (W–L–T), hard checks before / after, what did not ship and why, how to roll back. Any announcement uses only measured claims.

## Verdict rules

| Result | Decision |
|---|---|
| Consistent wins ≥ 2× losses, no hard check worse | Ship (after a fresh-sample confirm) |
| Mostly ties, or wins ≈ losses | Iterate, or keep current |
| Any hard check worse | Do not ship until fixed |
| Fewer than ~8 cases | Not enough evidence — get more cases |

## Common mistakes

| Mistake | Instead |
|---|---|
| Improving from a generic best-practice list | Prove each change against the current version |
| Judging your own work | Independent judge from another vendor, blind, both orders |
| Invented test inputs when real ones exist | Real cases from production / history |
| Averaged 1–10 scores | Pairwise verdicts plus hard checks |
| Shipping the first winning number | Confirm on a fresh sample |
| No way back | Per-unit switch and automatic fallback |
| Stopping at "deployed" | Verify live, then compare the live metric |
| Starting before access is sorted | Phase 0 first; ask for everything in one message |

## Supporting files

- `references/judging.md` — writing criteria, the judge prompt, bias controls, sample sizes.
- `references/adapting.md` — applying this to copy, marketing, code / performance, cost, and processes.
- `scripts/judge.py`, `scripts/scoreboard.py`, `scripts/checks.py` — run `--help` on each.
- `templates/tracker.md`, `templates/report.md`.
