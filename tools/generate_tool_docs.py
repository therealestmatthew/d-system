#!/usr/bin/env python3
"""Regenerate the generated-reference block inside each tool's OPS document.

Each tool under `tools/` is paired with an `OPS-*` document in `docs/08-governance/` by the
repository's own `<code>-<slug>.md` filename convention: `tools/rebuild_db.py` pairs with
whichever `docs/08-governance/OPS-*-rebuild-db.md` exists. The narrative half of that document
(what the tool is for, its contract, its failure modes) is hand-written and never touched here.
The reference half — the tool's module docstring, its `argparse` arguments and the exit codes its
source actually returns or raises — is mechanical and lives between two HTML comment markers this
script owns exclusively:

    <!-- generated:tool-reference:start -->
    ...
    <!-- generated:tool-reference:end -->

This script never creates a document. A tool with no matching OPS document is reported and left
alone; writing one, with its narrative half, is a human decision (PLAN-013).

    uv run python tools/generate_tool_docs.py           # update every paired doc in place
    uv run python tools/generate_tool_docs.py --check   # exit 1 if any paired doc is stale
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
DOCS_DIR = ROOT / "docs" / "08-governance"

START = "<!-- generated:tool-reference:start -->"
END = "<!-- generated:tool-reference:end -->"


def _literal(node: ast.expr | None) -> object:
    """Best-effort literal value of an AST node; None for anything not a constant."""
    if node is None:
        return None
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return None


def discover_tools() -> list[Path]:
    """Every tool script this generator can document, itself included.

    Parsing is static (`ast`, never `import`), so there is no self-execution hazard in reading
    this file's own source the same way it reads any other tool's.
    """
    return sorted(p for p in TOOLS_DIR.glob("*.py") if not p.name.startswith("__"))


def find_doc(tool: Path) -> Path | None:
    """The OPS document naming itself after this tool, by filename convention."""
    slug = tool.stem.replace("_", "-")
    matches = sorted(DOCS_DIR.glob(f"OPS-*-{slug}.md"))
    return matches[0] if matches else None


def extract_arguments(tree: ast.Module) -> list[dict[str, object]]:
    """Every `parser.add_argument(...)` call in the module, in source order."""
    found: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_argument"
        ):
            continue
        flags = [f for f in (_literal(a) for a in node.args) if isinstance(f, str)]
        if not flags:
            continue
        kwargs = {kw.arg: _literal(kw.value) for kw in node.keywords if kw.arg}
        found.append(
            {
                "flags": flags,
                "help": kwargs.get("help"),
                "choices": kwargs.get("choices"),
                "default": kwargs.get("default"),
                "required": kwargs.get("required"),
            }
        )
    return found


def extract_exit_codes(tree: ast.Module) -> list[int]:
    """Every literal `return <int>` and `SystemExit(<int>)` in the module."""
    codes: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, int) and not isinstance(node.value.value, bool):
                codes.add(node.value.value)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "SystemExit"
        ):
            for value in (_literal(a) for a in node.args):
                if isinstance(value, int) and not isinstance(value, bool):
                    codes.add(value)
    return sorted(codes)


def render(tool: Path) -> str:
    """The generated reference block for one tool: docstring, arguments, exit codes."""
    tree = ast.parse(tool.read_text(encoding="utf-8"), filename=str(tool))
    docstring = (ast.get_docstring(tree) or "").strip()
    arguments = extract_arguments(tree)
    codes = extract_exit_codes(tree)

    parts = [START, "", f"### Reference: `tools/{tool.name}`", ""]
    if docstring:
        parts += [docstring, ""]

    if arguments:
        parts += ["| Flag | Help | Choices | Default | Required |", "|---|---|---|---|---|"]
        for arg in arguments:
            flags = ", ".join(f"`{f}`" for f in cast("list[str]", arg["flags"]))
            help_text = str(arg["help"]) if arg["help"] else ""
            choices = arg["choices"]
            choices_text = ", ".join(str(c) for c in choices) if isinstance(choices, list) else ""
            default = arg["default"]
            default_text = "" if default is None else str(default)
            required_text = "yes" if arg["required"] else ""
            row = f"| {flags} | {help_text} | {choices_text} | {default_text} | {required_text} |"
            parts.append(row)
        parts.append("")
    else:
        parts += ["No CLI arguments.", ""]

    if codes:
        joined = ", ".join(str(c) for c in codes)
        parts += [f"Exit codes found in source: {joined}.", ""]

    parts.append(END)
    return "\n".join(parts)


def update_doc(doc: Path, rendered: str) -> str:
    """The doc's full text with its generated block replaced -- narrative untouched.

    Splits on the *first* START and the *last* END, not the first of each. A rendered block can
    itself quote the marker text as an example (this generator's own docstring does, describing
    the very markers it owns) -- taking the first END would then cut the block off at that quoted
    example instead of the real closing marker.
    """
    text = doc.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise ValueError(f"{doc} has no {START} .. {END} block for the generator to update")
    before, _, rest = text.partition(START)
    _, _, after = rest.rpartition(END)
    return before + rendered + after


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check", action="store_true", help="Exit 1 if any paired doc is missing or stale"
    )
    args = parser.parse_args(argv)

    tools = discover_tools()
    unpaired: list[Path] = []
    stale: list[Path] = []
    updated: list[Path] = []

    for tool in tools:
        doc = find_doc(tool)
        if doc is None:
            unpaired.append(tool)
            continue
        rendered = render(tool)
        new_text = update_doc(doc, rendered)
        current = doc.read_text(encoding="utf-8")
        if current == new_text:
            continue
        if args.check:
            stale.append(doc)
        else:
            doc.write_text(new_text, encoding="utf-8")
            updated.append(doc)

    if unpaired:
        names = ", ".join(t.name for t in unpaired)
        print(f"no OPS document found for: {names}", file=sys.stderr)

    if args.check:
        if stale or unpaired:
            if stale:
                print(
                    "stale generated section(s): " + ", ".join(str(d) for d in stale),
                    file=sys.stderr,
                )
            return 1
        print(f"{len(tools)} tool document(s) current")
        return 0

    print(f"updated {len(updated)} of {len(tools) - len(unpaired)} paired tool document(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
