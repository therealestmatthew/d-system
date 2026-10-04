"""Tests for tools/check_diff_patterns.py over fixture commits in a throwaway repository (R08).

R08's table: each pattern added (1); `# type: ignore[import-untyped]` (0); `except
FileNotFoundError: pass` (0); an unchanged existing ignore in context lines (0); a removed ignore
(0).
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


patterns = _load("check_diff_patterns")

BASE_SOURCE = '''\
from typing import Any, cast

import yaml  # type: ignore[import-untyped]


def existing(value: object) -> int:
    return value  # type: ignore[return-value]


def guarded() -> None:
    try:
        existing(1)
    except Exception:
        pass
'''


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "dev")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg/mod.py").write_text(BASE_SOURCE)
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "base")
    git(tmp_path, "tag", "base")
    return tmp_path


def commit(repo: Path, source: str, path: str = "pkg/mod.py") -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "head")


def run(repo: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    code = patterns.main(["base..HEAD", "--repo", str(repo)])
    return code, capsys.readouterr().out


def appended(text: str) -> str:
    return BASE_SOURCE + "\n\n" + text


@pytest.mark.parametrize(
    ("added", "pattern"),
    [
        ("def f(v: object) -> int:\n    return v  # type: ignore\n", "type-ignore"),
        ("def f(v: object) -> int:\n    return v  # type: ignore[arg-type]\n", "type-ignore"),
        ("import z  # type: ignore[import-untyped, attr-defined]\n", "type-ignore"),
        ("def f(v: object) -> Any:\n    return cast(Any, v)\n", "cast-any"),
        ("import typing\nX = typing.cast(typing.Any, 1)\n", "cast-any"),
        ("def f() -> None:\n    try:\n        f()\n    except:\n        pass\n", "except-pass"),
        ("def f() -> None:\n    try:\n        f()\n    except BaseException:\n        pass\n",
         "except-pass"),
        ("def f() -> None:\n    try:\n        f()\n    except (ValueError, Exception):\n"
         "        pass\n", "except-pass"),
        ("def f() -> None:\n    try:\n        f()\n    except Exception: pass\n", "except-pass"),
    ],
)
def test_each_added_pattern_fails(
    repo: Path, capsys: pytest.CaptureFixture[str], added: str, pattern: str
) -> None:
    commit(repo, appended(added))
    code, out = run(repo, capsys)
    assert code == 1
    assert f": {pattern}: " in out
    assert out.count("pkg/mod.py:") == 1


@pytest.mark.parametrize(
    "added",
    [
        "import z  # type: ignore[import-untyped]\n",
        "import z  # type: ignore[ import-untyped ]\n",
        "def f() -> None:\n    try:\n        f()\n    except FileNotFoundError:\n        pass\n",
        "def f() -> None:\n    try:\n        f()\n    except Exception:\n        raise\n",
        "def f() -> None:\n    try:\n        f()\n    except Exception:\n        pass\n"
        "        return\n",
        "X = cast(int, 1)\n",
        "TEXT = 'cast(Any, x)  # type: ignore[arg-type]'\n",
        "def f() -> None:\n    '''except Exception: pass'''\n",
    ],
)
def test_allowed_additions_pass(
    repo: Path, capsys: pytest.CaptureFixture[str], added: str
) -> None:
    commit(repo, appended(added))
    code, out = run(repo, capsys)
    assert code == 0, out
    assert out.startswith("Diff patterns OK")


def test_an_unchanged_existing_ignore_in_context_passes(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Edits next to the existing ignore and the existing except/pass, which stay as context.
    source = BASE_SOURCE.replace(
        "def existing(value: object) -> int:", "def existing(value: object) -> int:  # edited"
    ).replace("        existing(1)", "        existing(2)")
    commit(repo, source)
    code, out = run(repo, capsys)
    assert code == 0, out


def test_a_body_replaced_by_pass_fails(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # The `except Exception:` line stays as context; only the body becomes `pass`.
    commit(repo, appended("def g() -> None:\n    try:\n        g()\n    except Exception:\n"
                          "        print('logged')\n"))
    git(repo, "tag", "-f", "base")
    commit(repo, appended("def g() -> None:\n    try:\n        g()\n    except Exception:\n"
                          "        pass\n"))
    code, out = run(repo, capsys)
    line = len(appended("def g() -> None:\n    try:\n        g()\n    except Exception:\n")
               .splitlines()) + 1
    assert code == 1
    assert f"pkg/mod.py:{line}: except-pass: pass" in out


def test_a_specific_handler_body_replaced_by_pass_passes(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    commit(repo, appended("def g() -> None:\n    try:\n        g()\n    except KeyError:\n"
                          "        print('logged')\n"))
    git(repo, "tag", "-f", "base")
    commit(repo, appended("def g() -> None:\n    try:\n        g()\n    except KeyError:\n"
                          "        pass\n"))
    code, out = run(repo, capsys)
    assert code == 0, out


def test_a_removed_ignore_passes(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(repo, BASE_SOURCE.replace("  # type: ignore[return-value]", ""))
    code, out = run(repo, capsys)
    assert code == 0, out


def test_a_new_file_is_checked(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(repo, "X = 1  # type: ignore\n", path="pkg/new.py")
    code, out = run(repo, capsys)
    assert code == 1
    assert "pkg/new.py:1: type-ignore: X = 1  # type: ignore" in out


def test_non_python_files_are_not_read(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(repo, "Never write `# type: ignore` or `except Exception: pass`.\n", path="doc.md")
    code, _ = run(repo, capsys)
    assert code == 0


def test_findings_name_file_line_and_text(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(repo, appended("def f(v: object) -> Any:\n    return cast(Any, v)\n"))
    code, out = run(repo, capsys)
    line = len(appended("def f(v: object) -> Any:\n").splitlines()) + 1
    assert code == 1
    assert out.splitlines() == [
        "1 added lines match a refused pattern in base..HEAD:",
        f"  pkg/mod.py:{line}: cast-any: return cast(Any, v)",
    ]


@pytest.mark.parametrize("value", ["base", "base..", "..HEAD", "base...HEAD"])
def test_a_malformed_range_exits_2(
    repo: Path, capsys: pytest.CaptureFixture[str], value: str
) -> None:
    assert patterns.main([value, "--repo", str(repo)]) == 2
    assert capsys.readouterr().err.startswith("ERROR range must be")


def test_an_unknown_revision_exits_2(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert patterns.main(["nosuchref..HEAD", "--repo", str(repo)]) == 2
    assert capsys.readouterr().err.startswith("ERROR git diff")


def test_a_file_that_does_not_parse_exits_2(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    commit(repo, appended("def broken(:\n"))
    assert patterns.main(["base..HEAD", "--repo", str(repo)]) == 2
    assert "does not parse at head" in capsys.readouterr().err
