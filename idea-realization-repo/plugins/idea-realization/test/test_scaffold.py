"""The scaffold records what it writes, never overwrites, and changes .gitignore only on consent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import paths
import scaffold


def config(root: Path) -> paths.Config:
    return paths.resolve({"root": str(root)}, env={})


def listing(root: Path) -> dict[str, bytes | None]:
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None)
            for p in sorted(root.rglob("*"))}


def record(root: Path) -> dict[str, object]:
    loaded: dict[str, object] = json.loads((root / scaffold.RECORD).read_text())
    return loaded


def test_record_has_one_hash_per_created_file(tmp_path: Path) -> None:
    lines = scaffold.scaffold(config(tmp_path), list(scaffold.FEATURES))
    created = [line.split()[1] for line in lines if line.startswith("created")]
    state = record(tmp_path)
    files = state["files"]
    assert isinstance(files, list)
    created_files = [name for name in created if not name.endswith("/")]
    assert sorted(entry["path"] for entry in files) == sorted(created_files)
    for entry in files:
        digest = hashlib.sha256((tmp_path / entry["path"]).read_bytes()).hexdigest()
        assert entry["sha256"] == digest
    assert {"ideas/ideas.jsonl", "ideas/ideas.md", "ideas/priority.yaml",
            "backlog/backlog.yaml"} <= set(created_files)
    assert state["plugin_version"] == json.loads(paths.MANIFEST.read_text())["version"]
    assert state["features"] == sorted(scaffold.FEATURES)


def test_second_run_creates_nothing(tmp_path: Path) -> None:
    scaffold.scaffold(config(tmp_path), list(scaffold.FEATURES))
    before = listing(tmp_path)
    lines = scaffold.scaffold(config(tmp_path), list(scaffold.FEATURES))
    paths_reported = [line for line in lines if not line.startswith("needs consent")]
    assert paths_reported and all(line.startswith("skipped") for line in paths_reported), lines
    assert listing(tmp_path) == before


def test_existing_backlog_is_left_byte_identical(tmp_path: Path) -> None:
    backlog = tmp_path / "backlog" / "backlog.yaml"
    backlog.parent.mkdir()
    original = b"items:\n- id: mine\n  keep: exactly this\r\n"
    backlog.write_bytes(original)
    lines = scaffold.scaffold(config(tmp_path), ["backlog"])
    assert backlog.read_bytes() == original
    assert "skipped  backlog/backlog.yaml (exists)" in lines
    if (tmp_path / scaffold.RECORD).exists():
        files = record(tmp_path)["files"]
        assert isinstance(files, list)
        assert "backlog/backlog.yaml" not in [entry["path"] for entry in files]


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    lines = scaffold.scaffold(config(tmp_path), list(scaffold.FEATURES), dry_run=True,
                              consent=["gitignore"])
    assert any(line.startswith("would create") for line in lines)
    assert list(tmp_path.iterdir()) == []


def test_only_the_selected_feature_is_scaffolded(tmp_path: Path) -> None:
    scaffold.scaffold(config(tmp_path), ["ideas"])
    assert (tmp_path / "ideas" / "ideas.jsonl").is_file()
    assert not (tmp_path / "backlog").exists()
    assert not (tmp_path / "docs").exists()


def test_configured_paths_are_honoured(tmp_path: Path) -> None:
    custom = paths.resolve({"root": str(tmp_path), "ideas_path": "notes/log.jsonl"}, env={})
    scaffold.scaffold(custom, ["ideas"])
    assert (tmp_path / "notes" / "log.jsonl").is_file()
    assert not (tmp_path / "ideas" / "ideas.jsonl").exists()


def test_plugin_files_are_copied_when_shipped(tmp_path: Path) -> None:
    plugin = tmp_path / "plugin"
    (plugin / "templates").mkdir(parents=True)
    (plugin / "schemas").mkdir()
    (plugin / "templates" / "codes.yaml").write_text("series: []\n")
    (plugin / "schemas" / "document.schema.json").write_text("{}\n")
    target = tmp_path / "target"
    target.mkdir()
    lines = scaffold.scaffold(config(target), ["documents"], plugin_root=plugin)
    assert (target / "docs" / "codes.yaml").read_text() == "series: []\n"
    assert (target / ".idea-realization" / "schemas" / "document.schema.json").is_file()
    assert "skipped  docs/systems.yaml (not shipped by this plugin version)" in lines


def test_gitignore_is_untouched_without_consent(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("node_modules/\n")
    lines = scaffold.scaffold(config(tmp_path), ["partition"])
    assert gitignore.read_text() == "node_modules/\n"
    assert any(line.startswith("needs consent  .gitignore") for line in lines)
    assert record(tmp_path)["consent"] == []
    assert not (tmp_path / ".claude").exists()


def test_gitignore_consent_is_recorded(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("node_modules/")
    scaffold.scaffold(config(tmp_path), ["partition"], consent=["gitignore"])
    assert gitignore.read_text() == "node_modules/\n/.idea-realization/staging/\n"
    consent = record(tmp_path)["consent"]
    assert isinstance(consent, list) and len(consent) == 1
    assert consent[0]["path"] == ".gitignore"
    assert consent[0]["sha256"] == hashlib.sha256(gitignore.read_bytes()).hexdigest()
    lines = scaffold.scaffold(config(tmp_path), ["partition"], consent=["gitignore"])
    assert all(line.startswith("skipped") for line in lines), lines


def test_cli_requires_a_feature(tmp_path: Path) -> None:
    assert scaffold.main(["--root", str(tmp_path)]) == 2
    assert list(tmp_path.iterdir()) == []


def test_a_file_appearing_mid_run_is_skipped_not_overwritten(tmp_path: Path,
                                                             monkeypatch: object) -> None:
    target = tmp_path / "ideas" / "ideas.jsonl"
    real_open = Path.open

    def racing_open(self: Path, mode: str = "r", *args: object, **kwargs: object) -> object:
        if self == target and mode == "xb":
            self.write_bytes(b"theirs\n")
        return real_open(self, mode, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "open", racing_open)  # type: ignore[attr-defined]
    lines = scaffold.scaffold(config(tmp_path), ["ideas"])
    assert "skipped  ideas/ideas.jsonl (appeared during this run)" in lines
    assert target.read_bytes() == b"theirs\n"
    files = record(tmp_path)["files"]
    assert isinstance(files, list)
    assert "ideas/ideas.jsonl" not in [entry["path"] for entry in files]
    assert "ideas/priority.yaml" in [entry["path"] for entry in files]


# --- the scaffold resolves every key before its first write ----------------------------------


def test_scaffold_refuses_an_outside_ideas_path_and_writes_nothing(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.jsonl"
    code = scaffold.main(["--feature", "all", "--consent", "gitignore", "--root", str(root),
                          "--ideas-path", str(outside)])
    assert code == 2
    assert listing(root) == {}
    assert not outside.exists()


def test_scaffold_refuses_an_outside_docs_root_and_writes_nothing(tmp_path: Path) -> None:
    """``docs_root`` is a later seed than ``ideas_path``, so a scaffold that resolves keys as it
    goes writes the ideas files before it reaches the bad key."""
    root = tmp_path / "repo"
    root.mkdir()
    code = scaffold.main(["--feature", "all", "--consent", "gitignore", "--root", str(root),
                          "--docs-root", "../outside"])
    assert code == 2
    assert listing(root) == {}
    assert not (tmp_path / "outside").exists()


def test_the_project_feature_seeds_its_files_and_ignores_local_yaml(tmp_path: Path) -> None:
    lines = scaffold.scaffold(config(tmp_path), ["project"], consent=["gitignore"])
    for name in ("project.yaml", "local.example.yaml", "schemas/project.schema.json",
                 "schemas/local.schema.json"):
        assert (tmp_path / ".idea-realization" / name).is_file(), lines
    assert (tmp_path / ".gitignore").read_text() == "/.idea-realization/local.yaml\n"
    # The seeded project.yaml is valid and supplies the integration branch.
    resolved = config(tmp_path)
    assert (resolved.text("integration_branch"), resolved.sources["integration_branch"]) == (
        "main", "project.yaml")


def test_the_seeded_local_example_is_valid_local_yaml(tmp_path: Path) -> None:
    scaffold.scaffold(config(tmp_path), ["project"])
    example = tmp_path / ".idea-realization" / "local.example.yaml"
    example.rename(tmp_path / ".idea-realization" / "local.yaml")
    resolved = config(tmp_path)
    assert resolved.text("dev_port_range") == "3000-3099"
    assert resolved.product_root() is None  # the placeholder counts as unset
    assert resolved.invalid() == []


def test_edit_consent_is_recorded_once_per_selected_config_file(tmp_path: Path) -> None:
    scaffold.scaffold(config(tmp_path), ["project"], consent=["edit"])
    lines = scaffold.scaffold(config(tmp_path), ["product", "project"], consent=["edit"])
    assert "recorded consent to edit .idea-realization/product.yaml" in lines
    consent = record(tmp_path)["consent"]
    assert isinstance(consent, list)
    assert sorted(entry["path"] for entry in consent if entry["target"] == "edit") == [
        ".idea-realization/product.yaml", ".idea-realization/project.yaml"]


def test_edit_consent_on_a_dry_run_records_nothing(tmp_path: Path) -> None:
    lines = scaffold.scaffold(config(tmp_path), ["project"], dry_run=True, consent=["edit"])
    assert "would record  consent to edit .idea-realization/project.yaml" in lines
    assert list(tmp_path.iterdir()) == []


# --- owners, and refreshing the plugin-owned schema copies -----------------------------------


def test_every_recorded_file_names_its_owner(tmp_path: Path) -> None:
    scaffold.scaffold(config(tmp_path), list(scaffold.FEATURES))
    files = record(tmp_path)["files"]
    assert isinstance(files, list)
    owners = {entry["path"]: entry["owner"] for entry in files}
    assert owners[".idea-realization/schemas/backlog.schema.json"] == "plugin"
    assert owners["backlog/backlog.yaml"] == "repository"
    assert owners[".idea-realization/project.yaml"] == "repository"
    assert {path for path, owner in owners.items() if owner == "plugin"} == {
        path for path in owners if path.startswith(".idea-realization/schemas/")}


def fake_plugin(tmp_path: Path, text: str) -> Path:
    plugin = tmp_path / "plugin"
    (plugin / "schemas").mkdir(parents=True, exist_ok=True)
    (plugin / "schemas" / "backlog.schema.json").write_text(text)
    return plugin


def test_refresh_replaces_a_stale_schema_copy_and_records_the_new_hash(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    plugin = fake_plugin(tmp_path, '{"maximum": 10}\n')
    scaffold.scaffold(config(root), ["backlog"], plugin_root=plugin)
    backlog = root / "backlog" / "backlog.yaml"
    backlog.write_text("edited by a claim\n")
    fake_plugin(tmp_path, '{"maximum": 15}\n')
    copy = root / ".idea-realization" / "schemas" / "backlog.schema.json"

    before = listing(root)
    lines = scaffold.scaffold(config(root), ["backlog"], plugin_root=plugin, dry_run=True,
                              refresh_schemas=True)
    assert "would refresh  .idea-realization/schemas/backlog.schema.json" in lines
    assert listing(root) == before

    lines = scaffold.scaffold(config(root), ["backlog"], plugin_root=plugin,
                              refresh_schemas=True)
    assert "refreshed  .idea-realization/schemas/backlog.schema.json" in lines
    assert "skipped  backlog/backlog.yaml (exists)" in lines
    assert copy.read_text() == '{"maximum": 15}\n'
    assert backlog.read_text() == "edited by a claim\n"
    files = record(root)["files"]
    assert isinstance(files, list)
    entry = next(item for item in files if item["path"] == copy.relative_to(root).as_posix())
    assert entry["sha256"] == hashlib.sha256(copy.read_bytes()).hexdigest()
    assert entry["owner"] == "plugin"

    lines = scaffold.scaffold(config(root), ["backlog"], plugin_root=plugin,
                              refresh_schemas=True)
    assert "skipped  .idea-realization/schemas/backlog.schema.json (current)" in lines


def test_without_refresh_a_stale_schema_copy_is_left_alone(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    plugin = fake_plugin(tmp_path, "old\n")
    scaffold.scaffold(config(root), ["backlog"], plugin_root=plugin)
    fake_plugin(tmp_path, "new\n")
    lines = scaffold.scaffold(config(root), ["backlog"], plugin_root=plugin)
    assert "skipped  .idea-realization/schemas/backlog.schema.json (exists)" in lines
    assert (root / ".idea-realization" / "schemas" / "backlog.schema.json").read_text() == "old\n"


def test_cli_refresh_schemas(tmp_path: Path) -> None:
    scaffold.scaffold(config(tmp_path), ["backlog"])
    copy = tmp_path / ".idea-realization" / "schemas" / "backlog.schema.json"
    shipped = copy.read_bytes()
    copy.write_text("{}\n")
    assert scaffold.main(["--feature", "backlog", "--refresh-schemas",
                          "--root", str(tmp_path)]) == 0
    assert copy.read_bytes() == shipped


def test_recreating_a_recorded_directory_leaves_the_record_byte_identical(tmp_path: Path) -> None:
    """A fresh clone has the tracked record but not the gitignored staging directory. Recreating
    the directory must not rewrite the record, or the checkout is dirty after the scaffold."""
    scaffold.scaffold(config(tmp_path), list(scaffold.FEATURES))
    before = (tmp_path / scaffold.RECORD).read_bytes()
    staging = config(tmp_path).path("staging_dir")
    staging.rmdir()
    lines = scaffold.scaffold(config(tmp_path), list(scaffold.FEATURES))
    assert staging.is_dir()
    assert (tmp_path / scaffold.RECORD).read_bytes() == before
    assert f"skipped  {scaffold.RECORD.as_posix()} (already records every path)" in lines


def test_a_new_path_still_updates_the_record(tmp_path: Path) -> None:
    scaffold.scaffold(config(tmp_path), ["ideas"])
    before = record(tmp_path)
    scaffold.scaffold(config(tmp_path), ["ideas", "backlog"])
    after = record(tmp_path)
    assert "backlog" in after["features"] and after != before
    assert any(entry["path"] == "backlog/backlog.yaml" for entry in after["files"])
