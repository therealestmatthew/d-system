---
schema_version: 1
id: doc-html-02-backend
code: PLAN-003.02
title: "Backend \u2014 FastAPI Endpoints & Models"
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

# Backend — FastAPI Endpoints & Models

## Dependencies

### [MODIFY] `pyproject.toml`

Add PyYAML for the YAML→JSON conversion tool:

```diff
 dependencies = [
     "fastapi>=0.115",
     "uvicorn[standard]>=0.30",
     "duckdb>=1.1",
     "pydantic>=2.9",
     "pydantic-settings>=2.6",
+    "pyyaml>=6.0",
 ]
```

---

## Pydantic Models

### [NEW] `src/models/pages.py`

```python
from __future__ import annotations

from pydantic import BaseModel


class BlockContent(BaseModel, extra="allow"):
    """Flexible block content — shape varies by block type."""
    pass


class BlockData(BaseModel):
    id: str
    type: str
    content: BlockContent


class PageData(BaseModel):
    title: str
    template: str
    description: str = ""
    blocks: list[BlockData]


class RouteConfig(BaseModel):
    path: str
    pageId: str
    label: str = ""


class NavItem(BaseModel):
    label: str
    path: str


class SiteConfig(BaseModel):
    title: str
    routes: list[RouteConfig]
    navigation: list[NavItem] = []
```

> **Design Note**: `BlockContent` uses Pydantic's `extra="allow"` to accept arbitrary fields per block type. The TypeScript types on the frontend enforce the discriminated union; the backend stays flexible to avoid double-maintenance of block schemas.

---

## API Routes

### [NEW] `src/api/routes/pages.py`

Serves page content and site structure from `_data/` JSON files.

```python
"""Page configuration endpoints.

Serves page content and site structure from _data/ JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.models.pages import PageData, SiteConfig

router = APIRouter(prefix="/pages", tags=["pages"])

_DATA = Path(__file__).parent.parent.parent.parent / "_data"


def _read_json(path: Path) -> dict:
    """Read and parse a JSON file, raising 404 if missing."""
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Config not found: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


@router.get("/site-config", response_model=SiteConfig)
async def get_site_config() -> SiteConfig:
    """Return the site-wide routing and navigation config."""
    data = _read_json(_DATA / "site.json")
    return SiteConfig(**data)


@router.get("/{page_id}", response_model=PageData)
async def get_page(page_id: str) -> PageData:
    """Return a single page config by ID.

    The page_id is validated to prevent path traversal.
    """
    # Sanitize: only allow alphanumeric, hyphens, underscores
    if not all(c.isalnum() or c in "-_" for c in page_id):
        raise HTTPException(status_code=400, detail="Invalid page ID")

    data = _read_json(_DATA / "pages" / f"{page_id}.json")
    return PageData(**data)
```

### Security

- **Path traversal prevention**: `page_id` is validated to only contain `[a-zA-Z0-9_-]` before being used in file path construction.
- **404 on missing**: Missing files return proper HTTP 404, not stack traces.
- **Pydantic validation**: Response data is validated through Pydantic models before being serialized.

---

## Router Registration

### [MODIFY] `src/api/__init__.py`

Append the pages router to the existing API router:

```diff
 from fastapi import APIRouter

 router = APIRouter(prefix="/api/v1")

+from src.api.routes.pages import router as pages_router
+router.include_router(pages_router)
```

This creates the following endpoints:
- `GET /api/v1/pages/site-config` — site-wide config
- `GET /api/v1/pages/{page_id}` — individual page data
