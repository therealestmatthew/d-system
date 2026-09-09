---
schema_version: 1
id: doc-html-05-sample-data
code: PLAN-003.05
title: "Sample Data \u2014 YAML Configuration Files"
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

# Sample Data — YAML Configuration Files

## Site Configuration

### [NEW] `_data/site.yaml`

Top-level routing and navigation. Converted to `_data/site.json` by `tools/build_pages.py`.

```yaml
title: D-System
routes:
  - path: /
    pageId: home
    label: Home
  - path: /about
    pageId: about
    label: About

navigation:
  - label: Home
    path: /
  - label: About
    path: /about
```

**After conversion**, `_data/site.json` will contain:

```json
{
  "title": "D-System",
  "routes": [
    { "path": "/", "pageId": "home", "label": "Home" },
    { "path": "/about", "pageId": "about", "label": "About" }
  ],
  "navigation": [
    { "label": "Home", "path": "/" },
    { "label": "About", "path": "/about" }
  ]
}
```

---

## Page Configurations

### [NEW] `_data/pages/home.yaml`

Landing page with a hero block and intro text.

```yaml
title: Home
template: landing
description: D-System dashboard landing page
blocks:
  - id: hero-1
    type: hero
    content:
      headline: Welcome to D-System
      subheadline: Consulting management, powered by configuration.
  - id: intro-text
    type: text
    content:
      body: >
        D-System centralizes work responsibilities — tracking people,
        projects, commitments, and tasks — reducing mental overhead
        through structured data and dynamic page generation.
```

---

### [NEW] `_data/pages/about.yaml`

Standard page with a text block.

```yaml
title: About
template: standard
description: About the D-System project
blocks:
  - id: about-text
    type: text
    content:
      body: >
        D-System is a personal consulting management system that doubles
        as a platform for HTML generation, reporting, and agentic
        workflow triggering.
```

---

## Authoring Workflow

```
1. Create/edit  _data/pages/my-page.yaml
2. Run          uv run python tools/build_pages.py
3. Verify       curl http://localhost:8000/api/v1/pages/my-page
4. View         http://localhost:5173/my-page
```

To add a new page:
1. Create `_data/pages/<pageId>.yaml`
2. Add a route entry to `_data/site.yaml`
3. Run `uv run python tools/build_pages.py`
4. Restart/refresh the frontend

> **Tip**: YAML supports comments (`# ...`), multi-line strings (`>`, `|`), and anchors/aliases for reuse — making it much friendlier for authoring than raw JSON.
