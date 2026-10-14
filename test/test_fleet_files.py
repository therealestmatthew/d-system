"""Schema, integrity and enum-agreement tests for the tracked fleet files (`phase-rep-01`,
`REQ-039` R01, R02, R04, R05, R13; `PLAN-054` D1-D3).

The fleet files under `docs/08-governance/fleet/` describe agent definitions, fleet-level roles
and orchestration systems. JSON Schema checks their shape. It cannot check that a role names a
definition that exists, that an edge joins two declared roles, or that a document a file cites is
on disk, so `reference_errors` checks those against the parsed files, both for the tracked fleet
and for the fixtures under `test/fixtures/fleet/`. Each `broken/<case>/` fixture breaks one kind of
reference.

The model document is found through `fleet.yaml`'s `model_document`, and every value list in
`schemas/fleet.schema.json` whose `$comment` names a section is compared with the first table under
that heading in the document. Nothing here names a particular session, role, system or document: the
files supply all of it.
"""

from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft7Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FLEET_DIR = ROOT / "docs" / "08-governance" / "fleet"
FIXTURES = ROOT / "test" / "fixtures" / "fleet"
VALID = FIXTURES / "valid"

SCHEMA_FOR = {
    "fleet.yaml": "fleet",
    "definitions.yaml": "fleet-definition",
    "systems": "fleet-system",
}
SECTION = re.compile(r"^section: (.+)$")


# --- loading -----------------------------------------------------------------------------


def _schema(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    return data


def _registry() -> Registry[Any]:
    return Registry().with_resources(
        (path.name, Resource.from_contents(json.loads(path.read_text(encoding="utf-8"))))
        for path in SCHEMAS.glob("fleet*.schema.json")
    )


def _validator(name: str) -> Draft7Validator:
    return Draft7Validator(_schema(name), registry=_registry())


def _yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_fleet(fleet_dir: Path) -> dict[str, Any]:
    """The fleet as parsed data: fleet.yaml, definitions.yaml and every system file by stem."""
    systems_dir = fleet_dir / "systems"
    return {
        "fleet": _yaml(fleet_dir / "fleet.yaml"),
        "definitions": _yaml(fleet_dir / "definitions.yaml"),
        "systems": {
            path.stem: _yaml(path) for path in sorted(systems_dir.glob("*.yaml"))
        }
        if systems_dir.is_dir()
        else {},
    }


def schema_errors(fleet_dir: Path) -> list[str]:
    """Every schema error in a fleet directory, prefixed with the file it came from."""
    loaded = load_fleet(fleet_dir)
    found = [
        f"fleet.yaml: {error.message}"
        for error in _validator(SCHEMA_FOR["fleet.yaml"]).iter_errors(loaded["fleet"])
    ]
    found += [
        f"definitions.yaml: {error.message}"
        for error in _validator(SCHEMA_FOR["definitions.yaml"]).iter_errors(loaded["definitions"])
    ]
    for stem, system in loaded["systems"].items():
        found += [
            f"systems/{stem}.yaml: {error.message}"
            for error in _validator(SCHEMA_FOR["systems"]).iter_errors(system)
        ]
    return found


# --- references ----------------------------------------------------------------------------


def _duplicates(ids: list[str]) -> list[str]:
    return sorted(key for key, count in Counter(ids).items() if count > 1)


def _headings(path: Path) -> set[str]:
    return {
        line.lstrip("#").strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("#")
    }


def reference_errors(fleet_dir: Path, repo_root: Path = ROOT) -> list[str]:
    """Every reference in a fleet directory that does not resolve (REQ-039 R04)."""
    loaded = load_fleet(fleet_dir)
    fleet, definitions, systems = loaded["fleet"], loaded["definitions"], loaded["systems"]
    errors: list[str] = []

    def exists(label: str, relative: str) -> None:
        if not (repo_root / relative).is_file():
            errors.append(f"{label}: {relative} does not exist")

    definition_ids = [item["id"] for item in definitions["definitions"]]
    errors += [f"definitions.yaml: duplicate id {key}" for key in _duplicates(definition_ids)]
    for item in definitions["definitions"]:
        for field in ("agent_file", "prompt_file"):
            if field in item:
                exists(f"definitions.yaml {item['id']} {field}", item[field])

    exists("fleet.yaml model_document", fleet["model_document"])
    fleet_role_ids = [role["id"] for role in fleet["fleet_roles"]]
    errors += [f"fleet.yaml: duplicate fleet role {key}" for key in _duplicates(fleet_role_ids)]
    for role in fleet["fleet_roles"]:
        if role["definition"] not in definition_ids:
            errors.append(
                f"fleet.yaml fleet role {role['id']}: unknown definition {role['definition']}"
            )
    for system_id in fleet["enabled_systems"]:
        if system_id not in systems:
            errors.append(f"fleet.yaml: enabled system {system_id} has no systems/{system_id}.yaml")

    for stem, system in systems.items():
        label = f"systems/{stem}.yaml"
        if system["id"] != stem:
            errors.append(f"{label}: id {system['id']} does not match the file name")
        role_ids = [role["id"] for role in system["roles"]]
        errors += [f"{label}: duplicate role {key}" for key in _duplicates(role_ids)]
        for role in system["roles"]:
            if "definition" in role and role["definition"] not in definition_ids:
                errors.append(f"{label} role {role['id']}: unknown definition {role['definition']}")
            if "fleet_role" in role and role["fleet_role"] not in fleet_role_ids:
                errors.append(f"{label} role {role['id']}: unknown fleet role {role['fleet_role']}")
        for edge in system["edges"]:
            for end in ("from", "to"):
                if edge[end] not in role_ids:
                    errors.append(f"{label} edge {edge['type']}: unknown role {edge[end]}")
        resource_ids = [resource["id"] for resource in system["resources"]]
        errors += [f"{label}: duplicate resource {key}" for key in _duplicates(resource_ids)]
        for resource in system["resources"]:
            if resource["granted_by"] not in role_ids:
                errors.append(
                    f"{label} resource {resource['id']}: unknown granter {resource['granted_by']}"
                )
        for message in system["messages"]:
            for sender in message["from_roles"]:
                if sender not in role_ids:
                    errors.append(f"{label} message {message['type']}: unknown role {sender}")
        for hook in ("wind_down_role", "kickoff_role"):
            if hook in system["hooks"] and system["hooks"][hook] not in role_ids:
                errors.append(f"{label} hook {hook}: unknown role {system['hooks'][hook]}")
        for document in system["governing_documents"]:
            exists(f"{label} governing document", document)
        roster = system.get("roster")
        if roster:
            if roster["document"] not in system["governing_documents"]:
                errors.append(f"{label} roster: {roster['document']} is not a governing document")
            if (repo_root / roster["document"]).is_file():
                if roster["section"] not in _headings(repo_root / roster["document"]):
                    errors.append(f"{label} roster: no section {roster['section']}")
            else:
                errors.append(f"{label} roster: {roster['document']} does not exist")
    return errors


def _with_case(tmp_path: Path, case: Path) -> Path:
    """A copy of the valid fixture fleet with one broken case's files laid over it."""
    target = tmp_path / "fleet"
    shutil.copytree(VALID, target)
    for path in case.rglob("*"):
        if path.is_file():
            destination = target / path.relative_to(case)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
    return target


# --- enum agreement --------------------------------------------------------------------------


def schema_value_lists(schema: dict[str, Any]) -> dict[str, list[str]]:
    """Section heading -> enum values, for every definition whose $comment names a section."""
    lists: dict[str, list[str]] = {}
    for definition in schema["definitions"].values():
        match = SECTION.match(definition.get("$comment", ""))
        if match:
            lists[match.group(1)] = list(definition["enum"])
    return lists


def document_value_lists(text: str, sections: list[str]) -> dict[str, list[str]]:
    """Section heading -> the backticked first-column values of the first table under it."""
    lists: dict[str, list[str]] = {}
    lines = text.splitlines()
    for section in sections:
        heading = next(
            (i for i, line in enumerate(lines) if line.lstrip("#").strip() == section
             and line.startswith("#")),
            None,
        )
        if heading is None:
            continue
        values: list[str] = []
        in_table = False
        for line in lines[heading + 1:]:
            if line.startswith("#"):
                break
            if line.startswith("|"):
                in_table = True
                cell = line.split("|")[1].strip()
                if cell.startswith("`") and cell.endswith("`"):
                    values.append(cell.strip("`"))
            elif in_table:
                break
        lists[section] = values
    return lists


def enum_disagreements(document: str, schema_lists: dict[str, list[str]]) -> list[str]:
    """Values a schema list has and its document section lacks, or the other way round."""
    found: list[str] = []
    document_lists = document_value_lists(document, list(schema_lists))
    for section, values in schema_lists.items():
        if section not in document_lists:
            found.append(f"{section}: no such section in the model document")
            continue
        documented = document_lists[section]
        found += [f"{section}: {value} is in the schema only" for value in values
                  if value not in documented]
        found += [f"{section}: {value} is in the document only" for value in documented
                  if value not in values]
    return found


def _tracked_model_document() -> str:
    path = ROOT / load_fleet(FLEET_DIR)["fleet"]["model_document"]
    return path.read_text(encoding="utf-8")


# --- the schemas themselves ---------------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(set(SCHEMA_FOR.values())))
def test_fleet_schema_is_a_valid_draft7_schema(name: str) -> None:
    Draft7Validator.check_schema(_schema(name))


def test_every_value_list_names_its_model_document_section() -> None:
    schema = _schema(SCHEMA_FOR["fleet.yaml"])
    unnamed = [
        key for key, definition in schema["definitions"].items()
        if "enum" in definition and not SECTION.match(definition.get("$comment", ""))
    ]
    assert unnamed == []


# --- the tracked fleet ---------------------------------------------------------------------------


def test_tracked_fleet_files_pass_their_schemas() -> None:
    assert schema_errors(FLEET_DIR) == []


def test_tracked_fleet_references_resolve() -> None:
    assert reference_errors(FLEET_DIR) == []


def test_tracked_schema_value_lists_agree_with_the_model_document() -> None:
    lists = schema_value_lists(_schema(SCHEMA_FOR["fleet.yaml"]))
    assert lists, "no value list names a model document section"
    assert enum_disagreements(_tracked_model_document(), lists) == []


def _names_the_fleet_supplies(loaded: dict[str, Any]) -> set[str]:
    """Every session name, role, system, definition and document code the fleet files supply."""
    names: set[str] = {item["id"] for item in loaded["definitions"]["definitions"]}
    documents = [loaded["fleet"]["model_document"]]
    for role in loaded["fleet"]["fleet_roles"]:
        names |= {role["id"], *role["session_names"]}
    for system in loaded["systems"].values():
        names.add(system["id"])
        documents += system["governing_documents"]
        for role in system["roles"]:
            names |= {role["id"], *role.get("session_names", [])}
    for document in documents:
        code = re.match(r"[A-Z]+-[0-9]+", Path(document).name)
        if code:
            names.add(code.group(0))
    return names


def test_this_test_names_nothing_the_fleet_files_supply() -> None:
    """REQ-039 R06 for this file: the fleet files supply every name, so none is written here."""
    source = Path(__file__).read_text(encoding="utf-8")
    names = _names_the_fleet_supplies(load_fleet(FLEET_DIR))
    assert names, "the tracked fleet supplies no names"
    assert sorted(name for name in names if name in source) == []


def test_fleet_level_roles_are_owner_only() -> None:
    fleet = load_fleet(FLEET_DIR)["fleet"]
    assert {role["lifecycle"] for role in fleet["fleet_roles"]} <= {"owner-only"}


# --- fixtures -----------------------------------------------------------------------------------


def test_valid_fixture_fleet_passes() -> None:
    assert schema_errors(VALID) == []
    assert reference_errors(VALID) == []


BROKEN = sorted(path for path in (FIXTURES / "broken").iterdir() if path.is_dir())

# What each broken case's single error must say, so a case cannot pass by breaking something else.
EXPECTED = {
    "agent-file-missing": "agent_file: .claude/agents/no-such-agent.md does not exist",
    "duplicate-definition": "duplicate id fx-planned",
    "duplicate-fleet-role": "duplicate fleet role fx-owner",
    "duplicate-role": "duplicate role helper",
    "edge-unknown-role": "unknown role nobody",
    "enabled-system-without-file": "enabled system absent has no systems/absent.yaml",
    "fleet-role-unknown-definition": "unknown definition no-such-definition",
    "governing-document-missing": "no-such-doc.md does not exist",
    "hook-unknown-role": "hook kickoff_role: unknown role nobody",
    "message-unknown-role": "message PING: unknown role nobody",
    "model-document-missing": "model_document: test/fixtures/fleet/valid/no-such-model.md",
    "prompt-file-missing": "prompt_file: test/fixtures/fleet/valid/no-such-prompt.md",
    "resource-granter-unknown-role": "unknown granter nobody",
    "role-unknown-definition": "role lead: unknown definition no-such-definition",
    "role-unknown-fleet-role": "unknown fleet role no-such-fleet-role",
    "roster-section-missing": "no section No Such Section",
    "system-id-not-filename": "id other does not match the file name",
}


def test_every_broken_case_has_an_expected_error() -> None:
    assert sorted(EXPECTED) == [path.name for path in BROKEN]


@pytest.mark.parametrize("case", BROKEN, ids=[path.name for path in BROKEN])
def test_each_broken_reference_fixture_is_reported(case: Path, tmp_path: Path) -> None:
    fleet_dir = _with_case(tmp_path, case)
    assert schema_errors(fleet_dir) == [], "a broken-reference fixture must still pass its schema"
    errors = reference_errors(fleet_dir)
    assert len(errors) == 1, errors
    assert EXPECTED[case.name] in errors[0]


INVALID = sorted((FIXTURES / "invalid").glob("*.yaml"))


def _schema_for_fixture(path: Path) -> str:
    prefix = path.name.split("-", 1)[0]
    return {"fleet": "fleet", "definitions": "fleet-definition", "system": "fleet-system"}[prefix]


@pytest.mark.parametrize("path", INVALID, ids=[path.stem for path in INVALID])
def test_each_invalid_fixture_fails_its_schema(path: Path) -> None:
    errors = list(_validator(_schema_for_fixture(path)).iter_errors(_yaml(path)))
    assert errors, f"{path.name} passed its schema"


def test_enum_agreement_fails_on_a_fixture_list_with_an_extra_edge_type() -> None:
    lists = schema_value_lists(_schema(SCHEMA_FOR["fleet.yaml"]))
    section = next(name for name, values in lists.items() if "holds" in values)
    lists[section] = json.loads((FIXTURES / "enum-extra-edge-type.json").read_text("utf-8"))
    disagreements = enum_disagreements(_tracked_model_document(), lists)
    assert disagreements == [f"{section}: supervises is in the schema only"]


def test_enum_agreement_fails_when_the_document_has_a_value_the_schema_lacks() -> None:
    lists = schema_value_lists(_schema(SCHEMA_FOR["fleet.yaml"]))
    section, values = next(iter(lists.items()))
    lists[section] = values[1:]
    disagreements = enum_disagreements(_tracked_model_document(), lists)
    assert disagreements == [f"{section}: {values[0]} is in the document only"]
