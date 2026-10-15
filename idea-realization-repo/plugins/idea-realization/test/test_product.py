"""The control repository names one product repository and refuses a checkout that is not it."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import paths
import product
import pytest
from checks import backlog as feature
from test_backlog import TODAY, phase

REMOTE = "git@forge.example.com:team/hack-product.git"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repos(tmp_path: Path) -> tuple[Path, Path]:
    """A control repository with a product record, and a product checkout beside it."""
    control, checkout = tmp_path / "control", tmp_path / "hack-product"
    for root in (control, checkout):
        root.mkdir()
        git(root, "init", "-q", "-b", "main")
    git(checkout, "remote", "add", "origin", REMOTE)
    (control / ".idea-realization").mkdir()
    (control / product.RECORD).write_text(
        f"schema_version: 1\nname: hack-product\nremote: {REMOTE}\nintegration_branch: main\n")
    return control, checkout


def config(control: Path, checkout: Path | None = None, **extra: str) -> paths.Config:
    env = {"IDEA_REALIZATION_PRODUCT_ROOT": str(checkout)} if checkout else {}
    env.update(extra)
    return paths.resolve({"root": str(control)}, env=env)


def test_split_names_the_repository_of_a_path_and_a_command() -> None:
    assert product.split("product:src/api/") == ("product", "src/api/")
    assert product.split("docs/plans/") == ("control", "docs/plans/")
    assert product.split_command("uv run pytest") == ("product", "uv run pytest")
    assert product.split_command("control: uv run check") == ("control", "uv run check")


@pytest.mark.parametrize("url", [
    "git@forge.example.com:team/hack-product.git",
    "https://forge.example.com/team/hack-product",
    "https://someone@forge.example.com/team/hack-product.git/",
    "ssh://git@forge.example.com/team/hack-product.git",
])
def test_remote_forms_of_one_repository_compare_equal(url: str) -> None:
    assert product.normalise_remote(url) == product.normalise_remote(REMOTE)


def test_another_repository_does_not_compare_equal() -> None:
    other = "git@forge.example.com:team/other-product.git"
    assert product.normalise_remote(other) != product.normalise_remote(REMOTE)


def test_verify_accepts_the_named_checkout(repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    found = product.verify(config(control, checkout))
    assert found.root == checkout.resolve()
    assert found.integration_branch == "main"
    assert found.worktree_dir == checkout.resolve().parent / "hack-product-worktrees"


def test_verify_refuses_a_checkout_of_another_repository(repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    git(checkout, "remote", "set-url", "origin", "git@forge.example.com:team/other.git")
    with pytest.raises(product.ProductError, match="wrong repository"):
        product.verify(config(control, checkout))


def test_verify_refuses_a_checkout_with_no_origin(repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    git(checkout, "remote", "remove", "origin")
    with pytest.raises(product.ProductError, match="no origin"):
        product.verify(config(control, checkout))


def test_unset_product_root_is_reported_not_guessed(repos: tuple[Path, Path]) -> None:
    control, _ = repos
    with pytest.raises(product.ProductError, match="product_root is not set"):
        product.load(config(control))
    assert config(control).invalid() == []


def test_missing_record_means_no_product_repository(tmp_path: Path) -> None:
    with pytest.raises(product.ProductError, match="does not exist"):
        product.load(config(tmp_path, tmp_path.parent))


def test_invalid_record_is_refused(repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    (control / product.RECORD).write_text("schema_version: 1\nname: hack-product\n")
    with pytest.raises(product.ProductError, match="integration_branch"):
        product.load(config(control, checkout))


def test_product_root_inside_the_control_repository_is_refused(repos: tuple[Path, Path]) -> None:
    control, _ = repos
    (control / "inner").mkdir()
    with pytest.raises(paths.PathError, match="product_root"):
        config(control, control / "inner").product_root()


def test_product_worktrees_inside_the_product_checkout_are_refused(
        repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    bad = config(control, checkout, IDEA_REALIZATION_PRODUCT_WORKTREE_DIR="worktrees")
    with pytest.raises(paths.PathError, match="product_worktree_dir"):
        bad.path("product_worktree_dir")
    assert any(error.name == "product_worktree_dir" for error in bad.invalid())


def test_aws_keys_are_plain_text_and_may_be_unset(tmp_path: Path) -> None:
    unset = paths.resolve({"root": str(tmp_path)}, env={})
    keys = ("aws_read_profile", "aws_deploy_profile", "aws_region")
    assert [unset.text(key) for key in keys] == ["", "", ""]
    env = {"IDEA_REALIZATION_AWS_READ_PROFILE": "hack-read",
           "IDEA_REALIZATION_AWS_DEPLOY_PROFILE": "hack-deploy",
           "IDEA_REALIZATION_AWS_REGION": "us-east-1"}
    named = paths.resolve({"root": str(tmp_path)}, env=env)
    assert [named.text(key) for key in keys] == ["hack-read", "hack-deploy", "us-east-1"]


def test_cli_verify_reports_a_match(repos: tuple[Path, Path], capsys: Any) -> None:
    control, checkout = repos
    code = product.main(["verify", "--root", str(control), "--product-root", str(checkout)])
    assert code == 0
    assert "origin: matches" in capsys.readouterr().out


def test_github_is_optional_and_printed(repos: tuple[Path, Path], capsys: Any) -> None:
    control, checkout = repos
    assert product.load(config(control, checkout)).github == ""
    record = control / product.RECORD
    record.write_text(record.read_text() + "github: team/hack-product\n")
    assert product.load(config(control, checkout)).github == "team/hack-product"
    assert product.main(["show", "--root", str(control), "--product-root", str(checkout)]) == 0
    assert "github: team/hack-product" in capsys.readouterr().out


@pytest.mark.parametrize("value", ["team", "a/b/c", "https://forge.example.com/team/x"])
def test_a_malformed_github_is_refused(repos: tuple[Path, Path], value: str) -> None:
    control, checkout = repos
    record = control / product.RECORD
    record.write_text(record.read_text() + f"github: {value}\n")
    with pytest.raises(product.ProductError, match="github"):
        product.load(config(control, checkout))


def test_this_repositorys_product_record_integrates_on_dev() -> None:
    from conftest import PLUGIN_ROOT

    record = product.read_record(PLUGIN_ROOT.parent.parent)
    assert record is not None
    assert record["integration_branch"] == "dev"
    assert record["ci_workflow"] == "product-ci.yml"
    # The URL and GitHub name can name a confidential organization: local.yaml holds them.
    assert "remote" not in record and "github" not in record


def evidence_errors(root: Path, product_root: Path | None, evidence: str,
                    note: Any = None, **changes: str) -> list[str]:
    catalog = {"schema_version": 1, "updated": TODAY.isoformat(), "items": [phase(
        status="complete", session="doc-session", completion_evidence=[evidence],
        result="Checks passed", deliverables=["product:src/api.py"], **changes)]}
    documents = {"doc-plan": {"kind": "plan", "status": "approved"},
                 "doc-decisions": {"kind": "governance", "status": "active"},
                 "doc-session": {"kind": "session", "status": "active"}}
    (root / "backlog").mkdir(exist_ok=True)
    (root / "backlog/backlog.yaml").write_text(json.dumps(catalog))
    return feature.inspect(root, catalog, documents, {"sys-demo"}, {"repository-owner"}, TODAY,
                           product_root, note=note)


def test_product_evidence_is_checked_in_the_product_checkout(repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    errors = evidence_errors(control, checkout, "product:src/api.py")
    assert any("missing completion evidence product:src/api.py" in e for e in errors)
    (checkout / "src").mkdir()
    (checkout / "src/api.py").write_text("print('ok')\n")
    assert evidence_errors(control, checkout, "product:src/api.py") == []


def commit_all(checkout: Path, message: str) -> str:
    git(checkout, "add", "-A")
    git(checkout, "-c", "user.email=a@example.com", "-c", "user.name=a", "commit", "-qm", message)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=checkout, check=True,
                          capture_output=True, text=True).stdout.strip()


def test_product_evidence_of_a_merged_phase_is_read_at_its_product_merge(
        repos: tuple[Path, Path]) -> None:
    """A checkout whose working tree is behind the phase's merge does not report the phase's
    evidence missing (workflow-sim M4): the evidence is read at ``product_merge``."""
    control, checkout = repos
    (checkout / "README.md").write_text("base\n")
    commit_all(checkout, "base")
    git(checkout, "checkout", "-q", "-b", f"agent/{phase()['id']}")
    (checkout / "src").mkdir()
    (checkout / "src/api.py").write_text("print('ok')\n")
    merge = commit_all(checkout, "phase work")
    git(checkout, "checkout", "-q", "main")  # the working tree no longer has src/api.py
    assert not (checkout / "src/api.py").exists()
    assert evidence_errors(control, checkout, "product:src/api.py", product_merge=merge) == []


def test_product_evidence_absent_at_the_product_merge_is_missing(
        repos: tuple[Path, Path]) -> None:
    """A file in the working tree does not stand in for evidence the merged commit lacks."""
    control, checkout = repos
    (checkout / "README.md").write_text("base\n")
    merge = commit_all(checkout, "base")
    (checkout / "src").mkdir()
    (checkout / "src/api.py").write_text("print('ok')\n")  # present, but never committed
    errors = evidence_errors(control, checkout, "product:src/api.py", product_merge=merge)
    assert any("missing completion evidence product:src/api.py" in e for e in errors), errors
    with_directory = commit_all(checkout, "src/api.py committed")  # src is a directory here
    errors = evidence_errors(control, checkout, "product:src", product_merge=with_directory)
    assert any("missing completion evidence product:src" in e for e in errors), errors
    (checkout / "link.py").symlink_to("README.md")
    linked = commit_all(checkout, "a symlink")
    errors = evidence_errors(control, checkout, "product:link.py", product_merge=linked)
    assert any("missing completion evidence product:link.py" in e for e in errors), errors


def test_product_evidence_at_an_unfetched_merge_cannot_be_told(repos: tuple[Path, Path]) -> None:
    """A product_merge this checkout has not fetched is a note to fetch, never a missing-evidence
    error."""
    control, checkout = repos
    (checkout / "README.md").write_text("base\n")
    commit_all(checkout, "base")
    notes: list[str] = []
    errors = evidence_errors(control, checkout, "product:src/api.py", note=notes.append,
                             product_merge="d" * 40)
    assert errors == []
    assert len(notes) == 1 and "cannot tell" in notes[0] and "fetch" in notes[0], notes


def test_product_evidence_is_taken_as_given_without_a_checkout(repos: tuple[Path, Path]) -> None:
    control, _ = repos
    assert evidence_errors(control, None, "product:src/api.py") == []
    escaped = evidence_errors(control, None, "product:../outside.py")
    assert any("expected repository-relative path" in e for e in escaped)


def test_a_refused_checkout_fails_the_backlog_check(repos: tuple[Path, Path]) -> None:
    """A product_root whose origin is another repository never makes product paths pass."""
    control, checkout = repos
    git(checkout, "remote", "set-url", "origin", "git@forge.example.com:team/other.git")
    (control / "backlog").mkdir()
    (control / "backlog/backlog.yaml").write_text(json.dumps(
        {"schema_version": 1, "updated": TODAY.isoformat(), "items": []}))
    (control / "docs").mkdir()
    (control / "docs/codes.yaml").write_text("schema_version: 1\nseries: []\n")
    (control / "docs/systems.yaml").write_text(
        "schema_version: 1\nowners:\n  repository-owner: Owner.\nsystems: []\n")
    errors = feature.audit(config(control, checkout))
    assert any("product checkout refused" in error for error in errors)
    assert product.verified_root(config(control, checkout))[0] is None


def test_resolve_never_returns_a_path_in_a_refused_checkout(repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    assert product.resolve(config(control, checkout), "product:src/a.py")[1] == checkout.resolve(
    ) / "src/a.py"
    git(checkout, "remote", "set-url", "origin", "git@forge.example.com:team/other.git")
    assert product.resolve(config(control, checkout), "product:src/a.py") == ("product", None)


def untracked(control: Path) -> None:
    """Drop the URL from the tracked record, as a team with a confidential URL does."""
    (control / product.RECORD).write_text(
        "schema_version: 1\nname: hack-product\nintegration_branch: main\n")


def test_verify_reads_the_remote_from_local_yaml(repos: tuple[Path, Path], capsys: Any) -> None:
    control, checkout = repos
    untracked(control)
    (control / ".idea-realization" / "local.yaml").write_text(
        f"product_root: {checkout}\nproduct_remote: {REMOTE}\nproduct_github: team/hack-product\n")
    found = product.verify(config(control))
    assert (found.remote, found.github) == (REMOTE, "team/hack-product")
    assert product.main(["verify", "--root", str(control)]) == 0
    out = capsys.readouterr().out
    assert f"remote: {REMOTE}  (from local.yaml)" in out and "origin: matches" in out


def test_local_yaml_overrides_the_tracked_remote(repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    (control / ".idea-realization" / "local.yaml").write_text(
        "product_remote: git@forge.example.com:team/other.git\n")
    with pytest.raises(product.ProductError, match=r"product_remote \(from local.yaml\)"):
        product.verify(config(control, checkout))


def test_verify_refuses_without_a_product_remote_and_names_local_yaml(
        repos: tuple[Path, Path], capsys: Any) -> None:
    control, checkout = repos
    untracked(control)
    with pytest.raises(product.ProductError, match="local.yaml"):
        product.verify(config(control, checkout))
    assert product.main(["verify", "--root", str(control), "--product-root", str(checkout)]) == 1
    assert "product_remote is not set" in capsys.readouterr().err
    assert product.main(["show", "--root", str(control), "--product-root", str(checkout)]) == 0
    assert "remote: (not set: product_remote in .idea-realization/local.yaml)" in (
        capsys.readouterr().out)
    assert product.verified_root(config(control, checkout))[1] is not None


def test_a_placeholder_product_remote_is_refused_like_an_unset_one(
        repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    record = control / product.RECORD
    record.write_text(record.read_text().replace(REMOTE, "REPLACE-WITH-THE-PRODUCT-GIT-URL"))
    with pytest.raises(product.ProductError, match="product_remote is not set"):
        product.verify(config(control, checkout))


class FakeGh:
    """A stand-in for ``gh`` that exits with ``code`` and records each command it is asked."""

    def __init__(self, code: int, stderr: str = "") -> None:
        self.code, self.stderr, self.calls = code, stderr, list[list[str]]()

    def __call__(self, command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        self.calls.append(command)
        return subprocess.CompletedProcess(command, self.code, "", self.stderr)


@pytest.mark.parametrize("url", [REMOTE, "https://github.com/example-owner/control.git",
                                 "ssh://git@github.com/example-owner/control.git",
                                 "git@github-work:example-owner/control.git"])
def test_a_hosted_origin_is_never_routed_to_a_local_merge_when_gh_fails(
        tmp_path: Path, url: str) -> None:
    """The fallback a failing gh used to select: session-close merged onto the integration branch
    locally and pushed. A hosted origin must stop instead, an SSH host alias included."""
    git(tmp_path, "init", "-q")
    git(tmp_path, "remote", "add", "origin", url)
    gh = FakeGh(1, "HTTP 401: Bad credentials\n")
    with pytest.raises(product.ProductError, match="never merged locally"):
        product.merge_route(tmp_path, gh)
    assert gh.calls == [["gh", "repo", "view", "--json", "nameWithOwner"]]


def test_a_hosted_origin_that_gh_reaches_takes_the_pull_request(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    git(tmp_path, "remote", "add", "origin", REMOTE)
    assert product.merge_route(tmp_path, FakeGh(0)) == "pull-request"


@pytest.mark.parametrize("url", ["/srv/git/control.git", "../control.git",
                                 "file:///srv/control.git", "C:/repos/control.git", None])
def test_a_local_origin_or_none_takes_the_local_merge_without_asking_gh(
        tmp_path: Path, url: str | None) -> None:
    git(tmp_path, "init", "-q")
    if url is not None:
        git(tmp_path, "remote", "add", "origin", url)
    gh = FakeGh(1)
    assert product.merge_route(tmp_path, gh) == "local"
    assert gh.calls == []


def test_cli_merge_route_exits_1_and_names_the_stop(tmp_path: Path, capsys: Any) -> None:
    git(tmp_path, "init", "-q")
    git(tmp_path, "remote", "add", "origin", REMOTE)
    code = product.main(["merge-route", "--checkout", str(tmp_path), "--root", str(tmp_path)])
    out = capsys.readouterr()
    # gh is either absent or cannot reach a made-up host; both must stop, never print "local".
    assert code == 1 and "local" not in out.out and "never merged locally" in out.err
