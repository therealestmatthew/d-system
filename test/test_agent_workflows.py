"""Contract tests for canonical agent workflows and generated host adapters."""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load() -> Any:
    spec = importlib.util.spec_from_file_location(
        "generate_agent_workflows", ROOT / "tools" / "generate_agent_workflows.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


generator = _load()


def _manifest() -> dict[str, Any]:
    return generator.load_manifest(ROOT / "agent-workflows" / "workflows.yaml")


def _fixture_root(tmp_path: Path, manifest: dict[str, Any]) -> tuple[Path, Path]:
    root = tmp_path / "repo"
    root.mkdir()
    for workflow in manifest["workflows"]:
        source = root / workflow["source"]
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(f"# {workflow['name']}\n\nFixture body.\n", encoding="utf-8")
    path = root / "agent-workflows" / "workflows.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return root, path


def test_committed_adapters_match_canonical_sources() -> None:
    outputs = generator.validate_and_render(_manifest(), ROOT)
    assert outputs
    for path, expected in outputs.items():
        assert path.read_text(encoding="utf-8") == expected


def test_rendering_is_deterministic() -> None:
    manifest = _manifest()
    first = generator.validate_and_render(manifest, ROOT)
    second = generator.validate_and_render(manifest, ROOT)
    assert first == second


def test_check_detects_a_hand_edit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, manifest_path = _fixture_root(tmp_path, _manifest())
    outputs = generator.validate_and_render(generator.load_manifest(manifest_path), root)
    for path, expected in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
    next(iter(outputs)).write_text("tampered\n", encoding="utf-8")
    monkeypatch.setattr(generator, "ROOT", root)
    monkeypatch.setattr(generator, "MANIFEST", manifest_path)
    assert generator.main(["--check"]) == 1


def test_owner_only_workflow_cannot_be_an_agent_adapter() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["workflows"][0]["authority"] = "owner-only"
    with pytest.raises(generator.WorkflowError, match="owner-only workflow"):
        generator.validate_and_render(manifest, ROOT)


def test_required_capability_must_be_mapped_or_explicitly_unsupported() -> None:
    manifest = copy.deepcopy(_manifest())
    target = manifest["workflows"][0]["targets"][0]
    del target["capabilities"]["read_files"]
    with pytest.raises(generator.WorkflowError, match="undeclared capabilities"):
        generator.validate_and_render(manifest, ROOT)

    target["unsupported"].append("read_files")
    generator.validate_and_render(manifest, ROOT)


def test_target_cannot_escape_its_host_directory() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["workflows"][0]["targets"][0]["path"] = "outside/SKILL.md"
    with pytest.raises(generator.WorkflowError, match="outside .claude/skills"):
        generator.validate_and_render(manifest, ROOT)


def test_target_cannot_traverse_out_of_its_host_directory() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["workflows"][0]["targets"][0]["path"] = (
        ".claude/skills/../agents/orient.md"
    )
    with pytest.raises(generator.WorkflowError, match="outside .claude/skills"):
        generator.validate_and_render(manifest, ROOT)


def test_source_must_exist_inside_the_canonical_directory() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["workflows"][0]["source"] = "AGENTS.md"
    with pytest.raises(generator.WorkflowError, match="outside agent-workflows"):
        generator.validate_and_render(manifest, ROOT)

    manifest["workflows"][0]["source"] = "agent-workflows/missing.md"
    with pytest.raises(generator.WorkflowError, match="source does not exist"):
        generator.validate_and_render(manifest, ROOT)


def test_checkpoint_source_and_outputs_forbid_completion() -> None:
    outputs = generator.validate_and_render(_manifest(), ROOT)
    checkpoint = (ROOT / "agent-workflows" / "checkpoint.md").read_text(encoding="utf-8")
    boundary = "Never set a phase's `status` to `complete`."
    assert boundary in checkpoint
    for path, rendered in outputs.items():
        if path.parent.name == "checkpoint":
            assert boundary in rendered


def test_execute_prompt_uses_canonical_checkpoint_fallback() -> None:
    prompt = (ROOT / "docs" / "02-prompts" / "PROMPT-008-execute-a-phase.md").read_text(
        encoding="utf-8"
    )
    assert "agent-workflows/checkpoint.md" in prompt
    assert ".claude/skills/checkpoint/SKILL.md" not in prompt
    assert "Never write `status: complete`." in prompt
