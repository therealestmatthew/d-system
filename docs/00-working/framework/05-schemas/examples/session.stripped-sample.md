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

## Summary

Built the route ordering module for phase-route-01. Stops are ordered by nearest
neighbour, and the module returns the ordered stops with the total distance.

## Acceptance

- REQ-012 R01, every stop visited exactly once — **Met.** The visits-every-stop test passes for
  routes of zero, one and ten stops.

## Decisions

- **Nearest neighbour, not an exact solver** (owner, this session): ten stops is small enough that
  the simpler ordering meets the latency target.

## New requirements

Routes need a maximum stop count, so an oversized request is refused rather than slow.
Recorded as idea 000214.

## Deferred and out of scope

Caching distances between requests was left out of scope by the plan. Recorded as idea
000215.

## Open investigations

Whether stops closer than ten metres should be merged before ordering.

## Outstanding actions

The owner provisions the routing service's credentials before phase-route-02 starts.

## Verification

```text
$ uv run pytest test/test_route_optimizer.py
6 passed in 0.41s
```

## Completion evidence

- `src/route/order.py`
- `test/test_route_optimizer.py`
