"""The git email names the developer; a stated handle can confirm it but never replace it."""

from __future__ import annotations

from pathlib import Path

import identity
import paths
import pytest
import yaml
from conftest import as_developer


@pytest.fixture
def config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> paths.Config:
    monkeypatch.delenv(identity.HANDLE_ENV, raising=False)
    team = {"repository-owner": "Owner.",
            "ana": {"description": "Ana.", "emails": ["ana@example.com"]},
            "ben": {"description": "Ben.", "emails": ["ben@example.com", "ben@work.example.com"]}}
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "systems.yaml").write_text(yaml.safe_dump({"owners": team}))
    return paths.resolve({"root": str(tmp_path)}, env={})


def test_the_git_email_names_the_developer(config: paths.Config,
                                           monkeypatch: pytest.MonkeyPatch) -> None:
    as_developer(monkeypatch, "ben", "Ben@Work.example.com")
    monkeypatch.delenv(identity.HANDLE_ENV)
    assert identity.handle(config) == "ben"


def test_a_stated_handle_that_matches_the_email_is_accepted(
        config: paths.Config, monkeypatch: pytest.MonkeyPatch) -> None:
    as_developer(monkeypatch, "ana")
    assert identity.handle(config) == "ana"


def test_a_stated_handle_cannot_assume_another_developers_identity(
        config: paths.Config, monkeypatch: pytest.MonkeyPatch) -> None:
    as_developer(monkeypatch, "ana", "ben@example.com")
    with pytest.raises(identity.IdentityError, match="belongs to 'ben'"):
        identity.handle(config)


def test_a_stranger_cannot_claim_a_handle(config: paths.Config,
                                          monkeypatch: pytest.MonkeyPatch) -> None:
    as_developer(monkeypatch, "ana", "mallory@example.com")
    with pytest.raises(identity.IdentityError, match="no developer"):
        identity.handle(config)


def test_no_git_email_resolves_no_handle(config: paths.Config,
                                         monkeypatch: pytest.MonkeyPatch) -> None:
    as_developer(monkeypatch, "ana", "")
    with pytest.raises(identity.IdentityError, match="not set"):
        identity.handle(config)


def test_an_unregistered_stated_handle_is_refused(config: paths.Config,
                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    as_developer(monkeypatch, "zed")
    with pytest.raises(identity.IdentityError, match="not a developer"):
        identity.handle(config)
