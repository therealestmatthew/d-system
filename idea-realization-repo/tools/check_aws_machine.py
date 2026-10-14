#!/usr/bin/env python3
"""Check the machine rule: a machine that runs agents holds no default or ambient AWS credentials.

The two sandbox IAM roles are the boundary only if they are the only credentials an agent can
reach. A command that slips past the PreToolUse hook (tools/hooks/aws_guard.py) uses whatever the
AWS SDKs find by default — the `default` profile, `AWS_` variables, an instance or container role —
so on a machine that runs agents there must be none of those, only the two named sandbox profiles
(`aws/README.md`).

    uv run python tools/check_aws_machine.py           # files, environment, instance metadata
    uv run python tools/check_aws_machine.py --probe   # also ask AWS who the default chain is

Each finding is printed with what to remove. `tools/aws-sandbox` runs the file and environment
checks on every call and prints the findings as warnings.

Exit codes: 0 when the machine follows the rule; 1 when anything ambient was found.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Variables through which the AWS SDKs and CLI pick up credentials or a profile with no --profile.
AMBIENT_VARIABLES = (
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_SECURITY_TOKEN",
    "AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_WEB_IDENTITY_TOKEN_FILE", "AWS_ROLE_ARN",
    "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI", "AWS_CONTAINER_CREDENTIALS_FULL_URI",
    "AWS_CONTAINER_AUTHORIZATION_TOKEN",
)
DEFAULT_SECTION = re.compile(r"^\s*\[\s*(profile\s+)?default\s*\]\s*$", re.MULTILINE)
IMDS = "http://169.254.169.254/latest/api/token"


def aws_files(env: dict[str, str]) -> list[Path]:
    home = Path(env.get("HOME", str(Path.home())))
    return [Path(env.get("AWS_SHARED_CREDENTIALS_FILE", home / ".aws" / "credentials")),
            Path(env.get("AWS_CONFIG_FILE", home / ".aws" / "config"))]


def static_findings(env: dict[str, str]) -> list[str]:
    """Ambient credentials visible without a network call."""
    findings = [f"{name} is set in the environment; unset it (profiles come only from "
                "tools/aws-sandbox)" for name in AMBIENT_VARIABLES if env.get(name)]
    for path in aws_files(env):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if DEFAULT_SECTION.search(text):
            findings.append(f"{path} has a default profile; rename or remove it, so that only "
                            "the two named sandbox profiles exist")
    return findings


def instance_metadata_reachable(timeout: float = 0.5) -> bool:
    request = urllib.request.Request(IMDS, method="PUT",
                                     headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"})
    try:
        with urllib.request.urlopen(request, timeout=timeout):
            return True
    except urllib.error.HTTPError:
        return True  # something answered at the metadata address
    except (urllib.error.URLError, OSError):
        return False


def default_chain_identity(env: dict[str, str]) -> str | None:
    """Who the default credential chain resolves to, or None when it resolves to nobody."""
    if not shutil.which("aws"):
        return None
    clean = {k: v for k, v in env.items() if not k.startswith("AWS_")}
    result = subprocess.run(["aws", "sts", "get-caller-identity", "--output", "text"],
                            env=clean, capture_output=True, text=True, check=False, timeout=30)
    return result.stdout.strip() if result.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--probe", action="store_true",
                        help="also call sts get-caller-identity with no profile")
    args = parser.parse_args(argv)
    env = dict(os.environ)
    findings = static_findings(env)
    if instance_metadata_reachable():
        findings.append("the instance metadata service answers at 169.254.169.254; an instance "
                        "role may supply credentials — run agents on a machine without one, or "
                        "disable metadata access for this machine")
    if args.probe:
        identity = default_chain_identity(env)
        if identity:
            findings.append(f"the default credential chain resolves to: {identity}")
    if findings:
        print("check_aws_machine: ambient AWS credentials found")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("check_aws_machine: OK (no default or ambient AWS credentials found)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
