"""tools/aws-sandbox: what it runs, and what it refuses, without calling AWS."""

from __future__ import annotations

import json
import re
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
                                       "start-query",
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


def test_the_missing_value_refusal_names_local_yaml_first() -> None:
    env = {k: v for k, v in ENV.items() if k != "IDEA_REALIZATION_AWS_READ_PROFILE"}
    message = refused("read", "s3", "ls", env=env)
    assert "aws_read_profile in .idea-realization/local.yaml" in message
    assert message.index("local.yaml") < message.index("IDEA_REALIZATION_AWS_READ_PROFILE")


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


@pytest.mark.parametrize("service,operation", [
    ("secretsmanager", "get-secret-value"), ("ssm", "get-parameter"),
    ("ssm", "get-parameter-history"), ("lambda", "get-function"),
    ("lambda", "list-functions"), ("lambda", "list-versions-by-function"),
    ("amplify", "get-app"), ("amplify", "list-apps"), ("amplify", "get-branch"),
    ("amplify", "list-branches"), ("amplify", "get-webhook"), ("amplify", "list-webhooks"),
    ("ecs", "describe-task-definition"), ("ecs", "describe-tasks"),
    ("codebuild", "batch-get-projects"), ("codebuild", "batch-get-builds"),
    ("codebuild", "batch-get-build-batches"), ("cognito-idp", "describe-user-pool-client"),
    ("cognito-idp", "describe-identity-provider")])
def test_secret_reads_refused(service: str, operation: str) -> None:
    assert "reveals a secret" in refused("read", service, operation)
    assert "reveals a secret" in refused("write", service, operation)


#: AWS CLI operation names that do not follow the IAM action's words split at capitals.
CLI_NAMES = {"amplify:GetWebHook": "get-webhook", "amplify:ListWebHooks": "list-webhooks"}
#: Guard actions the wrapper refuses some other way: not a read operation in read mode, and
#: denied to the deploy role (DenyEveryIamChangeOutsideAppRoles) in write mode.
NOT_A_READ = {"iam:GenerateCredentialReport"}


def test_the_wrapper_refuses_every_read_the_guard_policy_denies() -> None:
    """Each action in the read guard's secret deny has a SECRET_OPERATIONS entry, so the wrapper
    refuses it before the role does (and in write mode, where no guard policy applies)."""
    guard = json.loads((WRAPPER.parent.parent / "aws" / "iam" / "read-only-guard-policy.json")
                       .read_text(encoding="utf-8"))
    statement = next(s for s in guard["Statement"] if s["Sid"] == "DenySecretAndCredentialReads")
    missing = []
    for action in statement["Action"]:
        if action in NOT_A_READ:
            continue
        service, name = action.split(":")
        operation = CLI_NAMES.get(action, re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower())
        if (service, operation) not in sandbox.SECRET_OPERATIONS:
            missing.append((service, operation))
    assert not missing, missing


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


# ---- synth: `cdk synth` with no AWS credential source -------------------------------------------

AMBIENT = {"AWS_ACCESS_KEY_ID": "AKIAEXAMPLE", "AWS_SECRET_ACCESS_KEY": "secret",
           "AWS_SESSION_TOKEN": "token", "AWS_PROFILE": "sandbox-deploy",
           "AWS_DEFAULT_PROFILE": "sandbox-deploy", "AWS_ROLE_ARN": "arn:aws:iam::0:role/x",
           "AWS_WEB_IDENTITY_TOKEN_FILE": "/tmp/token", "AWS_CONFIG_FILE": "/home/x/.aws/config",
           "AWS_SHARED_CREDENTIALS_FILE": "/home/x/.aws/credentials",
           "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI": "/v2/credentials",
           "AWS_CONTAINER_CREDENTIALS_FULL_URI": "http://169.254.170.2/creds",
           "AWS_EC2_METADATA_DISABLED": "false", "BOTO_CONFIG": "/home/x/.boto",
           "CDK_DEFAULT_ACCOUNT": "000000000000"}


def assert_no_credential_source(env: dict[str, str]) -> None:
    aws = {k: v for k, v in env.items() if k.startswith(("AWS_", "BOTO_"))}
    assert aws == {"AWS_EC2_METADATA_DISABLED": "true", "AWS_CONFIG_FILE": "/dev/null",
                   "AWS_SHARED_CREDENTIALS_FILE": "/dev/null"}
    assert "CDK_DEFAULT_ACCOUNT" not in env
    assert "sandbox-read" not in env.values() and "sandbox-deploy" not in env.values()


def test_synth_strips_every_credential_source() -> None:
    command, env = build("synth", env={**ENV, **AMBIENT})
    assert command[-1] == "synth"
    assert_no_credential_source(env)


def test_synth_needs_no_profile_configuration() -> None:
    command, env = build("synth", "--quiet", env={"PATH": "", **AMBIENT})
    assert command[-2:] == ["synth", "--quiet"]
    assert_no_credential_source(env)


@pytest.mark.parametrize("option", ["--profile", "--profile=x", "--role-arn", "-r"])
def test_synth_refuses_a_credential_option(option: str) -> None:
    assert "names a credential source" in refused("synth", option, "x")


def test_synth_dir_must_exist(tmp_path: Path) -> None:
    assert "not a directory" in refused("synth", "--dir", str(tmp_path / "missing"))


FAKE = """#!/usr/bin/env python3
import json, os, subprocess, sys
name = os.path.basename(sys.argv[0])
with open(os.path.join(os.environ["RECORD_DIR"], name + ".json"), "w") as out:
    json.dump({"argv": sys.argv[1:], "env": dict(os.environ), "cwd": os.getcwd()}, out)
if name == "cdk":
    # The CDK app asking AWS who it is, as a lookup would: it reaches the fake aws CLI below.
    subprocess.run(["aws", "sts", "get-caller-identity"], check=False)
"""


def test_synth_runs_cdk_and_cannot_reach_aws(tmp_path: Path) -> None:
    """A fake cdk and a fake aws on PATH record the environment they were given."""
    import json
    import os
    import subprocess
    import sys

    bin_dir, record, app = tmp_path / "bin", tmp_path / "record", tmp_path / "infra"
    for directory in (bin_dir, record, app):
        directory.mkdir()
    for name in ("cdk", "aws"):
        fake = bin_dir / name
        fake.write_text(FAKE, encoding="utf-8")
        fake.chmod(0o755)
    env = {**ENV, **AMBIENT, "RECORD_DIR": str(record),
           "PATH": os.pathsep.join([str(bin_dir), os.path.dirname(sys.executable),
                                    "/usr/bin", "/bin"]),
           "HOME": str(tmp_path)}
    result = subprocess.run([sys.executable, str(WRAPPER), "synth", "--dir", str(app), "--quiet"],
                            env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    cdk = json.loads((record / "cdk.json").read_text(encoding="utf-8"))
    aws = json.loads((record / "aws.json").read_text(encoding="utf-8"))
    assert cdk["argv"] == ["synth", "--quiet"]
    assert os.path.realpath(cdk["cwd"]) == os.path.realpath(app)
    for seen in (cdk["env"], aws["env"]):
        assert_no_credential_source(seen)
    assert "--profile" not in aws["argv"]
