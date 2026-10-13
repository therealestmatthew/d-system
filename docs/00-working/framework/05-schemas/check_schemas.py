"""Validate the example documents in examples/ against the framework document schemas.

A Markdown document is converted to {front_matter, sections} before validation:
front_matter is the parsed YAML front matter, and sections is the list of level-2 heading
texts in document order, ignoring headings inside fenced code blocks and HTML comments.

Each case in CASES names an example, a schema and whether the example must validate.
The script also checks that each template's headings satisfy its schema's section
requirements, so a template and its schema cannot drift apart unnoticed, and that each example
listed in PLACEHOLDER_FREE carries none of the templates' placeholders (REQ-024 R04: a filled,
placeholder-free instance).

A backlog phase is a YAML item in backlog.yaml, not a Markdown document, so it is checked
separately (REQ-024 R03): the item named by REFERENCE_PHASE is cut out of backlog.yaml as text,
unchanged, and parsed as its own YAML document; it must validate, and copies with a required
field removed must not, while an active copy with no agent must (the host decides when an
active phase needs one). Every phase in backlog.yaml must also validate, and the keys in
phase.template.md's YAML block must match the schema. backlog.yaml is only read.

To check one real document instead of the examples, name it and its kind:

    uv run python docs/00-working/framework/05-schemas/check_schemas.py \
        --document path/to/REQ-031-example.md --kind requirement

That validates the document against the kind's schema, runs the placeholder check on it, and
compares its front-matter title and each section body against the kind's template's own sample
text, so a copied template fails whether or not its comments and "Example:" lead-ins were
removed. It exits 0 when every check passes, 1 otherwise (including when the path does not
exist). DOCUMENT_CASES runs the same check on examples, including such copies.

Run from the repository root:

    uv run python docs/00-working/framework/05-schemas/check_schemas.py

Exits 0 when every case matches its expectation, 1 otherwise.
"""

from __future__ import annotations

import argparse
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
    # REQ-024 R04: a filled requirement passes; without acceptance criteria it fails.
    ("requirement.valid.md", "requirement.schema.json", True),
    ("requirement.no-acceptance.md", "requirement.schema.json", False),
    # REQ-024 R04: a filled plan passes; without scope, or without phases, it fails.
    ("plan.valid.md", "plan.schema.json", True),
    ("plan.no-scope.md", "plan.schema.json", False),
    ("plan.no-phases.md", "plan.schema.json", False),
]

# Examples that must be filled instances of their template, with no placeholder left in them.
PLACEHOLDER_FREE: list[str] = ["requirement.valid.md", "plan.valid.md"]

# The schema for each document kind the --document mode accepts.
KINDS: dict[str, str] = {
    "governance": "governance.schema.json",
    "protocol": "protocol.schema.json",
    "requirement": "requirement.schema.json",
    "plan": "plan.schema.json",
}

# (example file, kind, must pass): the --document check, schema and placeholders together.
DOCUMENT_CASES: list[tuple[str, str, bool]] = [
    ("governance.valid.md", "governance", True),
    ("protocol.valid.md", "protocol", True),
    ("requirement.valid.md", "requirement", True),
    ("plan.valid.md", "plan", True),
    # A copied template with only code, created and the title line filled in.
    ("requirement.boilerplate.md", "requirement", False),
    ("plan.boilerplate.md", "plan", False),
    # The same copies with every comment and "Example:" lead-in removed, sample text kept.
    ("requirement.stripped-sample.md", "requirement", False),
    ("plan.stripped-sample.md", "plan", False),
    # requirement.valid.md saved with a UTF-8 byte-order mark.
    ("requirement.bom.md", "requirement", True),
]

# The placeholder forms the four --document templates use: a NNN code, a YYYY-MM-DD date, a
# [Bracketed Name] in the title line, an HTML comment, and an "Example:" lead-in. Angle-bracket
# slots are not included: of the Markdown templates only phase.template.md uses them, phase is
# not a --document kind, and a filled document may contain one in a code span.
PLACEHOLDER = re.compile(r"[A-Z]+-NNN|YYYY-MM-DD|^# .*\[[^\]]+\]|<!--|^Example:", re.MULTILINE)

# (template file, schema file): the template's headings must satisfy the schema's `sections`.
TEMPLATES: list[tuple[str, str]] = [
    ("governance.template.md", "governance.schema.json"),
    ("protocol.template.md", "protocol.schema.json"),
    ("requirement.template.md", "requirement.schema.json"),
    ("plan.template.md", "plan.schema.json"),
]

# (field removed from the reference phase, reason the copy must fail)
PHASE_OMISSIONS: list[tuple[str, str]] = [
    ("acceptance", "a required field"),
    ("result", "required once status is complete"),
]

# A sentence of a template's sample text shorter than this is not compared, so a short generic
# phrase cannot fail a real document.
MIN_SAMPLE = 30

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


def split_document(text: str) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    """The parsed front matter and each level-2 section as (heading, body), with HTML comments
    removed and headings inside fenced code blocks ignored. A leading byte-order mark is
    dropped first, so it cannot hide the front matter."""
    text = text.removeprefix("\ufeff")
    match = FRONT_MATTER.match(text)
    front_matter = _stringify_dates(yaml.safe_load(match.group(1))) if match else {}
    body = COMMENT.sub("", text[match.end():] if match else text)

    sections: list[tuple[str, list[str]]] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            sections.append((line[3:].strip(), []))
            continue
        if sections:
            sections[-1][1].append(line)
    return front_matter or {}, [(heading, "\n".join(lines)) for heading, lines in sections]


def to_instance(text: str) -> dict[str, Any]:
    """Convert a Markdown document to the {front_matter, sections} shape the schemas validate."""
    front_matter, sections = split_document(text)
    return {"front_matter": front_matter, "sections": [heading for heading, _ in sections]}


def _collapse(text: str) -> str:
    return " ".join(text.split())


def template_sample(kind: str) -> tuple[str, list[str]]:
    """A template's sample front-matter title and the sentences of its sample section text,
    with "Example:" lead-ins removed, whitespace collapsed, and sentences shorter than
    MIN_SAMPLE dropped."""
    front_matter, sections = split_document(
        (HERE / f"{kind}.template.md").read_text(encoding="utf-8"))
    sentences: list[str] = []
    for _, body in sections:
        body = re.sub(r"^Example:", "", body, flags=re.MULTILINE)
        # A block is a paragraph, list item or bold-led line, so one kept item still matches.
        blocks = re.split(r"\n\s*\n|\n(?=\s*(?:[-*] |\d+\. |\*\*|\*[A-Z]))", body)
        for block in blocks:
            block = _collapse(re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", block))
            sentences += [s.strip() for s in re.split(r"(?<=[.:;])\s+", block)]
    return str(front_matter.get("title", "")), [s for s in sentences if len(s) >= MIN_SAMPLE]


def retained_sample(text: str, kind: str) -> list[str]:
    """Where a document still carries its template's sample title or sample sentences."""
    title, sentences = template_sample(kind)
    front_matter, sections = split_document(text)
    found: list[str] = []
    if title and _collapse(str(front_matter.get("title", ""))) == _collapse(title):
        found.append(f"front-matter title is the template's sample: {title!r}")
    for heading, body in sections:
        collapsed = _collapse(body)
        found += [f"section {heading!r} keeps the template's sample text: {s[:60]!r}"
                  for s in sentences if s in collapsed]
    return found


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


def check_document(path: Path, kind: str) -> list[str]:
    """Schema errors, placeholders and retained template sample text in one document."""
    if not path.is_file():
        return [f"no such file: {path}"]
    text = path.read_text(encoding="utf-8")
    errors = describe_errors(load_schema(KINDS[kind]), to_instance(text))
    errors += [f"placeholder: {found!r}" for found in PLACEHOLDER.findall(text)]
    return errors + retained_sample(text, kind)


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

    # The host's concurrency rule, not the schema, decides when an active phase needs an agent:
    # d-system requires none while max_active is 1, so an unclaimed active phase must validate.
    unclaimed = {k: v for k, v in extracted.items()
                 if k not in {"agent", "session", "completion_evidence", "result"}}
    unclaimed["status"] = "active"
    errors = describe_errors(schema, unclaimed)
    report(not errors, f"{REFERENCE_PHASE} as active with no agent against phase.schema.json: "
           f"{'valid' if not errors else 'invalid'} (expected valid)", errors)

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

    for example in PLACEHOLDER_FREE:
        found = PLACEHOLDER.findall((EXAMPLES / example).read_text(encoding="utf-8"))
        ok = not found
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {example} has no template placeholders")
        for placeholder in found:
            print(f"        placeholder: {placeholder!r}")

    for example, kind, expected in DOCUMENT_CASES:
        errors = check_document(EXAMPLES / example, kind)
        ok = (not errors) == expected
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {example} as a {kind} document (--document): "
              f"{'passes' if not errors else 'fails'} (expected {'pass' if expected else 'fail'})")
        for message in errors:
            print(f"        {message}")

    failures += check_phases()

    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


def check_one(path: Path, kind: str) -> int:
    """The --document mode: 0 when the document passes its schema and has no placeholders."""
    errors = check_document(path, kind)
    print(f"{'PASS' if not errors else 'FAIL'}  {path} as a {kind} document")
    # A missing path comes back as one "no such file" error, so it prints a FAIL line too.
    for message in errors:
        print(f"        {message}")
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--document", type=Path,
                        help="check this document instead of the examples")
    parser.add_argument("--kind", choices=sorted(KINDS),
                        help="the document's kind (with --document)")
    args = parser.parse_args()
    if (args.document is None) != (args.kind is None):
        parser.error("--document and --kind are used together")
    sys.exit(check_one(args.document, args.kind) if args.document else main())
