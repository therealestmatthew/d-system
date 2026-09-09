---
schema_version: 1
id: doc-html-06-verification
code: PLAN-003.06
title: Verification Plan
kind: plan
status: approved
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
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
