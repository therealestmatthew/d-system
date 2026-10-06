"""The planner's safe-write rule must survive both hazardous draft content and a hazardous path.

The documented command shape in `agent-workflows/idea-planner-agent.md` (and its generated
`.claude/agents/idea-planner.md`) must never let the draft's path or bytes pass through shell
parsing or appear as Python source text:

- round 2: substituting the draft's bytes into a Python string literal via `$(cat <path>)` broke
  on a draft containing `\"\"\"` (ends a triple-quoted literal early).
- round 3: an unquoted, then double-quoted, trailing path argument broke on a path containing a
  space, an apostrophe, a double quote, a `$`-prefixed token or a backtick - double quotes still
  let the shell expand `$...`/backticks inside them, and break outright on an embedded `"`.
- round 4 (current): the fix passes the path on stdin through a heredoc with a quoted delimiter
  (`<<'EOF'`), which expands nothing, and has Python read it from `sys.stdin` - no path text and
  no draft bytes ever appear on the command line or inside the Python source.

Every test here extracts the exact command from the generated agent file (not a hand-written
equivalent) and runs it via the shell, so a regression back to any earlier shape fails the same
way it failed review.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_FILE = ROOT / ".claude" / "agents" / "idea-planner.md"

_FENCE_RE = re.compile(r"```bash\n(.*?)\n```", re.DOTALL)
_PLACEHOLDER = "docs/00-working/promoted/<reserved-code>-<slug>.md"

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


def _extract_safe_write_command() -> str:
    """The last `bash` fenced block in the generated agent file — the safe-write example."""
    text = AGENT_FILE.read_text()
    blocks = _FENCE_RE.findall(text)
    assert blocks, "no fenced bash block found in the generated planner agent file"
    command = blocks[-1]
    assert "sys.stdin" in command, (
        "expected the safe-write example (reads the path from sys.stdin); found something else - "
        f"got:\n{command}"
    )
    assert _PLACEHOLDER in command, "expected the draft-path placeholder in the example command"
    return command


def _run_for_path(path: Path) -> subprocess.CompletedProcess[str]:
    """Fill in `path` on the heredoc's own line and substitute the real pairing inputs, then run."""
    command = _extract_safe_write_command()
    command = command.replace("depends_on=[...], documents={...}", "depends_on=[], documents={}")
    command = command.replace(_PLACEHOLDER, str(path))
    return subprocess.run(["bash", "-c", command], cwd=ROOT, capture_output=True, text=True)


def test_documented_command_reads_the_path_from_stdin_not_the_command_line_or_source() -> None:
    """Round 4: no path text and no `$(cat ...)` byte-substitution anywhere in the example."""
    command = _extract_safe_write_command()
    assert "$(cat" not in command
    assert "sys.argv" not in command
    assert "sys.stdin.read()" in command
    # The path appears exactly once: on its own line inside the quoted heredoc, nowhere else.
    assert command.count(_PLACEHOLDER) == 1
    assert "<<'EOF'" in command, "the heredoc delimiter must be quoted so nothing is expanded"


def test_documented_command_handles_a_draft_containing_triple_quotes(tmp_path: Path) -> None:
    """Round 2's regression case: a draft containing `\"\"\"` must not raise a SyntaxError."""
    draft = tmp_path / "fixture-draft.md"
    draft.write_text(_draft().replace("Fixture body.", 'Contains a literal """ sequence.'))

    result = _run_for_path(draft)

    assert "SyntaxError" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "conformant" in result.stdout.lower()


def test_documented_command_reads_the_exact_file_for_a_combined_hazardous_path(
    tmp_path: Path,
) -> None:
    """Round 3/4's regression case, combined: a path containing `"`, `$HOME`-style text, a
    backtick, an apostrophe and a space, under a quoted heredoc the shell never expands.

    Two distinct drafts are written at two distinct hazardous paths, each missing a *different*
    GOV-010 section. The command is run once per path, and each result must name that path's own
    missing section and only that one - proving the exact file named by that path was read, not a
    cached, wrong, or partially-expanded one.
    """
    hazard_a = tmp_path / 'it\'s "weird" $HOME `touch pwned` dir one'
    hazard_a.mkdir()
    draft_a = hazard_a / "draft one.md"
    draft_a.write_text(_draft(omit="Open questions"))

    hazard_b = tmp_path / 'another `$(rm -rf)` "dir" with spaces'
    hazard_b.mkdir()
    draft_b = hazard_b / "draft two.md"
    draft_b.write_text(_draft(omit="Decisions"))

    result_a = _run_for_path(draft_a)
    assert result_a.returncode == 0, result_a.stderr
    assert "missing=('Open questions" in result_a.stdout
    assert "missing=('Design" not in result_a.stdout

    result_b = _run_for_path(draft_b)
    assert result_b.returncode == 0, result_b.stderr
    assert "missing=('Design" in result_b.stdout
    assert "missing=('Open questions" not in result_b.stdout
