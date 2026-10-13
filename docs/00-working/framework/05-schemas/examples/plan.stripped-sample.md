---
code: PLAN-052
title: "Short name of what will be built"
kind: plan
status: draft
created: 2026-10-13
depends_on: [REQ-031]
---

# Route optimiser implementation plan


## Overview


Build the route optimiser as a nearest-neighbour ordering behind one HTTP endpoint,
meeting REQ-012 R01 and R02. Nearest-neighbour is fast enough for ten stops and simple enough to
finish in two sessions; an exact solver is deferred unless the latency target is missed.

## Scope


In scope: the ordering module, the endpoint, and their tests.

Out of scope: caching distances between requests, and any user interface.

## Phases


1. `phase-route-01` — Ordering module. Orders stops by nearest neighbour and returns the total
   distance. Depends on nothing. Files: `src/route/order.py`, `test/test_route_optimizer.py`.
2. `phase-route-02` — Endpoint. Exposes the ordering over HTTP and returns an error that names an
   invalid field. Depends on `phase-route-01`. Files: `src/api/routes/route.py`,
   `test/test_route_api.py`.
