# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Generate tool reference documentation from each script's docstring, arguments and exit codes.

Every script is read with ``ast`` and never imported, so documenting a script never runs it. Two
modes share one renderer:

- **Paired documents** (the default). Each script in ``--tools`` is paired with the operations
  document in ``--docs`` whose filename matches ``--pattern`` with the script's stem, underscores
  as hyphens, in place of ``{slug}``. The narrative half of that document is hand-written and never
  touched; the reference half lives between two markers this script owns::

      <!-- generated:tool-reference:start -->
      <!-- generated:tool-reference:end -->

  A script with no paired document is reported and left alone; writing one is a person's decision.
- **One reference document** (``--reference``). Writes a whole document with one section per
  script, in name order: its purpose, its invocation, its arguments and its exit codes. A script
  named by ``--preamble-from`` has its docstring stated once at the top instead of a section; a
  script that adds the shared path flags (``paths.add_arguments``) lists them and refers back to it.

Either mode with ``--check`` writes nothing and reports every stale or unpaired file. Relative
paths resolve against the repository root.

Exit codes: 0 when everything was written or is current; 1 under ``--check`` when a file is stale
or a script is unpaired, naming each file; 2 on a usage error, such as a paired document with no
generated block.
"""

from __future__ import annotations

import argparse
import ast
import shlex
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

import paths

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


def discover(tools: Path, exclude: Sequence[str] = ()) -> list[Path]:
    """Every script directly under ``tools``, in name order, less dunder files and ``exclude``."""
    return sorted(p for p in tools.glob("*.py")
                  if not p.name.startswith("__") and p.name not in exclude)


def find_doc(tool: Path, docs: Path, pattern: str) -> Path | None:
    """The operations document naming itself after this tool, by filename pattern."""
    matches = sorted(docs.glob(pattern.replace("{slug}", tool.stem.replace("_", "-"))))
    return matches[0] if matches else None


def extract_arguments(tree: ast.Module) -> list[dict[str, object]]:
    """Every ``add_argument(...)`` call in the module, in source order."""
    found: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"):
            continue
        flags = [f for f in (_literal(a) for a in node.args) if isinstance(f, str)]
        if not flags:
            continue
        kwargs = {kw.arg: _literal(kw.value) for kw in node.keywords if kw.arg}
        found.append({
            "flags": flags,
            "help": kwargs.get("help"),
            "choices": kwargs.get("choices"),
            "default": kwargs.get("default"),
            "required": kwargs.get("required"),
        })
    return found


def extract_path_keys(tree: ast.Module) -> list[str] | None:
    """The configured keys a script adds through ``paths.add_arguments``, or None when it adds none.

    An empty list means only ``--root``; a call with no list names every configured key, shown as
    ``["*"]``.
    """
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_arguments" and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "paths"):
            names = _literal(node.args[1]) if len(node.args) > 1 else None
            if isinstance(names, list) and all(isinstance(n, str) for n in names):
                return cast("list[str]", names)
            return ["*"]
    return None


def extract_exit_codes(tree: ast.Module) -> list[int]:
    """Every literal ``return <int>`` and ``SystemExit(<int>)`` in the module."""
    codes: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, int) and not isinstance(node.value.value, bool):
                codes.add(node.value.value)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "SystemExit"):
            for value in (_literal(a) for a in node.args):
                if isinstance(value, int) and not isinstance(value, bool):
                    codes.add(value)
    return sorted(codes)


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _parse(tool: Path) -> ast.Module:
    return ast.parse(tool.read_text(encoding="utf-8"), filename=str(tool))


def reference_body(tool: Path) -> list[str]:
    """Docstring, argument table, shared path flags and exit codes for one script."""
    tree = _parse(tool)
    docstring = (ast.get_docstring(tree) or "").strip()
    arguments = extract_arguments(tree)
    keys = extract_path_keys(tree)
    codes = extract_exit_codes(tree)
    parts: list[str] = []
    if docstring:
        parts += [docstring, ""]
    if arguments:
        parts += ["| Flag | Help | Choices | Default | Required |", "|---|---|---|---|---|"]
        for arg in arguments:
            flags = ", ".join(f"`{f}`" for f in cast("list[str]", arg["flags"]))
            help_text = _cell(str(arg["help"])) if arg["help"] else ""
            choices = arg["choices"]
            choices_text = ", ".join(str(c) for c in choices) if isinstance(choices, list) else ""
            default = arg["default"]
            default_text = "" if default is None else _cell(str(default))
            required_text = "yes" if arg["required"] else ""
            parts.append(f"| {flags} | {help_text} | {choices_text} | {default_text} | "
                         f"{required_text} |")
        parts.append("")
    elif keys is None:
        parts += ["No command-line arguments.", ""]
    if keys is not None:
        if keys == ["*"]:
            named = "every configured path and value"
        else:
            named = ", ".join(f"`--{key.replace('_', '-')}`" for key in ["root", *keys])
        parts += [f"Shared configuration flags: {named}, resolved by the shared configuration "
                  "precedence rule.", ""]
    if codes:
        parts += [f"Exit codes found in source: {', '.join(str(c) for c in codes)}.", ""]
    return parts


def render_block(tool: Path, label: str) -> str:
    """The generated block for one paired document."""
    return "\n".join([START, "", f"### Reference: `{label}`", "", *reference_body(tool), END])


def update_doc(text: str, rendered: str, doc: Path) -> str:
    """The document's text with its generated block replaced, narrative untouched.

    Splits on the first start marker and the last end marker: a rendered block may quote the
    marker text itself, as this script's own docstring does.
    """
    if START not in text or END not in text:
        raise ValueError(f"{doc} has no generated block for the generator to update")
    before, _, rest = text.partition(START)
    _, _, after = rest.rpartition(END)
    return before + rendered + after


def render_reference(tools: list[Path], title: str, invocation: str,
                     preamble: Path | None, command: str) -> str:
    """One document: a title, the preamble script's docstring, then one section per script.

    ``command`` is the argument list that regenerates the document, with ``--root .`` whatever root
    was given, stated in its header so a reader can reproduce it exactly from any checkout.
    """
    lines = [f"# {title}", "",
             "Generated from the scripts themselves. Never edit this file by hand. Regenerate it,",
             "from the directory its paths are relative to, with",
             f"`generate_tool_docs.py {command}`;",
             "`--check` with the same arguments compares the committed file with a fresh render.",
             ""]
    if preamble is not None:
        text = (ast.get_docstring(_parse(preamble)) or "").strip()
        if text:
            lines += ["## Configuration", "", text, ""]
    for tool in tools:
        lines += [f"## `{tool.name}`", "", "```bash",
                  invocation.replace("{name}", tool.name), "```", ""]
        lines += reference_body(tool)
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate tool reference documentation from each script's docstring, "
                    "arguments and exit codes, into paired documents or one reference document.",
    )
    parser.add_argument("--tools", default="tools",
                        help="directory holding the scripts to document")
    parser.add_argument("--docs", default="docs/governance",
                        help="directory holding the paired operations documents")
    parser.add_argument("--pattern", default="OPS-*-{slug}.md",
                        help="filename pattern of a paired document; {slug} is the script stem")
    parser.add_argument("--reference", metavar="FILE",
                        help="write one reference document to FILE instead of paired documents")
    parser.add_argument("--title", default="Tools reference",
                        help="title of the reference document")
    parser.add_argument("--invocation", default="uv run {name}",
                        help="how to run a script, shown in the reference; {name} is its filename")
    parser.add_argument("--preamble-from", metavar="SCRIPT",
                        help="script whose docstring opens the reference instead of a section")
    parser.add_argument("--exclude", action="append", default=[], metavar="SCRIPT",
                        help="script filename to leave out; repeatable")
    parser.add_argument("--check", action="store_true",
                        help="write nothing; exit 1 if any output is stale or a script unpaired")
    paths.add_arguments(parser, [])
    args = parser.parse_args(argv)
    root = paths.repository_root(args.root)

    def resolve(value: str) -> Path:
        path = Path(value).expanduser()
        return path if path.is_absolute() else root / path

    tools_dir = resolve(args.tools)
    if not tools_dir.is_dir():
        print(f"no scripts directory at {tools_dir}", file=sys.stderr)
        return 2
    excluded = list(args.exclude)
    if args.preamble_from:
        excluded.append(args.preamble_from)
    tools = discover(tools_dir, excluded)

    if args.reference:
        target = resolve(args.reference)
        preamble = tools_dir / args.preamble_from if args.preamble_from else None
        if preamble is not None and not preamble.is_file():
            print(f"no preamble script {preamble}", file=sys.stderr)
            return 2
        command = shlex.join([
            "--root", ".", "--tools", args.tools, "--reference", args.reference,
            "--title", args.title,
            "--invocation", args.invocation,
            *(["--preamble-from", args.preamble_from] if args.preamble_from else []),
            *[item for name in args.exclude for item in ("--exclude", name)],
        ])
        rendered = render_reference(tools, args.title, args.invocation, preamble, command)
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        if args.check:
            if current != rendered:
                print(f"stale generated reference: {target}", file=sys.stderr)
                return 1
            print(f"{target} is current ({len(tools)} scripts)")
            return 0
        if current != rendered:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
        print(f"wrote {target} ({len(tools)} scripts)")
        return 0

    docs_dir = resolve(args.docs)
    unpaired: list[Path] = []
    stale: list[Path] = []
    updated: list[Path] = []
    for tool in tools:
        doc = find_doc(tool, docs_dir, args.pattern)
        if doc is None:
            unpaired.append(tool)
            continue
        current = doc.read_text(encoding="utf-8")
        label = tool.relative_to(root).as_posix() if tool.is_relative_to(root) else tool.name
        try:
            new_text = update_doc(current, render_block(tool, label), doc)
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 2
        if current == new_text:
            continue
        if args.check:
            stale.append(doc)
        else:
            doc.write_text(new_text, encoding="utf-8")
            updated.append(doc)
    if unpaired:
        print("no paired document for: " + ", ".join(t.name for t in unpaired), file=sys.stderr)
    if args.check:
        if stale:
            print("stale generated block: " + ", ".join(str(d) for d in stale), file=sys.stderr)
        if stale or unpaired:
            return 1
        print(f"{len(tools)} paired document(s) current")
        return 0
    print(f"updated {len(updated)} of {len(tools) - len(unpaired)} paired document(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
