#!/usr/bin/env python3
"""PreToolUse hook: keep every AWS action inside tools/aws-sandbox, and writes inside aws-deploy.

Claude Code runs this before every Bash command, in the main session and in every subagent
(`.claude/settings.json`, `hooks.PreToolUse`). It reads the hook's JSON on stdin and exits 2, with
the reason on stderr, to refuse the command. It refuses:

- the AWS CLI, and AWS deployment tools (CDK, SAM, Terraform, Pulumi and the like), run anywhere
  but through `tools/aws-sandbox`;
- code that loads an AWS SDK (boto3, botocore, the JavaScript SDK, the CDK libraries), whether
  inline (`python -c`, `node -e`) or in a script file passed to an interpreter, unless it runs
  through `tools/aws-sandbox exec`, which gives it the deploy profile;
- reading or changing `~/.aws/`, and setting AWS credential or profile variables;
- `tools/aws-sandbox write` and `exec` from any caller but the `aws-deploy` agent. Read-only
  agents, and the main session, use `read` and `whoami`; a person who wants to deploy dispatches
  `aws-deploy`.

It inspects each command of a compound command line (`&&`, `||`, `;`, `|`, `&`, new lines), the
command each one runs after environment assignments, `env`, `sudo` and package runners, and the
code inside `bash -c` and `eval`. It matches text, so it is a guardrail: the boundary is the IAM
roles behind the two sandbox profiles (`aws/README.md`). The settings rules are a second layer.

Exit codes: 0 to let the command run; 2 to refuse it.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

WRAPPER = "tools/aws-sandbox"
DEPLOY_AGENT = "aws-deploy"

AWS_TOOLS = {"aws", "cdk", "aws-cdk", "cdktf", "sam", "terraform", "tofu", "pulumi", "aws-vault", "copilot",
             "eb", "sst", "serverless", "sls", "amplify", "chalice", "zappa"}
SDK = re.compile(r"(?<![\w-])(boto3|botocore|aioboto3|aiobotocore|awscli|aws_cdk|aws-cdk-lib|"
                 r"@aws-sdk|aws-sdk|@aws-cdk|cdktf|aws_lambda_powertools)(?![\w-])")
AWS_FILES = re.compile(r"(~|\$HOME|\$\{HOME\}|/home/[^/\s]+|/root|/Users/[^/\s]+)/\.aws(/|\b)")
AWS_VARIABLE = re.compile(r"^(AWS_[A-Z_]*|BOTO_[A-Z_]*)=")
INTERPRETERS = re.compile(r"^(python[0-9.]*|node|nodejs|deno|bun|ruby|perl|ts-node|tsx)$")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish"}
PREFIXES = {"sudo", "nohup", "time", "command", "builtin", "exec", "nice", "stdbuf", "timeout",
            "xargs"}
RUNNERS = {"npx": 1, "bunx": 1, "uvx": 1, "pnpx": 1}
TWO_WORD_RUNNERS = {("uv", "run"), ("pipx", "run"), ("poetry", "run"), ("pnpm", "dlx"),
                    ("yarn", "dlx"), ("npm", "exec"), ("pnpm", "exec"), ("hatch", "run"),
                    ("pdm", "run")}
SEPARATORS = {"&&", "||", ";", "|", "&", "|&", ";;", "(", ")"}
SCRIPT_LIMIT = 1_000_000


class Refusal(Exception):
    """The command is refused; the message says why."""


def tokenize(command: str) -> list[list[str]]:
    """The command line as segments of tokens, split at shell control operators and new lines."""
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        tokens = list(lexer)
    except ValueError:
        tokens = command.replace("\n", " ; ").split()
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in SEPARATORS or set(token) <= set(";&|()"):
            segments.append([])
        else:
            segments[-1].append(token)
    return [segment for segment in segments if segment]


def strip_prefixes(tokens: list[str]) -> list[str]:
    """The tokens from the command actually run: past assignments, env, sudo and runners."""
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if AWS_VARIABLE.match(token):
            raise Refusal(f"sets {token.split('=')[0]}; AWS credentials and profiles come only "
                          "from tools/aws-sandbox")
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", token):
            i += 1
        elif token == "env":
            i += 1
            while i < len(tokens) and tokens[i].startswith("-"):
                i += 1
        elif token in PREFIXES:
            i += 1
            while i < len(tokens) and tokens[i].startswith("-"):
                i += 1
            if token == "timeout" and i < len(tokens):
                i += 1  # the duration
        elif token in RUNNERS:
            i += 1
            while i < len(tokens) and tokens[i].startswith("-"):
                i += 1
        elif i + 1 < len(tokens) and (token, tokens[i + 1]) in TWO_WORD_RUNNERS:
            i += 2
            while i < len(tokens) and tokens[i].startswith("-"):
                i += 1
        else:
            break
    return tokens[i:]


def check_code(code: str, where: str) -> None:
    match = SDK.search(code)
    if match:
        raise Refusal(f"{where} uses {match.group(1)}; AWS SDK code runs only as "
                      f"`{WRAPPER} exec ...` from the aws-deploy agent")


def check_script(path_text: str, cwd: Path) -> None:
    path = Path(path_text).expanduser()
    path = path if path.is_absolute() else cwd / path
    if path.is_file():
        try:
            check_code(path.read_bytes()[:SCRIPT_LIMIT].decode("utf-8", errors="ignore"),
                       f"the script {path_text}")
        except OSError:
            pass


def check_segment(tokens: list[str], agent: str | None, cwd: Path, depth: int) -> None:
    for token in tokens:
        if AWS_FILES.search(token) or token.startswith(".aws/") or token == ".aws":
            raise Refusal("touches the AWS configuration directory; agents never read or "
                          "change ~/.aws")
    tokens = strip_prefixes(tokens)
    if not tokens:
        return
    word, rest = tokens[0], tokens[1:]
    name = word.rsplit("/", 1)[-1]
    package = word if word.startswith("@") else word.split("@", 1)[0]  # npx aws-cdk@2

    if name in {"export", "declare", "typeset", "readonly", "unset", "set"}:
        for token in rest:
            if AWS_VARIABLE.match(token) or re.fullmatch(r"(AWS|BOTO)_[A-Z_]*", token):
                raise Refusal(f"sets {token.split('=')[0]}; AWS credentials and profiles come "
                              "only from tools/aws-sandbox")
        return

    if word.endswith(WRAPPER) or name == "aws-sandbox":
        mode = rest[0] if rest else ""
        if mode in {"write", "exec"} and agent != DEPLOY_AGENT:
            caller = f"the {agent} agent" if agent else "the main session"
            raise Refusal(f"`aws-sandbox {mode}` is for the aws-deploy agent only, not {caller}; "
                          "use `read`, or dispatch aws-deploy")
        return
    if name in AWS_TOOLS or package in AWS_TOOLS or SDK.fullmatch(package.split("/", 1)[0]):
        raise Refusal(f"runs {word} directly; every AWS command goes through `{WRAPPER}`")
    if name in SHELLS or name == "eval":
        code = " ".join(rest) if name == "eval" else next(
            (rest[i + 1] for i, t in enumerate(rest[:-1]) if t.startswith("-") and "c" in t),
            "")
        if code and depth < 4:
            check_command(code, agent, cwd, depth + 1)
        elif rest and name in SHELLS and not rest[0].startswith("-"):
            check_script(rest[0], cwd)
        return
    if INTERPRETERS.match(name):
        for i, token in enumerate(rest):
            if token in {"-c", "-e", "--eval", "-p", "--print"} and i + 1 < len(rest):
                check_code(rest[i + 1], f"inline {name} code")
                return
            if token == "-m" and i + 1 < len(rest):
                check_code(rest[i + 1], f"the module {rest[i + 1]}")
                return
            if not token.startswith("-"):
                check_script(token, cwd)
                return


def check_command(command: str, agent: str | None, cwd: Path, depth: int = 0) -> None:
    for segment in tokenize(command):
        check_segment(segment, agent, cwd, depth)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (ValueError, OSError):
        print("aws_guard: could not read the hook input; refusing", file=sys.stderr)
        return 2
    if event.get("tool_name") != "Bash":
        return 0
    command = str((event.get("tool_input") or {}).get("command", ""))
    agent = event.get("agent_type") or None
    cwd = Path(event.get("cwd") or ".")
    try:
        check_command(command, agent, cwd)
    except Refusal as refusal:
        print(f"aws_guard: refused: {refusal}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
