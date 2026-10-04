---
schema_version: 1
id: doc-html-05-sample-data
code: PLAN-003.05
title: "Sample Data \u2014 YAML Configuration Files"
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

## Audit disposition (`phase-des-01`, 2026-10-04)

This plan is deprecated. On 2026-10-04 the owner retired the authored YAML content site that `PLAN-003` describes; [ADR-027](../../04-decisions/ADR-027-retire-plan-003.md) records the decision and what it leaves behind. Every requirement this document states is listed below with its disposition, as `REQ-021` R01 requires. Line numbers refer to this document above this section. An accomplished or superseded row names the shipped work, by file and commit or phase (`REQ-021` R03); a retired row gives the reason nothing will be built.

15 requirements: 15 retired.

| Id | Line | Requirement | Disposition | Evidence or reason |
|---|---|---|---|---|
| 05-R1 | 23-25 | NEW `_data/site.yaml`, converted to `_data/site.json` | retired | the authored YAML content site is retired (ADR-027) |
| 05-R2 | 28 | Site title `D-System` | retired | the authored YAML content site is retired (ADR-027) |
| 05-R3 | 29-35 | Routes `/` (home) and `/about` (about) | retired | the authored YAML content site is retired (ADR-027) |
| 05-R4 | 37-41 | Navigation: Home, About | retired | the authored YAML content site is retired (ADR-027) |
| 05-R5 | 44-57 | The exact `site.json` the conversion produces | retired | the authored YAML content site is retired (ADR-027) |
| 05-R6 | 64-66 | NEW `_data/pages/home.yaml`, a landing page | retired | the authored YAML content site is retired (ADR-027) |
| 05-R7 | 69-71 | Home: title, `landing` template, description | retired | the authored YAML content site is retired (ADR-027) |
| 05-R8 | 73-77 | Block `hero-1`: "Welcome to D-System" | retired | the authored YAML content site is retired (ADR-027) |
| 05-R9 | 78-84 | Block `intro-text` | retired | the authored YAML content site is retired (ADR-027) |
| 05-R10 | 89-91 | NEW `_data/pages/about.yaml`, a standard page | retired | the authored YAML content site is retired (ADR-027) |
| 05-R11 | 94-96 | About: title, `standard` template, description | retired | the authored YAML content site is retired (ADR-027) |
| 05-R12 | 98-104 | Block `about-text` describing D-System | retired | the authored YAML content site is retired (ADR-027) |
| 05-R13 | 111-116 | Authoring workflow: edit YAML, build, check the API, view the page | retired | the authored YAML content site is retired (ADR-027) |
| 05-R14 | 118-122 | Adding a page: YAML, route, build, refresh | retired | the authored YAML content site is retired (ADR-027) |
| 05-R15 | 124 | Tip: YAML comments, multi-line strings, anchors | retired | the authored YAML content site is retired (ADR-027) |
