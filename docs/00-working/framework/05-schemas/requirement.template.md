---
code: REQ-NNN
title: "Short name of the feature or subsystem"
kind: requirement
status: draft
created: YYYY-MM-DD
---

# [Feature Name] Requirements

<!--
A requirement document states what is needed and how anyone will know it was delivered. It does
not say how to build it or in what order — that is a plan document (plan.template.md), which
cites this requirement. If you find yourself naming files to write or phases to run, that
material belongs in the plan.

Checked by requirement.schema.json via check_schemas.py: the front matter above and the four
level-2 headings below are required, spelled exactly as written. Other level-2 sections (for
example Dependencies or Risks) may be added; the schema does not check them.
The requirement's current state is the front-matter `status` field.
-->

## Overview

<!-- What is needed, for whom, and the problem it solves. Two to four sentences. -->

Example: Route planners need a multi-stop route ordered to minimise distance. Today they order
stops by hand, which takes several minutes per route and is often longer than necessary.

## Requirements

<!-- One numbered requirement per observable behaviour or quality, each with its own
verification method. Number them R01, R02, ... so plans, phases and reviews can cite them. -->

Example:

**R01 — An optimised route visits every stop.**
Given a start, an end and up to ten stops, the response lists every stop exactly once.
*Verification:* `uv run pytest test/test_route_optimizer.py -k visits_every_stop`

**R02 — The response arrives within two seconds.**
*Verification:* a load test of ten concurrent requests reports a 99th-percentile latency below
two seconds.

## Scope

<!-- What this requirement covers and, as a separate list, what it does not. The out-of-scope list
prevents a plan from quietly widening the work. -->

Example:

In scope: the ordering algorithm and the HTTP endpoint that returns the ordered route.

Out of scope: a user interface for viewing routes, and storing routes between requests.

## Acceptance criteria

<!-- The conditions that must all hold before the requirement counts as met. Each should be
checkable by someone who did not do the work, and each should trace to a requirement above. -->

Example:

- R01 and R02 each pass their stated verification.
- An invalid coordinate returns an error that names the offending field.
