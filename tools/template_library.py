#!/usr/bin/env python3
"""The template library: declared templates, and a renderer that dispatches on how each one is
populated — `REQ-021` R05 and R06, `phase-des-03`.

`templates/html/library.yaml` declares every template under `templates/html/`: its family, and
its population method — deterministic slot-filling, AI adaptation, or both. This module reads
that declaration, finds each template's `{{SLOT}}` names in the template itself, and renders by
dispatching on the declared method, so a caller never needs to know which templates an agent
populates:

- `slot-fill` fills every slot from the data, strictly: an unknown or missing slot is an error.
- `ai-adaptation` returns an adaptation brief — the template, its slots and the data — for an
  agent to work from. No page comes back and no model is called; the library stays
  deterministic.
- `both` fills the deterministic slots first, then returns a brief naming the slots in the
  declaration's `ai_slots`, which stay in the partly filled template for the agent.

Adding a template needs no change here. A file matching a family's pattern is declared already,
and a new family is a manifest entry. `load()` rejects an undeclared template, a declaration
that matches no file, and an `ai_slots` name the template lacks, so the declaration cannot
drift from the files.

The existing generators (`tools/generate_overview.py`, `tools/generate_engine_pages.py`,
`tools/generate_house_css.py`, `tools/lit_report_render.py`) keep their own template loading.
The library sits beside them and changes nothing they render; its tests replay
`generate_overview.py`'s fills through `render()` and compare the bytes.

Slot filling here is the same contract every family documents: the template's leading
`<!-- ... -->` comment is removed first, because it names the slots literally, and the fill is
one pass over the original text, so a value containing `{{...}}` is never re-substituted.

    uv run python tools/template_library.py list
    uv run python tools/template_library.py show overview-page.html
    uv run python tools/template_library.py render house-page.html --data DATA.json --out PAGE.html
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path("templates") / "html" / "library.yaml"

POPULATION_METHODS = ("slot-fill", "ai-adaptation", "both")

_LEADING_COMMENT = re.compile(r"^\s*<!--.*?-->\s*", re.DOTALL)
_CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_SLOT = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


class LibraryError(ValueError):
    """The manifest, a template, or a render request is inconsistent."""


@dataclass(frozen=True)
class InlineStyles:
    files: tuple[str, ...]
    separator: str
    strip_comments: bool


@dataclass(frozen=True)
class Template:
    """One declared template, with what its file and its declaration say about it."""

    name: str
    family: str
    population: str
    ai_slots: tuple[str, ...]
    reference: bool
    page: bool
    slots: tuple[str, ...]
    generator: str | None
    inline_styles: InlineStyles | None
    path: Path = field(compare=False)

    def body(self) -> str:
        """The template text with its leading doc comment removed, ready to fill."""
        return _LEADING_COMMENT.sub("", self.path.read_text(encoding="utf-8"), count=1)


@dataclass(frozen=True)
class Rendered:
    """A finished page or fragment: every slot was filled deterministically."""

    template: str
    html: str


@dataclass(frozen=True)
class AdaptationBrief:
    """What an agent needs to finish a template the declaration says it populates.

    `partial` is the template with every deterministic slot already filled and the agent's
    slots still in place as `{{SLOT}}`; for `ai-adaptation` nothing is filled.
    """

    template: str
    family: str
    population: str
    ai_slots: tuple[str, ...]
    filled_slots: tuple[str, ...]
    partial: str
    data: dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(
            {
                "template": self.template,
                "family": self.family,
                "population": self.population,
                "ai_slots": list(self.ai_slots),
                "filled_slots": list(self.filled_slots),
                "instructions": (
                    f"Fill {', '.join('{{' + s + '}}' for s in self.ai_slots)} in `partial`, "
                    f"following the token contract and companion markup of the {self.family} "
                    "family, using `data` as the content. Leave every other part unchanged."
                ),
                "data": self.data,
                "partial": self.partial,
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )


def _slots(text: str) -> tuple[str, ...]:
    return tuple(sorted(set(_SLOT.findall(text))))


def fill(template: str, values: dict[str, str]) -> str:
    """Replace every `{{SLOT}}` in one pass; refuse a slot the template lacks or leaves unfilled.

    Both checks read the template, not the output, because a filled value may itself contain
    `{{...}}` text (an inlined stylesheet's comment, a rendered fragment).
    """
    wanted = set(_SLOT.findall(template))
    unknown = sorted(set(values) - wanted)
    if unknown:
        raise LibraryError(f"template has no slot(s): {', '.join(unknown)}")
    missing = sorted(wanted - set(values))
    if missing:
        raise LibraryError(f"unfilled slot(s): {', '.join(missing)}")
    return _SLOT.sub(lambda match: values[match.group(1)], template)


def _fill_some(template: str, values: dict[str, str]) -> str:
    """Replace only the slots in `values`, in one pass; leave the others as written."""
    return _SLOT.sub(lambda match: values.get(match.group(1), match.group(0)), template)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LibraryError(message)


class Library:
    """The declared templates of one repository tree."""

    def __init__(self, templates: dict[str, Template], root: Path) -> None:
        self.templates = templates
        self.root = root

    def get(self, name: str) -> Template:
        try:
            return self.templates[name]
        except KeyError:
            raise LibraryError(f"no declared template named {name}") from None

    def inline_styles(self, template: Template) -> str:
        spec = template.inline_styles
        _require(spec is not None, f"{template.name}: its family declares no inline_styles")
        assert spec is not None
        parts = []
        for name in spec.files:
            text = (self.root / name).read_text(encoding="utf-8")
            parts.append(_CSS_COMMENT.sub("", text) if spec.strip_comments else text)
        return spec.separator.join(parts)

    def render(self, name: str, data: dict[str, str]) -> Rendered | AdaptationBrief:
        """Dispatch on the template's declared population method."""
        template = self.get(name)
        _require(not template.reference, f"{name} is a reference catalogue, not rendered")
        values = dict(data)
        if (
            template.page
            and "INLINE_STYLES" in template.slots
            and "INLINE_STYLES" not in values
            and template.inline_styles is not None
        ):
            values["INLINE_STYLES"] = self.inline_styles(template)
        unknown = sorted(set(values) - set(template.slots))
        _require(not unknown, f"{name}: template has no slot(s): {', '.join(unknown)}")

        if template.population == "slot-fill":
            return Rendered(name, fill(template.body(), values))

        ai_slots = template.ai_slots if template.population == "both" else template.slots
        deterministic = {k: v for k, v in values.items() if k not in ai_slots}
        if template.population == "both":
            missing = sorted(set(template.slots) - set(ai_slots) - set(deterministic))
            _require(not missing, f"{name}: unfilled deterministic slot(s): {', '.join(missing)}")
        return AdaptationBrief(
            template=name,
            family=template.family,
            population=template.population,
            ai_slots=tuple(ai_slots),
            filled_slots=tuple(sorted(deterministic)),
            partial=_fill_some(template.body(), deterministic),
            data=dict(data),
        )


def load(root: Path = ROOT) -> Library:
    """Read and check `templates/html/library.yaml` against the files it declares."""
    manifest_path = root / MANIFEST
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    _require(isinstance(manifest, dict), f"{MANIFEST}: not a mapping")
    _require(manifest.get("schema_version") == 1, f"{MANIFEST}: schema_version must be 1")
    html_dir = manifest_path.parent
    files = sorted(p.name for p in html_dir.glob("*.html"))

    # file name -> (specificity, declaration, family); an exact `file` entry beats a pattern.
    chosen: dict[str, tuple[int, dict[str, Any], dict[str, Any]]] = {}
    family_ids: set[str] = set()
    for family in manifest.get("families") or []:
        fid = family.get("id")
        _require(isinstance(fid, str) and fid not in family_ids, f"bad or duplicate family {fid!r}")
        family_ids.add(fid)
        generator = family.get("generator")
        _require(
            generator is None or (root / generator).is_file(),
            f"{fid}: generator {generator} does not exist",
        )
        styles = family.get("inline_styles")
        if styles is not None:
            for name in styles.get("files") or []:
                _require((root / name).is_file(), f"{fid}: stylesheet {name} does not exist")
        for entry in family.get("templates") or []:
            has_file, has_pattern = "file" in entry, "pattern" in entry
            _require(has_file != has_pattern, f"{fid}: each entry needs one of file or pattern")
            target = entry["file"] if has_file else entry["pattern"]
            if has_file:
                matches = [n for n in files if n == target]
            else:
                matches = [n for n in files if fnmatch.fnmatch(n, target)]
            _require(bool(matches), f"{fid}: {target} matches no file in templates/html/")
            population = entry.get("population")
            _require(
                population in POPULATION_METHODS,
                f"{fid}: {target}: population must be one of {', '.join(POPULATION_METHODS)}",
            )
            _require(
                ("ai_slots" in entry) == (population == "both"),
                f"{fid}: {target}: ai_slots is required for both and allowed only there",
            )
            rank = 2 if has_file else 1
            for name in matches:
                current = chosen.get(name)
                _require(
                    current is None or current[0] != rank,
                    f"{name} is declared twice at the same level",
                )
                if current is None or rank > current[0]:
                    chosen[name] = (rank, entry, family)

    undeclared = [n for n in files if n not in chosen]
    _require(not undeclared, f"undeclared template(s): {', '.join(undeclared)}")

    templates: dict[str, Template] = {}
    for name, (_rank, entry, family) in sorted(chosen.items()):
        path = html_dir / name
        text = path.read_text(encoding="utf-8")
        body = _LEADING_COMMENT.sub("", text, count=1)
        slots = _slots(body)
        ai_slots = tuple(entry.get("ai_slots") or ())
        stray = sorted(set(ai_slots) - set(slots))
        _require(not stray, f"{name}: ai_slots not in the template: {', '.join(stray)}")
        styles = family.get("inline_styles")
        templates[name] = Template(
            name=name,
            family=family["id"],
            population=entry["population"],
            ai_slots=ai_slots,
            reference=bool(entry.get("reference", False)),
            page=body.lstrip().lower().startswith("<!doctype html"),
            slots=slots,
            generator=family.get("generator"),
            inline_styles=(
                InlineStyles(
                    tuple(styles.get("files") or ()),
                    str(styles.get("separator", "")),
                    bool(styles.get("strip_comments", False)),
                )
                if styles is not None
                else None
            ),
            path=path,
        )
    return Library(templates, root)


def _describe(template: Template) -> dict[str, Any]:
    return {
        "template": template.name,
        "family": template.family,
        "population": template.population,
        "ai_slots": list(template.ai_slots),
        "reference": template.reference,
        "page": template.page,
        "slots": list(template.slots),
        "generator": template.generator,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="every declared template, one JSON object per line")
    show = commands.add_parser("show", help="one template's declaration and slots, as JSON")
    show.add_argument("template")
    render = commands.add_parser(
        "render", help="render a template from a JSON object of slot values"
    )
    render.add_argument("template")
    render.add_argument("--data", type=Path, required=True, help="JSON object: slot -> text")
    render.add_argument("--out", type=Path, required=True, help="page, or brief (JSON) for AI")
    args = parser.parse_args(argv)

    try:
        library = load(ROOT)
        if args.command == "list":
            for template in library.templates.values():
                print(json.dumps(_describe(template), sort_keys=True))
            return 0
        if args.command == "show":
            print(json.dumps(_describe(library.get(args.template)), indent=2, sort_keys=True))
            return 0
        data = json.loads(args.data.read_text(encoding="utf-8"))
        _require(
            isinstance(data, dict) and all(isinstance(v, str) for v in data.values()),
            "--data must be a JSON object of slot names to strings",
        )
        result = library.render(args.template, data)
    except LibraryError as exc:
        print(f"template_library: {exc}", file=sys.stderr)
        return 1

    if isinstance(result, Rendered):
        args.out.write_text(result.html, encoding="utf-8")
        print(f"rendered {args.template} -> {args.out}")
    else:
        args.out.write_text(result.to_json() + "\n", encoding="utf-8")
        print(
            f"{args.template} is populated by {result.population}; "
            f"wrote an adaptation brief -> {args.out}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
