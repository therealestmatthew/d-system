"""Read routes the demo stage page needs — talking points and overview location.

Unlike `src/api/routes/demo_terminal.py`, this module carries no capability of its own: both
routes only read from the filesystem and return what they find, never a computed or model-derived
value. Both routes are registered unconditionally in `src/api/__init__.py` — nothing here is
gated by `D_SYSTEM_DEMO_TERMINAL` (ADR-013 governs the terminal capability only).
"""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Final

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

# Repository root: three levels above this file (src/api/routes/demo_stage.py -> src/api ->
# src -> repo root).
REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

TALKING_POINTS_PATH_ENV_VAR: Final[str] = "D_SYSTEM_TALKING_POINTS_PATH"
DEFAULT_TALKING_POINTS_PATH: Final[Path] = REPO_ROOT / "ts" / "public" / "talking-points.json"

OVERVIEW_PAGE_PATH_ENV_VAR: Final[str] = "D_SYSTEM_OVERVIEW_PAGE_PATH"
DEFAULT_OVERVIEW_PAGE_PATH: Final[Path] = REPO_ROOT / "_public" / "d-system-overview.html"

router = APIRouter()


def resolve_talking_points_path() -> Path:
    """The talking-points data file — `D_SYSTEM_TALKING_POINTS_PATH` if set, else the default
    location under `ts/public/` (REQ-006 R01: a talking-points panel loaded from a data file,
    not hardcoded).
    """
    override = os.environ.get(TALKING_POINTS_PATH_ENV_VAR)
    if override:
        return Path(override)
    return DEFAULT_TALKING_POINTS_PATH


def resolve_overview_page_path() -> Path:
    """The generated overview page's location under `_public/` — `D_SYSTEM_OVERVIEW_PAGE_PATH`
    if set, else the default filename. The file itself is produced by the `d-system-overview`
    skill (REQ-006 R08, `phase-demo-04`); this route only reports where it lives.
    """
    override = os.environ.get(OVERVIEW_PAGE_PATH_ENV_VAR)
    if override:
        return Path(override)
    return DEFAULT_OVERVIEW_PAGE_PATH


@router.get("/talking-points")
async def get_talking_points() -> FileResponse:
    """The talking-points data file's content, unchanged — no parsing, no re-serialization.

    404 with a clear message when the file does not exist, rather than an opaque error, since
    the file is authored separately (`phase-demo-05`) and is genuinely absent until then.
    """
    path = resolve_talking_points_path()
    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Talking-points data file not found at {path}.",
        )
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type)


@router.get("/overview-location")
async def get_overview_location() -> dict[str, str]:
    """Where the generated overview page lives under `_public/` — path only, not its content.

    The frontend embeds the page itself (REQ-006 R01c); this route exists so the stage page
    never hardcodes that path. The file may not exist yet (it is produced by the
    `d-system-overview` skill, `phase-demo-04`) — reporting the configured location is this
    route's whole job, so it does not check for the file's existence.
    """
    path = resolve_overview_page_path()
    if path.is_relative_to(REPO_ROOT):
        return {"path": str(path.relative_to(REPO_ROOT))}
    return {"path": str(path)}
