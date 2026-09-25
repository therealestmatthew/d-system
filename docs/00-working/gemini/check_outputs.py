"""The "done" check for one PROMPT-040 prompt's outputs. Run it in that prompt's worktree.

    uv run python docs/00-working/gemini/check_outputs.py G1

It prints one line per problem and exits 1 if there is any, or prints "OK" and exits 0. It checks:
- report.md exists and opens with the provenance block, matching the JSON provenance;
- every JSON output validates against its schema in docs/00-working/gemini/schemas/;
- every alt-*.schema.json (G1) is itself a valid JSON Schema;
- every cited path is a tracked file, every line range is inside it, and the quote appears there;
- finding, design and rule ids are unique, and G2 has exactly one recommended design per parameter;
- `git status` shows changes only under the prompt's output directory.
Ungoverned staging (ADR-010); it is not a tool under tools/ and has no OPS document.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft7Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/00-working/gemini"
OUTPUT_DIRS = {
    "G1": "g1-three-axis-stress",
    "G2": "g2-adr-023-parameters",
    "G3": "g3-governance-analysis",
}
REQUIRED_JSON = {
    "G1": {"findings.json": "findings.schema.json"},
    "G2": {"findings.json": "findings.schema.json", "designs.json": "designs.schema.json"},
    "G3": {
        "findings.json": "findings.schema.json",
        "rule-register.json": "rule-register.schema.json",
    },
}
PROVENANCE_KEYS = ("model", "date", "prompt", "dev_sha", "branch")


def load_registry() -> Registry:
    registry: Registry = Registry()
    for path in (BASE / "schemas").glob("*.schema.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        registry = registry.with_resource(path.name, Resource.from_contents(schema))
    return registry


def tracked_files() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True)
    return set(out.stdout.splitlines())


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def check_evidence(item: dict, where: str, tracked: set[str], problems: list[str]) -> None:
    if "url" in item:
        return
    path, line = item["path"], item["line"]
    if path not in tracked:
        problems.append(f"{where}: cited path is not a tracked file: {path}")
        return
    lines = (ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines()
    start, _, end = line.partition("-")
    first, last = int(start), int(end or start)
    if not 1 <= first <= last <= len(lines):
        problems.append(f"{where}: line {line} is outside {path} ({len(lines)} lines)")
        return
    if normalise(item["quote"]) not in normalise(" ".join(lines[first - 1 : last])):
        problems.append(f"{where}: quote not found at {path}:{line}")


def walk_evidence(node: object, where: str, tracked: set[str], problems: list[str]) -> None:
    """Check every object that looks like an evidence item, wherever it sits."""
    if isinstance(node, dict):
        if "quote" in node and ("path" in node or "url" in node):
            check_evidence(node, where, tracked, problems)
        for key, value in node.items():
            walk_evidence(value, f"{where}.{key}", tracked, problems)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            walk_evidence(value, f"{where}[{index}]", tracked, problems)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in OUTPUT_DIRS:
        print("usage: check_outputs.py G1|G2|G3")
        return 2
    prompt = sys.argv[1]
    out_dir = BASE / OUTPUT_DIRS[prompt]
    problems: list[str] = []
    registry = load_registry()
    tracked = tracked_files()
    provenances: list[dict] = []

    for name, schema_name in REQUIRED_JSON[prompt].items():
        path = out_dir / name
        if not path.exists():
            problems.append(f"missing required output: {path.relative_to(ROOT)}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{name}: not valid JSON: {exc}")
            continue
        schema = registry.get_or_retrieve(schema_name).value.contents
        for error in Draft7Validator(schema, registry=registry).iter_errors(data):
            problems.append(f"{name}: schema: {'/'.join(map(str, error.path))}: {error.message}")
        if isinstance(data, dict):
            provenance = data.get("provenance", {})
            provenances.append(provenance)
            if provenance.get("prompt") != f"PROMPT-040 {prompt}":
                problems.append(f"{name}: provenance.prompt must be 'PROMPT-040 {prompt}'")
            for key in ("findings", "designs", "rules"):
                ids = [entry.get("id") for entry in data.get(key, []) if isinstance(entry, dict)]
                duplicates = {i for i in ids if ids.count(i) > 1}
                if duplicates:
                    problems.append(f"{name}: duplicate ids: {sorted(duplicates)}")
            if name == "designs.json":
                for parameter in (
                    "router-shadow",
                    "grant-records",
                    "owner-desk-events",
                    "lease-file",
                ):
                    group = [d for d in data.get("designs", []) if d.get("parameter") == parameter]
                    if len(group) < 2:
                        problems.append(
                            f"designs.json: {parameter} needs at least 2 designs, has {len(group)}"
                        )
                    if sum(1 for d in group if d.get("recommended")) != 1:
                        problems.append(
                            f"designs.json: {parameter} needs exactly one recommended design"
                        )
            walk_evidence(data, name, tracked, problems)

    if prompt == "G1":
        for name in ("alt-a.schema.json", "alt-b.schema.json"):
            if not (out_dir / name).exists():
                problems.append(f"missing required output: {(out_dir / name).relative_to(ROOT)}")
    for path in sorted(out_dir.glob("alt-*.schema.json")):
        try:
            Draft7Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001 - report any failure as a problem line
            problems.append(f"{path.name}: not a valid JSON Schema: {exc}")

    report = out_dir / "report.md"
    if not report.exists():
        problems.append(f"missing required output: {report.relative_to(ROOT)}")
    else:
        head = report.read_text(encoding="utf-8").split("\n## ", 1)[0]
        for provenance in provenances[:1]:
            for key in PROVENANCE_KEYS:
                line = f"{key}: {provenance.get(key)}"
                if line not in head:
                    problems.append(f"report.md: provenance line '{line}' missing before ## ")

    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    prefix = f"docs/00-working/gemini/{OUTPUT_DIRS[prompt]}/"
    for entry in status.stdout.splitlines():
        changed = entry[3:].split(" -> ")[-1].strip('"')
        if not changed.startswith(prefix):
            problems.append(f"git status: change outside {prefix}: {entry}")

    for problem in problems:
        print(problem)
    if problems:
        print(f"FAILED: {len(problems)} problem(s)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
