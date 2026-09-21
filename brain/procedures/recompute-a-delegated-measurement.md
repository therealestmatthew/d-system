---
id: mem-proc-recompute-a-delegated-measurement
title: Recompute A Delegated Measurement
type: procedure
tags: [agentic-systems, ai-tools, automation]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-20
updated: 2026-09-20
confidence: high
related: [mem-proc-check-that-cannot-fail, mem-proc-runtime-behavior-needs-runtime-evidence]
scope: global
---

## The rule

When you delegate a measurement and the answer decides something — whether work passes, whether a
phase closes, whether a condition is met — **recompute the load-bearing numbers yourself before
acting on them**. A delegated measurement is a claim, not a result. It becomes a result when a
second, independent computation reproduces it.

Recompute the ones that decide. Not every number in a report needs this; the ones whose value
changes what happens next do.

The failure this prevents is not a worker lying. It is a worker **answering a different question
than the one asked** — silently narrowing the population, matching a literal string where the
contract meant a concept, or reading a range as an index. The number comes back well-formed and
confident, and nothing about its shape reveals that it ranged over the wrong thing.

**Putting the warning in the dispatch text does not substitute.** That is the part worth
remembering, because it is the part that looks like it should work.

## Worked example (2026-09-14 and 2026-09-20, the literature-review campaign)

Three consecutive runs of one gate reported false results. The gate's own dispatch text carried an
explicit, written warning against exactly this failure — "a gate that narrows its own scope
silently reports PASS on the part it skipped" — and the warning did not prevent any of the three.

- **2026-09-14.** Measurement 1 counted a domain's title as one of its mandated variants.
  Measurement 4 read the contract phrase "rows 20–30" as a line-number range rather than a
  row-count target. Both were caught and corrected in a fix cycle.
- **2026-09-20, same gate, files changed.** Measurement 1 silently restricted its row population to
  one `strategy_phase` value and **failed two domains that pass comfortably** — they had 6 and 10
  distinct queries against a threshold of 2. Measurement 4 **repeated the 2026-09-14 line-range
  error exactly**, reporting PASS over 473 of 2,881 cells. The contract text had not changed.
- **The fix cycle for those errors introduced a third.** Re-running measurement 1's variant half,
  the gate failed two more domains for not reproducing parenthetical notation — `cognitive
  architecture (SOAR, ACT-R)` — verbatim in a query string, when every component term was present.
  The parenthetical was notation meaning "these examples", not a string to match.

Unreviewed, that gate would have failed the phase on two conditions that are met. Every one of the
errors was caught by independently recomputing the number, and every recomputation took a few lines
of script against files already on disk.

## The tell

A delegated measurement is most suspect where it is cheapest to check. If reproducing the number
takes one short script over files you already have, the argument for trusting the report instead is
only that you are tired. Recompute it.

A second tell: **a measurement that fails where you expected a pass deserves the same recomputation
as one that passes where you expected a failure.** Two of the three errors above produced false
FAILs. Scepticism that only runs toward comfortable answers is not scepticism.

## When the measurement is mechanical, the delegation is the defect

If every measurement in a battery is computable from files on disk by a deterministic script, giving
that battery to a language model is the wrong instrument, and no amount of recomputation fixes the
instrument. Recompute today; then record the work to replace the dispatch with a script.

## Why this is model-agnostic

Any agent coordinating any other agent inherits this. The coordinating role's whole value is
independent verification, and the pressure to skip it is strongest at the end of a long session,
which is exactly when a gate's output is most likely to be read rather than checked. It is filed
alongside `mem-proc-check-that-cannot-fail`, which covers a check that cannot fail; this
one covers a check that can fail and failed at the wrong thing.
