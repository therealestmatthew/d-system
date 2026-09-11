"""The workbench read routes (ADR-015): injection-source enumeration, directory listing,
recursive file search, idea and backlog explorers, and the single reveal-in-explorer action.

Every route here is mounted only when `D_SYSTEM_DEMO_TERMINAL=1` —
`src/api/__init__.py` imports this module only under that flag, exactly like
`src/api/routes/demo_terminal.py`, so with the flag unset none of these routes exist (404), not
merely refuse. Importing this module also
re-runs `enforce_loopback_bind()` (ADR-015 rule 1: "one gate, one binding"), so a launch with the
flag set on a non-loopback bind host fails fast here too, independent of whether
`src.api.routes.demo_terminal` happened to be imported first.

Five capabilities, all read-only except the one named action (ADR-015 rule 4):

- `GET /injection-sources` live-enumerates `.claude/skills/`, `.claude/agents/` and
  `docs/02-prompts/` (governed `PROMPT-*` files only), applying the curated overrides file
  `_data/workbench/injection-overrides.json` (relabel, replace injected text, or hide, per entry).
- `GET /list` (one level) and `GET /search` (recursive, file filter) walk the repository tree
  rooted at a caller-supplied repository-relative path, validated against `REPO_ROOT` on the
  *resolved* path — traversal, absolute escapes, and symlink escapes are all caught the same way,
  by checking where the resolved path actually lands. Both exclude `.git` and anything
  `git check-ignore` reports as ignored (ADR-015 rule 3): the repository's own ignore rules, not a
  hand-kept list, so `_private/`, `.venv/`, `data/`, `node_modules/`, etc. are never listed while
  `_public/` and the tracked tree are.
- `GET /absolute-path` resolves a caller-supplied repository-relative path the same way (ADR-015
  rule 2) and reports the absolute filesystem path it names — "the repository root joined
  server-side", per ADR-015's consequences ("Copy-absolute-path (W09) is served from the
  backend's knowledge of the repository root"), for the File Browser's copy-absolute-path action.
- `GET /ideas` and `GET /ideas/queue` read idea state exclusively through `load_events()` and
  `fold()` (`src/db/ideas.py`) — never a direct parse of `_data/ideas.jsonl` — and report id,
  title, status, created/updated, annotation count and link count per idea; the `queue` variant
  ranks by status precedence then age (see `IDEA_QUEUE_STATUS_PRECEDENCE` below for the one
  wording correction this applies against REQ-007 W10's literal text).
- `GET /backlog` and `GET /backlog/queue` read `docs/09-backlog/backlog.yaml` and report id,
  title, status, priority, queue position (`next_up` index, or null) and `depends_on` per phase;
  the `queue` variant reuses `queue_order()` and `readiness()` from `src.governance.backlog`
  directly, so it matches the governance `--ready` rendering by construction rather than by a
  second, hand-kept ordering rule.
- `POST /reveal` is the sole non-GET route: it validates its path per rule 2 above, refuses a
  path `_private/` or `git check-ignore` would exclude from the listing routes (the same check
  `_git_ignored_paths` performs there, applied here to the single resolved path before spawning
  anything), then spawns exactly one fixed opener via an argument list, never a shell string
  (ADR-015 rule 5).
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import yaml  # type: ignore[import-untyped]
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.api.routes.demo_terminal import enforce_loopback_bind
from src.db.ideas import fold, load_events
from src.governance.backlog import queue_order, readiness

# Repository root: three levels above this file (src/api/routes/workbench.py -> src/api ->
# src -> repo root) — same derivation as src/api/routes/demo_stage.py.
REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

SKILLS_DIR: Final[Path] = REPO_ROOT / ".claude" / "skills"
AGENTS_DIR: Final[Path] = REPO_ROOT / ".claude" / "agents"
PROMPTS_DIR: Final[Path] = REPO_ROOT / "docs" / "02-prompts"
PROMPT_FILENAME_PREFIX: Final[str] = "PROMPT-"

INJECTION_OVERRIDES_PATH_ENV_VAR: Final[str] = "D_SYSTEM_WORKBENCH_OVERRIDES_PATH"
DEFAULT_INJECTION_OVERRIDES_PATH: Final[Path] = (
    REPO_ROOT / "_data" / "workbench" / "injection-overrides.json"
)

INJECTION_CATEGORIES: Final[tuple[str, ...]] = ("skills", "agents", "prompts")

# Names never listed regardless of git's ignore rules: `.git` is the repository's own metadata,
# not tracked content or a shareable output (ADR-015's "what the repository tracks plus its
# shareable outputs"), and `git check-ignore` does not flag it because no `.gitignore` pattern
# names it.
ALWAYS_EXCLUDED_NAMES: Final[frozenset[str]] = frozenset({".git"})

router = APIRouter()


class InjectionSourceEntry(BaseModel):
    id: str
    label: str
    injection: str


class InjectionSources(BaseModel):
    skills: list[InjectionSourceEntry]
    agents: list[InjectionSourceEntry]
    prompts: list[InjectionSourceEntry]


class DirectoryEntry(BaseModel):
    name: str
    path: str
    is_dir: bool


class AbsolutePathResult(BaseModel):
    absolute_path: str


class PathEscapesRepositoryError(ValueError):
    """Raised when a caller-supplied path does not resolve inside `REPO_ROOT`."""


BACKLOG_PATH: Final[Path] = REPO_ROOT / "docs" / "09-backlog" / "backlog.yaml"

REVEAL_WINDOWS_OPENER: Final[str] = "explorer.exe"
REVEAL_LINUX_OPENER: Final[str] = "xdg-open"


# --- Path validation (ADR-015 rule 2) ---------------------------------------------------------


def resolve_repo_relative_path(raw_path: str) -> Path:
    """The absolute, resolved path `raw_path` names — repository-relative input only.

    Validation happens on the *resolved* path, per ADR-015: an absolute input is rejected
    outright (the API takes repository-relative paths only, per REQ-007 W07); a relative input
    is joined onto `REPO_ROOT` and resolved (following symlinks), and the result must land
    inside `REPO_ROOT` — this one check catches `..` traversal and a symlink whose target leaves
    the repository the same way, since both simply produce a resolved path outside the root.
    """
    candidate = Path(raw_path) if raw_path else Path(".")
    if candidate.is_absolute():
        raise PathEscapesRepositoryError(f"Absolute paths are not accepted: {raw_path!r}")
    resolved = (REPO_ROOT / candidate).resolve()
    if resolved != REPO_ROOT and REPO_ROOT not in resolved.parents:
        raise PathEscapesRepositoryError(f"Path escapes the repository root: {raw_path!r}")
    return resolved


# --- git-ignore-aware filesystem walking (ADR-015 rule 3) -------------------------------------


def _git_ignored_paths(paths: list[Path]) -> set[Path]:
    """The subset of `paths` (which must all exist under `REPO_ROOT`) that `git check-ignore`
    reports as ignored — one subprocess call for the whole batch, using `-z` so pathnames with
    unusual characters cannot be misparsed. Non-ignored paths are simply absent from the tool's
    output; a non-zero exit status (no path matched) is not an error here.
    """
    if not paths:
        return set()
    relative = [str(path.relative_to(REPO_ROOT)) for path in paths]
    payload = b"\0".join(part.encode() for part in relative) + b"\0"
    result = subprocess.run(
        ["git", "check-ignore", "-v", "-z", "--stdin"],
        input=payload,
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    ignored: set[Path] = set()
    if not result.stdout:
        return ignored
    # -v -z emits four NUL-separated fields per ignored path: source, line number, pattern,
    # pathname — with a trailing NUL after the last record.
    fields = result.stdout.split(b"\0")
    for index in range(0, len(fields) - 3, 4):
        pathname = fields[index + 3].decode()
        if pathname:
            ignored.add(REPO_ROOT / pathname)
    return ignored


def _visible_children(directory: Path) -> list[Path]:
    """`directory`'s immediate children, `.git` and gitignored entries excluded."""
    children = [child for child in directory.iterdir() if child.name not in ALWAYS_EXCLUDED_NAMES]
    ignored = _git_ignored_paths(children)
    return sorted(child for child in children if child not in ignored)


def _walk_visible_tree(start: Path) -> list[Path]:
    """Every non-ignored file and directory under `start`, `.git` and ignored directories pruned
    before descending into them — so a large ignored subtree (`.venv/`, `node_modules/`) is never
    even scanned. Symlinked directories are listed but not followed, so a symlink cannot walk
    this search outside the repository or into a cycle.
    """
    results: list[Path] = []
    stack = [start]
    while stack:
        current = stack.pop()
        try:
            children = _visible_children(current)
        except (PermissionError, NotADirectoryError):
            continue
        for child in children:
            results.append(child)
            if child.is_dir() and not child.is_symlink():
                stack.append(child)
    return results


def _to_entry(path: Path) -> DirectoryEntry:
    return DirectoryEntry(
        name=path.name,
        path=path.relative_to(REPO_ROOT).as_posix(),
        is_dir=path.is_dir(),
    )


def _normalize_extensions(extensions: list[str] | None) -> set[str] | None:
    if not extensions:
        return None
    return {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions}


def _matches_filters(
    path: Path, *, extensions: set[str] | None, text_filter: str | None
) -> bool:
    if extensions is not None and path.suffix.lower() not in extensions:
        return False
    if text_filter is not None and text_filter.lower() not in path.name.lower():
        return False
    return True


# --- Injection-source enumeration (ADR-015 rule 4, REQ-007 W04) -------------------------------


def _enumerate_skills() -> list[InjectionSourceEntry]:
    """One entry per subdirectory of `.claude/skills/`; a skill's invocation is `/<skill-name>`."""
    if not SKILLS_DIR.is_dir():
        return []
    names = sorted(entry.name for entry in SKILLS_DIR.iterdir() if entry.is_dir())
    return [
        InjectionSourceEntry(id=name, label=name, injection=f"/{name}") for name in names
    ]


def _enumerate_agents() -> list[InjectionSourceEntry]:
    """One entry per `.claude/agents/*.md` file, keyed by filename stem.

    The dispatch phrase is injected with the cursor intended at the trailing space — the caller
    types the rest, nothing here executes on selection.
    """
    if not AGENTS_DIR.is_dir():
        return []
    names = sorted(
        entry.stem for entry in AGENTS_DIR.iterdir() if entry.is_file() and entry.suffix == ".md"
    )
    return [
        InjectionSourceEntry(id=name, label=name, injection=f"Use the {name} agent to ")
        for name in names
    ]


def _enumerate_prompts() -> list[InjectionSourceEntry]:
    """One entry per governed `PROMPT-*.md` file directly under `docs/02-prompts/` — `README.md`
    and other non-`PROMPT-*` files there (e.g. `codex_governance_prompt.md`) are not governed
    prompt documents and are excluded.
    """
    if not PROMPTS_DIR.is_dir():
        return []
    names = sorted(
        entry.name
        for entry in PROMPTS_DIR.iterdir()
        if entry.is_file()
        and entry.suffix == ".md"
        and entry.name.startswith(PROMPT_FILENAME_PREFIX)
    )
    return [
        InjectionSourceEntry(
            id=name,
            label=name,
            injection=(
                f"Execute docs/02-prompts/{name}: read it in full and follow its prompt block"
            ),
        )
        for name in names
    ]


def _resolve_overrides_path() -> Path:
    override = os.environ.get(INJECTION_OVERRIDES_PATH_ENV_VAR)
    return Path(override) if override else DEFAULT_INJECTION_OVERRIDES_PATH


def _empty_overrides() -> dict[str, dict[str, Any]]:
    return {category: {} for category in INJECTION_CATEGORIES}


def _load_overrides() -> dict[str, dict[str, Any]]:
    """The curated overrides file, one section per category — missing, unreadable, or malformed
    is treated as "no active overrides" rather than an error, since this route must stay
    available even if the data file is briefly invalid mid-edit.
    """
    path = _resolve_overrides_path()
    if not path.is_file():
        return _empty_overrides()
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError:
        return _empty_overrides()
    if not isinstance(raw, dict):
        return _empty_overrides()
    return {
        category: raw[category] if isinstance(raw.get(category), dict) else {}
        for category in INJECTION_CATEGORIES
    }


def _apply_overrides(
    entries: list[InjectionSourceEntry], overrides: dict[str, Any]
) -> list[InjectionSourceEntry]:
    """Apply one category's overrides section: relabel, replace injected text, or hide, keyed by
    entry id. Ids in `overrides` with no matching enumerated entry are silently unused — the data
    file may be curated ahead of a source appearing or after it disappears.
    """
    result: list[InjectionSourceEntry] = []
    for entry in entries:
        override = overrides.get(entry.id)
        if not isinstance(override, dict):
            result.append(entry)
            continue
        if override.get("hidden") is True:
            continue
        result.append(
            InjectionSourceEntry(
                id=entry.id,
                label=override.get("label", entry.label),
                injection=override.get("injection", entry.injection),
            )
        )
    return result


@router.get("/injection-sources", response_model=InjectionSources)
async def get_injection_sources() -> InjectionSources:
    overrides = _load_overrides()
    return InjectionSources(
        skills=_apply_overrides(_enumerate_skills(), overrides["skills"]),
        agents=_apply_overrides(_enumerate_agents(), overrides["agents"]),
        prompts=_apply_overrides(_enumerate_prompts(), overrides["prompts"]),
    )


# --- Directory listing and recursive file search (ADR-015 rules 2 and 3) ----------------------


@router.get("/list", response_model=list[DirectoryEntry])
async def list_directory(
    path: str = ".",
    ext: list[str] | None = Query(default=None),
    q: str | None = Query(default=None),
) -> list[DirectoryEntry]:
    """The immediate, non-ignored children of a repository-relative directory."""
    try:
        resolved = resolve_repo_relative_path(path)
    except PathEscapesRepositoryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not resolved.is_dir():
        raise HTTPException(status_code=404, detail=f"Not a directory: {path!r}")
    extensions = _normalize_extensions(ext)
    children = _visible_children(resolved)
    return [
        _to_entry(child)
        for child in children
        if _matches_filters(child, extensions=extensions, text_filter=q)
    ]


@router.get("/search", response_model=list[DirectoryEntry])
async def search_files(
    path: str = ".",
    ext: list[str] | None = Query(default=None),
    q: str | None = Query(default=None),
) -> list[DirectoryEntry]:
    """Every non-ignored *file* found recursively under a repository-relative directory,
    optionally narrowed by an extension filter (e.g. `.html`/`.svg` for the HTML Viewer, REQ-007
    W07) and a case-insensitive text filter on filenames.
    """
    try:
        resolved = resolve_repo_relative_path(path)
    except PathEscapesRepositoryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not resolved.is_dir():
        raise HTTPException(status_code=404, detail=f"Not a directory: {path!r}")
    extensions = _normalize_extensions(ext)
    files = [entry for entry in _walk_visible_tree(resolved) if entry.is_file()]
    matched = [
        entry for entry in files if _matches_filters(entry, extensions=extensions, text_filter=q)
    ]
    return [_to_entry(entry) for entry in sorted(matched)]


# --- Copy absolute path (ADR-015 consequences, REQ-007 W09) -----------------------------------


@router.get("/absolute-path", response_model=AbsolutePathResult)
async def get_absolute_path(path: str = ".") -> AbsolutePathResult:
    """The absolute filesystem path a repository-relative `path` resolves to, validated
    identically to `/list` and `/search` (ADR-015 rule 2) — the repository root joined
    server-side, never trusting a client-supplied absolute path.
    """
    try:
        resolved = resolve_repo_relative_path(path)
    except PathEscapesRepositoryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"No such path: {path!r}")
    return AbsolutePathResult(absolute_path=str(resolved))


# --- Idea Explorer (ADR-015 rule 4, REQ-007 W10) -----------------------------------------------


class IdeaRow(BaseModel):
    id: str
    title: str
    status: str
    created: str
    updated: str
    annotation_count: int
    link_count: int


#: Status precedence for the queue-ordered view. REQ-007 W10's own text reads "open → triaged →
#: planned then age", but `planned` is not a legal idea status (`schemas/idea.schema.json`
#: enumerates `open`, `triaged`, `reviewing`, `promoted`, `discarded`) — it never matches any
#: idea and would leave the third tier permanently empty. `docs/01-plans/PLAN-019-idea-priority-
#: queue.md`, which predates and motivates that requirement row, names the identical three-tier
#: working precedence as "open before triaged before reviewing", so `reviewing` is applied here
#: as the evident wording correction for `planned`. `promoted` and `discarded` are terminal
#: (`src/db/ideas.py`'s `WORKING_STATES` excludes both) and rank after the three working states,
#: tied with each other, so the queue view still surfaces every idea rather than dropping ones
#: past scouting.
IDEA_QUEUE_STATUS_PRECEDENCE: Final[dict[str, int]] = {
    "open": 0,
    "triaged": 1,
    "reviewing": 2,
    "promoted": 3,
    "discarded": 3,
}

#: Precedence assigned to a status this mapping does not recognize — schema-illegal today, but a
#: deterministic fallback (last, not an error) keeps this route from ever refusing to answer over
#: a status it does not yet know about.
_IDEA_QUEUE_UNKNOWN_STATUS_PRECEDENCE: Final[int] = max(IDEA_QUEUE_STATUS_PRECEDENCE.values()) + 1


def _idea_row(idea_id: str, entry: dict[str, Any]) -> IdeaRow:
    return IdeaRow(
        id=idea_id,
        title=entry["title"],
        status=entry["status"],
        created=entry["created"],
        updated=entry["updated"],
        annotation_count=len(entry["annotations"]),
        link_count=len(entry["links"]),
    )


def _load_idea_state() -> dict[str, dict[str, Any]]:
    """Idea state exclusively via `load_events()` + `fold()` — never a raw parse of the log."""
    return fold(load_events())


def _idea_queue_sort_key(idea_id: str, entry: dict[str, Any]) -> tuple[int, datetime, str]:
    precedence = IDEA_QUEUE_STATUS_PRECEDENCE.get(
        entry["status"], _IDEA_QUEUE_UNKNOWN_STATUS_PRECEDENCE
    )
    return (precedence, datetime.fromisoformat(entry["created"]), idea_id)


@router.get("/ideas", response_model=list[IdeaRow])
async def get_ideas() -> list[IdeaRow]:
    """Every idea, id order — deterministic, and zero ideas is an empty list, not an error."""
    state = _load_idea_state()
    return [_idea_row(idea_id, entry) for idea_id, entry in sorted(state.items())]


@router.get("/ideas/queue", response_model=list[IdeaRow])
async def get_ideas_queue() -> list[IdeaRow]:
    """The priority-queue view: status precedence, then age (oldest first), then id."""
    state = _load_idea_state()
    ordered = sorted(state.items(), key=lambda pair: _idea_queue_sort_key(*pair))
    return [_idea_row(idea_id, entry) for idea_id, entry in ordered]


# --- Backlog Explorer (ADR-015 rule 4, REQ-007 W11) ---------------------------------------------


class BacklogPhaseRow(BaseModel):
    id: str
    title: str
    status: str
    priority: int
    queue_position: int | None
    depends_on: list[str]


def _load_backlog_catalog() -> dict[str, Any]:
    """`docs/09-backlog/backlog.yaml`, parsed with no schema validation of its own — this route
    only reports what governance has already accepted, the same file `uv run python -m
    src.governance` validates on every run.
    """
    raw = yaml.safe_load(BACKLOG_PATH.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _backlog_row(item: dict[str, Any], next_up: list[str]) -> BacklogPhaseRow:
    return BacklogPhaseRow(
        id=item["id"],
        title=item["title"],
        status=item["status"],
        priority=item["priority"],
        queue_position=(next_up.index(item["id"]) + 1) if item["id"] in next_up else None,
        depends_on=list(item["depends_on"]),
    )


@router.get("/backlog", response_model=list[BacklogPhaseRow])
async def get_backlog() -> list[BacklogPhaseRow]:
    """Every phase, id order — deterministic, independent of `next_up` or readiness."""
    catalog = _load_backlog_catalog()
    items = {item["id"]: item for item in catalog.get("items", [])}
    next_up = catalog.get("next_up", [])
    return [_backlog_row(items[key], next_up) for key in sorted(items)]


@router.get("/backlog/queue", response_model=list[BacklogPhaseRow])
async def get_backlog_queue() -> list[BacklogPhaseRow]:
    """The priority-queue view, matching `uv run python -m src.governance --ready` by
    construction: `queue_order()` places `next_up` phases first in listed order, then the rest
    by priority then id (both from `src.governance.backlog`, the same functions that command
    uses); the result is then narrowed to `readiness() == "ready"`, exactly as that command's
    `--ready` rendering does — a `next_up` phase that is not itself ready (already active, still
    waiting on a dependency, and so on) is excluded here exactly as it is there.
    """
    catalog = _load_backlog_catalog()
    items = {item["id"]: item for item in catalog.get("items", [])}
    next_up = catalog.get("next_up", [])
    ordered = queue_order(items, next_up)
    ready = [item for item in ordered if readiness(item, items) == "ready"]
    return [_backlog_row(item, next_up) for item in ready]


# --- Reveal-in-explorer (ADR-015 rule 5, REQ-007 W09) -------------------------------------------


class RevealRequest(BaseModel):
    path: str


class RevealResult(BaseModel):
    opened: str


def _is_reveal_excluded(resolved: Path) -> bool:
    """`True` if `resolved` is `_private/` (or anywhere under it) or otherwise `git
    check-ignore`d — the same exclusion `_visible_children`/`_walk_visible_tree` apply to the
    listing routes via `_git_ignored_paths`, reused here on the single resolved path so `/reveal`
    cannot spawn an opener on a path the listing routes would never show. `_private/` is itself
    listed in `.gitignore`, so this one call covers both; `resolved` is required to exist (the
    caller checks that first), which `_git_ignored_paths` requires.
    """
    return bool(_git_ignored_paths([resolved]))


def _is_windows() -> bool:
    return platform.system() == "Windows"


def _reveal_argv(resolved: Path) -> list[str]:
    """The one fixed opener argument list for `resolved` — an argument list, never a shell
    string, per ADR-015 rule 5. On Windows, `explorer.exe /select,<path>` opens the entry's
    parent folder with the entry itself selected, for a file or a directory alike. On Linux,
    `xdg-open` has no selection concept, so it is given a directory to open outright: a file's
    parent directory, or the directory itself when the entry already is one — never that
    directory's own parent, which keeps the opened target inside the repository even when the
    entry is the repository root itself.
    """
    if _is_windows():
        return [REVEAL_WINDOWS_OPENER, f"/select,{resolved}"]
    target_dir = resolved.parent if resolved.is_file() else resolved
    return [REVEAL_LINUX_OPENER, str(target_dir)]


def _launch_reveal_opener(argv: list[str]) -> None:
    """Spawn the opener without waiting for it — a file manager window is not expected to exit
    promptly, and this route reports success once the process is launched, not once it closes.
    Isolated in its own function so tests can monkeypatch it and assert on `argv` without ever
    starting a real opener process.
    """
    subprocess.Popen(argv)  # noqa: S603 - argument list built above, never a shell string


@router.post("/reveal", response_model=RevealResult)
async def reveal_in_explorer(request: RevealRequest) -> RevealResult:
    try:
        resolved = resolve_repo_relative_path(request.path)
    except PathEscapesRepositoryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"No such path: {request.path!r}")
    if _is_reveal_excluded(resolved):
        raise HTTPException(
            status_code=400, detail=f"Path is excluded from reveal: {request.path!r}"
        )
    argv = _reveal_argv(resolved)
    _launch_reveal_opener(argv)
    return RevealResult(opened=argv[-1])


# This module is imported only when D_SYSTEM_DEMO_TERMINAL=1 (see src/api/__init__.py), exactly
# like src/api/routes/demo_terminal.py — re-running the same loopback-bind check here means this
# module enforces ADR-015 rule 1 on its own, independent of import order with demo_terminal.
enforce_loopback_bind()
