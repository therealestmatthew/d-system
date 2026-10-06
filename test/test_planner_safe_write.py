"""F03 (reopened): the planner's safe-write rule must survive a draft containing `\"\"\"`.

The documented command shape in `agent-workflows/idea-planner-agent.md` (and its generated
`.claude/agents/idea-planner.md`) must pass the draft's file path to Python and have Python read
the file itself, never substitute the draft's bytes into a Python string literal via `$(cat
<path>)` — a draft containing `\"\"\"` would end a triple-quoted literal early and raise a
SyntaxError under that shape, which is exactly what the round-2 review reproduced against the
pre-fix command.

This test extracts the exact command from the generated agent file (not a hand-written
equivalent) and runs it, via the shell, against a real temporary draft containing `\"\"\"`, so a
regression back to string-literal interpolation fails this test the same way it failed review.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_FILE = ROOT / ".claude" / "agents" / "idea-planner.md"

_FENCE_RE = re.compile(r"```bash\n(.*?)\n```", re.DOTALL)
_PLACEHOLDER = "docs/00-working/promoted/<reserved-code>-<slug>.md"


def _extract_safe_write_command() -> str:
    """The last `bash` fenced block in the generated agent file — the safe-write example."""
    text = AGENT_FILE.read_text()
    blocks = _FENCE_RE.findall(text)
    assert blocks, "no fenced bash block found in the generated planner agent file"
    command = blocks[-1]
    assert "sys.argv[1]" in command, (
        "expected the safe-write example (reads sys.argv[1]); found something else - "
        f"got:\n{command}"
    )
    assert _PLACEHOLDER in command, "expected the draft-path placeholder in the example command"
    return command


def test_documented_command_reads_path_not_string_literal() -> None:
    """The example never substitutes `$(cat ...)` into Python source, only passes a path."""
    command = _extract_safe_write_command()
    assert "$(cat" not in command
    assert "open(sys.argv[1])" in command


def test_documented_command_handles_a_draft_containing_triple_quotes(tmp_path: Path) -> None:
    """Run the literal extracted command against a draft containing `\"\"\"` and confirm it
    does not raise a SyntaxError - the exact failure the round-2 review reproduced against the
    pre-fix `$(cat <path>)`-into-a-triple-quoted-literal shape.
    """
    draft = tmp_path / "fixture-draft.md"
    draft.write_text(
        '# Fixture draft\n\n## Context and scope\n\nContains a literal """ sequence '
        "that would end a Python triple-quoted string early if inlined as source.\n"
        "## Decisions\n## Implementation phases\n## Acceptance and verification\n"
        "## Out of scope\n## Open questions\n"
    )

    command = _extract_safe_write_command()
    # The documented `depends_on=[...], documents={...}` is prose shorthand for "decide the real
    # pairing inputs" (F01); substitute concrete fixture values, and the draft's real path, to
    # make the example runnable - nothing about the safe-write shape itself changes. The extracted
    # block is already a complete, runnable shell command (`uv run python -c "..." <path>`).
    command = command.replace("depends_on=[...], documents={...}", "depends_on=[], documents={}")
    command = command.replace(_PLACEHOLDER, str(draft))

    result = subprocess.run(
        ["bash", "-c", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert "SyntaxError" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "conformant" in result.stdout.lower()
