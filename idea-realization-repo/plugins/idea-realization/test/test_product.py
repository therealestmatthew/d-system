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
    with pytest.raises(product.ProductError, match="remote"):
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


def evidence_errors(root: Path, product_root: Path | None, evidence: str) -> list[str]:
    catalog = {"schema_version": 1, "updated": TODAY.isoformat(), "items": [phase(
        status="complete", session="doc-session", completion_evidence=[evidence],
        result="Checks passed", deliverables=["product:src/api.py"])]}
    documents = {"doc-plan": {"kind": "plan", "status": "approved"},
                 "doc-decisions": {"kind": "governance", "status": "active"},
                 "doc-session": {"kind": "session", "status": "active"}}
    (root / "backlog").mkdir(exist_ok=True)
    (root / "backlog/backlog.yaml").write_text(json.dumps(catalog))
    return feature.inspect(root, catalog, documents, {"sys-demo"}, {"repository-owner"}, TODAY,
                           product_root)


def test_product_evidence_is_checked_in_the_product_checkout(repos: tuple[Path, Path]) -> None:
    control, checkout = repos
    errors = evidence_errors(control, checkout, "product:src/api.py")
    assert any("missing completion evidence product:src/api.py" in e for e in errors)
    (checkout / "src").mkdir()
    (checkout / "src/api.py").write_text("print('ok')\n")
    assert evidence_errors(control, checkout, "product:src/api.py") == []


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
