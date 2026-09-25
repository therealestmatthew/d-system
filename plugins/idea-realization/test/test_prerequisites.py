"""The check reports what is missing and changes nothing; only --yes installs."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import prerequisites
from conftest import SCRIPTS


def listing(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def path_without_uv(tmp_path: Path) -> str:
    """A PATH holding only git, so uv and claude are absent."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    git = shutil.which("git")
    assert git, "git is needed to run this test"
    (bin_dir / "git").symlink_to(git)
    return str(bin_dir)


def test_check_without_uv_names_it_and_changes_nothing(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    (work / "keep.txt").write_text("unchanged\n")
    before = listing(work)
    env = {**os.environ, "PATH": path_without_uv(tmp_path)}
    result = subprocess.run([sys.executable, str(SCRIPTS / "prerequisites.py")], cwd=work,
                            env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "missing  uv" in result.stdout
    assert prerequisites.UV_INSTALL["other"] in result.stdout
    assert "nothing was installed" in result.stdout
    assert listing(work) == before


def test_everything_present_exits_zero(capsys: object) -> None:
    def which(name: str) -> str | None:
        return f"/usr/bin/{name}"

    calls: list[str] = []
    assert prerequisites.main([], which=which, runner=calls.append) == 0  # type: ignore[arg-type]
    assert calls == []


def test_check_mode_never_runs_an_installer() -> None:
    calls: list[str] = []

    def runner(command: str) -> int:
        calls.append(command)
        return 0

    def which(name: str) -> str | None:
        return None if name == "uv" else f"/usr/bin/{name}"

    assert prerequisites.main([], which=which, runner=runner) == 1
    assert calls == []


def test_yes_installs_only_what_is_missing() -> None:
    installed: set[str] = set()
    calls: list[str] = []

    def which(name: str) -> str | None:
        return f"/usr/bin/{name}" if name != "uv" or "uv" in installed else None

    def runner(command: str) -> int:
        calls.append(command)
        installed.add("uv")
        return 0

    assert prerequisites.main(["--yes"], which=which, runner=runner) == 0
    assert calls == [prerequisites.UV_INSTALL["other"]] or calls == [
        prerequisites.UV_INSTALL["windows"]]


def test_claude_is_required_only_for_triage_and_partition() -> None:
    def which(name: str) -> str | None:
        return None if name == "claude" else f"/usr/bin/{name}"

    assert prerequisites.main(["--feature", "ideas"], which=which, runner=lambda c: 0) == 0
    assert prerequisites.main(["--feature", "triage"], which=which, runner=lambda c: 0) == 1
    assert prerequisites.main(["--feature", "partition"], which=which, runner=lambda c: 0) == 1


def test_old_python_is_reported() -> None:
    items = prerequisites.survey([], which=lambda name: "/x", version=(3, 11), system="linux")
    python = next(item for item in items if item.name == "python")
    assert not python.present
    assert python.install == "uv python install 3.12"


def test_git_install_follows_the_package_manager() -> None:
    def which(name: str) -> str | None:
        return "/usr/bin/dnf" if name == "dnf" else None

    assert prerequisites.git_install(which, "linux") == "sudo dnf install -y git"
    assert prerequisites.git_install(which, "darwin") == "xcode-select --install"
