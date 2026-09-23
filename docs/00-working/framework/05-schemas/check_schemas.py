"""Validate the example documents in examples/ against the framework document schemas.

A Markdown document is converted to {front_matter, sections} before validation:
front_matter is the parsed YAML front matter, and sections is the list of level-2 heading
texts in document order, ignoring headings inside fenced code blocks and HTML comments.

Each case in CASES names an example, a schema and whether the example must validate.
The script also checks that each template's headings satisfy its schema's section
requirements, so a template and its schema cannot drift apart unnoticed.

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

    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
