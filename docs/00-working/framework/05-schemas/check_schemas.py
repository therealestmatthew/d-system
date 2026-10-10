"""Validate the example documents in examples/ against the framework document schemas.

A Markdown document is converted to {front_matter, sections} before validation:
front_matter is the parsed YAML front matter, and sections is the list of level-2 heading
texts in document order, ignoring headings inside fenced code blocks and HTML comments.

Each case in CASES names an example, a schema and whether the example must validate.
The script also checks that each template's headings satisfy its schema's section
requirements, so a template and its schema cannot drift apart unnoticed.

A backlog phase is a YAML item in backlog.yaml, not a Markdown document, so it is checked
separately (REQ-024 R03): the item named by REFERENCE_PHASE is cut out of backlog.yaml as text,
unchanged, and parsed as its own YAML document; it must validate, and copies with a required
field removed must not. Every phase in backlog.yaml must also validate, and the keys in
phase.template.md's YAML block must match the schema. backlog.yaml is only read.

Run from the repository root:

    uv run python docs/00-working/framework/05-schemas/check_schemas.py

Exits 0 when every case matches its expectation, 1 otherwise.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE / "examples"
BACKLOG = HERE.parents[3] / "docs" / "09-backlog" / "backlog.yaml"
REFERENCE_PHASE = "phase-conc-01"

# (example file, schema file, must validate)
CASES: list[tuple[str, str, bool]] = [
    # REQ-024 R01: filled governance example passes; without its incident section it fails.
    ("governance.valid.md", "governance.schema.json", True),
    ("governance.no-incident.md", "governance.schema.json", False),
    # REQ-024 R02: filled protocol example passes; each schema rejects the other's shape,
    # both as labelled and with the kind relabelled, so rejection rests on structure.
    ("protocol.valid.md", "protocol.schema.json", True),
    ("governance.valid.md", "protocol.schema.json", False),
    ("protocol.valid.md", "governance.schema.json", False),
    ("governance-shape-labelled-protocol.md", "protocol.schema.json", False),
    ("protocol-shape-labelled-governance.md", "governance.schema.json", False),
]

# (template file, schema file): the template's headings must satisfy the schema's `sections`.
TEMPLATES: list[tuple[str, str]] = [
    ("governance.template.md", "governance.schema.json"),
    ("protocol.template.md", "protocol.schema.json"),
]

# (field removed from the reference phase, reason the copy must fail)
PHASE_OMISSIONS: list[tuple[str, str]] = [
    ("acceptance", "a required field"),
    ("result", "required once status is complete"),
]

FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _stringify_dates(value: Any) -> Any:
    """YAML reads an unquoted YYYY-MM-DD as a date; JSON Schema expects a string."""
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _stringify_dates(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_stringify_dates(v) for v in value]
    return value


def to_instance(text: str) -> dict[str, Any]:
    """Convert a Markdown document to the {front_matter, sections} shape the schemas validate."""
    match = FRONT_MATTER.match(text)
    front_matter = _stringify_dates(yaml.safe_load(match.group(1))) if match else {}
    body = COMMENT.sub("", text[match.end():] if match else text)

    sections: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## "):
            sections.append(line[3:].strip())
    return {"front_matter": front_matter or {}, "sections": sections}


def describe_errors(schema: dict[str, Any], instance: Any) -> list[str]:
    """Validation messages, naming the heading when a required section is missing."""
    messages: list[str] = []
    for error in Draft202012Validator(schema).iter_errors(instance):
        required = error.schema.get("contains", {}) if isinstance(error.schema, dict) else {}
        if error.validator == "contains" and "const" in required:
            messages.append(f"missing section: {required['const']!r}")
        else:
            messages.append(error.message)
    return messages


def load_schema(name: str) -> dict[str, Any]:
    schema: dict[str, Any] = json.loads((HERE / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def extract_phase(backlog_text: str, phase_id: str) -> str:
    """Cut one item out of backlog.yaml's `items:` list as text and return it as its own YAML
    document: the `- ` that opens the item and the two-space list indent are removed, and no
    other character is changed."""
    lines = backlog_text.splitlines()
    start = lines.index(f"- id: {phase_id}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("- ")), len(lines))
    item = [lines[start][2:]] + [line[2:] if line.startswith("  ") else line
                                 for line in lines[start + 1:end]]
    return "\n".join(item).rstrip() + "\n"


def template_yaml_keys(text: str) -> set[str]:
    """Keys of the first fenced YAML block in a template, which holds a one-item list."""
    match = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
    if not match:
        return set()
    block = yaml.safe_load(match.group(1))
    return set(block[0]) if isinstance(block, list) and block else set()


def check_phases() -> int:
    """REQ-024 R03: phase.schema.json fits phases already in backlog.yaml, unchanged."""
    failures = 0
    schema = load_schema("phase.schema.json")
    backlog_text = BACKLOG.read_text(encoding="utf-8")
    items = yaml.safe_load(backlog_text)["items"]

    def report(ok: bool, label: str, errors: list[str]) -> None:
        nonlocal failures
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
        for message in errors:
            print(f"        {message}")

    extracted = yaml.safe_load(extract_phase(backlog_text, REFERENCE_PHASE))
    in_backlog = next(item for item in items if item["id"] == REFERENCE_PHASE)
    report(extracted == in_backlog,
           f"{REFERENCE_PHASE} cut from backlog.yaml as text equals the parsed backlog item", [])
    errors = describe_errors(schema, extracted)
    report(not errors, f"{REFERENCE_PHASE} against phase.schema.json: "
           f"{'valid' if not errors else 'invalid'} (expected valid)", errors)

    for field, reason in PHASE_OMISSIONS:
        copy = {k: v for k, v in extracted.items() if k != field}
        errors = describe_errors(schema, copy)
        report(bool(errors), f"{REFERENCE_PHASE} without {field} ({reason}) against "
               f"phase.schema.json: {'invalid' if errors else 'valid'} (expected invalid)", errors)

    invalid = [(item.get("id", "?"), describe_errors(schema, item)) for item in items]
    invalid = [(phase_id, errors) for phase_id, errors in invalid if errors]
    report(not invalid, f"all {len(items)} phases in backlog.yaml against phase.schema.json: "
           f"{len(items) - len(invalid)} valid (expected all)",
           [f"{phase_id}: {message}" for phase_id, errors in invalid for message in errors])

    keys = template_yaml_keys((HERE / "phase.template.md").read_text(encoding="utf-8"))
    unknown = sorted(keys - set(schema["properties"]))
    missing = sorted(set(schema["required"]) - keys)
    report(bool(keys) and not unknown and not missing,
           "phase.template.md YAML keys against phase.schema.json properties",
           [f"unknown key: {k!r}" for k in unknown]
           + [f"missing required key: {k!r}" for k in missing])
    return failures


def main() -> int:
    failures = 0

    for example, schema_name, expected in CASES:
        instance = to_instance((EXAMPLES / example).read_text(encoding="utf-8"))
        errors = describe_errors(load_schema(schema_name), instance)
        valid = not errors
        ok = valid == expected
        failures += not ok
        verdict = "valid" if valid else "invalid"
        print(f"{'PASS' if ok else 'FAIL'}  {example} against {schema_name}: {verdict}"
              f" (expected {'valid' if expected else 'invalid'})")
        for message in errors:
            print(f"        {message}")

    for template, schema_name in TEMPLATES:
        sections_schema = load_schema(schema_name)["properties"]["sections"]
        instance = to_instance((HERE / template).read_text(encoding="utf-8"))
        errors = describe_errors(sections_schema, instance["sections"])
        ok = not errors
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {template} headings against {schema_name} sections")
        for message in errors:
            print(f"        {message}")

    failures += check_phases()

    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
