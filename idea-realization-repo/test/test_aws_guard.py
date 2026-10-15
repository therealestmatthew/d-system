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


@pytest.mark.parametrize("command", [
    "echo `aws s3 ls`",
    "x=$(aws sts get-caller-identity)",
    "diff <(aws s3 ls) expected.txt",
    "awscurl https://example.execute-api.us-east-1.amazonaws.com/",
    "docker run --rm amazon/aws-cli s3 ls",
    "docker run --rm public.ecr.aws/aws-cli/aws-cli s3 ls",
    "podman run -e AWS_ACCESS_KEY_ID=x python:3 python app.py",
    "docker run --env=AWS_PROFILE=default python:3 true",
    "docker run -v ~/.aws:/root/.aws python:3 true",
    "printf 'import boto3\\n' > /tmp/x.py && python3 /tmp/x.py",
    "cat > run.sh <<'X'\naws s3 ls\nX\nbash run.sh",
    "echo 'aws s3 rb s3://b' | tee go.sh && sh go.sh",
])
def test_round_two_bypasses_are_refused(command: str) -> None:
    result = run(command, agent="aws-deploy")
    assert result.returncode == 2, command
    assert result.stderr.startswith("aws_guard: refused:")


def test_a_shell_script_calling_the_aws_cli_is_refused(tmp_path: Path) -> None:
    (tmp_path / "deploy.sh").write_text("#!/bin/sh\nset -e\naws s3 ls\n", encoding="utf-8")
    (tmp_path / "build.sh").write_text("#!/bin/sh\nnpm run build\n", encoding="utf-8")
    assert not allowed("bash deploy.sh", cwd=tmp_path)
    assert not allowed("./deploy.sh", cwd=tmp_path)
    assert not allowed("sh ./deploy.sh", cwd=tmp_path)
    assert allowed("./build.sh", cwd=tmp_path)


def test_a_python_script_calling_the_aws_cli_is_refused(tmp_path: Path) -> None:
    (tmp_path / "x.py").write_text("import subprocess\nsubprocess.run(['aws', 's3', 'ls'])\n",
                                   encoding="utf-8")
    assert not allowed("python3 x.py", cwd=tmp_path)


def test_go_run_with_the_aws_sdk_is_refused(tmp_path: Path) -> None:
    (tmp_path / "main.go").write_text(
        'package main\nimport "github.com/aws/aws-sdk-go-v2/config"\n', encoding="utf-8")
    assert not allowed("go run .", cwd=tmp_path)
    assert not allowed("go run main.go", cwd=tmp_path)


def test_java_jar_with_the_aws_sdk_is_refused(tmp_path: Path) -> None:
    import zipfile
    with zipfile.ZipFile(tmp_path / "app.jar", "w") as archive:
        archive.writestr("software/amazon/awssdk/core/X.class", b"")
    with zipfile.ZipFile(tmp_path / "plain.jar", "w") as archive:
        archive.writestr("com/example/App.class", b"")
    assert not allowed("java -jar app.jar", cwd=tmp_path)
    assert allowed("java -jar plain.jar", cwd=tmp_path)


def test_package_scripts_are_checked(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(json.dumps({"scripts": {
        "deploy": "cdk deploy --all", "build": "tsc", "start": "aws s3 ls"}}), encoding="utf-8")
    assert not allowed("npm run deploy", cwd=tmp_path)
    assert not allowed("npm start", cwd=tmp_path)
    assert not allowed("yarn deploy", cwd=tmp_path)
    assert allowed("npm run build", cwd=tmp_path)


@pytest.mark.parametrize("command", [
    'echo "remember to check the aws console" > notes.md',
    'git commit -m "$(cat message.txt)"',
    "docker run --rm -e APP_MODE=dev python:3 python -V",
    "printf 'print(1)\\n' > /tmp/y.py && python3 /tmp/y.py",
])
def test_ordinary_commands_still_pass(command: str) -> None:
    assert allowed(command)


@pytest.mark.parametrize("agent", [None, "aws-infra-reviewer", "aws-ops-inspector",
                                   "bedrock-claude-advisor", "aws-cost-optimizer",
                                   "phase-adversary", "validator-code", "aws-deploy"])
def test_synth_is_open_to_every_caller(agent: str | None) -> None:
    assert allowed("tools/aws-sandbox synth", agent=agent)
    assert allowed("./tools/aws-sandbox synth --dir ../product/infra --quiet", agent=agent)


@pytest.mark.parametrize("command", [
    "npx ampx sandbox",
    "ampx pipeline-deploy --branch dev",
    "npx @aws-amplify/backend-cli sandbox",
    "npx @aws-amplify/backend-cli@1 sandbox",
    "amplify push",
])
def test_amplify_clis_are_guarded_like_cdk(command: str) -> None:
    result = run(command, agent="aws-deploy")
    assert result.returncode == 2, command
    assert "runs" in result.stderr and "directly" in result.stderr


def test_ampx_under_exec_from_aws_deploy() -> None:
    assert allowed("tools/aws-sandbox exec npx ampx sandbox --once", agent="aws-deploy")
    assert not allowed("tools/aws-sandbox exec npx ampx sandbox --once", agent="aws-ops-inspector")
