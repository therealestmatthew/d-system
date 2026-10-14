"""tools/aws-sandbox: what it runs, and what it refuses, without calling AWS."""

from __future__ import annotations

from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import pytest

WRAPPER = Path(__file__).resolve().parent.parent / "tools" / "aws-sandbox"
loader = SourceFileLoader("aws_sandbox", str(WRAPPER))
spec = spec_from_loader("aws_sandbox", loader)
assert spec is not None
sandbox = module_from_spec(spec)
loader.exec_module(sandbox)

ENV = {"IDEA_REALIZATION_AWS_PROFILE": "team-sandbox", "IDEA_REALIZATION_AWS_REGION": "us-east-1",
       "PATH": "/usr/bin"}


def build(*argv: str, env: dict[str, str] | None = None) -> tuple[list[str], dict[str, str]]:
    result: tuple[list[str], dict[str, str]] = sandbox.build(list(argv), dict(env or ENV))
    return result


def refused(*argv: str, env: dict[str, str] | None = None) -> str:
    with pytest.raises(sandbox.Refused) as caught:
        build(*argv, env=env)
    return str(caught.value)


def test_read_runs_with_the_configured_profile_and_region() -> None:
    command, _ = build("read", "ec2", "describe-instances", "--max-items", "5")
    assert command == ["aws", "ec2", "describe-instances", "--max-items", "5",
                       "--profile", "team-sandbox", "--region", "us-east-1"]


@pytest.mark.parametrize("operation", ["list-buckets", "get-caller-identity", "ls", "tail",
                                       "filter-log-events", "describe-stacks"])
def test_read_operations_pass(operation: str) -> None:
    build("read", "svc", operation)


@pytest.mark.parametrize("operation", ["create-bucket", "delete-stack", "put-object",
                                       "update-function-code", "run-instances", "cp"])
def test_read_mode_refuses_writes(operation: str) -> None:
    assert "not a read operation" in refused("read", "svc", operation)


def test_write_mode_allows_create() -> None:
    command, _ = build("write", "s3api", "create-bucket", "--bucket", "demo")
    assert command[:3] == ["aws", "s3api", "create-bucket"]


def test_missing_profile_refused() -> None:
    assert "no sandbox profile configured" in refused(
        "read", "s3", "ls", env={"IDEA_REALIZATION_AWS_REGION": "us-east-1", "PATH": ""})


def test_default_profile_refused() -> None:
    assert "'default'" in refused(
        "read", "s3", "ls", env={**ENV, "IDEA_REALIZATION_AWS_PROFILE": "default"})


def test_missing_region_refused() -> None:
    assert "no sandbox region configured" in refused(
        "read", "s3", "ls", env={"IDEA_REALIZATION_AWS_PROFILE": "team-sandbox", "PATH": ""})


@pytest.mark.parametrize("option", ["--profile", "--profile=other", "--region", "--endpoint-url"])
def test_caller_cannot_choose_profile_region_or_endpoint(option: str) -> None:
    assert "set by the wrapper" in refused("read", "s3", "ls", option)


@pytest.mark.parametrize("service,operation", [("secretsmanager", "get-secret-value"),
                                               ("ssm", "get-parameter"),
                                               ("lambda", "get-function")])
def test_secret_reads_refused(service: str, operation: str) -> None:
    assert "reveals a secret" in refused("read", service, operation)
    assert "reveals a secret" in refused("write", service, operation)


def test_configure_refused() -> None:
    assert "a person does that" in refused("write", "configure", "set")


def test_credentials_in_the_environment_are_removed() -> None:
    _, env = build("read", "s3", "ls", env={**ENV, "AWS_PROFILE": "default",
                                            "AWS_ACCESS_KEY_ID": "x", "AWS_SECRET_ACCESS_KEY": "y"})
    assert not {"AWS_PROFILE", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"} & set(env)


def test_exec_sets_profile_and_region_for_other_tools() -> None:
    command, env = build("exec", "cdk", "deploy", env={**ENV, "AWS_PROFILE": "default"})
    assert command == ["cdk", "deploy"]
    assert env["AWS_PROFILE"] == "team-sandbox" and env["AWS_REGION"] == "us-east-1"


def test_exec_refuses_the_aws_cli() -> None:
    assert "not exec" in refused("exec", "/usr/local/bin/aws", "s3", "ls")


def test_unknown_mode_refused() -> None:
    assert "usage" in refused("delete", "s3", "rb")
