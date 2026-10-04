---
schema_version: 1
id: doc-html-06-verification
code: PLAN-003.06
title: Verification Plan
kind: plan
status: deprecated
owner: repository-owner
created: '2026-09-05'
updated: '2026-10-04'
systems:
- sys-html
depends_on: []
parent: doc-html-00-overview
---

> Delivery is approved in phases. The [accepted user choices](../../08-governance/GOV-003-backlog-decisions.md) resolve conflicting details below; the [session backlog](../../09-backlog/README.md) tracks execution and completion. This document is a design source, not evidence of implementation.

# Verification Plan

## Build Order

Execute in this order to verify end-to-end:

```bash
# 1. Install Python dependency
uv sync

# 2. Convert YAML → JSON
uv run python tools/build_pages.py

# 3. Python lint & type check
uv run ruff check src/ tools/
uv run mypy src/

# 4. Run Python tests
uv run pytest

# 5. Install frontend dependencies
cd ts && npm install

# 6. Frontend type check
cd ts && npm run lint

# 7. Frontend production build
cd ts && npm run build
```

---

## Automated Tests

### Python

```bash
uv run ruff check src/ tools/       # Lint
uv run mypy src/                     # Type check
uv run pytest                        # Unit tests
```

### Frontend

```bash
cd ts && npm run lint                # TypeScript type check (tsc --noEmit)
cd ts && npm run build               # Full production build (tsc -b && vite build)
```

---

## Manual Verification

### 1. Start Services

```bash
# Terminal 1: Backend
uv run uvicorn src.main:app --reload

# Terminal 2: Frontend
cd ts && npm run dev
```

### 2. API Endpoints

| Test | Command | Expected |
|---|---|---|
| Site config | `curl http://localhost:8000/api/v1/pages/site-config` | Returns JSON with `title`, `routes`, `navigation` |
| Page data | `curl http://localhost:8000/api/v1/pages/home` | Returns JSON with `title: "Home"`, `template: "landing"`, `blocks` array |
| Missing page | `curl http://localhost:8000/api/v1/pages/nonexistent` | HTTP 404 with `detail` message |
| Path traversal | `curl http://localhost:8000/api/v1/pages/../../etc/passwd` | HTTP 400 "Invalid page ID" |

### 3. UI Verification

Open `http://localhost:5173` and verify:

- [ ] Home page renders with hero block (blue background, white text)
- [ ] Intro text block appears below the hero
- [ ] Navigation bar shows "Home" and "About" links
- [ ] Clicking "About" navigates without full page reload
- [ ] About page renders with text block
- [ ] Loading indicator appears briefly during navigation
- [ ] Navigating to `/nonexistent` shows 404 page
- [ ] "Back to home" link on 404 page works
- [ ] Tailwind utility classes are applied correctly (colors, spacing, fonts)

### 4. YAML Workflow

- [ ] Edit `_data/pages/home.yaml` (e.g., change the headline)
- [ ] Run `uv run python tools/build_pages.py`
- [ ] Refresh `http://localhost:5173` — changes are visible
- [ ] Add a new `_data/pages/test.yaml` and route in `site.yaml`
- [ ] Run `tools/build_pages.py`, restart backend, refresh — new page accessible

### 5. Error Handling

- [ ] Stop the backend → frontend shows "Failed to load D-System" error
- [ ] With backend running, navigate to a page whose YAML has invalid content → error boundary renders
- [ ] Retry button on error page reloads the current route

## Audit disposition (`phase-des-01`, 2026-10-04)

This plan is deprecated. On 2026-10-04 the owner retired the authored YAML content site that `PLAN-003` describes; [ADR-027](../../04-decisions/ADR-027-retire-plan-003.md) records the decision and what it leaves behind. Every requirement this document states is listed below with its disposition, as `REQ-021` R01 requires. Line numbers refer to this document above this section. An accomplished or superseded row names the shipped work, by file and commit or phase (`REQ-021` R03); a retired row gives the reason nothing will be built.

32 requirements: 5 accomplished, 2 superseded, 25 retired.

| Id | Line | Requirement | Disposition | Evidence or reason |
|---|---|---|---|---|
| 06-R1 | 27 | `uv sync` | superseded | `.github/workflows/ci.yaml` line 17 runs `uv sync --extra dev`, which also installs the dev tools the later checks need |
| 06-R2 | 30 | `uv run python tools/build_pages.py` | retired | the authored YAML content site is retired (ADR-027) |
| 06-R3 | 33, 56 | `uv run ruff check src/ tools/` | retired | The page tool will not exist. CI's ruff step (``.github/workflows/ci.yaml`` line 28) lints `src/ test/` only; linting `tools/` is idea 000570 |
| 06-R4 | 34, 57 | `uv run mypy src/` | accomplished | `.github/workflows/ci.yaml` line 29, on every push |
| 06-R5 | 37, 58 | `uv run pytest` | accomplished | `.github/workflows/ci.yaml` line 30, on every push. The page tests it would have run are retired with the plan |
| 06-R6 | 40 | `cd ts && npm install` | superseded | `.github/workflows/ci.yaml` line 45 runs `npm ci` against the lockfile |
| 06-R7 | 43, 64 | `cd ts && npm run lint` | retired | Type checking runs inside `npm run build` (`tsc -b`, `.github/workflows/ci.yaml` line 46); no page code remains to lint separately |
| 06-R8 | 46, 65 | `cd ts && npm run build` | accomplished | `.github/workflows/ci.yaml` line 46, on every push |
| 06-R9 | 76 | Start the backend with uvicorn | accomplished | `src/main.py` line 6 defines `app` |
| 06-R10 | 79 | Start the frontend with `npm run dev` | accomplished | `ts/package.json` `dev` script |
| 06-R11 | 86 | `curl /api/v1/pages/site-config` | retired | no `/api/v1/pages` backend will exist (ADR-027) |
| 06-R12 | 87 | `curl /api/v1/pages/home` | retired | no `/api/v1/pages` backend will exist (ADR-027) |
| 06-R13 | 88 | `curl` of a missing page returns 404 | retired | no `/api/v1/pages` backend will exist (ADR-027) |
| 06-R14 | 89 | `curl` of a traversal path returns 400 | retired | no `/api/v1/pages` backend will exist (ADR-027). ARCH-003 M5 had already shown curl normalises the path before sending |
| 06-R15 | 95 | Home renders the hero | retired | the authored YAML content site is retired (ADR-027) |
| 06-R16 | 96 | Intro text below the hero | retired | the authored YAML content site is retired (ADR-027) |
| 06-R17 | 97 | Navigation shows Home and About | retired | the authored YAML content site is retired (ADR-027) |
| 06-R18 | 98 | About opens without a full reload | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 06-R19 | 99 | About renders its text block | retired | the authored YAML content site is retired (ADR-027) |
| 06-R20 | 100 | A loading indicator appears during navigation | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 06-R21 | 101 | `/nonexistent` shows the 404 page | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 06-R22 | 102 | "Back to home" works from the 404 page | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 06-R23 | 103 | Tailwind utility classes are applied | retired | Tailwind is not adopted; generated pages use the house tokens (ADR-027) |
| 06-R24 | 107 | Edit the home headline in YAML | retired | the authored YAML content site is retired (ADR-027) |
| 06-R25 | 108 | Run the build | retired | the authored YAML content site is retired (ADR-027) |
| 06-R26 | 109 | Refresh shows the change | retired | the authored YAML content site is retired (ADR-027) |
| 06-R27 | 110 | Add a page and a route | retired | the authored YAML content site is retired (ADR-027) |
| 06-R28 | 111 | The new page is reachable after rebuild and restart | retired | the authored YAML content site is retired (ADR-027) |
| 06-R29 | 115 | With the backend stopped, "Failed to load D-System" appears | retired | no `/api/v1/pages` backend will exist (ADR-027) |
| 06-R30 | 116 | Invalid YAML renders the error boundary | retired | the authored YAML content site is retired (ADR-027) |
| 06-R31 | 117 | Retry reloads the current route | retired | the React app has no URL routing; it is the demo stage and workbench (ADR-027) |
| 06-R32 | 23 | Execute the steps in order end to end | retired | the authored YAML content site is retired (ADR-027) |
