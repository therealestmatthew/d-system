---
schema_version: 1
id: doc-html-01-build-tooling
code: PLAN-003.01
title: Build Tooling & Schemas
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

# Build Tooling & Schemas

## YAML → JSON Conversion Tool

### [NEW] `tools/build_pages.py`

Converts YAML page configs to JSON. Mirrors the pattern of `tools/rebuild_db.py`.

Run after editing any `_data/pages/*.yaml` or `_data/site.yaml`:

```bash
uv run python tools/build_pages.py
```

#### Implementation

```python
#!/usr/bin/env python3
"""Convert YAML page configs to validated JSON.

Run after editing any _data/pages/*.yaml or _data/site.yaml:
    uv run python tools/build_pages.py
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
DATA = ROOT / "_data"


def convert_file(yaml_path: Path) -> None:
    """Convert a single YAML file to JSON alongside it."""
    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    json_path = yaml_path.with_suffix(".json")
    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  {yaml_path.name} → {json_path.name}")


def build() -> None:
    # Convert site.yaml
    site_yaml = DATA / "site.yaml"
    if site_yaml.exists():
        convert_file(site_yaml)

    # Convert all page YAMLs
    pages_dir = DATA / "pages"
    if not pages_dir.exists():
        pages_dir.mkdir(parents=True)
        print(f"Created {pages_dir}")
        return

    yaml_files = sorted(pages_dir.glob("*.yaml")) + sorted(pages_dir.glob("*.yml"))
    if not yaml_files:
        print("No YAML page files found in _data/pages/")
        return

    print("Converting page configs:")
    for yf in yaml_files:
        convert_file(yf)

    print(f"\nConverted {len(yaml_files)} file(s).")


if __name__ == "__main__":
    build()
```

---

## JSON Schemas

### [NEW] `schemas/site.schema.json`

Validates the site-level routing and navigation configuration.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Site Configuration",
  "type": "object",
  "required": ["title", "routes"],
  "properties": {
    "title": { "type": "string" },
    "routes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "pageId"],
        "properties": {
          "path": { "type": "string", "pattern": "^/" },
          "pageId": { "type": "string", "pattern": "^[a-z0-9_-]+$" },
          "label": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "navigation": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "path": { "type": "string" }
        },
        "required": ["label", "path"]
      }
    }
  },
  "additionalProperties": false
}
```

---

### [NEW] `schemas/page.schema.json`

Validates individual page configurations with typed block content.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Page Configuration",
  "type": "object",
  "required": ["title", "template", "blocks"],
  "properties": {
    "title": { "type": "string" },
    "template": { "type": "string", "enum": ["standard", "landing"] },
    "description": { "type": "string" },
    "blocks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type", "content"],
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string", "enum": ["hero", "text", "image", "columns"] },
          "content": { "type": "object" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

> **Note**: The `pageId` pattern in `site.schema.json` (`^[a-z0-9_-]+$`) prevents path traversal attacks at the schema validation level, complementing the server-side sanitization in `src/api/routes/pages.py`.

## Audit disposition (`phase-des-01`, 2026-10-04)

This plan is deprecated. On 2026-10-04 the owner retired the authored YAML content site that `PLAN-003` describes; [ADR-027](../../04-decisions/ADR-027-retire-plan-003.md) records the decision and what it leaves behind. Every requirement this document states is listed below with its disposition, as `REQ-021` R01 requires. Line numbers refer to this document above this section. An accomplished or superseded row names the shipped work, by file and commit or phase (`REQ-021` R03); a retired row gives the reason nothing will be built.

17 requirements: 17 retired.

| Id | Line | Requirement | Disposition | Evidence or reason |
|---|---|---|---|---|
| 01-R1 | 23-25 | NEW `tools/build_pages.py`, converting YAML page configuration to JSON | retired | the authored YAML content site is retired (ADR-027) |
| 01-R2 | 27-31, 39-40 | Run the converter after editing `_data/pages/*.yaml` or `_data/site.yaml` | retired | the authored YAML content site is retired (ADR-027) |
| 01-R3 | 54-63 | `convert_file`: `yaml.safe_load`, then JSON written next to the source | retired | the authored YAML content site is retired (ADR-027) |
| 01-R4 | 67-70 | Convert `_data/site.yaml` if it exists, skipping silently otherwise | retired | the authored YAML content site is retired (ADR-027). ARCH-003 H2 had already rejected the silent skip |
| 01-R5 | 73-77 | Create `_data/pages/` when missing | retired | the authored YAML content site is retired (ADR-027) |
| 01-R6 | 79 | Discover `*.yaml` and `*.yml` in `_data/pages/`, sorted | retired | the authored YAML content site is retired (ADR-027) |
| 01-R7 | 80-82 | Report "No YAML page files found" for an empty directory | retired | the authored YAML content site is retired (ADR-027) |
| 01-R8 | 84-88 | Print progress and "Converted N file(s)." | retired | the authored YAML content site is retired (ADR-027) |
| 01-R9 | 99-105 | Create `schemas/site.schema.json`, draft 2020-12 | retired | the authored YAML content site is retired (ADR-027) |
| 01-R10 | 108-110, 136 | Site requires `title` and `routes`, optional `navigation`, no extra properties | retired | the authored YAML content site is retired (ADR-027) |
| 01-R11 | 111-122 | Route item: `path` matching `^/`, `pageId` matching `^[a-z0-9_-]+$`, optional `label` | retired | the authored YAML content site is retired (ADR-027) |
| 01-R12 | 124-134 | Navigation items require `label` and `path` | retired | the authored YAML content site is retired (ADR-027) |
| 01-R13 | 142-144 | Create `schemas/page.schema.json` | retired | the authored YAML content site is retired (ADR-027) |
| 01-R14 | 151-156, 170 | Page requires `title`, `template`, `blocks`; optional `description` | retired | the authored YAML content site is retired (ADR-027) |
| 01-R15 | 154 | `template` enum `standard` / `landing` | retired | the authored YAML content site is retired (ADR-027). Page templates are the house family's (`templates/html/house-page.html`, 49b0ca2) |
| 01-R16 | 158-166 | Block item: `id`, `type` (hero/text/image/columns), free-form `content` object | retired | the authored YAML content site is retired (ADR-027). GOV-003 had already overruled the free-form `content` |
| 01-R17 | 174 | `pageId` pattern blocks path traversal at the schema level | retired | no `/api/v1/pages` backend will exist (ADR-027) |
