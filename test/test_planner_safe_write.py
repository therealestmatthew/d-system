"""The planner's safe-write rule must never pass draft content or its path through the shell, and
two concurrent dispatches must never be able to overwrite each other's staged path.

The documented command shape in `agent-workflows/idea-planner-agent.md` (and its generated
`.claude/agents/idea-planner.md`) has gone through several hazards:

- round 2: substituting the draft's bytes into a Python string literal via `$(cat <path>)` broke
  on a draft containing `\"\"\"`.
- round 3/4: an unquoted, then double-quoted, then heredoc-on-stdin path argument broke on a path
  containing a space, an apostrophe, a double quote, a `$`-prefixed token, a backtick, or an
  embedded newline whose own line matched the heredoc delimiter.
- round 6: the heredoc delimiter, however long and fixed, is public - written directly in this
  file - so a payload containing that exact line still ended the heredoc early and let a trailing
  `touch ...` run as a real shell command before `re.fullmatch()` ever ran. The fix moved the path
  off `Bash` entirely: `Write` wrote it to a fixed scratch file the constant check command read.
- round 7 (current, gating major): that fixed scratch file is shared, so two concurrent planner
  dispatches in one worktree could overwrite each other's path and have the check silently
  validate the wrong draft. The fix names the scratch file by the dispatch's own reserved code
  (`<code>.path`), and the constant check command now globs every staged `.path` file, validates
  each file's name against the code pattern and each file's content against the ADR-019 path
  pattern - requiring the embedded code to equal the file name - printing one result line per
  valid draft (naming its own path) and a `refusing ...` line per invalid one, and exiting nonzero
  if any staged file was refused.

Every test here extracts the exact command from the generated agent file (not a hand-written
equivalent) and runs it via the shell against a temporary repository layout, so a regression back
to any earlier shape - or a real file under the real repository's `_working/idea-planner/` -
never happens.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AGENT_FILE = ROOT / ".claude" / "agents" / "idea-planner.md"

_FENCE_RE = re.compile(r"```bash\n(.*?)\n```", re.DOTALL)
_SCRATCH_DIR = "_working/idea-planner"

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
    assert _SCRATCH_DIR in command, "expected the scratch directory in the command"
    assert "glob.glob" in command, "expected the command to glob every staged .path file"
    return command


def _write_path_file(workdir: Path, code: str, content: str) -> None:
    scratch = workdir / _SCRATCH_DIR / f"{code}.path"
    scratch.parent.mkdir(parents=True, exist_ok=True)
    scratch.write_text(content)


def _run(workdir: Path) -> subprocess.CompletedProcess[str]:
    command = _extract_check_command()
    command = command.replace("depends_on=[...], documents={...}", "depends_on=[], documents={}")
    return subprocess.run(["bash", "-c", command], cwd=workdir, capture_output=True, text=True)


def _stage_draft(workdir: Path, code: str, relative_path: str, content: str) -> None:
    """Write a real draft file at `relative_path` and its matching `<code>.path` scratch file."""
    full = workdir / relative_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content)
    _write_path_file(workdir, code, relative_path + "\n")


def test_generated_command_has_no_heredoc_bash_substitution_or_shared_fixed_name() -> None:
    """Round 6/7: no heredoc, no stdin/argv substitution, and no single shared scratch file name -
    the command globs every `*.path` file instead of naming one fixed file."""
    command = _extract_check_command()
    assert "<<" not in command, "no heredoc of any kind"
    assert "$(cat" not in command
    assert "sys.argv" not in command
    assert "sys.stdin" not in command
    assert "draft-path.txt" not in command, "the single shared scratch file must be gone"
    assert "glob.glob('_working/idea-planner/*.path')" in command


def test_generated_agent_declares_write_in_its_tools() -> None:
    """The planner's generated frontmatter includes `Write`."""
    frontmatter = AGENT_FILE.read_text().split("---", 2)[1]
    tools_line = next(line for line in frontmatter.splitlines() if line.startswith("tools:"))
    tools = {t.strip() for t in tools_line.split(":", 1)[1].split(",")}
    assert "Write" in tools
    assert "Bash" in tools


def test_two_concurrent_drafts_each_get_their_own_result_line(tmp_path: Path) -> None:
    """Round 7's actual fix: two distinct codes staged at once, each missing a *different* GOV-010
    section, each produce a result line naming only that draft's own path and its own missing
    section - proving one dispatch's check can never read or report on another's draft."""
    _stage_draft(
        tmp_path,
        "PLAN-930",
        "docs/00-working/promoted/PLAN-930-track-one.md",
        _draft(omit="Open questions"),
    )
    _stage_draft(
        tmp_path,
        "REQ-931",
        "docs/00-working/promoted/REQ-931-track-two.md",
        _draft(omit="Decisions"),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 2
    plan_line = next(line for line in lines if "PLAN-930" in line)
    req_line = next(line for line in lines if "REQ-931" in line)
    assert "missing=('Open questions" in plan_line
    assert "missing=('Design" not in plan_line
    assert "missing=('Design" in req_line
    assert "missing=('Open questions" not in req_line


def test_mismatched_code_between_file_name_and_content_is_refused(tmp_path: Path) -> None:
    """A `.path` file named `PLAN-932.path` whose content names a *different* code
    (`PLAN-933-...`) is refused - the file name is the only thing a concurrent dispatch cannot
    collide on, so content must be checked against it, not trusted alone."""
    draft = tmp_path / "docs/00-working/promoted/PLAN-933-track.md"
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(_draft())
    _write_path_file(tmp_path, "PLAN-932", "docs/00-working/promoted/PLAN-933-track.md\n")

    result = _run(tmp_path)

    assert result.returncode != 0
    assert "does not match" in result.stderr
    assert "PLAN-930" not in result.stdout


def test_path_file_name_outside_the_code_pattern_is_refused(tmp_path: Path) -> None:
    """A `.path` file whose stem is not a reserved-code shape at all is refused, not silently
    skipped."""
    _write_path_file(tmp_path, "not-a-code", "docs/00-working/promoted/PLAN-934-track.md\n")

    result = _run(tmp_path)

    assert result.returncode != 0
    assert "is not a reserved code" in result.stderr


def test_live_reject_payload_is_refused_and_marker_never_created(tmp_path: Path) -> None:
    """Round 6's reproduced REJECT, restaged under the new per-code file: the old heredoc
    delimiter line, an `EOF` line, and a `touch <marker>` line as file *content* never execute -
    there is no heredoc any more, so this is just inert text `open()` reads, and the embedded
    newlines fail the path pattern regardless."""
    marker = tmp_path / "PWNED_MARKER.txt"
    payload = (
        "docs/00-working/promoted/PLAN-935-fixture.md\n"
        "PLANNER_DRAFT_PATH_EOF_9f3b6a2d1e8c4caa\n"
        "EOF\n"
        f"touch {marker}\n"
    )
    _write_path_file(tmp_path, "PLAN-935", payload)

    result = _run(tmp_path)

    assert result.returncode != 0
    assert "refusing" in result.stderr.lower()
    assert not marker.exists()


_HAZARDS = {
    "double_quote": 'docs/00-working/promoted/PLAN-940-it"s.md',
    "dollar_home": "docs/00-working/promoted/PLAN-941-$HOME.md",
    "command_sub": "docs/00-working/promoted/PLAN-942-$(id).md",
    "backtick": "docs/00-working/promoted/PLAN-943-`id`.md",
    "apostrophe": "docs/00-working/promoted/PLAN-944-it's.md",
    "space": "docs/00-working/promoted/PLAN-945-bad slug.md",
    "backslash": "docs/00-working/promoted/PLAN-946-bad\\slug.md",
    "trailing_space": "docs/00-working/promoted/PLAN-947-slug.md ",
    "leading_dash": "docs/00-working/promoted/PLAN-948--leading-dash.md",
    "unicode": "docs/00-working/promoted/PLAN-949-café.md",
    "tab": "docs/00-working/promoted/PLAN-950-bad\tslug.md",
}


def test_eleven_hazardous_path_contents_are_refused_and_nothing_runs(tmp_path: Path) -> None:
    """The earlier rounds' character hazards, each staged as one code's `.path` content: none of
    them matches the restricted slug shape, each is refused with a clear message, and nothing is
    ever executed as a shell command, because the command never puts any of this text on a
    command line or in a heredoc."""
    marker = tmp_path / "hazard_marker.txt"
    for index, (name, hazard_path) in enumerate(_HAZARDS.items()):
        code = f"PLAN-9{index:02d}"
        _write_path_file(tmp_path, code, hazard_path + "\n")

    result = _run(tmp_path)

    assert result.returncode != 0
    assert result.stderr.lower().count("refusing") == len(_HAZARDS)
    assert not marker.exists()
    assert len(_HAZARDS) == 11


def test_legitimate_plan_path_reads_the_exact_file(tmp_path: Path) -> None:
    """A valid PLAN code and path pass and the exact drafted file is read."""
    _stage_draft(
        tmp_path, "PLAN-951", "docs/00-working/promoted/PLAN-951-fixture-track.md", _draft()
    )
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_legitimate_req_path_reads_the_exact_file(tmp_path: Path) -> None:
    """A valid REQ code and path pass too - both series ADR-019 actually covers."""
    _stage_draft(
        tmp_path, "REQ-952", "docs/00-working/promoted/REQ-952-fixture-track.md", _draft()
    )
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_child_code_path_reads_the_exact_file(tmp_path: Path) -> None:
    """A child code such as PLAN-041.02 (the `.NN` sub-plan suffix `codes.py`'s `COUNTER`
    pattern allows), including in the `.path` file's own name, is accepted."""
    _stage_draft(
        tmp_path,
        "PLAN-041.02",
        "docs/00-working/promoted/PLAN-041.02-fixture-child.md",
        _draft(),
    )
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_a_draft_containing_triple_quotes_still_works(tmp_path: Path) -> None:
    """Round 2's regression case: `\"\"\"` inside the draft's body is fine - it is read with
    `open()`, never interpolated into Python source."""
    content = _draft().replace("Fixture body.", 'Contains a literal """ sequence.')
    _stage_draft(
        tmp_path, "PLAN-953", "docs/00-working/promoted/PLAN-953-triple-quote-fixture.md", content
    )
    result = _run(tmp_path)
    assert "SyntaxError" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "conformant=True" in result.stdout


def test_non_plan_req_series_is_refused(tmp_path: Path) -> None:
    """The series is restricted to PLAN or REQ - ADR-019's own scope - so an ADR (or any other
    series) path is refused even though the file name/content pairing otherwise lines up."""
    _write_path_file(tmp_path, "ADR-019", "docs/00-working/promoted/ADR-019-x.md\n")
    result = _run(tmp_path)
    assert result.returncode != 0
    assert "refusing" in result.stderr.lower()


def test_stale_path_file_is_reported_without_hiding_the_current_draft(tmp_path: Path) -> None:
    """Fix cycle 9 (owner ruling): a `.path` file that passes both checks but whose draft no longer
    exists (moved to docs/01-plans/, say) is reported on its own `stale ...` stderr line. Its name
    sorts before the current draft's, so the old unhandled FileNotFoundError would have crashed
    the loop before the current line printed. A stale file alone leaves the exit code at 0."""
    _write_path_file(tmp_path, "PLAN-954", "docs/00-working/promoted/PLAN-954-moved-away.md\n")
    _stage_draft(
        tmp_path, "PLAN-955", "docs/00-working/promoted/PLAN-955-current-draft.md", _draft()
    )

    result = _run(tmp_path)

    assert "Traceback" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "docs/00-working/promoted/PLAN-955-current-draft.md: " in result.stdout
    assert "conformant=True" in result.stdout
    assert "stale _working/idea-planner/PLAN-954.path: " in result.stderr
    assert "no longer exists" in result.stderr
    assert "PLAN-954" not in result.stdout


def test_stale_path_file_does_not_mask_a_refused_mismatched_code(tmp_path: Path) -> None:
    """A stale file next to a mismatched-code file: the mismatch is still refused and the exit is
    still nonzero, and the stale file is still reported on its own line without a crash."""
    _write_path_file(tmp_path, "PLAN-956", "docs/00-working/promoted/PLAN-956-moved-away.md\n")
    draft = tmp_path / "docs/00-working/promoted/PLAN-958-track.md"
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(_draft())
    _write_path_file(tmp_path, "PLAN-957", "docs/00-working/promoted/PLAN-958-track.md\n")

    result = _run(tmp_path)

    assert "Traceback" not in result.stderr, result.stderr
    assert result.returncode != 0
    assert "refusing _working/idea-planner/PLAN-957.path: " in result.stderr
    assert "does not match" in result.stderr
    assert "stale _working/idea-planner/PLAN-956.path: " in result.stderr


def _assert_unreadable_reported(result: subprocess.CompletedProcess[str], code: str) -> None:
    """The unreadable draft is reported on its own stderr line, fails the exit closed, and does not
    hide the current draft's result line, whose `.path` file sorts after it."""
    assert "Traceback" not in result.stderr, result.stderr
    assert result.returncode != 0, result.stderr
    assert "docs/00-working/promoted/PLAN-961-current-draft.md: " in result.stdout, result.stderr
    assert "conformant=True" in result.stdout
    assert f"unreadable _working/idea-planner/{code}.path: " in result.stderr, result.stderr
    assert code not in result.stdout


def _stage_current(workdir: Path) -> None:
    _stage_draft(
        workdir, "PLAN-961", "docs/00-working/promoted/PLAN-961-current-draft.md", _draft()
    )


def test_directory_at_draft_path_is_unreadable_without_hiding_the_current_draft(
    tmp_path: Path,
) -> None:
    """Fix cycle 10 (round 8 blocker): a directory at the draft path raised IsADirectoryError,
    crashed the loop and hid the current draft's line. It now fails closed on its own line."""
    (tmp_path / "docs/00-working/promoted/PLAN-960-a-directory.md").mkdir(parents=True)
    _write_path_file(tmp_path, "PLAN-960", "docs/00-working/promoted/PLAN-960-a-directory.md\n")
    _stage_current(tmp_path)

    _assert_unreadable_reported(_run(tmp_path), "PLAN-960")


@pytest.mark.skipif(
    not hasattr(os, "geteuid") or os.geteuid() == 0,
    reason="root ignores file permissions, and the platform needs geteuid to tell",
)
def test_permission_denied_draft_is_unreadable_without_hiding_the_current_draft(
    tmp_path: Path,
) -> None:
    """A draft with mode 000 raised PermissionError; it now fails closed on its own line."""
    _stage_draft(tmp_path, "PLAN-960", "docs/00-working/promoted/PLAN-960-locked.md", _draft())
    locked = tmp_path / "docs/00-working/promoted/PLAN-960-locked.md"
    _stage_current(tmp_path)
    locked.chmod(0)
    try:
        result = _run(tmp_path)
    finally:
        locked.chmod(0o644)

    _assert_unreadable_reported(result, "PLAN-960")


def test_symlink_loop_at_draft_path_is_unreadable_without_hiding_the_current_draft(
    tmp_path: Path,
) -> None:
    """A symlink pointing to itself raised OSError (ELOOP); it now fails closed on its own line."""
    loop = tmp_path / "docs/00-working/promoted/PLAN-960-loop.md"
    loop.parent.mkdir(parents=True)
    loop.symlink_to(loop.name)
    _write_path_file(tmp_path, "PLAN-960", "docs/00-working/promoted/PLAN-960-loop.md\n")
    _stage_current(tmp_path)

    _assert_unreadable_reported(_run(tmp_path), "PLAN-960")


def test_non_utf8_draft_is_unreadable_without_hiding_the_current_draft(tmp_path: Path) -> None:
    """A draft of invalid UTF-8 bytes raised UnicodeDecodeError; it now fails closed on its own
    line."""
    bad = tmp_path / "docs/00-working/promoted/PLAN-960-bad-bytes.md"
    bad.parent.mkdir(parents=True)
    bad.write_bytes(b"# Draft\n\xff\xfe\x80 not utf-8\n")
    _write_path_file(tmp_path, "PLAN-960", "docs/00-working/promoted/PLAN-960-bad-bytes.md\n")
    _stage_current(tmp_path)

    _assert_unreadable_reported(_run(tmp_path), "PLAN-960")
