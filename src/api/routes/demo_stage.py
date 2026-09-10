"""Read routes the demo stage page needs — talking points, overview location, and whether the
terminal route exists.

Unlike `src/api/routes/demo_terminal.py`, this module carries no capability of its own: all
three routes only read from the filesystem or the process's own environment and return what
they find, never a computed or model-derived value. All three routes are registered
unconditionally in `src/api/__init__.py` — nothing here is gated by `D_SYSTEM_DEMO_TERMINAL`
itself (ADR-013 governs the terminal capability only); `terminal-enabled` merely reports that
flag's value, it does not depend on it to exist.

`terminal-enabled` exists because a failed browser WebSocket upgrade exposes no HTTP status to
JavaScript, and a plain GET on the terminal's `/ws` path returns 404 whether the flag is set or
not — so the frontend has no reliable way to distinguish "the terminal route was never
registered" from any other websocket failure by probing the websocket path itself. This route
gives it that signal directly, on an ordinary GET, so the stage page (`phase-demo-02`) can show
a clear in-page message when the terminal is absent rather than a generic connection error.
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

# Mirrors the flag name `src/api/__init__.py` checks to decide whether to import
# `src.api.routes.demo_terminal` at all, and the flag `src/api/routes/demo_terminal.py` itself
# checks in its own loopback-bind enforcement. Not imported from either module: importing
# `demo_terminal` here would run its loopback-bind fail-fast as a side effect of import,
# unconditionally, regardless of this flag's value — exactly what registering this route
# unconditionally is meant to avoid.
DEMO_TERMINAL_FLAG_ENV_VAR: Final[str] = "D_SYSTEM_DEMO_TERMINAL"
DEMO_TERMINAL_FLAG_ENABLED_VALUE: Final[str] = "1"

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


@router.get("/terminal-enabled")
async def get_terminal_enabled() -> dict[str, bool]:
    """Whether `D_SYSTEM_DEMO_TERMINAL` is active in this process, right now.

    A plain GET here always succeeds and reports the flag's actual value — unlike probing the
    terminal websocket path directly, whose failure the browser exposes to JavaScript as an
    undifferentiated close event, with no HTTP status to tell "route never registered" apart
    from any other connection failure. This is the reliable signal `phase-demo-02`'s stage page
    uses to show a clear in-page message when the terminal capability is absent (ADR-013).
    """
    enabled = os.environ.get(DEMO_TERMINAL_FLAG_ENV_VAR) == DEMO_TERMINAL_FLAG_ENABLED_VALUE
    return {"terminal_enabled": enabled}
