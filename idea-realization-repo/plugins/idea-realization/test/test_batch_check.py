"""The batch check (docs/batches.md section 3) and the owner-claim warning.

Phase ids are built at run time so this file carries none for the source-reference check to flag.
"""

from __future__ import annotations

from typing import Any

import batch_check
import pytest
import yaml
from test_backlog import PH, TargetRepo, phase

from backlog import owner_claim_warnings

A, B, C = (f"{PH}-demo-0{n}" for n in (1, 2, 3))


def items(*phases: dict[str, Any]) -> dict[str, Any]:
    return {item["id"]: item for item in phases}


def disjoint() -> dict[str, Any]:
    """Three queued phases: A alone; B depends on A; C shares nothing with either."""
    return items(
        phase(id=A, systems=["sys-a"], deliverables=["src/a/"]),
        phase(id=B, systems=["sys-b"], deliverables=["src/b/"], depends_on=[A]),
        phase(id=C, systems=["sys-c"], deliverables=["src/c/"]),
    )


def batch(*stages: list[str], **changes: Any) -> dict[str, Any]:
    return {"id": "batch-demo", "title": "Demo", "status": "proposed",
            "stages": [{"phases": stage} for stage in stages], **changes}


def test_a_good_batch_passes_the_composition_check() -> None:
    assert batch_check.batch_problems(batch([A, C], [B]), disjoint(), composition=True) == []


def test_a_batch_that_is_not_dependency_closed_is_rejected() -> None:
    # B needs A, but A is neither in the batch nor complete.
    found = batch_check.batch_problems(batch([B, C]), disjoint(), composition=True)
    assert any(f"not dependency-closed: {B} depends on {A}" in line for line in found), found


def test_a_prerequisite_in_the_same_or_a_later_stage_is_rejected() -> None:
    for shape in (batch([A, B, C]), batch([B], [A, C])):
        found = batch_check.batch_problems(shape, disjoint())
        assert any(f"not dependency-closed: {B}" in line and f"depends on {A}" in line
                   for line in found), found


def test_two_colliding_phases_in_one_stage_are_rejected() -> None:
    phases = disjoint()
    phases[C]["deliverables"] = ["src/a/inner.py"]  # inside A's declared directory
    found = batch_check.batch_problems(batch([A, C], [B]), phases, composition=True)
    assert f"batch-demo: stage 1: {A}/{C} share deliverable path src/a/inner.py" in found
    phases[C].update(deliverables=["src/c/"], systems=["sys-a"])
    found = batch_check.batch_problems(batch([A, C], [B]), phases, composition=True)
    assert f"batch-demo: stage 1: {A}/{C} share system sys-a" in found


def test_a_complete_external_prerequisite_must_be_listed() -> None:
    phases = disjoint()
    phases[A]["status"] = "complete"
    found = batch_check.batch_problems(batch([B, C]), phases)
    assert any("external_dependencies does not list" in line for line in found), found
    assert batch_check.batch_problems(batch([B, C], external_dependencies=[A]), phases) == []
    extra = batch_check.batch_problems(batch([C], external_dependencies=[A]), phases)
    assert any("which no phase in the batch depends on" in line for line in extra), extra


def test_a_stage_boundary_needs_a_dependency_or_a_collision() -> None:
    found = batch_check.batch_problems(batch([A], [C]), disjoint())
    assert any("boundary between stages 1 and 2" in line for line in found), found
    phases = disjoint()
    phases[C]["systems"] = ["sys-a"]  # a collision justifies the boundary
    assert batch_check.batch_problems(batch([A], [C]), phases) == []


def test_the_composition_check_needs_queued_unclaimed_phases_and_known_ids() -> None:
    phases = disjoint()
    phases[A].update(status="active", agent="ana/agent-one")
    found = batch_check.batch_problems(batch([A, C], [B, f"{PH}-demo-77"]), phases,
                                       composition=True)
    assert f"batch-demo: {A} is active, not queued" in found
    assert f"batch-demo: {A} is claimed by ana/agent-one" in found
    assert f"batch-demo: {PH}-demo-77 does not resolve in the backlog" in found
    # The structural rules alone accept a running batch whose first stage is under way.
    assert batch_check.batch_problems(batch([A, C], [B]), phases) == []


def test_finished_batches_are_history_and_successors_must_resolve() -> None:
    registry = {"schema_version": 1, "batches": [
        batch([B, C], id="batch-old", status="superseded", superseded_by="batch-gone"),
    ]}
    assert batch_check.file_problems(registry, disjoint()) == [
        "batch-old: superseded_by names unknown batch batch-gone"]


# --- The real script and check.py on a fixture repository ----------------------------------------


def target_with(tmp_path: Any, registry: dict[str, Any]) -> TargetRepo:
    target = TargetRepo(tmp_path / "target")
    target.catalog["items"] = [
        phase(id=key, plan="doc-plan", sources=[], systems=["sys-core" if key == A else
                                                            "sys-other"],
              deliverables=[f"src/{key}/"], depends_on=deps)
        for key, deps in ((A, []), (B, [A]))
    ]
    target.write()
    (target.root / "backlog" / "batches.yaml").write_text(yaml.safe_dump(registry))
    return target


def test_the_script_accepts_a_good_batch_and_rejects_a_bad_one(tmp_path: Any) -> None:
    good = target_with(tmp_path / "good", {"schema_version": 1,
                                           "batches": [batch([A], [B])]})
    result = good.run("batch_check.py", "batch-demo")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK (composition): batch-demo" in result.stdout
    assert good.run("check.py", "--feature", "batches").returncode == 0

    bad = target_with(tmp_path / "bad", {"schema_version": 1, "batches": [batch([B])]})
    result = bad.run("batch_check.py", "batch-demo")
    assert result.returncode == 1
    assert f"not dependency-closed: {B} depends on {A}" in result.stdout
    checked = bad.run("check.py", "--feature", "batches")
    assert checked.returncode == 1 and "batches: batch-demo: not dependency-closed" in \
        checked.stdout


def test_the_script_refuses_an_invalid_file_and_an_unknown_batch(tmp_path: Any) -> None:
    target = target_with(tmp_path, {"schema_version": 1, "batches": [{"id": "batch-x"}]})
    result = target.run("batch_check.py")
    assert result.returncode == 2 and "'title' is a required property" in result.stderr
    (target.root / "backlog" / "batches.yaml").write_text("schema_version: 1\nbatches: []\n")
    assert target.run("batch_check.py", "batch-missing").returncode == 2
    assert target.run("batch_check.py").returncode == 0


def test_no_batches_file_has_nothing_to_check(tmp_path: Any) -> None:
    target = TargetRepo(tmp_path / "target")
    result = target.check()
    assert result.returncode == 0
    assert target.run("check.py", "--feature", "batches").stdout.strip() == "batches: OK"


# --- The owner-claim warning ---------------------------------------------------------------------


@pytest.mark.parametrize(("agent", "warned"), [
    ("ana/agent-one", False),
    ("ben/agent-two", True),
    ("agent-three", True),
])
def test_owner_claim_warning_names_a_claim_by_someone_else(agent: str, warned: bool) -> None:
    phases = items(phase(id=A, owner="ana", status="active", agent=agent))
    found = owner_claim_warnings(phases, {"ana", "ben"})
    assert bool(found) is warned, found
    if warned:
        assert found[0].startswith(f"warning: {A} is assigned to ana but claimed by")


def test_owner_claim_warning_ignores_role_owners_and_unclaimed_phases() -> None:
    phases = items(phase(id=A, owner="repository-owner", status="active", agent="ben/agent-x"),
                   phase(id=B, owner="ana"))
    assert owner_claim_warnings(phases, {"ana", "ben"}) == []


def test_the_owner_warning_surfaces_and_never_fails_the_check(tmp_path: Any) -> None:
    target = TargetRepo(tmp_path / "target")
    systems = target.root / "docs" / "systems.yaml"
    registry = yaml.safe_load(systems.read_text())
    registry["owners"]["ana"] = {"description": "Ana.", "emails": ["ana@example.com"]}
    systems.write_text(yaml.safe_dump(registry))
    target.catalog["items"][0].update(owner="ana", status="active", agent="ben/agent-one")
    result = target.check()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "backlog: OK" in result.stdout
    assert f"backlog: warning: {A} is assigned to ana but claimed by developer ben " \
           "(ben/agent-one)" in result.stderr
