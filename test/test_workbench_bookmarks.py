"""Tests for the workbench bookmark-category routes (`src/api/routes/workbench_bookmarks.py`,
ADR-029) and their record schema (`schemas/workbench-bookmark-category.schema.json`), REQ-012 R09.

Every route test builds its own category under a temporary data root and a temporary git
repository standing in for the repository root, so none depends on the tracked example category
(the owner's machine sets `D_SYSTEM_DATA_ROOT`) and none writes into the real working tree. The
repository stand-in is a real `git init` directory, because the path rules call `git check-ignore`.

Covers: every route absent (404) with the flag unset; the six operations and the stored
representation each one changes; the id rules (slug, empty-slug fallback, Windows reserved names,
collision suffixes, length cap, immutability across rename); name rules; the ADR-015 path rules on
write (absolute, `..`, symlink escape, directory, `_private/`, gitignored, missing); resolution of
every entry to present, missing or excluded on read, with nothing pruned; concurrent adds losing
nothing; and the schema against both the tracked example and deliberately broken records.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from jsonschema import Draft7Validator

import src.api as api_module
import src.main as main_module

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "workbench-bookmark-category.schema.json"
EXAMPLE_DIR = ROOT / "_data" / "workbench" / "bookmarks"

BOOKMARKS = "/api/v1/workbench/bookmarks"

WORKBENCH_MODULE = "src.api.routes.workbench"
BOOKMARKS_MODULE = "src.api.routes.workbench_bookmarks"
ROUTE_MODULES = ("src.api.routes.demo_terminal", WORKBENCH_MODULE, BOOKMARKS_MODULE)


# --- fixtures ---------------------------------------------------------------------------------


def _uncache_route_modules() -> None:
    """Force the next import of the gated route modules to re-execute them (see
    `test_workbench_api.py`'s `_uncache_workbench_modules` for why the parent package's
    attribute must be cleared as well)."""
    routes_package = sys.modules.get("src.api.routes")
    for name in ROUTE_MODULES:
        sys.modules.pop(name, None)
        if routes_package is not None and hasattr(routes_package, name.rsplit(".", 1)[1]):
            delattr(routes_package, name.rsplit(".", 1)[1])


@pytest.fixture
def rebuild_app(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[..., FastAPI]]:
    def _build(*, flag: str | None) -> FastAPI:
        if flag is None:
            monkeypatch.delenv("D_SYSTEM_DEMO_TERMINAL", raising=False)
        else:
            monkeypatch.setenv("D_SYSTEM_DEMO_TERMINAL", flag)
        _uncache_route_modules()
        importlib.reload(api_module)
        importlib.reload(main_module)
        return main_module.app

    yield _build

    monkeypatch.delenv("D_SYSTEM_DEMO_TERMINAL", raising=False)
    _uncache_route_modules()
    importlib.reload(api_module)
    importlib.reload(main_module)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class Sandbox:
    """A temporary git repository (the stand-in repository root) plus a temporary data root."""

    def __init__(self, repo: Path, data: Path, client: TestClient) -> None:
        self.repo = repo
        self.data = data
        self.client = client

    @property
    def records_dir(self) -> Path:
        return self.data / "workbench" / "bookmarks"

    def write_file(self, relative: str, text: str = "x\n") -> Path:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def create(self, name: str) -> dict[str, Any]:
        response = self.client.post(BOOKMARKS, json={"name": name})
        assert response.status_code == 201, response.text
        body: dict[str, Any] = response.json()
        return body

    def add(self, category_id: str, path: str) -> Any:
        return self.client.post(f"{BOOKMARKS}/{category_id}/entries", json={"path": path})

    def remove(self, category_id: str, path: str) -> Any:
        return self.client.request(
            "DELETE", f"{BOOKMARKS}/{category_id}/entries", json={"path": path}
        )

    def record(self, category_id: str) -> dict[str, Any]:
        loaded: dict[str, Any] = json.loads(
            (self.records_dir / f"{category_id}.json").read_text(encoding="utf-8")
        )
        return loaded


@pytest.fixture
def sandbox(
    rebuild_app: Callable[..., FastAPI],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Sandbox:
    repo = (tmp_path / "repo").resolve()
    repo.mkdir()
    _git(repo, "init", "--quiet")
    (repo / ".gitignore").write_text("_private/\ndata/\nignored.txt\n", encoding="utf-8")
    data = tmp_path / "data-root"
    monkeypatch.setenv("D_SYSTEM_DATA_ROOT", str(data))

    app = rebuild_app(flag="1")
    # The route modules read `REPO_ROOT` from their own globals; point both at the stand-in so
    # path validation, `git check-ignore` and the data root all see the temporary repository.
    monkeypatch.setattr(sys.modules[WORKBENCH_MODULE], "REPO_ROOT", repo)
    monkeypatch.setattr(sys.modules[BOOKMARKS_MODULE], "REPO_ROOT", repo)
    return Sandbox(repo, data, TestClient(app))


# --- flag gating ------------------------------------------------------------------------------


def test_every_bookmark_route_absent_with_flag_unset(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag=None)
    assert BOOKMARKS_MODULE not in sys.modules
    client = TestClient(app)
    entry_body = {"path": "README.md"}
    name_body = {"name": "Anything"}
    assert client.get(BOOKMARKS).status_code == 404
    assert client.get(f"{BOOKMARKS}/demo-tour").status_code == 404
    assert client.post(BOOKMARKS, json=name_body).status_code == 404
    assert client.patch(f"{BOOKMARKS}/demo-tour", json=name_body).status_code == 404
    assert client.delete(f"{BOOKMARKS}/demo-tour").status_code == 404
    assert client.post(f"{BOOKMARKS}/demo-tour/entries", json=entry_body).status_code == 404
    assert (
        client.request("DELETE", f"{BOOKMARKS}/demo-tour/entries", json=entry_body).status_code
        == 404
    )


def test_routes_registered_with_flag_set(sandbox: Sandbox) -> None:
    assert BOOKMARKS_MODULE in sys.modules
    assert sandbox.client.get(BOOKMARKS).json() == []


def test_other_methods_are_refused(sandbox: Sandbox) -> None:
    created = sandbox.create("Alpha")
    base = f"{BOOKMARKS}/{created['category_id']}"
    assert sandbox.client.put(BOOKMARKS, json={"name": "x"}).status_code == 405
    assert sandbox.client.patch(BOOKMARKS, json={"name": "x"}).status_code == 405
    assert sandbox.client.put(base, json={"name": "x"}).status_code == 405
    assert sandbox.client.post(base, json={"name": "x"}).status_code == 405
    assert sandbox.client.get(f"{base}/entries").status_code == 405
    assert sandbox.client.patch(f"{base}/entries", json={"path": "x"}).status_code == 405


def test_records_live_under_the_data_root_resolved_per_request(
    monkeypatch: pytest.MonkeyPatch, rebuild_app: Callable[..., FastAPI]
) -> None:
    rebuild_app(flag="1")
    module = sys.modules[BOOKMARKS_MODULE]
    monkeypatch.delenv("D_SYSTEM_DATA_ROOT", raising=False)
    assert module.bookmarks_directory() == module.REPO_ROOT / "_data" / "workbench" / "bookmarks"
    monkeypatch.setenv("D_SYSTEM_DATA_ROOT", "/somewhere/else")
    assert module.bookmarks_directory() == Path("/somewhere/else/workbench/bookmarks")


# --- the six operations and the stored representation (R09) -----------------------------------


def test_create_stores_one_record_and_lists_it(sandbox: Sandbox) -> None:
    created = sandbox.create("Live demo")
    assert created == {"category_id": "live-demo", "name": "Live demo", "entries": []}
    assert sandbox.record("live-demo") == {
        "schema_version": 1,
        "category_id": "live-demo",
        "name": "Live demo",
        "entries": [],
    }
    assert sandbox.client.get(BOOKMARKS).json() == [
        {"category_id": "live-demo", "name": "Live demo", "entry_count": 0}
    ]
    assert sandbox.client.get(f"{BOOKMARKS}/live-demo").json() == created


def test_rename_changes_name_only(sandbox: Sandbox) -> None:
    sandbox.write_file("a.md")
    sandbox.create("Live demo")
    sandbox.add("live-demo", "a.md")
    response = sandbox.client.patch(
        f"{BOOKMARKS}/live-demo", json={"name": "Customer walk-through"}
    )
    assert response.status_code == 200
    assert response.json()["category_id"] == "live-demo"
    assert response.json()["name"] == "Customer walk-through"
    assert sorted(path.name for path in sandbox.records_dir.iterdir()) == ["live-demo.json"]
    assert sandbox.record("live-demo") == {
        "schema_version": 1,
        "category_id": "live-demo",
        "name": "Customer walk-through",
        "entries": ["a.md"],
    }


def test_rename_may_change_only_the_case_of_its_own_name(sandbox: Sandbox) -> None:
    sandbox.create("Favorites")
    response = sandbox.client.patch(f"{BOOKMARKS}/favorites", json={"name": "FAVORITES"})
    assert response.status_code == 200
    assert response.json()["name"] == "FAVORITES"


def test_rename_to_another_categorys_name_is_refused(sandbox: Sandbox) -> None:
    sandbox.create("One")
    sandbox.create("Two")
    response = sandbox.client.patch(f"{BOOKMARKS}/two", json={"name": "ONE"})
    assert response.status_code == 409
    assert sandbox.record("two")["name"] == "Two"


def test_delete_removes_the_record(sandbox: Sandbox) -> None:
    sandbox.create("Gone soon")
    response = sandbox.client.delete(f"{BOOKMARKS}/gone-soon")
    assert response.status_code == 200
    assert response.json() == {"deleted": "gone-soon"}
    assert not (sandbox.records_dir / "gone-soon.json").exists()
    assert sandbox.client.get(f"{BOOKMARKS}/gone-soon").status_code == 404
    assert sandbox.client.delete(f"{BOOKMARKS}/gone-soon").status_code == 404
    assert sandbox.client.get(BOOKMARKS).json() == []


def test_add_and_remove_files_keep_order_and_change_the_record(sandbox: Sandbox) -> None:
    for name in ("a.md", "docs/b.html", "docs/c.svg"):
        sandbox.write_file(name)
    sandbox.create("Set")
    assert sandbox.add("set", "docs/b.html").status_code == 201
    assert sandbox.add("set", "a.md").status_code == 201
    response = sandbox.add("set", "docs/c.svg")
    assert response.status_code == 201
    assert [entry["path"] for entry in response.json()["entries"]] == [
        "docs/b.html",
        "a.md",
        "docs/c.svg",
    ]
    assert sandbox.record("set")["entries"] == ["docs/b.html", "a.md", "docs/c.svg"]

    removed = sandbox.remove("set", "a.md")
    assert removed.status_code == 200
    assert [entry["path"] for entry in removed.json()["entries"]] == ["docs/b.html", "docs/c.svg"]
    assert sandbox.record("set")["entries"] == ["docs/b.html", "docs/c.svg"]
    assert sandbox.client.get(BOOKMARKS).json()[0]["entry_count"] == 2


def test_adding_a_file_twice_is_refused_and_removing_an_absent_one_is_404(sandbox: Sandbox) -> None:
    sandbox.write_file("a.md")
    sandbox.create("Set")
    assert sandbox.add("set", "a.md").status_code == 201
    assert sandbox.add("set", "a.md").status_code == 409
    assert sandbox.add("set", "./a.md").status_code == 409
    assert sandbox.record("set")["entries"] == ["a.md"]
    assert sandbox.remove("set", "nothing.md").status_code == 404


def test_entry_routes_on_an_unknown_category_are_404(sandbox: Sandbox) -> None:
    sandbox.write_file("a.md")
    assert sandbox.add("nope", "a.md").status_code == 404
    assert sandbox.remove("nope", "a.md").status_code == 404
    assert sandbox.client.patch(f"{BOOKMARKS}/nope", json={"name": "x"}).status_code == 404


def test_stored_records_validate_against_the_schema(sandbox: Sandbox) -> None:
    sandbox.write_file("a.md")
    sandbox.create("Live demo")
    sandbox.add("live-demo", "a.md")
    sandbox.create("!!!")
    validator = _validator()
    for path in sandbox.records_dir.glob("*.json"):
        assert list(validator.iter_errors(json.loads(path.read_text(encoding="utf-8")))) == []


def test_writes_leave_no_temporary_files(sandbox: Sandbox) -> None:
    sandbox.write_file("a.md")
    sandbox.create("Set")
    sandbox.add("set", "a.md")
    sandbox.remove("set", "a.md")
    sandbox.client.patch(f"{BOOKMARKS}/set", json={"name": "Renamed"})
    assert [path.name for path in sandbox.records_dir.iterdir()] == ["set.json"]


def test_concurrent_adds_to_one_category_lose_nothing(sandbox: Sandbox) -> None:
    names = [f"file-{index:02d}.md" for index in range(12)]
    for name in names:
        sandbox.write_file(name)
    sandbox.create("Busy")

    def add(name: str) -> int:
        return int(sandbox.add("busy", name).status_code)

    with ThreadPoolExecutor(max_workers=6) as pool:
        statuses = list(pool.map(add, names))
    assert statuses == [201] * len(names)
    assert sorted(sandbox.record("busy")["entries"]) == names


# --- ids --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "expected_id"),
    [
        ("Live demo", "live-demo"),
        ("  Favorites  ", "favorites"),
        ("Q3 / Client: review (draft)", "q3-client-review-draft"),
        ("---a---b---", "a-b"),
        ("!!!", "category"),
        ("日本語", "category"),
        ("con", "con-category"),
        ("CON", "con-category"),
        ("Prn", "prn-category"),
        ("aux", "aux-category"),
        ("nul", "nul-category"),
        ("COM1", "com1-category"),
        ("com9", "com9-category"),
        ("LPT1", "lpt1-category"),
        ("lpt9", "lpt9-category"),
        ("com0", "com0"),
        ("console", "console"),
    ],
)
def test_id_is_derived_from_the_name(sandbox: Sandbox, name: str, expected_id: str) -> None:
    created = sandbox.create(name)
    assert created["category_id"] == expected_id
    assert created["name"] == name.strip()
    assert (sandbox.records_dir / f"{expected_id}.json").is_file()


def test_the_display_name_of_a_reserved_slug_is_unchanged(sandbox: Sandbox) -> None:
    assert sandbox.create("Con")["name"] == "Con"


def test_colliding_slugs_get_numeric_suffixes(sandbox: Sandbox) -> None:
    ids = [sandbox.create(name)["category_id"] for name in ("Live demo", "Live-demo", "live  demo")]
    assert ids == ["live-demo", "live-demo-2", "live-demo-3"]


def test_empty_slug_names_get_numeric_suffixes(sandbox: Sandbox) -> None:
    ids = [sandbox.create(name)["category_id"] for name in ("!!!", "???", "日本語")]
    assert ids == ["category", "category-2", "category-3"]


def test_reserved_slug_names_get_numeric_suffixes_after_the_reserved_rule(sandbox: Sandbox) -> None:
    ids = [sandbox.create(name)["category_id"] for name in ("con", "CON!")]
    assert ids == ["con-category", "con-category-2"]
    # "con " is the same name as "con" once trimmed, so it is refused rather than suffixed.
    assert sandbox.client.post(BOOKMARKS, json={"name": "con "}).status_code == 409


def test_a_long_name_yields_a_valid_id_within_the_cap(sandbox: Sandbox) -> None:
    long_name = ("word " * 16).strip()
    first = sandbox.create(long_name)["category_id"]
    second = sandbox.create(long_name.upper() + ".")["category_id"]
    for category_id in (first, second):
        assert len(category_id) <= 64
        assert category_id == category_id.strip("-")
        assert "--" not in category_id
    assert first != second
    module = sys.modules[BOOKMARKS_MODULE]
    assert module.is_valid_category_id(first) and module.is_valid_category_id(second)


def test_a_name_that_trims_to_64_chars_ending_in_a_hyphen_has_no_trailing_hyphen(
    sandbox: Sandbox,
) -> None:
    name = "a" * 63 + " b"
    assert sandbox.create(name)["category_id"] == "a" * 63


def test_names_are_unique_case_insensitively(sandbox: Sandbox) -> None:
    sandbox.create("Live demo")
    assert sandbox.client.post(BOOKMARKS, json={"name": "LIVE DEMO"}).status_code == 409
    assert sandbox.client.post(BOOKMARKS, json={"name": "  live demo  "}).status_code == 409


@pytest.mark.parametrize("name", ["", "   ", "x" * 81, "line\nbreak", "tab\there", "nul\x00char"])
def test_invalid_names_are_refused(sandbox: Sandbox, name: str) -> None:
    assert sandbox.client.post(BOOKMARKS, json={"name": name}).status_code == 400
    sandbox.create("Fine")
    assert sandbox.client.patch(f"{BOOKMARKS}/fine", json={"name": name}).status_code == 400
    assert sandbox.client.get(BOOKMARKS).json() == [
        {"category_id": "fine", "name": "Fine", "entry_count": 0}
    ]


def test_an_80_character_name_is_accepted(sandbox: Sandbox) -> None:
    assert sandbox.create("x" * 80)["name"] == "x" * 80


def test_a_missing_name_is_refused(sandbox: Sandbox) -> None:
    assert sandbox.client.post(BOOKMARKS, json={}).status_code == 422


@pytest.mark.parametrize(
    "category_id",
    [
        "Live-Demo",
        "live_demo",
        "-live",
        "live-",
        "a--b",
        "con",
        "com1",
        "lpt9",
        "nul",
        "x" * 65,
        "%2e%2e",
        "a.b",
    ],
)
def test_malformed_or_reserved_ids_are_reported_like_unknown_ones(
    sandbox: Sandbox, category_id: str
) -> None:
    sandbox.write_file("a.md")
    base = f"{BOOKMARKS}/{category_id}"
    assert sandbox.client.get(base).status_code == 404
    assert sandbox.client.patch(base, json={"name": "x"}).status_code == 404
    assert sandbox.client.delete(base).status_code == 404
    assert sandbox.add(category_id, "a.md").status_code == 404
    assert list(sandbox.records_dir.glob("*")) == []


def test_an_id_cannot_steer_a_delete_outside_the_bookmarks_directory(sandbox: Sandbox) -> None:
    outside = sandbox.data / "workbench" / "secret.json"
    outside.parent.mkdir(parents=True, exist_ok=True)
    outside.write_text("{}", encoding="utf-8")
    for attempt in ("..%2Fsecret", "%2e%2e%2fsecret", "..", "secret/../.."):
        assert sandbox.client.delete(f"{BOOKMARKS}/{attempt}").status_code in (404, 405)
    assert outside.is_file()


def test_a_deleted_id_is_not_reserved(sandbox: Sandbox) -> None:
    sandbox.create("Live demo")
    sandbox.client.delete(f"{BOOKMARKS}/live-demo")
    assert sandbox.create("Live demo")["category_id"] == "live-demo"


def test_a_broken_record_is_skipped_in_the_list_and_reported_on_read(sandbox: Sandbox) -> None:
    sandbox.create("Fine")
    (sandbox.records_dir / "broken.json").write_text("{ not json", encoding="utf-8")
    (sandbox.records_dir / "mismatch.json").write_text(
        json.dumps({"schema_version": 1, "category_id": "other", "name": "M", "entries": []}),
        encoding="utf-8",
    )
    assert [row["category_id"] for row in sandbox.client.get(BOOKMARKS).json()] == ["fine"]
    assert sandbox.client.get(f"{BOOKMARKS}/broken").status_code == 500
    # A broken record still owns its file name, so a new category cannot overwrite it.
    assert sandbox.create("Broken")["category_id"] == "broken-2"


# --- path rules on write (ADR-015 rules 2 and 3) ----------------------------------------------


def test_backslashes_and_dot_segments_are_normalised_to_forward_slash(sandbox: Sandbox) -> None:
    sandbox.write_file("docs/a.md")
    sandbox.create("Set")
    response = sandbox.add("set", ".\\docs\\\\a.md")
    assert response.status_code == 201
    assert sandbox.record("set")["entries"] == ["docs/a.md"]


def test_case_is_preserved_as_stored(sandbox: Sandbox) -> None:
    sandbox.write_file("Docs/ReadMe.md")
    sandbox.create("Set")
    sandbox.add("set", "Docs/ReadMe.md")
    assert sandbox.record("set")["entries"] == ["Docs/ReadMe.md"]


@pytest.mark.parametrize(
    ("path", "status"),
    [
        ("", 400),
        ("   ", 400),
        (".", 400),
        ("/etc/passwd", 400),
        ("\\windows\\system32", 400),
        ("C:/Users/x/file.md", 400),
        ("C:\\Users\\x\\file.md", 400),
        ("../outside.md", 400),
        ("docs/../a.md", 400),
        ("docs/..\\..\\a.md", 400),
        ("docs", 400),
        ("_private/secret.md", 400),
        ("_private", 400),
        (".git/config", 400),
        ("ignored.txt", 400),
        ("data/cached.txt", 400),
        ("nope.md", 404),
        ("docs/nope.md", 404),
    ],
)
def test_invalid_paths_are_refused_on_write(sandbox: Sandbox, path: str, status: int) -> None:
    sandbox.write_file("a.md")
    sandbox.write_file("docs/a.md")
    sandbox.write_file("_private/secret.md")
    sandbox.write_file("ignored.txt")
    sandbox.write_file("data/cached.txt")
    sandbox.create("Set")
    response = sandbox.add("set", path)
    assert response.status_code == status, response.text
    assert sandbox.record("set")["entries"] == []


def test_a_symlink_leaving_the_repository_is_refused(sandbox: Sandbox, tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    (sandbox.repo / "link.md").symlink_to(outside)
    (sandbox.repo / "linkdir").symlink_to(tmp_path, target_is_directory=True)
    sandbox.create("Set")
    assert sandbox.add("set", "link.md").status_code == 400
    assert sandbox.add("set", "linkdir/outside.md").status_code == 400
    assert sandbox.record("set")["entries"] == []


def test_a_symlink_to_a_private_file_inside_the_repository_is_refused(sandbox: Sandbox) -> None:
    sandbox.write_file("_private/secret.md")
    (sandbox.repo / "shortcut.md").symlink_to(sandbox.repo / "_private" / "secret.md")
    sandbox.create("Set")
    assert sandbox.add("set", "shortcut.md").status_code == 400


# --- resolution on read (R11 on the API side) -------------------------------------------------


def _statuses(sandbox: Sandbox, category_id: str) -> dict[str, str]:
    body = sandbox.client.get(f"{BOOKMARKS}/{category_id}").json()
    return {entry["path"]: entry["status"] for entry in body["entries"]}


def test_entries_resolve_to_present_missing_or_excluded_on_every_read(sandbox: Sandbox) -> None:
    keep = sandbox.write_file("keep.md")
    gone = sandbox.write_file("gone.md")
    later_ignored = sandbox.write_file("later.md")
    sandbox.create("Set")
    for name in ("keep.md", "gone.md", "later.md"):
        assert sandbox.add("set", name).status_code == 201
    assert _statuses(sandbox, "set") == {
        "keep.md": "present",
        "gone.md": "present",
        "later.md": "present",
    }

    gone.unlink()
    with (sandbox.repo / ".gitignore").open("a", encoding="utf-8") as handle:
        handle.write("later.md\n")
    assert _statuses(sandbox, "set") == {
        "keep.md": "present",
        "gone.md": "missing",
        "later.md": "excluded",
    }
    # Nothing was pruned and the order is unchanged.
    assert sandbox.record("set")["entries"] == ["keep.md", "gone.md", "later.md"]

    # The file comes back (a branch switch): the same entry reads present again.
    gone.write_text("back\n", encoding="utf-8")
    assert _statuses(sandbox, "set")["gone.md"] == "present"
    assert keep.is_file() and later_ignored.is_file()


def test_a_directory_in_place_of_an_entry_reads_missing(sandbox: Sandbox) -> None:
    file = sandbox.write_file("thing.md")
    sandbox.create("Set")
    sandbox.add("set", "thing.md")
    file.unlink()
    file.mkdir()
    assert _statuses(sandbox, "set") == {"thing.md": "missing"}


def test_hand_edited_unsafe_entries_read_excluded_and_nothing_raises(sandbox: Sandbox) -> None:
    sandbox.write_file("_private/secret.md")
    sandbox.write_file("ok.md")
    sandbox.create("Set")
    record = sandbox.record("set")
    record["entries"] = [
        "ok.md",
        "_private/secret.md",
        "/etc/passwd",
        "../outside.md",
        ".git/config",
    ]
    (sandbox.records_dir / "set.json").write_text(json.dumps(record), encoding="utf-8")
    assert _statuses(sandbox, "set") == {
        "ok.md": "present",
        "_private/secret.md": "excluded",
        "/etc/passwd": "excluded",
        "../outside.md": "excluded",
        ".git/config": "excluded",
    }


def test_a_missing_entry_can_still_be_removed(sandbox: Sandbox) -> None:
    file = sandbox.write_file("a.md")
    sandbox.write_file("b.md")
    sandbox.create("Set")
    sandbox.add("set", "a.md")
    sandbox.add("set", "b.md")
    file.unlink()
    response = sandbox.remove("set", "a.md")
    assert response.status_code == 200
    assert [entry["path"] for entry in response.json()["entries"]] == ["b.md"]


def test_the_list_counts_entries_without_resolving_them(sandbox: Sandbox) -> None:
    file = sandbox.write_file("a.md")
    sandbox.create("Set")
    sandbox.add("set", "a.md")
    file.unlink()
    assert sandbox.client.get(BOOKMARKS).json() == [
        {"category_id": "set", "name": "Set", "entry_count": 1}
    ]


# --- review findings: symlinks, hostile paths, content type, limits ---------------------------


def _bookmarks_module() -> Any:
    return sys.modules[BOOKMARKS_MODULE]


def test_a_symlinked_directory_into_private_is_refused_and_reads_excluded(
    sandbox: Sandbox,
) -> None:
    sandbox.write_file("_private/s.md")
    (sandbox.repo / "linkdir").symlink_to(sandbox.repo / "_private", target_is_directory=True)
    sandbox.create("Set")
    assert sandbox.add("set", "linkdir/s.md").status_code == 400
    assert sandbox.record("set")["entries"] == []

    record = sandbox.record("set")
    record["entries"] = ["linkdir/s.md"]
    (sandbox.records_dir / "set.json").write_text(json.dumps(record), encoding="utf-8")
    assert _statuses(sandbox, "set") == {"linkdir/s.md": "excluded"}


def test_symlinks_to_git_internals_are_refused_and_read_excluded(sandbox: Sandbox) -> None:
    (sandbox.repo / "gitlink").symlink_to(sandbox.repo / ".git", target_is_directory=True)
    (sandbox.repo / "headlink.md").symlink_to(sandbox.repo / ".git" / "HEAD")
    sandbox.create("Set")
    assert sandbox.add("set", "gitlink/HEAD").status_code == 400
    assert sandbox.add("set", "headlink.md").status_code == 400
    record = sandbox.record("set")
    record["entries"] = ["gitlink/HEAD", "headlink.md"]
    (sandbox.records_dir / "set.json").write_text(json.dumps(record), encoding="utf-8")
    assert _statuses(sandbox, "set") == {"gitlink/HEAD": "excluded", "headlink.md": "excluded"}


def test_a_symlink_to_an_ordinary_file_inside_the_repository_is_refused(sandbox: Sandbox) -> None:
    sandbox.write_file("real.md")
    (sandbox.repo / "alias.md").symlink_to(sandbox.repo / "real.md")
    sandbox.create("Set")
    assert sandbox.add("set", "alias.md").status_code == 400
    assert sandbox.add("set", "real.md").status_code == 201


def test_an_ignore_check_that_fails_is_treated_as_everything_ignored(
    sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch
) -> None:
    sandbox.write_file("a.md")
    sandbox.write_file("b.md")
    sandbox.create("Set")
    assert sandbox.add("set", "a.md").status_code == 201

    def broken(payload: bytes) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(["git"], 128, stdout=b"", stderr=b"fatal: broken")

    monkeypatch.setattr(_bookmarks_module(), "_run_check_ignore", broken)
    assert sandbox.add("set", "b.md").status_code == 400
    assert _statuses(sandbox, "set") == {"a.md": "excluded"}


def test_an_ignore_check_that_cannot_run_is_treated_as_everything_ignored(
    sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch
) -> None:
    sandbox.write_file("a.md")
    sandbox.create("Set")

    def missing(payload: bytes) -> subprocess.CompletedProcess[bytes]:
        raise FileNotFoundError("git")

    monkeypatch.setattr(_bookmarks_module(), "_run_check_ignore", missing)
    assert sandbox.add("set", "a.md").status_code == 400


@pytest.mark.parametrize(
    "path",
    [
        "sub/.git/config",
        ".GIT/config",
        ".git./config",
        ".git /config",
        "docs/_PRIVATE/x.md",
        "a/_private/x.md",
        "_Private/x.md",
    ],
)
def test_git_and_private_segments_are_refused_at_any_depth_and_case(
    sandbox: Sandbox, path: str
) -> None:
    sandbox.write_file(path)
    sandbox.create("Set")
    assert sandbox.add("set", path).status_code == 400
    assert sandbox.record("set")["entries"] == []


def test_hand_edited_nested_git_and_cased_entries_read_excluded(sandbox: Sandbox) -> None:
    sandbox.write_file("sub/.git/config")
    sandbox.create("Set")
    record = sandbox.record("set")
    record["entries"] = ["sub/.git/config", ".GIT/config", "docs/_PRIVATE/x.md"]
    (sandbox.records_dir / "set.json").write_text(json.dumps(record), encoding="utf-8")
    assert set(_statuses(sandbox, "set").values()) == {"excluded"}


@pytest.mark.parametrize(
    "path",
    [
        "a.md\x00",
        "\x00",
        "dir\x00/a.md",
        "x" * 300 + ".md",
        "docs/" + "y" * 256,
        "z/" * 600 + "a.md",
    ],
)
def test_hostile_paths_are_refused_with_400_not_500(sandbox: Sandbox, path: str) -> None:
    sandbox.write_file("a.md")
    sandbox.create("Set")
    assert sandbox.add("set", path).status_code == 400
    assert sandbox.record("set")["entries"] == []


def test_a_path_with_a_lone_surrogate_is_refused_not_a_server_error(sandbox: Sandbox) -> None:
    sandbox.create("Set")
    response = sandbox.client.post(
        f"{BOOKMARKS}/set/entries",
        content=b'{"path": "a\\ud800.md"}',
        headers={"content-type": "application/json"},
    )
    assert response.status_code in (400, 422)
    named = sandbox.client.post(
        BOOKMARKS, content=b'{"name": "x\\ud800"}', headers={"content-type": "application/json"}
    )
    assert named.status_code in (400, 422)


def test_a_path_of_exactly_the_limits_is_accepted_in_shape(sandbox: Sandbox) -> None:
    module = _bookmarks_module()
    assert module.normalize_entry_path("a" * 255) == "a" * 255
    assert module.MAX_PATH_LENGTH == 1024 and module.MAX_SEGMENT_LENGTH == 255


def test_hand_edited_unusable_entries_read_excluded_and_the_rest_still_read(
    sandbox: Sandbox,
) -> None:
    sandbox.write_file("ok.md")
    sandbox.create("Set")
    record = sandbox.record("set")
    record["entries"] = ["ok.md", "bad\x00.md", "q" * 300, "w/" * 700 + "z"]
    (sandbox.records_dir / "set.json").write_text(json.dumps(record), encoding="utf-8")
    response = sandbox.client.get(f"{BOOKMARKS}/set")
    assert response.status_code == 200
    statuses = {entry["path"]: entry["status"] for entry in response.json()["entries"]}
    assert statuses["ok.md"] == "present"
    assert statuses["bad\x00.md"] == "excluded"
    assert statuses["q" * 300] == "excluded"
    # The unusable entry can still be removed, by its stored text.
    removed = sandbox.remove("set", "bad\x00.md")
    assert removed.status_code == 200
    assert "bad\x00.md" not in [entry["path"] for entry in removed.json()["entries"]]


def test_a_record_holding_a_lone_surrogate_is_unreadable_not_a_crash(sandbox: Sandbox) -> None:
    sandbox.create("Set")
    path = sandbox.records_dir / "set.json"
    path.write_text(
        '{"schema_version": 1, "category_id": "set", "name": "Set", "entries": ["a\\ud800"]}',
        encoding="utf-8",
    )
    assert sandbox.client.get(f"{BOOKMARKS}/set").status_code == 500
    assert sandbox.client.get(BOOKMARKS).json() == []


@pytest.mark.parametrize("content_type", ["text/plain", "application/x-www-form-urlencoded", None])
def test_writes_without_a_json_content_type_are_refused_with_415(
    sandbox: Sandbox, content_type: str | None
) -> None:
    sandbox.write_file("a.md")
    sandbox.create("Set")
    headers = {"content-type": content_type} if content_type else {"content-type": ""}
    body = b'{"name": "Other"}'
    entry = b'{"path": "a.md"}'
    assert sandbox.client.post(BOOKMARKS, content=body, headers=headers).status_code == 415
    assert (
        sandbox.client.patch(f"{BOOKMARKS}/set", content=body, headers=headers).status_code == 415
    )
    assert (
        sandbox.client.post(f"{BOOKMARKS}/set/entries", content=entry, headers=headers).status_code
        == 415
    )
    assert sandbox.add("set", "a.md").status_code == 201
    assert (
        sandbox.client.request(
            "DELETE", f"{BOOKMARKS}/set/entries", content=entry, headers=headers
        ).status_code
        == 415
    )
    assert [row["name"] for row in sandbox.client.get(BOOKMARKS).json()] == ["Set"]
    assert sandbox.record("set")["entries"] == ["a.md"]


def test_a_json_content_type_with_a_charset_is_accepted(sandbox: Sandbox) -> None:
    response = sandbox.client.post(
        BOOKMARKS,
        content=b'{"name": "Charset"}',
        headers={"content-type": "Application/JSON; charset=utf-8"},
    )
    assert response.status_code == 201


def test_a_category_delete_needs_no_body_or_content_type(sandbox: Sandbox) -> None:
    sandbox.create("Set")
    assert sandbox.client.delete(f"{BOOKMARKS}/set").status_code == 200


def test_an_oversized_body_is_refused_with_413(sandbox: Sandbox) -> None:
    sandbox.create("Set")
    big = {"name": "x" * 70_000}
    assert sandbox.client.post(BOOKMARKS, json=big).status_code == 413
    assert sandbox.client.patch(f"{BOOKMARKS}/set", json=big).status_code == 413
    assert (
        sandbox.client.post(f"{BOOKMARKS}/set/entries", json={"path": "p" * 70_000}).status_code
        == 413
    )
    assert [row["name"] for row in sandbox.client.get(BOOKMARKS).json()] == ["Set"]


def test_the_default_limits_are_the_documented_ones() -> None:
    importlib.import_module("src.api.routes.workbench")  # the module under test imports it
    module = importlib.import_module(BOOKMARKS_MODULE)
    assert module.MAX_ENTRIES_PER_CATEGORY == 500
    assert module.MAX_CATEGORIES == 200
    assert module.MAX_REQUEST_BYTES == 64 * 1024


def test_a_category_holds_a_bounded_number_of_files(
    sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_bookmarks_module(), "MAX_ENTRIES_PER_CATEGORY", 2)
    for name in ("a.md", "b.md", "c.md"):
        sandbox.write_file(name)
    sandbox.create("Set")
    assert sandbox.add("set", "a.md").status_code == 201
    assert sandbox.add("set", "b.md").status_code == 201
    assert sandbox.add("set", "c.md").status_code == 409
    assert sandbox.record("set")["entries"] == ["a.md", "b.md"]
    # A removal makes room again.
    sandbox.remove("set", "a.md")
    assert sandbox.add("set", "c.md").status_code == 201


def test_the_number_of_categories_is_bounded(
    sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_bookmarks_module(), "MAX_CATEGORIES", 2)
    sandbox.create("One")
    sandbox.create("Two")
    assert sandbox.client.post(BOOKMARKS, json={"name": "Three"}).status_code == 409
    sandbox.client.delete(f"{BOOKMARKS}/one")
    assert sandbox.client.post(BOOKMARKS, json={"name": "Three"}).status_code == 201


def test_a_write_flushes_the_temporary_file_to_disk_before_the_replace(
    sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch
) -> None:
    events: list[str] = []
    real_fsync = os.fsync
    real_replace = os.replace

    def spy_fsync(descriptor: int) -> None:
        events.append("fsync")
        real_fsync(descriptor)

    def spy_replace(source: Any, target: Any) -> None:
        events.append("replace")
        real_replace(source, target)

    monkeypatch.setattr(os, "fsync", spy_fsync)
    monkeypatch.setattr(os, "replace", spy_replace)
    sandbox.create("Set")
    assert events == ["fsync", "replace"]


@pytest.mark.parametrize(
    "category_id",
    [
        "a\\b",
        "..",
        "../x",
        "a/b",
        "Live",
        "con",
        "COM1",
        "com1",
        "nul",
        "x" * 65,
        "",
        "a--b",
        "-a",
        "a-",
        "a b",
    ],
)
def test_the_id_guard_rejects_what_cannot_be_a_file_name_stem(category_id: str) -> None:
    importlib.import_module("src.api.routes.workbench")
    module = importlib.import_module(BOOKMARKS_MODULE)
    assert module.is_valid_category_id(category_id) is False
    with pytest.raises(HTTPException) as caught:
        module._record_path(category_id)
    assert caught.value.status_code == 404


@pytest.mark.parametrize(
    "category_id", ["a", "live-demo", "x" * 64, "com0", "console", "con-category"]
)
def test_the_id_guard_accepts_valid_ids(category_id: str) -> None:
    importlib.import_module("src.api.routes.workbench")
    module = importlib.import_module(BOOKMARKS_MODULE)
    assert module.is_valid_category_id(category_id) is True
    assert module._record_path(category_id).name == f"{category_id}.json"


# --- the schema -------------------------------------------------------------------------------


def _validator() -> Draft7Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema)


def _valid_record() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "category_id": "live-demo",
        "name": "Live demo",
        "entries": ["docs/a.md", "_public/index.html"],
    }


def test_the_valid_record_passes() -> None:
    assert list(_validator().iter_errors(_valid_record())) == []


def _with(**changes: Any) -> dict[str, Any]:
    record = _valid_record()
    record.update(changes)
    return record


@pytest.mark.parametrize(
    "record",
    [
        _with(schema_version=2),
        _with(schema_version="1"),
        _with(category_id="Live-Demo"),
        _with(category_id="live_demo"),
        _with(category_id="-live"),
        _with(category_id="a--b"),
        _with(category_id=""),
        _with(category_id="x" * 65),
        _with(name=""),
        _with(name="x" * 81),
        _with(name=7),
        _with(entries="docs/a.md"),
        _with(entries=["docs/a.md", "docs/a.md"]),
        _with(entries=[""]),
        _with(entries=["/etc/passwd"]),
        _with(entries=["docs\\a.md"]),
        _with(entries=["C:/x/a.md"]),
        _with(entries=["../a.md"]),
        _with(entries=["docs/../a.md"]),
        _with(entries=["./a.md"]),
        _with(entries=["docs//a.md"]),
        _with(entries=["docs/"]),
        _with(entries=[3]),
        _with(entries=[f"f{index}.md" for index in range(501)]),
        _with(entries=["p" * 1025]),
        _with(extra="nope"),
    ],
)
def test_the_schema_rejects_malformed_records(record: dict[str, Any]) -> None:
    assert list(_validator().iter_errors(record)) != []


@pytest.mark.parametrize("missing", ["schema_version", "category_id", "name", "entries"])
def test_the_schema_requires_every_field(missing: str) -> None:
    record = _valid_record()
    del record[missing]
    assert list(_validator().iter_errors(record)) != []


EXAMPLE_FILES = sorted(EXAMPLE_DIR.glob("*.json"))


def test_a_tracked_example_category_exists() -> None:
    assert EXAMPLE_FILES, f"no example category under {EXAMPLE_DIR}"


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=lambda path: path.name)
def test_tracked_example_categories_satisfy_the_schema_and_name_tracked_files(path: Path) -> None:
    record = json.loads(path.read_text(encoding="utf-8"))
    assert list(_validator().iter_errors(record)) == []
    assert record["category_id"] == path.stem
    tracked = set(
        subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], check=True, capture_output=True)
        .stdout.decode()
        .split("\0")
    )
    for entry in record["entries"]:
        assert entry in tracked, f"{entry} is not a tracked file"
        assert (ROOT / entry).is_file()
    assert os.sep == "/" or "\\" not in "".join(record["entries"])
