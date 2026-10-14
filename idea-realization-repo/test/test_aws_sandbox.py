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

ENV = {"IDEA_REALIZATION_AWS_READ_PROFILE": "sandbox-read",
       "IDEA_REALIZATION_AWS_DEPLOY_PROFILE": "sandbox-deploy",
       "IDEA_REALIZATION_AWS_REGION": "us-east-1", "PATH": ""}


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
                       "--profile", "sandbox-read", "--region", "us-east-1"]


@pytest.mark.parametrize("operation", ["list-buckets", "get-caller-identity", "ls", "tail",
                                       "filter-log-events", "describe-stacks"])
def test_read_operations_pass(operation: str) -> None:
    build("read", "svc", operation)


@pytest.mark.parametrize("operation", ["create-bucket", "delete-stack", "put-object",
                                       "update-function-code", "run-instances", "cp"])
def test_read_mode_refuses_writes(operation: str) -> None:
    assert "not a read operation" in refused("read", "svc", operation)


def test_write_mode_uses_the_deploy_profile() -> None:
    command, _ = build("write", "s3api", "create-bucket", "--bucket", "demo")
    assert command == ["aws", "s3api", "create-bucket", "--bucket", "demo",
                       "--profile", "sandbox-deploy", "--region", "us-east-1"]


def test_read_mode_never_gets_the_deploy_profile() -> None:
    for operation in ("describe-stacks", "list-buckets", "get-caller-identity"):
        command, _ = build("read", "svc", operation)
        assert "sandbox-deploy" not in command


@pytest.mark.parametrize("missing", ["IDEA_REALIZATION_AWS_READ_PROFILE",
                                     "IDEA_REALIZATION_AWS_DEPLOY_PROFILE",
                                     "IDEA_REALIZATION_AWS_REGION"])
def test_any_missing_value_refused_in_every_mode(missing: str) -> None:
    env = {k: v for k, v in ENV.items() if k != missing}
    for mode in ("read", "write"):
        assert "is not configured" in refused(mode, "s3", "ls", env=env)


@pytest.mark.parametrize("variable", ["IDEA_REALIZATION_AWS_READ_PROFILE",
                                      "IDEA_REALIZATION_AWS_DEPLOY_PROFILE"])
def test_default_profile_refused(variable: str) -> None:
    assert "'default'" in refused("read", "s3", "ls", env={**ENV, variable: "default"})


def test_one_profile_for_both_roles_refused() -> None:
    assert "the same profile" in refused(
        "read", "s3", "ls", env={**ENV, "IDEA_REALIZATION_AWS_DEPLOY_PROFILE": "sandbox-read"})


def test_read_mode_refuses_sync_delete() -> None:
    assert "--delete is not a read" in refused("read", "s3", "ls", "--delete")


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


def test_exec_gives_other_tools_the_deploy_profile() -> None:
    command, env = build("exec", "cdk", "deploy", env={**ENV, "AWS_PROFILE": "default"})
    assert command == ["cdk", "deploy"]
    assert env["AWS_PROFILE"] == "sandbox-deploy" and env["AWS_REGION"] == "us-east-1"


def test_exec_of_the_aws_cli_gets_the_write_checks() -> None:
    command, _ = build("exec", "/usr/local/bin/aws", "s3api", "create-bucket")
    assert command[-4:] == ["--profile", "sandbox-deploy", "--region", "us-east-1"]
    assert "reveals a secret" in refused("exec", "aws", "secretsmanager", "get-secret-value")
    assert "set by the wrapper" in refused("exec", "aws", "s3", "ls", "--profile", "x")


def test_exec_refuses_a_caller_profile() -> None:
    assert "set by the wrapper" in refused("exec", "cdk", "deploy", "--profile", "other")


def test_unknown_mode_refused() -> None:
    assert "usage" in refused("delete", "s3", "rb")
