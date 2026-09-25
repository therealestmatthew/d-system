"""The workflow-adapter generator, on fixture manifests.

These are the source's generic contract tests. The tests that checked particular workflows of the
repository the generator came from stay there; the plugin ships an empty manifest.
"""

from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path
from typing import Any

import generate_workflows as gen
import pytest
import yaml
from conftest import PLUGIN_ROOT, SCRIPTS

SOURCES = "agent-workflows"


def workflow(**changes: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "orient",
        "name": "orient",
        "description": "Show the state of the repository without changing anything.",
        "authority": "read-only",
        "source": f"{SOURCES}/orient.md",
        "requires": ["read_files", "run_commands"],
        "targets": [
            {"host": "claude", "kind": "skill", "path": ".claude/skills/orient/SKILL.md",
             "capabilities": {"read_files": "Read", "run_commands": "Bash"}, "unsupported": []},
            {"host": "open-agent-skills", "kind": "skill",
             "path": ".agents/skills/orient/SKILL.md",
             "capabilities": {"read_files": "filesystem", "run_commands": "shell"},
             "unsupported": []},
        ],
    }
    base.update(changes)
    return base


def claude_agent(**render: Any) -> dict[str, Any]:
    return {"host": "claude", "kind": "agent", "path": ".claude/agents/scout.md",
            "capabilities": {"read_files": "Read", "run_commands": "Bash"}, "unsupported": [],
            "render": {"tools": "Read, Bash", "model": "a-model", "effort": "low",
                       "max_turns": 10, **render}}


def codex_agent(**render: Any) -> dict[str, Any]:
    return {"host": "codex", "kind": "agent", "path": ".codex/agents/scout.toml",
            "capabilities": {"read_files": "read", "run_commands": "shell"}, "unsupported": [],
            "render": {"model": "a-model", "model_reasoning_effort": "low",
                       "sandbox_mode": "read-only",
                       "unsupported_limits": ["No per-agent turn budget."], **render}}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / SOURCES).mkdir()
    (tmp_path / SOURCES / "orient.md").write_text("# Orient\n\nRead, then report.\n")
    write_manifest(tmp_path, [workflow()])
    return tmp_path


def write_manifest(root: Path, workflows: list[dict[str, Any]]) -> None:
    (root / SOURCES / "workflows.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "workflows": workflows}, sort_keys=False))


def render(root: Path, workflows: list[dict[str, Any]]) -> dict[Path, str]:
    manifest = {"schema_version": 1, "workflows": workflows}
    return gen.validate_and_render(manifest, root, root / SOURCES)


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / "generate_workflows.py"),
                           "--root", str(root), *args],
                          cwd=root, capture_output=True, text=True, check=False)


def test_the_generator_writes_each_target(repo: Path) -> None:
    assert run(repo).returncode == 0
    skill = (repo / ".claude/skills/orient/SKILL.md").read_text()
    assert skill.startswith('---\nname: orient\ndescription: "Show the state')
    assert gen.GENERATED_NOTICE in skill and skill.endswith("Read, then report.\n")
    assert (repo / ".agents/skills/orient/SKILL.md").is_file()


def test_rendering_is_deterministic(repo: Path) -> None:
    assert render(repo, [workflow()]) == render(repo, [workflow()])
    run(repo)
    first = (repo / ".claude/skills/orient/SKILL.md").read_bytes()
    run(repo)
    assert (repo / ".claude/skills/orient/SKILL.md").read_bytes() == first
    assert run(repo, "--check").returncode == 0


def test_a_hand_edit_fails_the_check_naming_the_file(repo: Path) -> None:
    run(repo)
    adapter = repo / ".claude/skills/orient/SKILL.md"
    adapter.write_text(adapter.read_text() + "\nA hand edit.\n")
    result = run(repo, "--check")
    assert result.returncode == 1
    assert str(adapter) in result.stderr


def test_a_missing_adapter_fails_the_check(repo: Path) -> None:
    result = run(repo, "--check")
    assert result.returncode == 1
    assert "missing or stale" in result.stderr


def test_agents_and_commands_render_their_own_fields(repo: Path) -> None:
    command = {"host": "claude", "kind": "command", "path": ".claude/commands/orient.md",
               "capabilities": {"read_files": "Read", "run_commands": "Bash"},
               "unsupported": [], "render": {"argument_hint": "[area]"}}
    outputs = render(repo, [workflow(targets=[claude_agent(), codex_agent(), command])])
    agent = outputs[(repo / ".claude/agents/scout.md").resolve()]
    assert "tools: Read, Bash\nmodel: a-model\neffort: low\nmaxTurns: 10\n" in agent
    codex = outputs[(repo / ".codex/agents/scout.toml").resolve()]
    assert codex.startswith(gen.GENERATED_NOTICE_TOML)
    assert "# No per-agent turn budget." in codex and 'sandbox_mode = "read-only"' in codex
    assert 'argument-hint: "[area]"' in outputs[(repo / ".claude/commands/orient.md").resolve()]


@pytest.mark.parametrize("kind", ["skill", "command", "agent"])
def test_an_owner_only_workflow_cannot_target_an_agent_discoverable_kind(
    repo: Path, kind: str
) -> None:
    target = claude_agent() if kind == "agent" else {
        "host": "claude", "kind": kind,
        "path": f".claude/{'skills/orient/SKILL.md' if kind == 'skill' else 'commands/o.md'}",
        "capabilities": {"read_files": "Read", "run_commands": "Bash"}, "unsupported": []}
    with pytest.raises(gen.WorkflowError, match="owner-only workflow cannot target"):
        render(repo, [workflow(authority="owner-only", targets=[target])])


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"capabilities": {"read_files": "Read"}}, "undeclared capabilities"),
        ({"capabilities": {"read_files": "Read", "run_commands": "Bash", "extra": "X"}},
         "unknown capabilities"),
        ({"unsupported": ["run_commands"]}, "mapped and unsupported"),
        ({"capabilities": {"read_files": "Read", "run_commands": ""}},
         "malformed capability mappings"),
        ({"path": ".claude/elsewhere/SKILL.md"}, "target path is outside"),
        ({"path": ".claude/skills/../../outside.md"}, "target path is outside"),
        ({"path": "/absolute/SKILL.md"}, "must be repository-relative"),
        ({"host": "nowhere"}, "unsupported target nowhere/skill"),
    ],
)
def test_a_malformed_target_is_refused(repo: Path, change: dict[str, Any], message: str) -> None:
    target = copy.deepcopy(workflow()["targets"][0])
    target.update(change)
    with pytest.raises(gen.WorkflowError, match=message):
        render(repo, [workflow(targets=[target])])


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"source": "elsewhere/orient.md"}, "source is outside"),
        ({"source": f"{SOURCES}/missing.md"}, "source does not exist"),
        ({"source": "../escape.md"}, "escapes the repository"),
        ({"name": "Not A Name"}, "invalid skill name"),
        ({"authority": "anyone"}, "unknown authority"),
        ({"description": "x" * 1025}, "description exceeds 1024 characters"),
        ({"targets": []}, "targets must be a nonempty list"),
    ],
)
def test_a_malformed_workflow_is_refused(repo: Path, change: dict[str, Any],
                                         message: str) -> None:
    (repo / "elsewhere").mkdir()
    (repo / "elsewhere" / "orient.md").write_text("x\n")
    with pytest.raises(gen.WorkflowError, match=message):
        render(repo, [workflow(**change)])


def test_duplicate_ids_and_targets_are_refused(repo: Path) -> None:
    with pytest.raises(gen.WorkflowError, match="duplicate workflow id"):
        render(repo, [workflow(), workflow()])
    with pytest.raises(gen.WorkflowError, match="duplicate target path"):
        render(repo, [workflow(), workflow(id="other")])


def test_a_codex_agent_must_declare_its_unsupported_limits(repo: Path) -> None:
    with pytest.raises(gen.WorkflowError, match="unsupported_limits"):
        render(repo, [workflow(targets=[codex_agent(unsupported_limits=[])])])


@pytest.mark.parametrize("field", ["tools", "model", "effort", "max_turns"])
def test_a_claude_agent_render_requires_every_field(repo: Path, field: str) -> None:
    target = claude_agent()
    del target["render"][field]
    with pytest.raises(gen.WorkflowError, match=f"render.{field}"):
        render(repo, [workflow(targets=[target])])


def test_an_invalid_manifest_exits_2(repo: Path) -> None:
    (repo / SOURCES / "workflows.yaml").write_text("schema_version: 2\nworkflows: []\n")
    result = run(repo)
    assert result.returncode == 2
    assert "schema_version must be 1" in result.stderr


def test_the_shipped_manifest_template_is_valid_and_empty(tmp_path: Path) -> None:
    manifest = gen.load_manifest(PLUGIN_ROOT / "templates" / "workflows.yaml")
    assert manifest["workflows"] == []
    assert gen.validate_and_render(manifest, tmp_path, tmp_path) == {}


def test_the_output_root_is_an_argument(repo: Path, tmp_path_factory: Any) -> None:
    out = tmp_path_factory.mktemp("out")
    assert run(repo, "--output-root", str(out)).returncode == 0
    assert (out / ".claude/skills/orient/SKILL.md").is_file()
    assert not (repo / ".claude").exists()
