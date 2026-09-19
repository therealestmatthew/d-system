---
code: PLAN-NNN
title: "Subsystem name or feature area"
kind: plan
created: YYYY-MM-DD
status: draft
depends_on: [REQ-NNN]
---

# [Subsystem Name] Implementation Plan

## Overview

<!-- 1-2 sentences: what are we building? Why this approach? -->

Example: "Build route optimization backend using nearest-neighbor algorithm + Claude API for reasoning. This approach is fast enough for demo and lets us showcase Claude's reasoning capabilities."

## Architecture

### High-Level Design

<!-- Diagram or prose description of components and data flow -->

**Components:**
- **FastAPI Server** — HTTP endpoint handler
- **Route Optimizer** — Reorder via points for shortest path
- **Location Service** — Query AWS for distance/traffic
- **Claude Integration** — Call Claude for reasoning

**Data Flow:**
```
POST /api/routes/optimize
  → Validate input (coordinates, constraints)
  → Call Location Service (distance matrix)
  → Call Optimizer (nearest-neighbor)
  → Call Claude (explain route)
  → Return response (route + reasoning)
```

### Technology Choices

- **Python + FastAPI** — Already in stack, good for API
- **Nearest-neighbor algorithm** — O(n²), simple, good enough for 10 points
- **In-memory caching** — No database needed, fast, good for demo
- **Claude API + AWS Location** — Non-negotiable per requirements

## Phase Breakdown

This plan decomposes into X phases (each ~4-6 hours of work):

### Phase 1: AWS Location Integration [phase-route-loc-01]
**Goal:** Query AWS for distance/traffic data  
**Deliverables:** `src/services/location_client.py`, tests  
**Acceptance:**
- Client queries distance matrix from AWS
- Caches results (same query within 1 hour returns cached)
- Handles errors (invalid coordinates, API down)

**Verification:**
```bash
uv run pytest test/test_location_client.py -v
```

**Dependencies:** AWS credentials (team lead)  
**Estimated effort:** 2 hours

---

### Phase 2: Route Optimization Algorithm [phase-route-opt-01]
**Goal:** Implement nearest-neighbor to order via points  
**Dependencies:** phase-route-loc-01 (uses distance matrix)  
**Deliverables:** `src/services/route_optimizer.py`, tests  
**Acceptance:**
- Orders via points to minimize total distance
- Handles edge cases (no via points, duplicate points)
- Returns optimized order + total distance

**Verification:**
```bash
uv run pytest test/test_route_optimizer.py -v
```

**Estimated effort:** 3 hours

---

### Phase 3: Claude Reasoning Integration [phase-route-reason-01]
**Goal:** Call Claude to explain route choice  
**Dependencies:** phase-route-opt-01 (has route to explain)  
**Deliverables:** `src/services/route_reasoner.py`, tests  
**Acceptance:**
- Calls Claude API with route context
- Returns explanation > 50 chars, < 1000 chars
- Handles API timeouts (returns empty reasoning)

**Verification:**
```bash
uv run pytest test/test_route_reasoner.py -v
```

**Estimated effort:** 2 hours

---

### Phase 4: API Endpoint [phase-route-api-01]
**Goal:** Wire up FastAPI endpoint  
**Dependencies:** phase-route-reason-01 (has all components)  
**Deliverables:** `src/api/routes/optimize.py`, tests  
**Acceptance:**
- POST /api/routes/optimize accepts valid request
- Returns optimized route + reasoning
- Validates input (returns 400 on invalid)
- Handles errors gracefully (AWS down, Claude timeout)

**Verification:**
```bash
uv run pytest test/test_optimize_api.py -v
```

**Estimated effort:** 2 hours

---

### Phase 5: Integration & Performance [phase-route-perf-01]
**Goal:** End-to-end testing, performance validation, fallback verification  
**Dependencies:** phase-route-api-01 (has full API)  
**Deliverables:** `test/test_integration_routes.py`, `docs/performance-report.md`  
**Acceptance:**
- 10 concurrent requests all succeed
- Response time < 2s (p99)
- API works when AWS/Claude are down (graceful degradation)
- Integration test passes (full flow)

**Verification:**
```bash
uv run pytest test/test_integration_routes.py -v
python test/load_test_routes.py  # 10 concurrent
python test/perf_test_routes.py  # latency check
```

**Estimated effort:** 3 hours

---

## Interdependencies

```
Phase 1 (Location)
  ↓
Phase 2 (Optimizer) ──→ Phase 3 (Claude Reasoning)
                            ↓
                        Phase 4 (API)
                            ↓
                        Phase 5 (Integration)
```

**Parallel opportunities:**
- Phases 2 and 3 can start in parallel (both depend on 1, not on each other)
- Phase 4 can mock Phases 2/3 if needed (though not recommended)

## Tech Decisions & Rationale

### Why nearest-neighbor algorithm?
**Decision:** Use nearest-neighbor for via-point ordering  
**Rationale:** 
- Simple to implement (1-2 hours vs. 8+ for TSP)
- Good enough for 10 points (< 1s computation)
- Produces visibly optimized routes (typically 20-30% improvement over naive)
**Tradeoff:** May not be globally optimal, but optimization takes exponential time
**Fallback:** If performance issues arise, switch to held-Karp or genetic algorithm

### Why in-memory caching?
**Decision:** Cache AWS queries in memory, expire after 1 hour  
**Rationale:**
- Hackathon scope: traffic doesn't change much in 24h
- Saves API calls (costs money)
- Fast (in-memory vs. database)
**Tradeoff:** Cache lost on service restart, lost across machines
**Fallback:** If demo needs to last > 1h, implement simple file cache

### Why call Claude per request (not batch)?
**Decision:** Call Claude for each route request  
**Rationale:**
- Reasoning is the value-add (part of the demo)
- Batch processing adds latency and complexity
**Tradeoff:** More API calls, higher cost, slower if Claude has latency
**Fallback:** If Claude times out too often, cache common reasoning patterns

## Risks & Mitigations

| Risk | Severity | Mitigation | Owner |
|---|---|---|---|
| Claude API latency | High | Timeout at 1.5s, return route without reasoning | alice (phase-route-reason-01) |
| AWS rate limiting | Medium | Cache aggressively; fall back to Haversine if limited | alice (phase-route-loc-01) |
| Algorithm too slow | Medium | Profile with 10 points; upgrade if needed | bob (phase-route-opt-01) |
| Missing edge case in tests | Low | Add tests during phase-route-perf-01 | charlie (phase-route-perf-01) |

## Success Criteria

All 5 phases complete and integrated = success:

- [x] All phases integrated to `dev`
- [x] All tests pass
- [x] Response time < 2s measured
- [x] Fallback works (AWS/Claude down, still responds)
- [x] Session records document decisions and learnings

## External Dependencies

### Must be provided by team lead:
- [ ] AWS Location API credentials
- [ ] Claude API credentials + quota allocation
- [ ] AWS account permissions

### Nice to have:
- [ ] Example route data (for testing)
- [ ] Performance SLA (current assumption: < 2s)

### Does NOT depend on:
- Frontend (can be mocked)
- Authentication (public API)
- Database (stateless)

## Open Questions / To Be Decided

- **Q: Should we cache reasoning (Claude results)?**  
  A: Defer to phase-route-reason-01; skip for now (stateless MVP)

- **Q: What if a via point is actually closer going backwards?**  
  A: Nearest-neighbor assumes directionality; if needed, try both directions (defer to phase-route-perf-01)

- **Q: Should we support constraints (avoid highways, etc.)?**  
  A: Out of scope for MVP; nice-to-have idea for post-hackathon

## Approval

**Reviewed by:** (team lead)  
**Approved:** YYYY-MM-DD  
**Status:** Ready for phase creation

---

## How to Use This Template

1. **Copy** as `PLAN-NNN-slug.md`
2. **Fill sections:** Overview, Architecture, Phase breakdown
3. **Estimate effort:** Realistic for your team
4. **Review:** Team lead checks feasibility
5. **Approve:** Status → approved
6. **Decompose:** Extract phases into backlog.yaml
7. **Execute:** Developers claim phases and build

