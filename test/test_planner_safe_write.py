"""The planner's safe-write rule must survive hazardous draft content and a hazardous path.

The documented command shape in `agent-workflows/idea-planner-agent.md` (and its generated
`.claude/agents/idea-planner.md`) must never let the draft's path or bytes pass through shell
parsing or appear as Python source text, and must never open a path that is not genuinely a
promoted-draft path (`ADR-019`):

- round 2: substituting the draft's bytes into a Python string literal via `$(cat <path>)` broke
  on a draft containing `\"\"\"` (ends a triple-quoted literal early).
- round 3: an unquoted, then double-quoted, trailing path argument broke on a path containing a
  space, an apostrophe, a double quote, a `$`-prefixed token or a backtick.
- round 4: passing the path on stdin through a heredoc with the bare delimiter `<<'EOF'` broke on
  a path containing a newline whose own line read exactly `EOF` - the heredoc ended early and the
  remainder of the path ran as shell commands.
- round 5 (current): the delimiter is a long, fixed, quoted token no legitimate slug (restricted
  to `[a-z0-9-]+`) can collide with, and - before opening anything - the script refuses any path
  that does not `re.fullmatch()` the exact promoted-draft pattern (code plus slug), which also
  refuses any path carrying an embedded newline, an uppercase slug character, or a space.

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
_DELIMITER = "PLANNER_DRAFT_PATH_EOF_9f3b6a2d1e8c4caa"

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
    assert "re.fullmatch" in command, "expected the pattern-validation safe-write example"
    assert _PLACEHOLDER in command, "expected the draft-path placeholder in the example command"
    assert command.count(_DELIMITER) == 2, "expected the fixed delimiter token opening and closing"
    return command


def _run_with_payload(workdir: Path, payload: str) -> subprocess.CompletedProcess[str]:
    """Substitute `payload` for the path line and the real pairing inputs, then run in `workdir`."""
    command = _extract_safe_write_command()
    command = command.replace("depends_on=[...], documents={...}", "depends_on=[], documents={}")
    command = command.replace(_PLACEHOLDER, payload)
    return subprocess.run(["bash", "-c", command], cwd=workdir, capture_output=True, text=True)


def _run_for_promoted_path(
    workdir: Path, relative_path: str, content: str
) -> subprocess.CompletedProcess[str]:
    """Write `content` at `relative_path` under `workdir` and run the command against that exact
    repository-relative path (matching `re.fullmatch`'s pattern requires a path under
    `docs/00-working/promoted/`, which this helper actually creates under a throwaway `workdir`
    rather than the real repository tree)."""
    full = workdir / relative_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content)
    return _run_with_payload(workdir, relative_path)


def test_documented_command_uses_fixed_quoted_delimiter_and_fullmatch_before_opening() -> None:
    """Round 5: the delimiter is the fixed token, not the bare word `EOF`, and the script
    validates the path with `re.fullmatch()` before any `open()` call."""
    command = _extract_safe_write_command()
    assert "<<'EOF'" not in command, "the bare EOF delimiter must not be used"
    assert f"<<'{_DELIMITER}'" in command
    assert "$(cat" not in command
    assert "sys.argv" not in command
    assert command.index("re.fullmatch") < command.index("open(path)")
    assert "sys.exit(1)" in command


def test_valid_promoted_path_reads_the_exact_file(tmp_path: Path) -> None:
    """A path that fully matches the ADR-019 pattern is accepted and the exact file is read."""
    result = _run_for_promoted_path(
        tmp_path, "docs/00-working/promoted/PLAN-999-fixture-track.md", _draft()
    )
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_two_distinct_valid_paths_each_read_their_own_exact_file(tmp_path: Path) -> None:
    """Two distinct, valid promoted-draft paths, each missing a *different* GOV-010 section, each
    produce a result naming only that path's own missing section - the exact-file-read guarantee,
    now exercised under the pattern check rather than a hazardous raw path."""
    result_a = _run_for_promoted_path(
        tmp_path,
        "docs/00-working/promoted/PLAN-901-track-one.md",
        _draft(omit="Open questions"),
    )
    assert result_a.returncode == 0, result_a.stderr
    assert "missing=('Open questions" in result_a.stdout
    assert "missing=('Design" not in result_a.stdout

    result_b = _run_for_promoted_path(
        tmp_path,
        "docs/00-working/promoted/REQ-902-track-two.md",
        _draft(omit="Decisions"),
    )
    assert result_b.returncode == 0, result_b.stderr
    assert "missing=('Design" in result_b.stdout
    assert "missing=('Open questions" not in result_b.stdout


def test_a_draft_containing_triple_quotes_still_works_under_a_valid_path(tmp_path: Path) -> None:
    """Round 2's regression case, content hazard: `\"\"\"` inside the draft's body is fine once
    the path itself is valid - this is the "content hazard, pattern allows it" case."""
    content = _draft().replace("Fixture body.", 'Contains a literal """ sequence.')
    result = _run_for_promoted_path(
        tmp_path, "docs/00-working/promoted/PLAN-903-triple-quote-fixture.md", content
    )
    assert "SyntaxError" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_uppercase_letter_in_slug_is_refused(tmp_path: Path) -> None:
    """Part 3: a slug containing an uppercase letter does not match `[a-z0-9-]+` and is refused."""
    payload = "docs/00-working/promoted/PLAN-904-Bad-Slug.md"
    result = _run_with_payload(tmp_path, payload)
    assert result.returncode != 0
    assert "refusing" in result.stderr.lower()


def test_space_in_slug_is_refused(tmp_path: Path) -> None:
    """Part 3: a slug containing a space does not match `[a-z0-9-]+` and is refused."""
    payload = "docs/00-working/promoted/PLAN-905-bad slug.md"
    result = _run_with_payload(tmp_path, payload)
    assert result.returncode != 0
    assert "refusing" in result.stderr.lower()


def test_hazardous_path_characters_are_refused_cleanly(tmp_path: Path) -> None:
    """The earlier round-3/4 hazards (`"`, `$HOME`, a backtick, an apostrophe, a space) do not
    form a valid slug either, and are now refused cleanly by the pattern check rather than
    mis-parsed by the shell."""
    payload = 'docs/00-working/promoted/PLAN-906-it\'s "weird" $HOME `x` dir.md'
    result = _run_with_payload(tmp_path, payload)
    assert result.returncode != 0
    assert "refusing" in result.stderr.lower()


def test_embedded_eof_line_is_refused_and_nothing_else_runs(tmp_path: Path) -> None:
    """Round 4's regression case: a path containing a newline whose own line reads exactly the
    bare word `EOF` must not end the heredoc early. The new delimiter is not `EOF`, so this line
    is just more heredoc body; the resulting multi-line "path" fails `re.fullmatch()` (which does
    not allow an embedded newline) and the script exits nonzero - and, crucially, the `touch`
    line that would create a marker file is heredoc data, never a shell command, so the marker is
    never created."""
    marker = tmp_path / "marker_from_old_eof_escape.txt"
    payload = (
        "docs/00-working/promoted/PLAN-907-fixture.md\n"
        "EOF\n"
        f"touch {marker}\n"
        "docs/00-working/promoted/PLAN-907-fixture.md"
    )
    result = _run_with_payload(tmp_path, payload)
    assert result.returncode != 0
    assert not marker.exists(), "the embedded EOF line must never terminate the heredoc early"


def test_delimiter_cannot_be_produced_by_any_legitimate_slug_or_code() -> None:
    """The fixed delimiter is public (written into this very file), so a payload that already
    violates part 1's slug restriction (an adversarial or buggy caller, not this agent's own
    correct construction) could still contain a line matching it verbatim and, by plain shell
    heredoc syntax, terminate the heredoc early - a known, accepted limit of any fixed,
    non-randomized delimiter that this agent's own documented construction can never trigger.
    This test is the actual guarantee behind calling it "unguessable" from a legitimately built
    path: the token mixes uppercase letters and underscores that neither the slug pattern
    (`[a-z0-9-]+`) nor the code pattern (`[A-Z]+-[0-9]{3}(?:\\.[0-9]{2})?`) can ever produce, so
    no path this agent legitimately builds from a reserved code and a conforming slug can equal
    it.
    """
    assert not re.fullmatch(r"[a-z0-9-]+", _DELIMITER)
    assert not re.fullmatch(r"[A-Z]+-[0-9]{3}(?:\.[0-9]{2})?", _DELIMITER)
    assert "_" in _DELIMITER, "the delimiter should use a character no code or slug can produce"
