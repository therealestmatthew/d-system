"""Tests for tools/check_test_baseline.py over JUnit XML fixtures (REQ-028 R07).

The five cases are R07's: one removed test (1), one newly skipped test (1), one added test (0),
an unchanged run (0), and a test skipped in both (0).
"""

from __future__ import annotations

import importlib.util
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


baseline = _load("check_test_baseline")


def report(path: Path, cases: dict[str, str]) -> Path:
    """Write a pytest-shaped JUnit report: `cases` maps `module::name` to an outcome."""
    rows = []
    for test_id, outcome in cases.items():
        classname, name = test_id.split("::")
        body = {
            "passed": "",
            "skipped": '<skipped type="pytest.skip" message="skip">skip</skipped>',
            "failed": '<failure message="assert False">assert False</failure>',
            "error": '<error message="boom">boom</error>',
        }[outcome]
        rows.append(
            f'<testcase classname="{classname}" name="{name}" time="0.001">{body}</testcase>'
        )
    path.write_text(
        '<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest">'
        + "".join(rows)
        + "</testsuite></testsuites>",
        encoding="utf-8",
    )
    return path


BASE = {
    "test.test_a::test_one": "passed",
    "test.test_a::test_two[x]": "passed",
    "test.test_b::test_three": "passed",
}


def run(tmp_path: Path, base: dict[str, str], branch: dict[str, str],
        capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    code = baseline.main([str(report(tmp_path / "base.xml", base)),
                          str(report(tmp_path / "branch.xml", branch))])
    return code, capsys.readouterr().out


def test_removed_test_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    branch = {k: v for k, v in BASE.items() if k != "test.test_a::test_two[x]"}
    code, out = run(tmp_path, BASE, branch, capsys)
    assert code == 1
    assert "missing  test.test_a::test_two[x]" in out


def test_newly_skipped_test_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(tmp_path, BASE, {**BASE, "test.test_b::test_three": "skipped"}, capsys)
    assert code == 1
    assert "skipped  test.test_b::test_three" in out


def test_added_test_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(tmp_path, BASE, {**BASE, "test.test_c::test_new": "passed"}, capsys)
    assert code == 0
    assert out.startswith("Test baseline OK: 3 tests passed in the base")


def test_unchanged_run_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, _ = run(tmp_path, BASE, BASE, capsys)
    assert code == 0


def test_skipped_in_both_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    both = {**BASE, "test.test_d::test_skipped": "skipped"}
    code, _ = run(tmp_path, both, both, capsys)
    assert code == 0


def test_each_dropped_test_is_listed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    branch = {"test.test_a::test_one": "skipped"}
    code, out = run(tmp_path, BASE, branch, capsys)
    assert code == 1
    assert out.splitlines() == [
        "3 tests passed in the base and are missing or skipped in the branch:",
        "  skipped  test.test_a::test_one",
        "  missing  test.test_a::test_two[x]",
        "  missing  test.test_b::test_three",
    ]


def test_a_test_failing_in_the_base_is_not_reported(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = {**BASE, "test.test_e::test_broken": "failed"}
    code, _ = run(tmp_path, base, BASE, capsys)
    assert code == 0


def test_outcomes_reads_errors_as_failed(tmp_path: Path) -> None:
    path = report(tmp_path / "r.xml", {"m::ok": "passed", "m::bad": "error", "m::s": "skipped"})
    assert baseline.outcomes(path) == {"m::ok": "passed", "m::bad": "failed", "m::s": "skipped"}


@pytest.mark.parametrize("content", ["not xml at all", "<testsuites></testsuites>"])
def test_an_unusable_report_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], content: str
) -> None:
    bad = tmp_path / "bad.xml"
    bad.write_text(content, encoding="utf-8")
    good = report(tmp_path / "good.xml", BASE)
    assert baseline.main([str(bad), str(good)]) == 2
    assert capsys.readouterr().err.startswith("ERROR ")


def test_a_missing_report_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = report(tmp_path / "good.xml", BASE)
    assert baseline.main([str(good), str(tmp_path / "absent.xml")]) == 2


def test_a_real_pytest_report_round_trips(tmp_path: Path) -> None:
    """The parser reads what this repository's pytest actually writes, not only the fixtures."""
    import subprocess

    xml = tmp_path / "real.xml"
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={xml}",
         "test/test_check_test_baseline.py::test_unchanged_run_passes"],
        cwd=ROOT, check=True, capture_output=True,
    )
    assert baseline.outcomes(xml) == {
        "test.test_check_test_baseline::test_unchanged_run_passes": "passed"
    }
