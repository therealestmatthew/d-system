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

Writes write a temporary file in the same directory, fsync it and atomically replace the record.
Every mutation is a read-modify-write under one process lock, so two browser tabs adding different
files to one category do not lose either.

Limits: the lock is per process, so two backends sharing one data root are not supported (the
worktree launcher can start several backends; give each its own `D_SYSTEM_DATA_ROOT` or run one).
A hard kill can leave a `.<id>.*.tmp` file in the bookmarks directory; it is not matched by `*.json`
and is ignored on read, but `.gitignore` does not cover it (outside this phase's deliverables).
Request bodies must be `application/json` and at most 64 KB, a category holds at most 500 entries,
the data root at most 200 categories, and a path at most 1024 characters with no segment over 255.

Symlinks: git cannot check a path that passes through a symlinked directory (it aborts the whole
batch), so an entry whose lexical path differs from its resolved path is refused on write and read
as `excluded`, and `git check-ignore` is run on resolved paths only. A `git check-ignore` exit code
other than 0 or 1 is treated as "everything ignored" (fail closed); the helper in `workbench.py`
does not do that, so this module has its own.
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any, Final, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.routes.workbench import (
    ALWAYS_EXCLUDED_NAMES,
    REPO_ROOT,
    PathEscapesRepositoryError,
    resolve_repo_relative_path,
)
from src.db.source_validation import data_root

MAX_REQUEST_BYTES: Final[int] = 64 * 1024
MAX_ENTRIES_PER_CATEGORY: Final[int] = 500
MAX_CATEGORIES: Final[int] = 200
MAX_PATH_LENGTH: Final[int] = 1024
MAX_SEGMENT_LENGTH: Final[int] = 255
_BODY_METHODS: Final[frozenset[str]] = frozenset({"POST", "PATCH", "DELETE"})


async def require_json_within_limit(request: Request) -> None:
    """Router dependency: a write must say it is JSON (415 otherwise) and be small (413).

    A cross-origin page can send a "simple" POST with `text/plain` and no preflight; refusing any
    other content type means such a request creates nothing, whatever the FastAPI version parses.
    POST and PATCH always need a JSON content type; DELETE needs one only when it carries a body
    (the category delete has none, and a cross-origin DELETE needs a preflight anyway).
    """
    if request.method not in _BODY_METHODS:
        return
    declared = request.headers.get("content-length")
    try:
        declared_length = int(declared) if declared is not None else 0
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Content-Length.") from None
    if declared_length > MAX_REQUEST_BYTES:
        raise HTTPException(status_code=413, detail="The request body is too large.")
    has_body = declared_length > 0 or "transfer-encoding" in request.headers
    if request.method != "DELETE" or has_body:
        media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if media_type != "application/json":
            raise HTTPException(
                status_code=415, detail="The request body must be application/json."
            )
    if has_body and len(await request.body()) > MAX_REQUEST_BYTES:
        raise HTTPException(status_code=413, detail="The request body is too large.")


router = APIRouter(dependencies=[Depends(require_json_within_limit)])

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


def _encodable(text: str) -> bool:
    """Whether `text` can be written as UTF-8 (a lone surrogate cannot, in a file or a response)."""
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


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
        or not all(isinstance(entry, str) and _encodable(entry) for entry in entries)
        or not _encodable(name)
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
            handle.flush()
            os.fsync(handle.fileno())
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
    if not _encodable(name):
        raise HTTPException(status_code=400, detail="A category name must be valid text.")
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
    empty, containing NUL or text that is not valid UTF-8, longer than `MAX_PATH_LENGTH`, with a
    segment longer than `MAX_SEGMENT_LENGTH`, absolute (POSIX, UNC or drive-lettered), or containing
    a `..` segment. Lexical only; whether the file exists and is allowed is `validate_entry_file`'s
    job."""
    if "\x00" in raw or not _encodable(raw):
        raise HTTPException(status_code=400, detail="A file path must be valid text without NUL.")
    if len(raw) > MAX_PATH_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"A file path is at most {MAX_PATH_LENGTH} characters."
        )
    unified = raw.replace("\\", "/")
    if not unified.strip():
        raise HTTPException(status_code=400, detail="A file path must not be empty.")
    if unified.startswith("/") or re.match(r"^[A-Za-z]:", unified):
        raise HTTPException(status_code=400, detail=f"Absolute paths are not accepted: {raw!r}")
    segments = [segment for segment in unified.split("/") if segment not in ("", ".")]
    if ".." in segments:
        raise HTTPException(status_code=400, detail=f"Path escapes the repository root: {raw!r}")
    if any(len(segment) > MAX_SEGMENT_LENGTH for segment in segments):
        raise HTTPException(
            status_code=400,
            detail=f"A path segment is at most {MAX_SEGMENT_LENGTH} characters.",
        )
    normalized = posixpath.normpath("/".join(segments)) if segments else "."
    if normalized == ".":
        raise HTTPException(status_code=400, detail="A file path must name a file.")
    return normalized


_BARRED_SEGMENTS: Final[frozenset[str]] = frozenset(
    name.casefold() for name in {PRIVATE_DIRECTORY_NAME, *ALWAYS_EXCLUDED_NAMES}
)


def _is_private_or_internal(parts: tuple[str, ...] | list[str]) -> bool:
    """Whether any segment names `_private` or `.git` (or another always-excluded name), at any
    depth, compared casefolded with trailing dots and spaces removed: a case-insensitive or
    Windows filesystem treats `.GIT` and `.git.` as `.git`."""
    return any(part.casefold().rstrip(". ") in _BARRED_SEGMENTS for part in parts)


def _ignored_paths(paths: list[Path]) -> set[Path]:
    """The subset of `paths` that `git check-ignore` reports ignored. Fails closed: a git exit code
    other than 0 (some ignored) or 1 (none ignored), or git being unavailable, reports every path
    ignored. Paths must be resolved (no symlink components) and inside `REPO_ROOT`."""
    if not paths:
        return set()
    payload = b"\0".join(str(path.relative_to(REPO_ROOT)).encode() for path in paths) + b"\0"
    try:
        result = _run_check_ignore(payload)
    except OSError:
        return set(paths)
    if result.returncode not in (0, 1):
        return set(paths)
    ignored: set[Path] = set()
    for name in result.stdout.split(b"\0"):
        if name:
            ignored.add(REPO_ROOT / name.decode())
    return ignored


def _run_check_ignore(payload: bytes) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "check-ignore", "-z", "--stdin"],
        input=payload,
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )


def _inspect(path: str) -> tuple[EntryStatus | None, Path | None]:
    """Where `path` (a stored entry, possibly hand-edited) stands before the ignore check:
    `("excluded" | "missing", None)` when that is already decided, else `(None, resolved)` for a
    regular file whose path does not pass through a symlink and holds no private or `.git` segment.
    Anything that raises while the path is examined (NUL, an over-long name, invalid text) is
    `excluded`; nothing here raises."""
    try:
        if _is_private_or_internal(path.replace("\\", "/").split("/")):
            return "excluded", None
        resolved = resolve_repo_relative_path(path)
        relative = resolved.relative_to(REPO_ROOT)
        if _is_private_or_internal(relative.parts):
            return "excluded", None
        if os.path.normcase(relative.as_posix()) != os.path.normcase(path):
            # A symlink (or a non-normalised hand edit): git cannot vouch for such a path.
            return "excluded", None
        if not resolved.is_file():
            return "missing", None
        return None, resolved
    except (OSError, ValueError, UnicodeError):
        return "excluded", None


def resolve_entries(paths: list[str]) -> list[ResolvedEntry]:
    """Every entry's status, recomputed now. One `git check-ignore` call covers the batch."""
    inspected = [(path, *_inspect(path)) for path in paths]
    ignored = _ignored_paths([resolved for _, _, resolved in inspected if resolved is not None])
    result: list[ResolvedEntry] = []
    for path, status, resolved in inspected:
        if status is None:
            status = "excluded" if resolved in ignored else "present"
        result.append(ResolvedEntry(path=path, status=status))
    return result


def validate_entry_file(raw: str) -> str:
    """The stored form of `raw`, after the ADR-015 rules for a path that is about to be written:
    it must exist, be a file, not pass through a symlink, stay inside the repository, and not be
    private, internal or ignored. Raises 400 for a path that can never be valid and 404 for one
    that does not exist."""
    normalized = normalize_entry_path(raw)
    private = HTTPException(
        status_code=400, detail=f"Private and internal paths are not accepted: {raw!r}"
    )
    if _is_private_or_internal(normalized.split("/")):
        raise private
    try:
        resolved = resolve_repo_relative_path(normalized)
        relative = resolved.relative_to(REPO_ROOT)
        exists = resolved.exists()
        is_file = resolved.is_file()
    except PathEscapesRepositoryError:
        raise HTTPException(
            status_code=400, detail=f"Path escapes the repository root: {raw!r}"
        ) from None
    except (OSError, ValueError, UnicodeError):
        raise HTTPException(status_code=400, detail=f"Not a usable file path: {raw!r}") from None
    if _is_private_or_internal(relative.parts):
        raise private
    if os.path.normcase(relative.as_posix()) != os.path.normcase(normalized):
        raise HTTPException(
            status_code=400, detail=f"Paths through a symbolic link are not accepted: {raw!r}"
        )
    if not exists:
        raise HTTPException(status_code=404, detail=f"No such file: {raw!r}")
    if not is_file:
        raise HTTPException(
            status_code=400, detail=f"Only files can be bookmarked, not directories: {raw!r}"
        )
    if _ignored_paths([resolved]):
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
        if len(taken) >= MAX_CATEGORIES:
            raise HTTPException(
                status_code=409, detail=f"At most {MAX_CATEGORIES} categories are allowed."
            )
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
        if len(record["entries"]) >= MAX_ENTRIES_PER_CATEGORY:
            raise HTTPException(
                status_code=409,
                detail=f"A category holds at most {MAX_ENTRIES_PER_CATEGORY} files.",
            )
        record["entries"] = [*record["entries"], stored]
        _write_record(record)
    return _detail(record)


@router.delete("/{category_id}/entries", response_model=CategoryDetail)
def remove_entry(category_id: str, request: EntryRequest) -> CategoryDetail:
    # The file may be gone, and a hand-edited entry may be unusable as a path, so removal matches
    # the stored text exactly first and only then its normalised form; no file access is needed.
    with _WRITE_LOCK:
        record = _load_record(category_id)
        stored = (
            request.path
            if request.path in record["entries"]
            else normalize_entry_path(request.path)
        )
        if stored not in record["entries"]:
            raise HTTPException(status_code=404, detail=f"Not in this category: {stored!r}")
        record["entries"] = [entry for entry in record["entries"] if entry != stored]
        _write_record(record)
    return _detail(record)
