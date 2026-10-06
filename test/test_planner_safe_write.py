"""The planner's safe-write rule must never pass draft content or its path through the shell.

The documented command shape in `agent-workflows/idea-planner-agent.md` (and its generated
`.claude/agents/idea-planner.md`) has gone through several hazards:

- round 2: substituting the draft's bytes into a Python string literal via `$(cat <path>)` broke
  on a draft containing `\"\"\"`.
- round 3/4: an unquoted, then double-quoted, then heredoc-on-stdin path argument broke on a path
  containing a space, an apostrophe, a double quote, a `$`-prefixed token, a backtick, or an
  embedded newline whose own line matched the heredoc delimiter.
- round 6 (current, a reproduced REJECT): the heredoc delimiter, however long and fixed, is
  public - written directly in this file - so a payload containing that exact line still ended
  the heredoc early and let a trailing `touch ...` run as a real shell command, with Python's
  `re.fullmatch()` never even reached. The fix removes the heredoc, `Bash`, and all path/byte
  substitution entirely: `Write` puts the draft at its destination and the chosen path, alone, in
  a fixed scratch file (`_working/idea-planner/draft-path.txt`); the check command that follows
  is byte-identical on every dispatch - it names that fixed file as a literal string in its own
  source and never receives the path or the draft's bytes as shell input of any kind.

Every test here extracts the exact command from the generated agent file (not a hand-written
equivalent) and runs it via the shell against a temporary repository layout, so a regression back
to any earlier shape - or a real draft-path.txt in the real repository - never happens.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_FILE = ROOT / ".claude" / "agents" / "idea-planner.md"

_FENCE_RE = re.compile(r"```bash\n(.*?)\n```", re.DOTALL)
_SCRATCH_PATH = "_working/idea-planner/draft-path.txt"

_SECTIONS = (
    "## Context and scope\n\nFixture body.\n",
    "## Decisions\n",
    "## Implementation phases\n",
    "## Acceptance and verification\n",
    "## Out of scope\n",
    "## Open questions\n",
)


def _draft(omit: str | None = None) -> str:
    """A fixture draft, optionally missing one named GOV-010 section heading."""
    return "# Fixture draft\n\n" + "".join(s for s in _SECTIONS if omit is None or omit not in s)


def _extract_check_command() -> str:
    """The last `bash` fenced block in the generated agent file — the constant check command."""
    text = AGENT_FILE.read_text()
    blocks = _FENCE_RE.findall(text)
    assert blocks, "no fenced bash block found in the generated planner agent file"
    command = blocks[-1]
    assert _SCRATCH_PATH in command, "expected the fixed scratch-file path in the command"
    assert "re.fullmatch" in command
    return command


def _run(workdir: Path, scratch_content: str) -> subprocess.CompletedProcess[str]:
    """Write `scratch_content` to the fixed scratch file under `workdir` and run the constant
    check command there, unmodified except for the pairing-decision placeholder."""
    scratch = workdir / _SCRATCH_PATH
    scratch.parent.mkdir(parents=True, exist_ok=True)
    scratch.write_text(scratch_content)

    command = _extract_check_command()
    command = command.replace("depends_on=[...], documents={...}", "depends_on=[], documents={}")
    return subprocess.run(["bash", "-c", command], cwd=workdir, capture_output=True, text=True)


def _run_for_promoted_path(
    workdir: Path, relative_path: str, content: str
) -> subprocess.CompletedProcess[str]:
    """Write a real draft at `relative_path` under `workdir`, point the scratch file at it (with
    a trailing newline, matching what `Write` would produce), and run the check command."""
    full = workdir / relative_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content)
    return _run(workdir, relative_path + "\n")


def test_generated_command_has_no_heredoc_bash_substitution_or_path_placeholder() -> None:
    """Round 6: the fix removes the heredoc and all shell-level path/byte substitution."""
    command = _extract_check_command()
    assert "<<" not in command, "no heredoc of any kind"
    assert "$(cat" not in command
    assert "sys.argv" not in command
    assert "sys.stdin" not in command
    assert "<reserved-code>" not in command, "no path placeholder - the command is constant"
    assert f"open('{_SCRATCH_PATH}')" in command


def test_generated_agent_declares_write_in_its_tools() -> None:
    """Part 1: the planner's generated frontmatter now includes `Write`."""
    frontmatter = AGENT_FILE.read_text().split("---", 2)[1]
    tools_line = next(line for line in frontmatter.splitlines() if line.startswith("tools:"))
    tools = {t.strip() for t in tools_line.split(":", 1)[1].split(",")}
    assert "Write" in tools
    assert "Bash" in tools


def test_live_reject_payload_in_scratch_file_is_refused_and_marker_never_created(
    tmp_path: Path,
) -> None:
    """The round-6 reproduced REJECT: a scratch-file payload carrying the old heredoc delimiter
    line, an `EOF` line, and a `touch <marker>` line. Since there is no heredoc any more, this is
    just inert file content read by `open()` - the `touch` line can never run as a shell command,
    and the embedded newlines fail `re.fullmatch()` regardless."""
    marker = tmp_path / "PWNED_MARKER.txt"
    payload = (
        "docs/00-working/promoted/PLAN-909-fixture.md\n"
        "PLANNER_DRAFT_PATH_EOF_9f3b6a2d1e8c4caa\n"
        "EOF\n"
        f"touch {marker}\n"
    )
    result = _run(tmp_path, payload)
    assert result.returncode != 0
    assert "refusing" in result.stderr.lower()
    assert not marker.exists(), "nothing in the scratch file may ever execute as a shell command"


_HAZARDS = {
    "double_quote": 'docs/00-working/promoted/PLAN-910-it"s.md',
    "dollar_home": "docs/00-working/promoted/PLAN-911-$HOME.md",
    "command_sub": "docs/00-working/promoted/PLAN-912-$(id).md",
    "backtick": "docs/00-working/promoted/PLAN-913-`id`.md",
    "apostrophe": "docs/00-working/promoted/PLAN-914-it's.md",
    "space": "docs/00-working/promoted/PLAN-915-bad slug.md",
    "backslash": "docs/00-working/promoted/PLAN-916-bad\\slug.md",
    "trailing_space": "docs/00-working/promoted/PLAN-917-slug.md ",
    "leading_dash": "docs/00-working/promoted/PLAN-918--leading-dash.md",
    "unicode": "docs/00-working/promoted/PLAN-919-café.md",
    "tab": "docs/00-working/promoted/PLAN-920-bad\tslug.md",
}


def test_eleven_hazardous_paths_are_refused_cleanly(tmp_path: Path) -> None:
    """The earlier rounds' character hazards, now all exercised as pure path-file content: none
    of them matches `[a-z0-9-]+`'s slug restriction, and each is refused with a clear message and
    a nonzero exit - nothing is ever executed as a shell command, because the command never puts
    any of this text on a command line or in a heredoc."""
    marker = tmp_path / "hazard_marker.txt"
    for name, hazard_path in _HAZARDS.items():
        result = _run(tmp_path, hazard_path + "\n")
        assert result.returncode != 0, f"{name}: expected refusal, got {result.stdout!r}"
        assert "refusing" in result.stderr.lower(), f"{name}: expected a refusal message"
    assert not marker.exists()
    assert len(_HAZARDS) == 11


def test_legitimate_plan_path_reads_the_exact_file(tmp_path: Path) -> None:
    """A valid PLAN path passes and the exact drafted file is read."""
    result = _run_for_promoted_path(
        tmp_path, "docs/00-working/promoted/PLAN-921-fixture-track.md", _draft()
    )
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_legitimate_req_path_reads_the_exact_file(tmp_path: Path) -> None:
    """A valid REQ path passes too - both series ADR-019 actually covers."""
    result = _run_for_promoted_path(
        tmp_path, "docs/00-working/promoted/REQ-922-fixture-track.md", _draft()
    )
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_child_code_path_reads_the_exact_file(tmp_path: Path) -> None:
    """A child code such as PLAN-041.02 (the `.NN` sub-plan suffix `codes.py`'s `COUNTER`
    pattern allows) is accepted."""
    result = _run_for_promoted_path(
        tmp_path, "docs/00-working/promoted/PLAN-041.02-fixture-child.md", _draft()
    )
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_two_distinct_valid_paths_each_read_their_own_exact_file(tmp_path: Path) -> None:
    """Two distinct, valid promoted-draft paths, each missing a *different* GOV-010 section, each
    produce a result naming only that path's own missing section."""
    result_a = _run_for_promoted_path(
        tmp_path,
        "docs/00-working/promoted/PLAN-923-track-one.md",
        _draft(omit="Open questions"),
    )
    assert result_a.returncode == 0, result_a.stderr
    assert "missing=('Open questions" in result_a.stdout
    assert "missing=('Design" not in result_a.stdout

    result_b = _run_for_promoted_path(
        tmp_path,
        "docs/00-working/promoted/REQ-924-track-two.md",
        _draft(omit="Decisions"),
    )
    assert result_b.returncode == 0, result_b.stderr
    assert "missing=('Design" in result_b.stdout
    assert "missing=('Open questions" not in result_b.stdout


def test_a_draft_containing_triple_quotes_still_works(tmp_path: Path) -> None:
    """Round 2's regression case: `\"\"\"` inside the draft's body is fine - it is read with
    `open()`, never interpolated into Python source."""
    content = _draft().replace("Fixture body.", 'Contains a literal """ sequence.')
    result = _run_for_promoted_path(
        tmp_path, "docs/00-working/promoted/PLAN-925-triple-quote-fixture.md", content
    )
    assert "SyntaxError" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_non_plan_req_series_is_refused(tmp_path: Path) -> None:
    """Minor finding: the series is restricted to PLAN or REQ - ADR-019's own scope - so an ADR
    (or any other series) path is refused even though it otherwise fits the shape."""
    result = _run(tmp_path, "docs/00-working/promoted/ADR-019-x.md\n")
    assert result.returncode != 0
    assert "refusing" in result.stderr.lower()
