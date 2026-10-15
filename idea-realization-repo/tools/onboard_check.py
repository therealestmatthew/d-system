#!/usr/bin/env python3
"""Check a developer machine against the first-day checklist in ONBOARDING.md.

    uv run python tools/onboard_check.py

Prints one line per checklist item it can check on this machine: ``OK`` when the item is done,
``FIX`` with what to do when it is not. Then it lists the steps it cannot check without the
network, to be run by hand. The doctor (``doctor.py``) is local, so it is a checked line, not a
manual step.

It reads local files and runs ``git`` and, for the GitHub CLI, ``gh auth status``. That is its
only network call. It never prints the deny-list's contents, an AWS credential or the output of
``gh auth status``, and it never changes a file. The AWS check uses the file and environment
part of ``tools/check_aws_machine.py``; the instance-metadata probe and ``--probe`` need the
network, so they are listed as manual steps.

AWS lines wait for the owner. Until this machine names an AWS read or deploy profile, nobody
can have finished the AWS steps (the owner creates the roles first, ``aws/README.md``), so the AWS
CLI, profile and region lines print as ``NOTE`` (pending) and do not fail the check. Once either
profile is named, they are checked like every other line, and a real problem is a ``FIX``. The
machine rule (no default profile, no ``AWS_`` credentials) is checked either way: ambient
credentials are unsafe whether or not the sandbox roles exist yet.

Exit codes: 0 when every line is OK or a pending note; 1 when any line is FIX.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins" / "idea-realization" / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

import check_aws_machine  # noqa: E402
import doctor  # noqa: E402
import identity  # noqa: E402
import paths  # noqa: E402
import product  # noqa: E402
import project  # noqa: E402

HOOKS_PATH = "tools/git-hooks"
DENY_LIST = Path(".private") / "deny-list.txt"

#: Steps that need the network or a person, printed after the checks.
MANUAL = (
    "uv run python tools/check_aws_machine.py --probe   (must print OK)",
    "tools/aws-sandbox whoami                           (prints both profiles and the read role)",
)
DOCTOR = "uv run plugins/idea-realization/scripts/doctor.py"


@dataclass(frozen=True)
class Line:
    ok: bool
    item: str
    detail: str
    pending: bool = False  # waiting for the owner's AWS setup: shown, never a failure

    def __str__(self) -> str:
        label = "NOTE" if self.pending else "OK  " if self.ok else "FIX "
        return f"{label} {self.item}: {self.detail}"

    @property
    def failed(self) -> bool:
        return not self.ok and not self.pending


Which = Callable[[str], str | None]
Runner = Callable[[Sequence[str]], int]


def run_quietly(command: Sequence[str]) -> int:
    """Run a command, discard its output, and return its exit code (127 when it cannot start)."""
    try:
        return subprocess.run(list(command), capture_output=True, check=False,
                              timeout=30).returncode
    except (OSError, subprocess.TimeoutExpired):
        return 127


def git_config(root: Path, name: str) -> str:
    result = subprocess.run(["git", "-C", str(root), "config", name],
                            env=paths.git_env(), capture_output=True, text=True, check=False)
    return result.stdout.strip()


def check_tools(which: Which, run: Runner) -> list[Line]:
    lines = [Line(bool(which("uv")), "uv", "installed" if which("uv") else
                  "not on PATH; install uv (https://docs.astral.sh/uv/)"),
             Line(bool(which("claude")), "Claude Code", "installed" if which("claude") else
                  "the claude command is not on PATH; install Claude Code")]
    if not which("gh"):
        lines.append(Line(False, "gh", "the GitHub CLI is not on PATH; install it, then "
                                       "gh auth login to the team's organization"))
    elif run(["gh", "auth", "status"]) != 0:
        lines.append(Line(False, "gh", "installed but not authenticated; run gh auth login "
                                       "(session-close merges pull requests with gh)"))
    else:
        lines.append(Line(True, "gh", "installed and authenticated (gh auth status)"))
    return lines


def check_git(root: Path) -> list[Line]:
    email = Line(bool(git_config(root, "user.email")), "git user.email",
                 "set" if git_config(root, "user.email") else
                 "not set; git config user.email <your work email>")
    hooks = git_config(root, "core.hooksPath")
    hook_line = Line(hooks == HOOKS_PATH, "core.hooksPath",
                     HOOKS_PATH if hooks == HOOKS_PATH else
                     f"is {hooks or 'unset'}; git config core.hooksPath {HOOKS_PATH}")
    return [email, hook_line]


def check_handle(config: paths.Config, env: Mapping[str, str]) -> Line:
    try:
        return Line(True, "developer handle", identity.handle(config, env))
    except identity.IdentityError as error:
        reason = re.sub(r"'[^']*@[^']*'", "<your git email>", str(error))
        return Line(False, "developer handle",
                    f"{reason}; add yourself to the owners map in docs/systems.yaml with your "
                    "git email (ONBOARDING.md, first-day checklist)")


def deny_list_path(root: Path, env: Mapping[str, str]) -> Path:
    configured = env.get("PRIVATE_DENY_LIST")
    # The primary checkout's file, at the root's place in it, where paths.local_record finds
    # local.yaml: the deny-list is untracked, so a session worktree has no copy of its own.
    return Path(configured) if configured else paths.local_record(root).parent.parent / DENY_LIST


def check_deny_list(root: Path, env: Mapping[str, str]) -> Line:
    """Present and not empty. The file is never opened: only its size is read."""
    location = deny_list_path(root, env)
    if not location.is_file():
        return Line(False, "deny-list", f"{location} is missing; ask the owner for the team's "
                                        "deny-list and save it there")
    if location.stat().st_size == 0:
        return Line(False, "deny-list", f"{location} is empty; ask the owner for the team's list")
    return Line(True, "deny-list", f"{location} present")


def check_local_yaml(root: Path) -> tuple[Line, bool]:
    """The local.yaml line, and whether the file can be read at all."""
    location = paths.local_record(root)
    if not location.is_file():
        return Line(False, "local.yaml", f"{location} is missing; copy "
                    ".idea-realization/local.example.yaml there and fill it in"), False
    try:
        record = paths.read_yaml_record(location, "local.schema.json") or {}
    except paths.PathError as error:
        return Line(False, "local.yaml", str(error)), False
    unfilled = sorted(name for name, value in record.items()
                      if str(value).startswith(paths.PLACEHOLDER))
    if unfilled:
        return Line(False, "local.yaml", "still a placeholder: " + ", ".join(unfilled)), True
    return Line(True, "local.yaml", f"{location} valid"), True


def check_config(config: paths.Config) -> list[Line]:
    lines = [Line(False, "configuration", str(error)) for error in config.invalid()]
    try:
        staging = config.path("staging_dir")
    except paths.PathError as error:
        return lines + [Line(False, "scaffold", str(error))]
    lines.append(Line(staging.is_dir(), "scaffold",
                      "staging directory present" if staging.is_dir() else
                      f"{staging} is missing; uv run plugins/idea-realization/scripts/"
                      "scaffold.py --feature all"))
    return lines


def check_doctor(config: paths.Config) -> Line:
    """The doctor's verdict on the scaffolded files, without its origin line (the control
    repository line covers that)."""
    if not (config.root / doctor.RECORD).is_file():
        return Line(False, "doctor", f"no {doctor.RECORD.as_posix()}; run the scaffold first")
    try:
        results = doctor.diagnose(config.root, config)
    except (OSError, ValueError, KeyError) as error:
        return Line(False, "doctor", f"cannot read {doctor.RECORD.as_posix()}: {error}")
    bad = [f"{path} {state}" for state, path, _ in results if state not in doctor.OK_STATES]
    if bad:
        return Line(False, "doctor", f"{len(bad)} not as recorded ({', '.join(bad[:3])}"
                                     f"{', ...' if len(bad) > 3 else ''}); run {DOCTOR}")
    return Line(True, "doctor", f"{len(results)} recorded, none drifted")


def check_control(config: paths.Config) -> Line:
    """The control checkout's origin against ``control_remote`` (``project.py``)."""
    try:
        problem, note = project.control_origin(config)
    except ValueError as error:  # PathError and a refused record
        return Line(False, "control repository", str(error))
    if problem:
        return Line(False, "control repository", problem)
    if not note or "not compared" in note:
        return Line(False, "control repository", note or "control_remote is not set; set it in "
                    ".idea-realization/local.yaml")
    return Line(True, "control repository", note)


def check_product(config: paths.Config) -> Line:
    if config.product_root() is None:
        return Line(False, "product checkout", "product_root is not set; clone the product "
                    "repository and set product_root in .idea-realization/local.yaml")
    try:
        found = product.verify(config)
    except ValueError as error:  # ProductError and PathError
        return Line(False, "product checkout", f"product.py verify fails: {error}")
    return Line(True, "product checkout", f"{found.root} (product.py verify passes)")


def aws_profile_names(env: Mapping[str, str]) -> set[str]:
    """The profile names in the AWS config and credentials files. Reads section headers only."""
    names: set[str] = set()
    for location in check_aws_machine.aws_files(dict(env)):
        try:
            text = location.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in re.finditer(r"^\s*\[\s*(?:profile\s+)?([^\]\s]+)\s*\]", text, re.MULTILINE):
            names.add(match.group(1))
    return names


PENDING = ("pending: no AWS profile is configured on this machine yet, so the AWS steps wait for "
           "the owner's setup (aws/README.md); then ")


def check_aws(config: paths.Config, env: Mapping[str, str], which: Which = shutil.which,
              ) -> list[Line]:
    read = config.text("aws_read_profile")
    deploy = config.text("aws_deploy_profile")
    region = config.text("aws_region")
    known = aws_profile_names(env)
    lines = [Line(bool(which("aws")), "AWS CLI", "installed" if which("aws") else
                  "the aws command is not on PATH; install AWS CLI v2 (tools/aws-sandbox and "
                  "check_aws_machine.py --probe need it)")]
    for item, name in (("AWS read profile", read), ("AWS deploy profile", deploy)):
        if not name:
            lines.append(Line(False, item, "not set; set it in .idea-realization/local.yaml "
                                           "(aws/README.md, each developer)"))
        elif name == "default":
            lines.append(Line(False, item, "must not be the default profile"))
        elif name not in known:
            lines.append(Line(False, item, f"{name} is not in your AWS config files; add it "
                                           "(aws/README.md, each developer, step 1)"))
        else:
            lines.append(Line(True, item, name))
    if read and read == deploy:
        lines.append(Line(False, "AWS profiles", "the read and deploy profiles are the same; "
                                                 "use one profile per role"))
    lines.append(Line(bool(region), "AWS region", region or "not set; set aws_region in "
                      "local.yaml, or aws.region in project.yaml"))
    if not read and not deploy:
        lines = [line if line.ok else Line(False, line.item, PENDING + line.detail, pending=True)
                 for line in lines]
    findings = check_aws_machine.static_findings(dict(env))
    if findings:
        lines += [Line(False, "AWS machine rule", finding) for finding in findings]
    else:
        lines.append(Line(True, "AWS machine rule", "no default profile or AWS_ variables"))
    return lines


def run_checks(root: Path, env: Mapping[str, str], which: Which = shutil.which,
               run: Runner = run_quietly) -> list[Line]:
    lines = check_tools(which, run) + check_git(root)
    lines.append(check_deny_list(root, env))
    local_line, readable = check_local_yaml(root)
    lines.append(local_line)
    if not readable and paths.local_record(root).is_file():
        lines.append(Line(False, "remaining checks", "skipped until local.yaml is valid"))
        return lines
    try:
        config = paths.resolve({"root": str(root)}, env)
    except paths.PathError as error:
        return lines + [Line(False, "configuration", str(error))]
    lines.append(check_handle(config, env))
    lines += check_config(config)
    lines.append(check_doctor(config))
    lines.append(check_control(config))
    lines.append(check_product(config))
    lines += check_aws(config, env, which)
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--root", help="control repository root (default: git top level)")
    args = parser.parse_args(argv)
    env = dict(os.environ)
    root = paths.repository_root(args.root, env)
    lines = run_checks(root, env, shutil.which, run_quietly)
    for line in lines:
        print(line)
    print("\nRun by hand (they need the network or a person):")
    for step in MANUAL:
        print(f"  {step}")
    failed = sum(line.failed for line in lines)
    pending = sum(line.pending for line in lines)
    waiting = f" ({pending} pending the owner's AWS setup)" if pending else ""
    print(f"\n{failed} to fix{waiting}" if failed else f"\nAll checks OK{waiting}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
