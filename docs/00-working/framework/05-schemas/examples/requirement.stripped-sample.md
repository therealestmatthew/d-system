---
code: REQ-031
title: "Short name of the feature or subsystem"
kind: requirement
status: draft
created: 2026-10-13
---

# Route optimiser requirements


## Overview


Route planners need a multi-stop route ordered to minimise distance. Today they order
stops by hand, which takes several minutes per route and is often longer than necessary.

## Requirements


**R01 — An optimised route visits every stop.**
Given a start, an end and up to ten stops, the response lists every stop exactly once.
*Verification:* `uv run pytest test/test_route_optimizer.py -k visits_every_stop`

**R02 — The response arrives within two seconds.**
*Verification:* a load test of ten concurrent requests reports a 99th-percentile latency below
two seconds.

## Scope


In scope: the ordering algorithm and the HTTP endpoint that returns the ordered route.

Out of scope: a user interface for viewing routes, and storing routes between requests.

## Acceptance criteria


- R01 and R02 each pass their stated verification.
- An invalid coordinate returns an error that names the offending field.
