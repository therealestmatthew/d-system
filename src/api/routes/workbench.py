"""The workbench read routes (ADR-015): injection-source enumeration, directory listing, and
recursive file search.

Every route here is GET-only and mounted only when `D_SYSTEM_DEMO_TERMINAL=1` —
`src/api/__init__.py` imports this module only under that flag, exactly like
`src/api/routes/demo_terminal.py`, so with the flag unset none of these routes exist (404), not
merely refuse. Importing this module also
re-runs `enforce_loopback_bind()` (ADR-015 rule 1: "one gate, one binding"), so a launch with the
flag set on a non-loopback bind host fails fast here too, independent of whether
`src.api.routes.demo_terminal` happened to be imported first.

Two capabilities, both read-only and repository-bounded (ADR-015 rule 2):

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
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Final

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.api.routes.demo_terminal import enforce_loopback_bind

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


class PathEscapesRepositoryError(ValueError):
    """Raised when a caller-supplied path does not resolve inside `REPO_ROOT`."""


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


# This module is imported only when D_SYSTEM_DEMO_TERMINAL=1 (see src/api/__init__.py), exactly
# like src/api/routes/demo_terminal.py — re-running the same loopback-bind check here means this
# module enforces ADR-015 rule 1 on its own, independent of import order with demo_terminal.
enforce_loopback_bind()
