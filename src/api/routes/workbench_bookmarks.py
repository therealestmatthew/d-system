"""The workbench bookmark-category routes (ADR-029, REQ-012 R09): named groupings of repository
files, stored as one JSON file per category under the data root.

Mounted only when `D_SYSTEM_DEMO_TERMINAL=1` — `src/api/__init__.py` imports this module under
the same flag as `src.api.routes.workbench`, so with the flag unset none of these routes exist
(404), not merely refuse. These are the workbench API's first write routes; ADR-029 section 4
extends ADR-015 rule 4 ("GET only") by exactly the six routes below and nothing else:

| Operation              | Route                                                  |
|------------------------|--------------------------------------------------------|
| list categories        | `GET /bookmarks`                                       |
| list a category's files| `GET /bookmarks/{category_id}`                         |
| create                 | `POST /bookmarks` (body: `name`)                       |
| rename                 | `PATCH /bookmarks/{category_id}` (body: `name`)        |
| delete                 | `DELETE /bookmarks/{category_id}`                      |
| add / remove a file    | `POST` / `DELETE /bookmarks/{category_id}/entries`     |

Storage and identity (ADR-029 sections 1 and 2):

- One record per category at `<data root>/workbench/bookmarks/<category_id>.json`, where the data
  root is `data_root()` from `src.db.source_validation` (`D_SYSTEM_DATA_ROOT` if set, else the
  tracked `_data/`). It is read on every request, never cached at import.
- `category_id` is a lowercase slug generated from the name at creation and never changed; it is
  also the file name stem. An id is validated against the slug pattern (and the Windows reserved
  device names) before any file name is formed, so a request cannot steer a write outside the
  bookmarks directory. A malformed or reserved id is reported exactly like an unknown one (404).
- Rename changes `name` only.

Entries (ADR-029 section 3): an ordered list of unique repository-relative forward-slash paths,
validated on write by the ADR-015 rules (no absolute path, no `..`, no symlink leaving the
repository, no directory, nothing under `_private/` or ignored by git, nothing under `.git`).
Entries are never repaired and never pruned: each read resolves every entry to `present`,
`missing` (not a file on disk) or `excluded` (ignored, private or leaving the repository now), so
a stale status cannot persist. A removal does not need the file to exist, so a `missing` entry can
always be removed.

Private files are deliberately unsupported: an entry under `_private/` or any gitignored path is
refused on write and reads as `excluded` if it became ignored later. A category is itself private
content when `D_SYSTEM_DATA_ROOT` points at the private portfolio, so it must not name files that
the File Browser and the other workbench routes would never show.

Writes write a temporary file in the same directory and atomically replace the record. Every
mutation is a read-modify-write under one process lock, so two browser tabs adding different files
to one category do not lose either.
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import tempfile
import threading
from pathlib import Path
from typing import Any, Final, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.routes.workbench import (
    ALWAYS_EXCLUDED_NAMES,
    REPO_ROOT,
    PathEscapesRepositoryError,
    _git_ignored_paths,
    resolve_repo_relative_path,
)
from src.db.source_validation import data_root

router = APIRouter()

SCHEMA_VERSION: Final[int] = 1
BOOKMARKS_SUBDIRECTORY: Final[tuple[str, ...]] = ("workbench", "bookmarks")

CATEGORY_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CATEGORY_ID_MAX_LENGTH: Final[int] = 64
NAME_MAX_LENGTH: Final[int] = 80
#: The id used when a name has no ASCII letters or digits (`!!!`, non-Latin text).
EMPTY_SLUG_FALLBACK: Final[str] = "category"
#: Suffix that keeps a slug equal to a Windows device name from becoming `con.json`.
RESERVED_NAME_SUFFIX: Final[str] = "-category"
WINDOWS_RESERVED_NAMES: Final[frozenset[str]] = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{number}" for number in range(1, 10)}
    | {f"lpt{number}" for number in range(1, 10)}
)
PRIVATE_DIRECTORY_NAME: Final[str] = "_private"

EntryStatus = Literal["present", "missing", "excluded"]

#: One lock for every mutation. Routes below are plain `def`, so FastAPI runs them in its thread
#: pool, and a read-modify-write of one record must not interleave with another.
_WRITE_LOCK = threading.Lock()


# --- Models -----------------------------------------------------------------------------------


class CategorySummary(BaseModel):
    category_id: str
    name: str
    entry_count: int


class ResolvedEntry(BaseModel):
    path: str
    status: EntryStatus


class CategoryDetail(BaseModel):
    category_id: str
    name: str
    entries: list[ResolvedEntry]


class CategoryNameRequest(BaseModel):
    name: str


class EntryRequest(BaseModel):
    path: str


class DeleteResult(BaseModel):
    deleted: str


# --- Storage ----------------------------------------------------------------------------------


def bookmarks_directory() -> Path:
    """`<data root>/workbench/bookmarks`, resolved on every call so the environment is read when
    the request arrives, not when the module was imported."""
    return data_root(REPO_ROOT).joinpath(*BOOKMARKS_SUBDIRECTORY)


def is_valid_category_id(category_id: str) -> bool:
    return (
        0 < len(category_id) <= CATEGORY_ID_MAX_LENGTH
        and CATEGORY_ID_PATTERN.fullmatch(category_id) is not None
        and category_id not in WINDOWS_RESERVED_NAMES
    )


def _not_found(category_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Category not found: {category_id!r}")


def _record_path(category_id: str) -> Path:
    """The record file for `category_id`, formed only from an id that passed validation."""
    if not is_valid_category_id(category_id):
        raise _not_found(category_id)
    return bookmarks_directory() / f"{category_id}.json"


def _read_record(path: Path) -> dict[str, Any] | None:
    """The parsed record, or `None` when the file is absent, unreadable, or not a record whose
    shape and `category_id` match its file name."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(raw, dict):
        return None
    name = raw.get("name")
    entries = raw.get("entries")
    if (
        raw.get("category_id") != path.stem
        or not isinstance(name, str)
        or not isinstance(entries, list)
        or not all(isinstance(entry, str) for entry in entries)
    ):
        return None
    return raw


def _load_record(category_id: str) -> dict[str, Any]:
    path = _record_path(category_id)
    if not path.is_file():
        raise _not_found(category_id)
    record = _read_record(path)
    if record is None:
        raise HTTPException(
            status_code=500, detail=f"Category record is unreadable: {category_id!r}"
        )
    return record


def _all_records() -> list[dict[str, Any]]:
    """Every readable record, ordered by `category_id`. An unreadable file is skipped, not raised:
    the listing must stay available while one record is broken."""
    directory = bookmarks_directory()
    if not directory.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        if not is_valid_category_id(path.stem):
            continue
        record = _read_record(path)
        if record is not None:
            records.append(record)
    return records


def _write_record(record: dict[str, Any]) -> None:
    """Write `record` to a temporary file in the bookmarks directory and atomically replace the
    category's file with it."""
    path = _record_path(record["category_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.stem}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


# --- Names and ids ----------------------------------------------------------------------------


def _clean_name(raw: str) -> str:
    name = raw.strip()
    if not name:
        raise HTTPException(status_code=400, detail="A category name must not be empty.")
    if len(name) > NAME_MAX_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"A category name is at most {NAME_MAX_LENGTH} characters.",
        )
    if any(ord(character) < 32 or ord(character) == 127 for character in name):
        raise HTTPException(
            status_code=400, detail="A category name must not contain control characters."
        )
    return name


def slugify(name: str) -> str:
    """The id stem a name yields before collision handling: lowercase ASCII letters and digits
    joined by single hyphens, at most `CATEGORY_ID_MAX_LENGTH` characters. A name with no ASCII
    letters or digits falls back to `category`; a result equal to a Windows reserved device name
    gets `-category` appended, because Windows cannot create `con.json`."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = slug[:CATEGORY_ID_MAX_LENGTH].strip("-")
    if not slug:
        slug = EMPTY_SLUG_FALLBACK
    if slug in WINDOWS_RESERVED_NAMES:
        slug = f"{slug}{RESERVED_NAME_SUFFIX}"
    return slug


def _unique_category_id(name: str, taken: set[str]) -> str:
    """`slugify(name)`, with `-2`, `-3`, ... appended while that id exists. The stem is cut so the
    suffixed id still fits `CATEGORY_ID_MAX_LENGTH`."""
    base = slugify(name)
    if base not in taken:
        return base
    counter = 2
    while True:
        suffix = f"-{counter}"
        candidate = f"{base[: CATEGORY_ID_MAX_LENGTH - len(suffix)].rstrip('-')}{suffix}"
        if candidate not in taken:
            return candidate
        counter += 1


def _ensure_name_unused(name: str, records: list[dict[str, Any]], *, except_id: str = "") -> None:
    folded = name.casefold()
    for record in records:
        if record["category_id"] != except_id and str(record["name"]).casefold() == folded:
            raise HTTPException(
                status_code=409, detail=f"A category named {name!r} already exists."
            )


# --- Entry paths ------------------------------------------------------------------------------


def normalize_entry_path(raw: str) -> str:
    """The stored form of a requested path: forward slashes, no `.` segments, no repeated
    separators, case preserved. Rejects what can never be a repository-relative file path:
    empty, absolute (POSIX, UNC or drive-lettered), or containing a `..` segment. Lexical only;
    whether the file exists and is allowed is `validate_entry_file`'s job."""
    unified = raw.replace("\\", "/")
    if not unified.strip():
        raise HTTPException(status_code=400, detail="A file path must not be empty.")
    if unified.startswith("/") or re.match(r"^[A-Za-z]:", unified):
        raise HTTPException(status_code=400, detail=f"Absolute paths are not accepted: {raw!r}")
    segments = [segment for segment in unified.split("/") if segment not in ("", ".")]
    if ".." in segments:
        raise HTTPException(status_code=400, detail=f"Path escapes the repository root: {raw!r}")
    normalized = posixpath.normpath("/".join(segments)) if segments else "."
    if normalized == ".":
        raise HTTPException(status_code=400, detail="A file path must name a file.")
    return normalized


def _is_private_or_internal(normalized: str) -> bool:
    first = normalized.split("/", 1)[0]
    return first == PRIVATE_DIRECTORY_NAME or first in ALWAYS_EXCLUDED_NAMES


def _resolved_inside_repository(normalized: str) -> Path | None:
    """The resolved path of `normalized`, or `None` when it resolves outside the repository (a
    symlink leaving the root)."""
    try:
        return resolve_repo_relative_path(normalized)
    except PathEscapesRepositoryError:
        return None


def _entry_status(normalized: str, ignored: set[Path]) -> EntryStatus:
    """Resolve one stored entry against the current working tree."""
    if _is_private_or_internal(normalized):
        return "excluded"
    resolved = _resolved_inside_repository(normalized)
    if resolved is None:
        return "excluded"
    lexical = REPO_ROOT / normalized
    if not lexical.is_file():
        return "missing"
    if lexical in ignored or resolved in ignored:
        return "excluded"
    return "present"


def resolve_entries(paths: list[str]) -> list[ResolvedEntry]:
    """Every entry's status, recomputed now. One `git check-ignore` call covers the batch."""
    candidates: list[Path] = []
    for normalized in paths:
        if _is_private_or_internal(normalized):
            continue
        resolved = _resolved_inside_repository(normalized)
        lexical = REPO_ROOT / normalized
        if resolved is not None and lexical.is_file():
            candidates.append(lexical)
            if resolved != lexical:
                candidates.append(resolved)
    ignored = _git_ignored_paths(candidates)
    return [ResolvedEntry(path=path, status=_entry_status(path, ignored)) for path in paths]


def validate_entry_file(raw: str) -> str:
    """The stored form of `raw`, after the ADR-015 rules for a path that is about to be written:
    it must exist, be a file, stay inside the repository when symlinks are followed, and not be
    private or ignored. Raises 400 for a path that can never be valid and 404 for one that does
    not exist."""
    normalized = normalize_entry_path(raw)
    if _is_private_or_internal(normalized):
        raise HTTPException(
            status_code=400, detail=f"Private and internal paths are not accepted: {raw!r}"
        )
    resolved = _resolved_inside_repository(normalized)
    if resolved is None:
        raise HTTPException(status_code=400, detail=f"Path escapes the repository root: {raw!r}")
    lexical = REPO_ROOT / normalized
    if not lexical.exists():
        raise HTTPException(status_code=404, detail=f"No such file: {raw!r}")
    if not lexical.is_file():
        raise HTTPException(
            status_code=400, detail=f"Only files can be bookmarked, not directories: {raw!r}"
        )
    ignored = _git_ignored_paths([lexical] if resolved == lexical else [lexical, resolved])
    if ignored:
        raise HTTPException(status_code=400, detail=f"Path is private or ignored by git: {raw!r}")
    return normalized


# --- Responses --------------------------------------------------------------------------------


def _detail(record: dict[str, Any]) -> CategoryDetail:
    return CategoryDetail(
        category_id=record["category_id"],
        name=record["name"],
        entries=resolve_entries(list(record["entries"])),
    )


# --- Routes -----------------------------------------------------------------------------------


@router.get("", response_model=list[CategorySummary])
def list_categories() -> list[CategorySummary]:
    return [
        CategorySummary(
            category_id=record["category_id"],
            name=record["name"],
            entry_count=len(record["entries"]),
        )
        for record in _all_records()
    ]


@router.get("/{category_id}", response_model=CategoryDetail)
def get_category(category_id: str) -> CategoryDetail:
    return _detail(_load_record(category_id))


@router.post("", response_model=CategoryDetail, status_code=201)
def create_category(request: CategoryNameRequest) -> CategoryDetail:
    name = _clean_name(request.name)
    with _WRITE_LOCK:
        records = _all_records()
        _ensure_name_unused(name, records)
        taken = {str(record["category_id"]) for record in records}
        # A broken record still occupies its file name, so it also blocks the id.
        directory = bookmarks_directory()
        if directory.is_dir():
            taken.update(path.stem for path in directory.glob("*.json"))
        record: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "category_id": _unique_category_id(name, taken),
            "name": name,
            "entries": [],
        }
        _write_record(record)
    return _detail(record)


@router.patch("/{category_id}", response_model=CategoryDetail)
def rename_category(category_id: str, request: CategoryNameRequest) -> CategoryDetail:
    name = _clean_name(request.name)
    with _WRITE_LOCK:
        record = _load_record(category_id)
        _ensure_name_unused(name, _all_records(), except_id=category_id)
        record["name"] = name
        _write_record(record)
    return _detail(record)


@router.delete("/{category_id}", response_model=DeleteResult)
def delete_category(category_id: str) -> DeleteResult:
    path = _record_path(category_id)
    with _WRITE_LOCK:
        if not path.is_file():
            raise _not_found(category_id)
        path.unlink()
    return DeleteResult(deleted=category_id)


@router.post("/{category_id}/entries", response_model=CategoryDetail, status_code=201)
def add_entry(category_id: str, request: EntryRequest) -> CategoryDetail:
    with _WRITE_LOCK:
        record = _load_record(category_id)
        stored = validate_entry_file(request.path)
        if stored in record["entries"]:
            raise HTTPException(status_code=409, detail=f"Already in this category: {stored!r}")
        record["entries"] = [*record["entries"], stored]
        _write_record(record)
    return _detail(record)


@router.delete("/{category_id}/entries", response_model=CategoryDetail)
def remove_entry(category_id: str, request: EntryRequest) -> CategoryDetail:
    # Lexical normalisation only: the file may be gone, and a missing entry must stay removable.
    stored = normalize_entry_path(request.path)
    with _WRITE_LOCK:
        record = _load_record(category_id)
        if stored not in record["entries"]:
            raise HTTPException(status_code=404, detail=f"Not in this category: {stored!r}")
        record["entries"] = [entry for entry in record["entries"] if entry != stored]
        _write_record(record)
    return _detail(record)
