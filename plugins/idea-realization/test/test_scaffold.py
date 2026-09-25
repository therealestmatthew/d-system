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
