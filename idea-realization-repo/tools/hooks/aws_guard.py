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
  agents, and the main session, use `read`, `whoami` and `synth`; a person who wants to deploy
  dispatches `aws-deploy`.

`tools/aws-sandbox synth` is allowed to every caller: it runs `cdk synth` with every AWS credential
source removed (no profile, no AWS_ variables, no config or credentials file, no instance
metadata), so it cannot reach AWS.

It inspects each command of a compound command line (`&&`, `||`, `;`, `|`, `&`, new lines), the
command each one runs after environment assignments, `env`, `sudo` and package runners, the code
inside `bash -c`, `eval`, `$(...)` and backticks, the scripts a command runs (shell scripts are
checked as commands; other scripts for AWS SDKs and AWS CLI calls), container runs of AWS images
or with AWS variables, `go run` sources, `java -jar` archives, and `npm`/`pnpm`/`yarn`/`bun run`
scripts. A command that writes a file and then runs it is refused when the command names an AWS
SDK or tool.

It is best effort, and it matches text. The boundary is the IAM roles behind the two sandbox
profiles together with the machine rule — a machine that runs agents holds no default or ambient
AWS credentials (`aws/README.md`) — so a command that slips past this hook finds no credentials
but the two sandbox profiles. The settings rules are a second layer.

Exit codes: 0 to let the command run; 2 to refuse it.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
import zipfile
from pathlib import Path

WRAPPER = "tools/aws-sandbox"
DEPLOY_AGENT = "aws-deploy"
DEPLOY_MODES = {"write", "exec"}  # every other mode (read, whoami, synth) is open to every caller

AWS_TOOLS = {"aws", "awscurl", "cdk", "aws-cdk", "cdktf", "sam", "terraform", "tofu", "pulumi",
             "aws-vault", "copilot", "eb", "sst", "serverless", "sls", "amplify", "ampx",
             "@aws-amplify/backend-cli", "chalice", "zappa"}
SDK = re.compile(r"(?<![\w-])(boto3|botocore|aioboto3|aiobotocore|awscli|aws_cdk|aws-cdk-lib|"
                 r"@aws-sdk|aws-sdk|@aws-cdk|cdktf|aws_lambda_powertools)(?![\w-])")
AWS_FILES = re.compile(r"(~|\$HOME|\$\{HOME\}|/home/[^/\s]+|/root|/Users/[^/\s]+)/\.aws(/|\b)")
AWS_VARIABLE = re.compile(r"^(AWS_[A-Z_]*|BOTO_[A-Z_]*)=")
# The AWS CLI called from code in another language: subprocess(["aws", ...]), exec("aws s3 ...").
AWS_CLI_CALL = re.compile(r"""["'`]aws["'`]\s*[,)\]]|["'`]aws\s+[a-z0-9-]+""")
# An AWS SDK or AWS tool named anywhere in a command line, for the write-then-run check.
AWS_NAMED = re.compile(r"(?<![\w./-])(aws|awscurl|cdk|aws-cdk|ampx|sam|terraform|pulumi|cdktf)"
                       r"(?![\w.-])|" + SDK.pattern)
SUBSTITUTION = re.compile(r"`([^`]*)`|\$\(([^()]*)\)|[<>]\(([^()]*)\)")
CONTAINER_TOOLS = {"docker", "podman", "nerdctl", "finch"}
AWS_IMAGE = re.compile(r"(aws-cli|amazon/|public\.ecr\.aws/aws|aws-sam|aws-cdk|awscli)")
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
    if AWS_CLI_CALL.search(code):
        raise Refusal(f"{where} calls the AWS CLI; every AWS command goes through `{WRAPPER}`")


def resolve(path_text: str, cwd: Path) -> Path:
    path = Path(path_text).expanduser()
    return path if path.is_absolute() else cwd / path


def read_text(path_text: str, cwd: Path) -> str | None:
    path = resolve(path_text, cwd)
    if not path.is_file():
        return None
    try:
        return path.read_bytes()[:SCRIPT_LIMIT].decode("utf-8", errors="ignore")
    except OSError:
        return None


def check_script(path_text: str, cwd: Path, agent: str | None, depth: int,
                 as_shell: bool = False) -> None:
    """A script a command runs: SDK use and AWS CLI calls in any language, and every command in
    a shell script."""
    text = read_text(path_text, cwd)
    if text is None:
        return
    check_code(text, f"the script {path_text}")
    first = text.split("\n", 1)[0]
    shell = as_shell or path_text.endswith((".sh", ".bash", ".zsh")) or (
        first.startswith("#!") and any(sh in first for sh in SHELLS))
    if shell and depth < 4:
        check_command(text, agent, cwd, depth + 1)


def check_container(rest: list[str]) -> None:
    if not rest or rest[0] not in {"run", "create", "exec", "start"}:
        return
    for i, token in enumerate(rest):
        following = rest[i + 1] if i + 1 < len(rest) else ""
        if AWS_IMAGE.search(token):
            raise Refusal(f"runs the AWS image {token}; every AWS command goes through "
                          f"`{WRAPPER}`")
        variable = following if token in {"-e", "--env"} else (
            token.split("=", 1)[1] if token.startswith("--env=") else
            token[2:] if token.startswith("-e") and len(token) > 2 else "")
        if variable and AWS_VARIABLE.match(variable + ("" if "=" in variable else "=")):
            raise Refusal(f"passes {variable.split('=')[0]} into a container; AWS credentials "
                          "come only from tools/aws-sandbox")


def check_go(rest: list[str], cwd: Path) -> None:
    if not rest or rest[0] != "run":
        return
    for token in rest[1:]:
        if token.startswith("-"):
            continue
        path = resolve(token, cwd)
        files = sorted(path.glob("*.go"))[:200] if path.is_dir() else [path]
        for file in files:
            text = read_text(str(file), cwd) or ""
            if "github.com/aws/aws-sdk-go" in text:
                raise Refusal(f"`go run` of {token} uses the AWS SDK for Go; it runs only as "
                              f"`{WRAPPER} exec ...` from the aws-deploy agent")


def check_jar(rest: list[str], cwd: Path) -> None:
    for i, token in enumerate(rest[:-1]):
        if token == "-jar":
            path = resolve(rest[i + 1], cwd)
            if not path.is_file():
                return
            try:
                with zipfile.ZipFile(path) as archive:
                    names = archive.namelist()
            except (OSError, zipfile.BadZipFile):
                return
            if any(n.startswith(("software/amazon/awssdk/", "com/amazonaws/")) for n in names):
                raise Refusal(f"{rest[i + 1]} contains the AWS SDK for Java; it runs only as "
                              f"`{WRAPPER} exec ...` from the aws-deploy agent")
            return


def check_package_script(name: str, rest: list[str], agent: str | None, cwd: Path,
                         depth: int) -> None:
    """`npm run <script>`, `npm start` and the like: check the script's command line."""
    if not rest:
        return
    script = rest[1] if rest[0] in {"run", "run-script"} and len(rest) > 1 else (
        rest[0] if rest[0] in {"start", "test"} or name in {"yarn", "bun"} else "")
    manifest = read_text("package.json", cwd)
    if not script or manifest is None:
        return
    try:
        scripts = json.loads(manifest).get("scripts") or {}
    except ValueError:
        return
    command = scripts.get(script)
    if isinstance(command, str) and depth < 4:
        check_command(command, agent, cwd, depth + 1)


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
    # npx aws-cdk@2, npx @aws-amplify/backend-cli@1: the package name without its version
    package = "@" + word[1:].split("@", 1)[0] if word.startswith("@") else word.split("@", 1)[0]

    if name in {"export", "declare", "typeset", "readonly", "unset", "set"}:
        for token in rest:
            if AWS_VARIABLE.match(token) or re.fullmatch(r"(AWS|BOTO)_[A-Z_]*", token):
                raise Refusal(f"sets {token.split('=')[0]}; AWS credentials and profiles come "
                              "only from tools/aws-sandbox")
        return

    if word.endswith(WRAPPER) or name == "aws-sandbox":
        mode = rest[0] if rest else ""
        if mode in DEPLOY_MODES and agent != DEPLOY_AGENT:
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
            check_script(rest[0], cwd, agent, depth, as_shell=True)
        return
    if INTERPRETERS.match(name):
        for i, token in enumerate(rest):
            if token in {"-c", "-e", "--eval", "-p", "--print"} and i + 1 < len(rest):
                check_code(rest[i + 1], f"inline {name} code")
                return
            if token == "-m" and i + 1 < len(rest):
                check_code(rest[i + 1], f"the module {rest[i + 1]}")
                return
            if token == "-jar":
                check_jar(rest, cwd)
                return
            if not token.startswith("-"):
                check_script(token, cwd, agent, depth)
                return
        return
    if name in {"java"}:
        check_jar(rest, cwd)
        return
    if name in CONTAINER_TOOLS:
        check_container(rest)
        return
    if name == "go":
        check_go(rest, cwd)
        return
    if name in {"npm", "pnpm", "yarn", "bun"}:
        check_package_script(name, rest, agent, cwd, depth)
        return
    if "/" in word:
        check_script(word, cwd, agent, depth)  # ./deploy.sh, scripts/run, /tmp/x


def written_files(segments: list[list[str]]) -> list[tuple[int, str]]:
    """(segment index, path) for each file a segment writes with `>`, `>>` or `tee`."""
    written: list[tuple[int, str]] = []
    for index, tokens in enumerate(segments):
        for i, token in enumerate(tokens):
            target = ""
            if token in {">", ">>", "1>", "1>>", ">|"} and i + 1 < len(tokens):
                target = tokens[i + 1]
            elif ">" in token and not token.startswith(("-", "2>")):
                target = token.rsplit(">", 1)[1]
            if target:
                written.append((index, target))
        if tokens and tokens[0].rsplit("/", 1)[-1] == "tee":
            written += [(index, t) for t in tokens[1:] if not t.startswith("-")]
    return written


def executed_files(tokens: list[str]) -> list[str]:
    """The paths a segment may run: its command word, and the first argument of a shell or an
    interpreter."""
    tokens = [t for t in tokens if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t)]
    if not tokens:
        return []
    name = tokens[0].rsplit("/", 1)[-1]
    paths = [tokens[0]]
    if name in SHELLS or name == "source" or name == "." or INTERPRETERS.match(name):
        paths += [t for t in tokens[1:] if not t.startswith("-")][:1]
    return paths


def check_write_then_run(command: str, segments: list[list[str]]) -> None:
    written = written_files(segments)
    if not written:
        return
    for index, path in written:
        target = Path(path).name
        for later in segments[index + 1:]:
            if any(Path(p).name == target and p.endswith(path.lstrip("./"))
                   for p in executed_files(later)):
                match = AWS_NAMED.search(command)
                if match:
                    raise Refusal(f"writes {path} and runs it in one command, and the command "
                                  f"names {match.group(0)}; run AWS code only through "
                                  f"`{WRAPPER}`")


def check_command(command: str, agent: str | None, cwd: Path, depth: int = 0) -> None:
    if depth < 4:
        for match in SUBSTITUTION.finditer(command):
            inner = next(group for group in match.groups() if group is not None)
            check_command(inner, agent, cwd, depth + 1)
    segments = tokenize(command)
    check_write_then_run(command, segments)
    for segment in segments:
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
