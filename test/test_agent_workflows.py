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


def test_source_and_target_paths_must_be_repository_relative() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["workflows"][0]["source"] = str(
        ROOT / "agent-workflows" / "orient.md"
    )
    with pytest.raises(generator.WorkflowError, match="must be repository-relative"):
        generator.validate_and_render(manifest, ROOT)

    manifest = copy.deepcopy(_manifest())
    manifest["workflows"][0]["targets"][0]["path"] = str(
        ROOT / ".claude" / "skills" / "orient" / "SKILL.md"
    )
    with pytest.raises(generator.WorkflowError, match="must be repository-relative"):
        generator.validate_and_render(manifest, ROOT)


def test_every_capability_mapping_must_be_a_nonempty_string() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["workflows"][0]["targets"][0]["capabilities"]["bogus"] = False
    with pytest.raises(generator.WorkflowError, match="malformed capability mappings"):
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


def _workflow(manifest: dict[str, Any], workflow_id: str) -> dict[str, Any]:
    for workflow in manifest["workflows"]:
        if workflow["id"] == workflow_id:
            return workflow
    raise KeyError(workflow_id)


def _target(workflow: dict[str, Any], host: str, kind: str) -> dict[str, Any]:
    for target in workflow["targets"]:
        if target["host"] == host and target["kind"] == kind:
            return target
    raise KeyError((host, kind))


# --- phase-port-02: safe commands and the idea-triage agent -----------------------------------


def test_owner_only_workflow_cannot_target_a_claude_command() -> None:
    """A command is reachable through Claude Code's SlashCommand tool, so it is agent-discoverable
    exactly like a skill — an owner-only workflow (e.g. a future session-close-shaped entry) must be
    refused there too, not only when targeting kind: skill."""
    manifest = copy.deepcopy(_manifest())
    workflow = _workflow(manifest, "idea")
    workflow["authority"] = "owner-only"
    with pytest.raises(generator.WorkflowError, match="owner-only workflow"):
        generator.validate_and_render(manifest, ROOT)


def test_session_close_is_not_a_declared_workflow() -> None:
    """Session closure stays owner-only and hand-authored. It must never enter the manifest that
    feeds agent-discoverable Claude/Codex adapters."""
    manifest = _manifest()
    ids = {workflow["id"] for workflow in manifest["workflows"]}
    names = {workflow["name"] for workflow in manifest["workflows"]}
    assert "session-close" not in ids
    assert "session-close" not in names

    outputs = generator.validate_and_render(manifest, ROOT)
    session_close = (ROOT / ".claude" / "commands" / "session-close.md").resolve()
    assert session_close not in outputs


def test_claude_idea_triage_agent_retains_haiku_medium_and_turn_cap() -> None:
    outputs = generator.validate_and_render(_manifest(), ROOT)
    path = ROOT / ".claude" / "agents" / "idea-triage.md"
    rendered = outputs[path]
    assert "name: idea-triage" in rendered
    assert "model: haiku" in rendered
    assert "effort: medium" in rendered
    assert "maxTurns: 30" in rendered
    assert "tools: Read, Grep, Bash" in rendered


def test_codex_idea_triage_agent_declares_verified_model_and_unsupported_limits() -> None:
    outputs = generator.validate_and_render(_manifest(), ROOT)
    path = ROOT / ".codex" / "agents" / "idea-triage.toml"
    rendered = outputs[path]
    assert 'model = "gpt-5.6-luna"' in rendered
    assert 'model_reasoning_effort = "medium"' in rendered
    assert 'sandbox_mode = "workspace-write"' in rendered
    assert "turn or token" in rendered and "budget" in rendered
    assert 'name = "idea-triage"' in rendered
    # The generator writes the canonical body verbatim as developer_instructions; it must round-trip
    # through TOML rather than being silently truncated or mis-escaped.
    import tomllib

    parsed = tomllib.loads(rendered)
    assert parsed["developer_instructions"].startswith("# idea-triage-agent")
    assert "Never write a `linked` event" in parsed["developer_instructions"]
    assert "Never call `status ... promoted`" in parsed["developer_instructions"]


def test_codex_agent_target_must_declare_unsupported_limits() -> None:
    manifest = copy.deepcopy(_manifest())
    workflow = _workflow(manifest, "idea-triage-agent")
    target = _target(workflow, "codex", "agent")
    target["render"]["unsupported_limits"] = []
    with pytest.raises(generator.WorkflowError, match="unsupported_limits"):
        generator.validate_and_render(manifest, ROOT)


def test_claude_agent_render_requires_every_field() -> None:
    manifest = copy.deepcopy(_manifest())
    workflow = _workflow(manifest, "idea-triage-agent")
    target = _target(workflow, "claude", "agent")
    del target["render"]["max_turns"]
    with pytest.raises(generator.WorkflowError, match="render.max_turns"):
        generator.validate_and_render(manifest, ROOT)


def test_no_generated_idea_triage_output_can_apply_a_link_or_promotion() -> None:
    """R05/acceptance: no generated agent or skill may apply a link, promotion, discard, or backlog
    completion transition. The role may only ever *propose* one and must say so explicitly in every
    rendered form."""
    outputs = generator.validate_and_render(_manifest(), ROOT)
    # Check the role's two generated forms (Claude agent, Codex agent) for the explicit
    # never-execute guarantees, and the driver's two generated forms (Claude command, Open Agent
    # Skills skill) for never containing an unconditional promotion/status call of their own.
    claude_role = outputs[ROOT / ".claude" / "agents" / "idea-triage.md"]
    codex_role_toml = outputs[ROOT / ".codex" / "agents" / "idea-triage.toml"]
    import tomllib

    codex_role = tomllib.loads(codex_role_toml)["developer_instructions"]
    for text in (claude_role, codex_role):
        assert "Never write a `linked` event" in text
        assert "Never call `status ... promoted`" in text
        assert "PROPOSED LINK:" in text
        assert "PROPOSED PROMOTION:" in text

    claude_driver = outputs[ROOT / ".claude" / "commands" / "idea-triage.md"]
    skills_driver = outputs[ROOT / ".agents" / "skills" / "idea-triage" / "SKILL.md"]
    for text in (claude_driver, skills_driver):
        assert "never moves an idea past `triaged`" in text
        # The driver only ever *names* the sanctioned link/promotion commands as candidates the
        # owner reviews by hand — it must never contain an executable invocation of either.
        assert "uv run python tools/append_idea.py link" not in text
        assert "uv run python tools/append_idea.py status <id> promoted" not in text


def test_idea_triage_agent_capabilities_never_grant_a_status_write_tool() -> None:
    """The idea-triage-agent role's tool allowlist must never include an edit/write capability,
    since it is only ever permitted to run the sanctioned `annotate` command through a shell/run
    capability — never `Edit`/`Write`, which could be used to hand-edit the append-only log."""
    manifest = _manifest()
    workflow = _workflow(manifest, "idea-triage-agent")
    for target in workflow["targets"]:
        assert "edit_files" not in target["capabilities"]
        assert "write_files" not in target["capabilities"]
        assert "ask_user" not in target["capabilities"]
