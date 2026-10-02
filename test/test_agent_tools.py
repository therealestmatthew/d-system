"""The review-judge agent type's declared tools stay exactly Read, Grep, Glob (REQ-030 R01)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
JUDGE = ROOT / ".claude" / "agents" / "review-judge.md"
READ_ONLY = ["Read", "Grep", "Glob"]


def _declared_tools(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no front matter"
    front_matter = yaml.safe_load(text.split("---\n", 2)[1])
    tools = front_matter.get("tools")
    assert tools, f"{path} declares no tools; an agent without the field inherits every tool"
    if isinstance(tools, str):
        tools = [tool.strip() for tool in tools.split(",")]
    return list(tools)


def _assert_read_only(path: Path) -> None:
    tools = _declared_tools(path)
    assert sorted(tools) == sorted(READ_ONLY), (
        f"{path} declares tools {tools}, expected exactly {READ_ONLY}"
    )


def test_review_judge_tools_are_exactly_read_grep_glob() -> None:
    _assert_read_only(JUDGE)


@pytest.mark.parametrize("extra", ["Bash", "Edit", "Write"])
def test_assertion_fails_on_a_copy_that_adds_a_tool(tmp_path: Path, extra: str) -> None:
    text = JUDGE.read_text(encoding="utf-8")
    line = "tools: Read, Grep, Glob\n"
    assert line in text
    fixture = tmp_path / "review-judge.md"
    fixture.write_text(
        text.replace(line, f"tools: Read, Grep, Glob, {extra}\n", 1), encoding="utf-8"
    )
    with pytest.raises(AssertionError, match=extra):
        _assert_read_only(fixture)


def test_assertion_fails_on_a_copy_without_a_tools_field(tmp_path: Path) -> None:
    text = JUDGE.read_text(encoding="utf-8")
    fixture = tmp_path / "review-judge.md"
    fixture.write_text(text.replace("tools: Read, Grep, Glob\n", "", 1), encoding="utf-8")
    with pytest.raises(AssertionError, match="declares no tools"):
        _assert_read_only(fixture)
