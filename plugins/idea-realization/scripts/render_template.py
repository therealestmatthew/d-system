# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Render one of the plugin's templates, such as the working agreement, by filling its placeholders.

A placeholder is ``{{name}}``. Four are known: ``integration_branch`` and ``worktree_dir``, which
default to the configured values, and ``data_root`` and ``confidential_dir``, which have no
default and must be given with ``--set``. A template naming any other placeholder is refused
before anything is written, and so is a rendering that would leave a ``{{`` behind.

The rendered file is written to ``--output`` (relative to the repository root), or printed when
none is given. An existing file is never overwritten: a repository that already has one keeps it,
and a person merges the rendered text by hand.

Exit codes: 0 when the file was rendered; 1 when a placeholder is unknown or has no value, or the
output file exists; 2 on a usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

import paths

PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z0-9_]*)\s*\}\}")
KNOWN = ("integration_branch", "worktree_dir", "data_root", "confidential_dir")


class TemplateError(ValueError):
    """A template that cannot be rendered as given."""


def placeholders(text: str) -> list[str]:
    """Every placeholder name in ``text``, in first-appearance order."""
    return list(dict.fromkeys(PLACEHOLDER.findall(text)))


def render(text: str, values: Mapping[str, str]) -> str:
    """Fill every placeholder; refuse an unknown one, a missing value or a leftover marker."""
    unknown = [name for name in placeholders(text) if name not in KNOWN]
    if unknown:
        raise TemplateError(f"unknown placeholder(s): {', '.join(unknown)}")
    missing = [name for name in placeholders(text) if not values.get(name)]
    if missing:
        raise TemplateError(f"no value for placeholder(s): {', '.join(missing)}; "
                            "give each with --set NAME=VALUE")
    rendered = PLACEHOLDER.sub(lambda match: values[match.group(1)], text)
    if "{{" in rendered:
        raise TemplateError("the rendered text still contains a '{{' marker")
    return rendered


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a plugin template by filling its {{placeholders}}.",
    )
    parser.add_argument("template", help="the template file, such as templates/AGENTS.md")
    parser.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                        help="a placeholder value; repeatable")
    parser.add_argument("--output", help="file to write, relative to the repository root; "
                                         "printed when omitted")
    paths.add_arguments(parser, ["integration_branch", "worktree_dir"])
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    values = {
        "integration_branch": config.text("integration_branch"),
        "worktree_dir": str(config.values["worktree_dir"]).replace("<repository>",
                                                                    config.root.name),
    }
    for item in args.set:
        name, sep, value = item.partition("=")
        if not sep or name not in KNOWN:
            print(f"--set expects one of {', '.join(KNOWN)} as NAME=VALUE, not {item!r}",
                  file=sys.stderr)
            return 2
        values[name] = value
    try:
        text = Path(args.template).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read {args.template}: {exc}", file=sys.stderr)
        return 2
    try:
        rendered = render(text, values)
    except TemplateError as exc:
        print(f"{args.template}: {exc}", file=sys.stderr)
        return 1
    if not args.output:
        sys.stdout.write(rendered)
        return 0
    target = Path(args.output)
    target = target if target.is_absolute() else config.root / target
    if target.exists():
        print(f"{target} exists; not overwritten. Merge the rendered text by hand.",
              file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
