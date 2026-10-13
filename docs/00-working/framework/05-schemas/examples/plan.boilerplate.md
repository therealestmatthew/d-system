---
code: PLAN-052
title: "Short name of what will be built"
kind: plan
status: draft
created: 2026-10-13
depends_on: [REQ-031]
---

# Route optimiser implementation plan

<!--
A plan document states how one or more requirements will be met and divides the work into
phases. It does not restate the requirements — it cites them in `depends_on` and by number. Each
phase listed here becomes one item in the backlog file (phase.template.md), and the backlog item,
not this document, is what an agent claims.

Checked by plan.schema.json via check_schemas.py: the front matter above and the three level-2
headings below are required, spelled exactly as written. Other level-2 sections (for example
Design, Risks or Open questions) may be added; the schema does not check them.
The plan's current state is the front-matter `status` field.
-->

## Overview

<!-- What will be built, which requirements it meets, and why this approach rather than another.
Two to four sentences. -->

Example: Build the route optimiser as a nearest-neighbour ordering behind one HTTP endpoint,
meeting REQ-012 R01 and R02. Nearest-neighbour is fast enough for ten stops and simple enough to
finish in two sessions; an exact solver is deferred unless the latency target is missed.

## Scope

<!-- What this plan delivers and, as a separate list, what it leaves out. It should not exceed the
requirement's scope; if it must, say so and why. -->

Example:

In scope: the ordering module, the endpoint, and their tests.

Out of scope: caching distances between requests, and any user interface.

## Phases

<!-- The ordered phases the work divides into. Each phase is one session of work with one
concrete outcome. Give each its phase id, the outcome, what it depends on, and the files it
creates or changes, so the backlog items can be written from this list. -->

Example:

1. `phase-route-01` — Ordering module. Orders stops by nearest neighbour and returns the total
   distance. Depends on nothing. Files: `src/route/order.py`, `test/test_route_optimizer.py`.
2. `phase-route-02` — Endpoint. Exposes the ordering over HTTP and returns an error that names an
   invalid field. Depends on `phase-route-01`. Files: `src/api/routes/route.py`,
   `test/test_route_api.py`.
