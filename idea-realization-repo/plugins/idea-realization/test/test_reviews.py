"""Review verdict records validate, are named by their id, and keep finding ids unique."""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import paths
import product
import pytest
import yaml
from checks import reviews

COMMIT = "a" * 40
SHA = "b" * 64


def record(**changes: Any) -> dict[str, Any]:
    return {
        "verdict_id": "day-build-api-phase-adversary",
        "date": date(2030, 1, 5).isoformat(),
        "phase": "build-api",
        "repository": "product",
        "reviewed_commit": COMMIT,
        "reviewer": {"type": "phase-adversary", "definition_sha256": SHA},
        "model": "a model",
        "verdict": "pass",
        "gating": True,
        "findings": [],
        "outcomes": [],
        **changes,
    }


def check(root: Path, *records: dict[str, Any], name: str | None = None) -> list[str]:
    directory = root / "docs" / "reviews"
    directory.mkdir(parents=True, exist_ok=True)
    for item in records:
        (directory / f"{name or item['verdict_id']}.json").write_text(json.dumps(item))
    return reviews.check(paths.resolve({"root": str(root)}, env={}))


def stamped(**changes: Any) -> dict[str, Any]:
    """A record whose id carries a date built at runtime, as real records do."""
    item = record(**changes)
    item["verdict_id"] = f"{item['date']}-build-api-phase-adversary"
    return item


def test_no_reviews_directory_is_clean(tmp_path: Path) -> None:
    assert reviews.check(paths.resolve({"root": str(tmp_path)}, env={})) == []


def test_a_valid_record_is_clean(tmp_path: Path) -> None:
    assert check(tmp_path, stamped()) == []


def test_a_record_must_be_named_by_its_id(tmp_path: Path) -> None:
    errors = check(tmp_path, stamped(), name="other-name")
    assert any("is not the file name" in error for error in errors)


def test_schema_violations_are_reported(tmp_path: Path) -> None:
    errors = check(tmp_path, stamped(verdict="maybe", repository="elsewhere"))
    assert any("verdict" in error for error in errors)
    assert any("repository" in error for error in errors)


def test_finding_ids_are_unique(tmp_path: Path) -> None:
    finding = {"id": "F01", "severity": "minor", "title": "A defect.", "evidence": "a file"}
    errors = check(tmp_path, stamped(findings=[finding, finding]))
    assert any("duplicate finding id" in error for error in errors)


def test_unreadable_json_is_reported(tmp_path: Path) -> None:
    directory = tmp_path / "docs" / "reviews"
    directory.mkdir(parents=True)
    (directory / "broken.json").write_text("{")
    assert any(error.startswith("reviews/broken.json") for error in check(tmp_path))


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


def complete_phase(root: Path, **changes: Any) -> None:
    item = {"id": "build-api", "status": "complete", **changes}
    (root / "backlog").mkdir(exist_ok=True)
    (root / "backlog" / "backlog.yaml").write_text(yaml.safe_dump({"items": [item]}))


def run(root: Path, product_root: Path | None = None) -> list[str]:
    env = {"IDEA_REALIZATION_PRODUCT_ROOT": str(product_root)} if product_root else {}
    return reviews.check(paths.resolve({"root": str(root)}, env=env))


def test_a_complete_phase_with_no_reviews_fails(tmp_path: Path) -> None:
    complete_phase(tmp_path)
    assert any("complete without a passing gating verdict" in e for e in run(tmp_path))


def test_a_complete_phase_with_a_passing_gating_verdict_is_clean(tmp_path: Path) -> None:
    complete_phase(tmp_path)
    assert check(tmp_path, stamped(phase="build-api")) == []


@pytest.mark.parametrize("changes", [{"gating": False}, {"verdict": "reject"}])
def test_a_shadow_or_rejecting_verdict_does_not_complete_a_phase(
        tmp_path: Path, changes: dict[str, Any]) -> None:
    complete_phase(tmp_path)
    errors = check(tmp_path, stamped(phase="build-api", **changes))
    assert any("complete without a passing gating verdict" in e for e in errors)


@pytest.fixture
def two_repos(tmp_path: Path) -> tuple[Path, Path, str, str]:
    """A control folder naming a product checkout whose main has one commit and whose phase
    branch has one more: (control, product checkout, main commit, branch commit).

    The checkout's ``origin`` is a bare repository beside it, holding main at the first commit and
    fetched, so the check can ask ``origin`` where main is without a network."""
    control, checkout = tmp_path / "control", tmp_path / "hack-product"
    origin = tmp_path / "hack-product.git"
    control.mkdir()
    checkout.mkdir()
    git(control, "init", "-q", "-b", "main")
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    git(checkout, "init", "-q", "-b", "main")
    git(checkout, "remote", "add", "origin", str(origin))
    for message in ("base", "phase work"):
        if message == "phase work":
            git(checkout, "checkout", "-q", "-b", "agent/build-api")
        (checkout / f"{message.replace(' ', '-')}.txt").write_text(message)
        git(checkout, "add", "-A")
        git(checkout, "-c", "user.email=a@example.com", "-c", "user.name=a", "commit", "-qm",
            message)
    base, tip = git(checkout, "rev-parse", "main"), git(checkout, "rev-parse", "HEAD")
    git(checkout, "checkout", "-q", "main")
    git(checkout, "push", "-q", "origin", "main")
    git(checkout, "fetch", "-q", "origin")
    (control / ".idea-realization").mkdir()
    (control / product.RECORD).write_text(
        f"schema_version: 1\nname: hack-product\nremote: {origin}\nintegration_branch: main\n")
    return control, checkout, base, tip


def test_two_repositories_need_the_product_merge(two_repos: tuple[Path, Path, str, str]) -> None:
    control, _, _, tip = two_repos
    complete_phase(control)
    errors = check(control, stamped(phase="build-api", reviewed_commit=tip))
    assert any("without product_merge" in e for e in errors)


def test_the_verdict_must_have_judged_the_merged_commit(
        two_repos: tuple[Path, Path, str, str]) -> None:
    control, checkout, base, tip = two_repos
    complete_phase(control, product_merge=tip)
    check(control, stamped(phase="build-api", reviewed_commit=base))
    assert any("judged its product_merge" in e for e in run(control, checkout))


def test_a_phase_needs_a_passing_product_verdict(two_repos: tuple[Path, Path, str, str]) -> None:
    control, _, _, tip = two_repos
    complete_phase(control, product_merge=tip)
    errors = check(control, stamped(phase="build-api", repository="control", reviewed_commit=tip))
    assert any("judged its product_merge" in e for e in errors)


def test_product_merge_must_be_a_full_commit_id(two_repos: tuple[Path, Path, str, str]) -> None:
    control, _, _, tip = two_repos
    complete_phase(control, product_merge="--" + tip[:10])
    errors = check(control, stamped(phase="build-api", reviewed_commit=tip))
    assert any("is not a full commit id" in e for e in errors)


def merge_commit(checkout: Path) -> str:
    """Merge the phase branch into main with a merge commit, as a pull request merge does."""
    git(checkout, "-c", "user.email=a@example.com", "-c", "user.name=a", "merge", "-q", "--no-ff",
        "-m", "Merge agent/build-api", "agent/build-api")
    return git(checkout, "rev-parse", "HEAD")


def test_a_merge_commit_whose_second_parent_was_reviewed_is_clean(
        two_repos: tuple[Path, Path, str, str]) -> None:
    control, checkout, _, tip = two_repos
    merge = merge_commit(checkout)
    assert merge != tip
    complete_phase(control, product_merge=merge)
    check(control, stamped(phase="build-api", reviewed_commit=tip))
    assert run(control, checkout) == []


def test_a_merge_commit_whose_second_parent_was_not_reviewed_fails(
        two_repos: tuple[Path, Path, str, str]) -> None:
    control, checkout, base, _ = two_repos
    merge = merge_commit(checkout)
    complete_phase(control, product_merge=merge)
    check(control, stamped(phase="build-api", reviewed_commit=base))  # the first parent
    errors = run(control, checkout)
    assert any("judged its product_merge" in e and "second parent" in e for e in errors)


def test_a_merge_commit_is_unchecked_without_a_checkout(
        two_repos: tuple[Path, Path, str, str]) -> None:
    """Without a product checkout on this machine a merge commit's parents cannot be read."""
    control, checkout, base, _ = two_repos
    merge = merge_commit(checkout)
    complete_phase(control, product_merge=merge)
    assert check(control, stamped(phase="build-api", reviewed_commit=base)) == []


def test_an_unmerged_merge_commit_is_stranded(two_repos: tuple[Path, Path, str, str]) -> None:
    """A merge commit made on a side branch, never on the integration branch, is stranded."""
    control, checkout, _, tip = two_repos
    git(checkout, "checkout", "-q", "-b", "side")
    merge = merge_commit(checkout)
    git(checkout, "checkout", "-q", "main")
    complete_phase(control, product_merge=merge)
    check(control, stamped(phase="build-api", reviewed_commit=tip))
    assert any("stranded" in e for e in run(control, checkout))


def test_a_product_merge_unknown_to_the_checkout_is_stranded(
        two_repos: tuple[Path, Path, str, str]) -> None:
    control, checkout, _, _ = two_repos
    complete_phase(control, product_merge="c" * 40)
    check(control, stamped(phase="build-api", reviewed_commit="c" * 40))
    assert any("stranded" in e for e in run(control, checkout))


def test_a_complete_phase_whose_merge_never_landed_is_stranded(
        two_repos: tuple[Path, Path, str, str]) -> None:
    control, checkout, _, tip = two_repos
    complete_phase(control, product_merge=tip)
    check(control, stamped(phase="build-api", reviewed_commit=tip))
    assert any("stranded" in e for e in run(control, checkout))
    assert run(control) == []  # without a checkout on this machine, landing cannot be checked
    git(checkout, "merge", "-q", "--ff-only", "agent/build-api")
    assert run(control, checkout) == []


def test_a_refused_product_checkout_is_an_error(two_repos: tuple[Path, Path, str, str]) -> None:
    """A wrong-origin checkout never lets the reviews check report OK or skip stranding."""
    control, checkout, _, tip = two_repos
    complete_phase(control, product_merge=tip)
    check(control, stamped(phase="build-api", reviewed_commit=tip))
    git(checkout, "remote", "set-url", "origin", str(checkout.parent / "other.git"))
    errors = run(control, checkout)
    assert any("product checkout refused" in e for e in errors)


def test_a_completion_without_a_checkout_says_it_was_not_checked(
        two_repos: tuple[Path, Path, str, str], capsys: pytest.CaptureFixture[str]) -> None:
    """Control CI has no product checkout. The gating review's reproduction (workflow-sim M3): a
    made-up product_merge beside a passing verdict on an unrelated commit. Whether it is a merge
    commit whose second parent was reviewed needs the product repository, so it is a note, not an
    error; the note names what could not be checked."""
    control, _, _, _ = two_repos
    made_up, unrelated = "f" * 40, "a" * 40
    complete_phase(control, product_merge=made_up)
    assert check(control, stamped(phase="build-api", reviewed_commit=unrelated)) == []
    printed = capsys.readouterr().err
    assert "reviews: build-api: product_merge " + made_up + " not checked" in printed
    assert "no product checkout" in printed
    assert "is not the reviewed commit " + unrelated in printed
    assert "second parent" in printed


def test_a_fast_forward_completion_without_a_checkout_needs_no_note(
        two_repos: tuple[Path, Path, str, str], capsys: pytest.CaptureFixture[str]) -> None:
    """product_merge equal to the reviewed commit is a fast-forward: the control records agree
    with each other, and nothing about the merge needs the product repository to read."""
    control, _, _, tip = two_repos
    complete_phase(control, product_merge=tip)
    capsys.readouterr()
    assert check(control, stamped(phase="build-api", reviewed_commit=tip)) == []
    assert "not checked" not in capsys.readouterr().err


@pytest.mark.parametrize(("changes", "merge", "expected"), [
    ({"phase": "build-ui"}, "f" * 40, "complete without a passing gating verdict"),
    ({"gating": False}, "f" * 40, "complete without a passing gating verdict"),
    ({"verdict": "reject"}, "f" * 40, "complete without a passing gating verdict"),
    ({"repository": "control"}, "f" * 40, "no passing gating verdict judged its product_merge"),
    ({"reviewed_commit": "a" * 39}, "f" * 40, "reviewed_commit"),
    ({"reviewed_commit": "A" * 40}, "f" * 40, "reviewed_commit"),
    ({}, "f" * 39, "is not a full commit id"),
    ({}, "F" * 40, "is not a full commit id"),
    ({}, None, "without product_merge"),
])
def test_a_completion_without_a_checkout_still_fails_what_needs_no_product_repository(
        two_repos: tuple[Path, Path, str, str], capsys: pytest.CaptureFixture[str],
        changes: dict[str, Any], merge: str | None, expected: str) -> None:
    """Without a product checkout, every check that reads only the control records still runs:
    a verdict for another phase, a shadow or rejecting verdict, a control-repository verdict, a
    malformed commit id and a missing product_merge are errors, not a ``not checked`` note."""
    control, _, _, _ = two_repos
    complete_phase(control, **({"product_merge": merge} if merge else {}))
    capsys.readouterr()
    errors = check(control, stamped(**{"phase": "build-api", "reviewed_commit": "a" * 40,
                                       **changes}))
    assert any(expected in e for e in errors), errors
    assert "not checked" not in capsys.readouterr().err


def test_no_verdict_at_all_without_a_checkout_fails(
        two_repos: tuple[Path, Path, str, str], capsys: pytest.CaptureFixture[str]) -> None:
    control, _, _, _ = two_repos
    complete_phase(control, product_merge="f" * 40)
    capsys.readouterr()
    assert any("complete without a passing gating verdict" in e for e in run(control))
    assert "not checked" not in capsys.readouterr().err


def peer_merges(checkout: Path, fast_forward: bool) -> str:
    """A peer merges the phase branch on origin's main; ``checkout`` does not fetch it."""
    git(checkout, "push", "-q", "origin", "agent/build-api")
    peer = checkout.parent / "peer"
    git(checkout.parent, "clone", "-q", git(checkout, "remote", "get-url", "origin"), str(peer))
    flag = "--ff-only" if fast_forward else "--no-ff"
    git(peer, "-c", "user.email=b@example.com", "-c", "user.name=b", "merge", "-q", flag,
        "-m", "Merge agent/build-api", "origin/agent/build-api")
    git(peer, "push", "-q", "origin", "main")
    return git(peer, "rev-parse", "HEAD")


@pytest.mark.parametrize("fast_forward", [False, True])
def test_a_checkout_behind_origin_does_not_report_a_peer_merge_as_stranded(
        two_repos: tuple[Path, Path, str, str], capsys: pytest.CaptureFixture[str],
        fast_forward: bool) -> None:
    """A peer's phase merged on origin is not stranded because this checkout has not fetched
    (workflow-sim M4)."""
    control, checkout, _, tip = two_repos
    merge = peer_merges(checkout, fast_forward)
    complete_phase(control, product_merge=merge)
    check(control, stamped(phase="build-api", reviewed_commit=tip))
    capsys.readouterr()
    errors = run(control, checkout)
    assert not any("stranded" in e for e in errors), errors
    assert errors == []
    if not fast_forward:  # the merge commit is not here, so nothing about it can be read
        assert "behind origin" in capsys.readouterr().err
    git(checkout, "fetch", "-q", "origin")
    assert run(control, checkout) == []


def test_a_phase_not_on_origin_is_stranded_even_when_the_checkout_is_behind(
        two_repos: tuple[Path, Path, str, str]) -> None:
    """Origin moved on without the phase: the commit is known here and not on origin's main."""
    control, checkout, _, tip = two_repos
    peer = checkout.parent / "peer"
    git(checkout.parent, "clone", "-q", git(checkout, "remote", "get-url", "origin"), str(peer))
    (peer / "other.txt").write_text("other")
    git(peer, "add", "-A")
    git(peer, "-c", "user.email=b@example.com", "-c", "user.name=b", "commit", "-qm", "other")
    git(peer, "push", "-q", "origin", "main")
    complete_phase(control, product_merge=tip)
    check(control, stamped(phase="build-api", reviewed_commit=tip))
    git(checkout, "fetch", "-q", "origin")
    assert any("stranded" in e for e in run(control, checkout))


def test_an_unreachable_origin_cannot_tell_stranding(
        two_repos: tuple[Path, Path, str, str], capsys: pytest.CaptureFixture[str]) -> None:
    control, checkout, _, _ = two_repos
    complete_phase(control, product_merge="c" * 40)
    check(control, stamped(phase="build-api", reviewed_commit="c" * 40))
    origin = Path(git(checkout, "remote", "get-url", "origin"))
    for path in sorted(origin.rglob("*"), reverse=True):
        path.unlink() if path.is_file() else path.rmdir()
    origin.rmdir()
    capsys.readouterr()
    assert run(control, checkout) == []
    assert "cannot tell" in capsys.readouterr().err


def test_the_stranded_recovery_stops_when_the_forge_cannot_tell() -> None:
    """The reopen step runs only on a forge answer that the pull request did not merge as
    product_merge; a failed or unclear forge check stops for the owner (gating review of M4)."""
    text = (paths.PLUGIN_ROOT / "docs" / "two-repositories.md").read_text(encoding="utf-8")
    section = text.split("## A stranded phase", 1)[1].split("\n## ", 1)[0]
    confirm, reopen = section.split("\n2. ", 1)[1].split("\n3. ", 1)
    assert "`gh pr view` fails" in confirm
    assert "no pull request number is recorded" in confirm
    assert "do not reopen the phase" in confirm
    assert reopen.startswith("Only when the forge shows the pull request did not merge")
