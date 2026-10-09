---
name: ship
description: Run the Trident pipeline on a request — refine, research-backed plan, build, verify, report. Use when the user runs /trident:ship or asks to run Trident.
---

Request: $ARGUMENTS
Flags inside the request: `--yes` skips the approval step, `--pr` opens a pull request at the end.

1. **Refine.** Send the request to the `trident:refiner` agent. Keep the spec.
2. **Plan.** Send the spec to the `trident:planner` agent. Keep the plan. Read its last line `BUILDER: sonnet|opus` (default sonnet).
3. **Approve.** Unless `--yes`, show the user a brief of at most 10 lines: goal, approach, key sources with licences, builder model, main risk. Ask to proceed, edit, or stop. Apply any edits to the plan.
4. **Build.** Invoke the `trident:builder` agent with the chosen model as the per-invocation `model`, passing the full spec and plan.
5. **Verify.** Send the spec, plan and builder summary to the `trident:verifier` agent. On `VERDICT: FAIL`, send the failures back to the builder once, then verify again.
6. **Report.** Write `.trident/reports/<YYYY-MM-DD>-<short-slug>.md` using the template below. Keep it under one page, plain business language, no filler.
7. **Share.** If `--pr` and `gh` is authenticated: create a branch, commit, and open a PR with the report as its body (CODEOWNERS are requested automatically). Otherwise tell the user the report path.

Reply to the user with the report's Summary and Status lines only, plus the report path.

Report template:

```markdown
# <Title>
**Date:** <YYYY-MM-DD> · **Builder:** <sonnet|opus> · **Status:** <Delivered | Delivered with open items | Blocked>

## Summary
<2–3 sentences: what was asked, what was delivered, why it matters.>

## Decisions
- <decision> — <reason>

## Sources and licences
| Source | Version | Licence | Used for |
|---|---|---|---|

## Verification
| Criterion | Result | Evidence |
|---|---|---|

## Changes
- <file> — <one line>

## Risks and next steps
- <item>
```
