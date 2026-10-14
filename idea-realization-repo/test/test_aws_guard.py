"""tools/hooks/aws_guard.py, run as Claude Code runs it: hook JSON on stdin, exit 2 to refuse."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / "tools" / "hooks" / "aws_guard.py"


def run(command: str, agent: str | None = None, cwd: Path | None = None,
        tool: str = "Bash") -> subprocess.CompletedProcess[str]:
    event: dict[str, object] = {"hook_event_name": "PreToolUse", "tool_name": tool,
                                "tool_input": {"command": command}, "cwd": str(cwd or ".")}
    if agent:
        event["agent_type"] = agent
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(event), text=True,
                          capture_output=True, check=False)


def allowed(command: str, agent: str | None = None, cwd: Path | None = None) -> bool:
    return run(command, agent, cwd).returncode == 0


@pytest.mark.parametrize("command", [
    "git status",
    'git commit -m "deploy the stack with cdk and aws"',
    "uv run pytest",
    "tools/aws-sandbox read s3 ls",
    "./tools/aws-sandbox whoami",
    "cd product && tools/aws-sandbox read cloudformation describe-stacks",
    "echo aws",
    "grep -rn boto3 src/",
])
def test_ordinary_and_read_commands_pass(command: str) -> None:
    assert allowed(command)


@pytest.mark.parametrize("command", [
    "aws s3 ls",
    "/usr/local/bin/aws sts get-caller-identity",
    "AWS_PROFILE=default aws s3 ls",
    "env AWS_PROFILE=x tools/aws-sandbox read s3 ls",
    "git status && aws iam create-access-key",
    "git status\naws s3 rb s3://bucket --force",
    'bash -c "aws s3 ls"',
    "sh -lc 'echo hi; aws s3 ls'",
    "eval aws s3 ls",
    "sudo aws s3 ls",
    "echo bucket | xargs aws s3 rb",
    "npx cdk deploy",
    "npx aws-cdk deploy",
    "uv run cdk deploy",
    "cdk destroy",
    "sam deploy",
    "terraform apply",
    "pulumi up",
    'python3 -c "import boto3; boto3.client(\'iam\').create_access_key()"',
    "python -m awscli s3 ls",
    "node -e \"require('@aws-sdk/client-iam')\"",
    "cat ~/.aws/credentials",
    "export AWS_ACCESS_KEY_ID=abc",
])
def test_aws_outside_the_wrapper_is_refused(command: str) -> None:
    result = run(command, agent="aws-deploy")
    assert result.returncode == 2, command
    assert result.stderr.startswith("aws_guard: refused:")


def test_a_script_that_imports_an_sdk_is_refused(tmp_path: Path) -> None:
    (tmp_path / "deploy.py").write_text("import boto3\n", encoding="utf-8")
    (tmp_path / "plain.py").write_text("print('hi')\n", encoding="utf-8")
    assert not allowed("python3 deploy.py", cwd=tmp_path)
    assert allowed("python3 plain.py", cwd=tmp_path)


def test_the_same_script_runs_under_exec_from_aws_deploy(tmp_path: Path) -> None:
    (tmp_path / "deploy.py").write_text("import boto3\n", encoding="utf-8")
    assert allowed("tools/aws-sandbox exec python3 deploy.py", agent="aws-deploy", cwd=tmp_path)


@pytest.mark.parametrize("mode", ["write", "exec"])
@pytest.mark.parametrize("agent", [None, "aws-infra-reviewer", "aws-ops-inspector",
                                   "bedrock-claude-advisor", "aws-cost-optimizer",
                                   "phase-adversary"])
def test_only_aws_deploy_writes(mode: str, agent: str | None) -> None:
    result = run(f"tools/aws-sandbox {mode} s3api create-bucket --bucket b", agent=agent)
    assert result.returncode == 2
    assert "aws-deploy agent only" in result.stderr


@pytest.mark.parametrize("mode", ["write", "exec"])
def test_aws_deploy_writes(mode: str) -> None:
    assert allowed(f"tools/aws-sandbox {mode} s3api create-bucket --bucket b", agent="aws-deploy")


def test_read_agents_read() -> None:
    assert allowed("tools/aws-sandbox read ce get-cost-and-usage", agent="aws-cost-optimizer")


def test_other_tools_are_not_inspected() -> None:
    assert run("aws s3 ls", tool="Read").returncode == 0


def test_unreadable_input_is_refused() -> None:
    result = subprocess.run([sys.executable, str(HOOK)], input="not json", text=True,
                            capture_output=True, check=False)
    assert result.returncode == 2
