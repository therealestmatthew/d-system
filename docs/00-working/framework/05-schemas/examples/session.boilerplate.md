---
code: SESS-2026-10-14-01
title: "Short name of the session's work"
kind: session
status: draft
created: 2026-10-14
phase: phase-id
agent: agent-name
---

# Route ordering module

<!--
A session record is the account one working session leaves behind: what it was for, whether the
phase's acceptance held, what was decided, what it found that belongs to later work, and the
evidence. It is read later by people and tools looking for decisions and loose ends, so each kind
of item has its own section rather than being mixed into narrative.

Checked by session-record.schema.json via check_schemas.py: the front matter above and the nine
level-2 headings below are required, spelled exactly as written. A section with nothing to report
stays in the record and says "None." so a reader can tell "nothing found" from "not recorded".
Other level-2 sections (for example Review, Timeline or Notes for the next agent) may be added; the
schema does not check them. `phase` and `agent` may be left out when the session worked no phase.
-->

## Summary

<!-- What the session set out to do and what it delivered. Two to four sentences. -->

Example: Built the route ordering module for phase-route-01. Stops are ordered by nearest
neighbour, and the module returns the ordered stops with the total distance.

## Acceptance

<!-- Each acceptance condition of the phase, marked met or not met, with the evidence for it. -->

Example:

- REQ-012 R01, every stop visited exactly once — **Met.** The visits-every-stop test passes for
  routes of zero, one and ten stops.

## Decisions

<!-- Choices made during the session: what was chosen, who chose it, and why. -->

Example:

- **Nearest neighbour, not an exact solver** (owner, this session): ten stops is small enough that
  the simpler ordering meets the latency target.

## New requirements

<!-- Needs discovered that no existing requirement covers, and where each was recorded. -->

Example: Routes need a maximum stop count, so an oversized request is refused rather than slow.
Recorded as idea 000214.

## Deferred and out of scope

<!-- Work noticed but deliberately left for later or outside the phase, and where each was
recorded. -->

Example: Caching distances between requests was left out of scope by the plan. Recorded as idea
000215.

## Open investigations

<!-- Questions the session raised and did not answer. -->

Example: Whether stops closer than ten metres should be merged before ordering.

## Outstanding actions

<!-- Concrete steps someone still has to take, with who should take them. -->

Example: The owner provisions the routing service's credentials before phase-route-02 starts.

## Verification

<!-- The verification commands run and their real output, pasted, not summarised. A failing
result is recorded here as it happened. -->

Example:

```text
$ uv run pytest test/test_route_optimizer.py
6 passed in 0.41s
```

## Completion evidence

<!-- The files the phase created or changed, by path. -->

Example:

- `src/route/order.py`
- `test/test_route_optimizer.py`
