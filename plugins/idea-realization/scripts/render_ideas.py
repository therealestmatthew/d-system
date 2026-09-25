# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Render the Markdown view of the idea log, priority queue first.

The log is the source; the view is generated from it. Rendering is deterministic: the same log
and priority file produce the same bytes, which is what lets ``check`` treat a hand edit as a
failure rather than a merge.

    render_ideas.py           # write the view
    render_ideas.py --check   # exit 1 if the committed view differs from a fresh render

The header is the text the scaffold seeds, so an empty log renders to exactly the seeded file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import paths
import yaml  # type: ignore[import-untyped]
from ideas import AXES, INVERSE_LINK_TYPE, IdeaError, fold, link_diagnostics, load_events

HEADER = "# Ideas\n\nGenerated from the idea log. Never edit by hand; re-render it.\n"
PATH_KEYS = ("ideas_path", "ideas_view_path", "priority_path")


def _inbound_links(state: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Derived inverse edges, keyed by the idea each one points at — never stored."""
    inbound: dict[str, list[dict[str, Any]]] = {idea: [] for idea in state}
    for idea, entry in state.items():
        for link in entry.get("links", []):
            if link["retracted"]:
                continue
            target = link["target"]
            if target in inbound:
                inbound[target].append({"type": link["type"], "source": idea})
    return inbound


def _render_annotations(entry: dict[str, Any]) -> str:
    """Notes and assessments stay visible; findings collapse so one triage run stays readable."""
    annotations = entry.get("annotations", [])
    if not annotations:
        return ""
    visible = [a for a in annotations if a["kind"] != "finding"]
    findings = [a for a in annotations if a["kind"] == "finding"]
    parts = ["\n**Annotations**\n\n"]
    for a in visible:
        parts.append(f"- **{a['kind']}** by {a['author']} ({a['at']}): {a['text']}\n")
    if findings:
        parts.append(f"\n<details>\n<summary>{len(findings)} finding(s)</summary>\n\n")
        for a in findings:
            parts.append(f"- **finding** by {a['author']} ({a['at']}): {a['text']}\n")
        parts.append("\n</details>\n")
    return "".join(parts)


def _render_links(
    idea: str, entry: dict[str, Any], inbound: dict[str, list[dict[str, Any]]]
) -> str:
    """Outbound edges to an idea or a document, then the derived inverses pointing here."""
    outbound = [link for link in entry.get("links", []) if not link["retracted"]]
    incoming = inbound.get(idea, [])
    if not outbound and not incoming:
        return ""
    parts = ["\n**Links**\n\n"]
    for link in outbound:
        if link["target"] is not None:
            parts.append(f"- {link['type']} → `{link['target']}`\n")
        else:
            parts.append(f"- {link['type']} → document `{link['target_code']}`\n")
    for edge in incoming:
        inverse = INVERSE_LINK_TYPE.get(edge["type"], edge["type"])
        parts.append(f"- {inverse} ← `{edge['source']}`\n")
    return "".join(parts)


def _render_classification(entry: dict[str, Any]) -> str:
    """The latest classification: record kind, then each axis with confidence and reason."""
    found = entry.get("classification")
    if not found:
        return ""
    parts = [
        f"\n**Classification** by {found['author']} ({found['at']}): "
        f"record kind `{found['record_kind']}`\n"
    ]
    reasons = found.get("reasons", {})
    confidence = found.get("confidence", {})
    lines = []
    if "record_kind" in reasons:
        lines.append(f"- record kind: {reasons['record_kind']}\n")
    for axis in AXES:
        if axis not in found:
            continue
        line = f"- {axis}: `{found[axis]}`"
        if axis in confidence:
            line += f" ({confidence[axis]})"
        if axis in reasons:
            line += f" — {reasons[axis]}"
        lines.append(line + "\n")
    if "lifecycle_remedy" in found:
        lines.append(f"- lifecycle remedy: `{found['lifecycle_remedy']}`\n")
    if found.get("decompose"):
        lines.append("- marked for decomposition\n")
    if found.get("tie_breaks"):
        lines.append(f"- tie-breaks applied: {', '.join(found['tie_breaks'])}\n")
    if lines:
        parts.append("\n" + "".join(lines))
    return "".join(parts)


def _closes_with(entry: dict[str, Any]) -> str:
    pointers = entry.get("closes_with") or []
    return ", ".join(f"{kind} `{value}`" for pointer in pointers for kind, value in pointer.items())


def render(state: dict[str, dict[str, Any]], next_up: list[str] | None = None) -> str:
    """The full file: priority queue first (if any), then every idea in identifier order."""
    parts = [HEADER]
    if next_up:
        parts.append("\n## Priority queue\n\nIdeas that jump the queue, in order.\n\n")
        for rank, idea in enumerate(next_up, start=1):
            title = state[idea]["title"] if idea in state else "unknown idea"
            parts.append(f"{rank}. `{idea}` — {title}\n")
    inbound = _inbound_links(state)
    for idea in sorted(state):
        entry = state[idea]
        stamp = f"**Created {entry['created']} · Status: `{entry['status']}`"
        if entry["revisits"]:
            stamp += f" · revisited {entry['revisits']}×"
        if entry["promoted_to"]:
            stamp += " · became " + ", ".join(entry["promoted_to"])
        closed = _closes_with(entry)
        if closed:
            stamp += " · closed with " + closed
        parts.append(f"\n---\n\n## {idea} · {entry['title']}\n\n{stamp}**\n\n{entry['body']}\n")
        parts.append(_render_classification(entry))
        parts.append(_render_annotations(entry))
        parts.append(_render_links(idea, entry, inbound))
    return "".join(parts)


def load_next_up(priority: Path) -> list[str]:
    """The priority file's ``next_up``, unvalidated; ``check`` is what validates it."""
    if not priority.is_file():
        return []
    data = yaml.safe_load(priority.read_text(encoding="utf-8")) or {}
    return list(data.get("next_up") or [])


def render_view(config: paths.Config) -> str:
    """What this script would write for ``config``'s log and priority file."""
    state = fold(load_events(config.path("ideas_path")))
    return render(state, load_next_up(config.path("priority_path")))


def stale_view_errors(config: paths.Config) -> list[str]:
    """One error naming the view when it differs from a fresh render; empty when current."""
    view = config.path("ideas_view_path")
    committed = view.read_text(encoding="utf-8") if view.is_file() else None
    if committed == render_view(config):
        return []
    state = "is missing" if committed is None else "differs from the rendered idea log"
    return [f"{_shown(config, view)} {state}; re-render it with render_ideas.py and commit it"]


def _shown(config: paths.Config, path: Path) -> str:
    try:
        return path.resolve().relative_to(config.root.resolve()).as_posix()
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if the view is stale")
    paths.add_arguments(parser, PATH_KEYS)
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    try:
        state = fold(load_events(config.path("ideas_path")))
        errors = stale_view_errors(config) if args.check else []
    except IdeaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for idea, messages in sorted(link_diagnostics(state).items()):
        for message in messages:
            print(f"warning: {idea}: {message}", file=sys.stderr)

    view = config.path("ideas_view_path")
    if args.check:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        if errors:
            return 1
        print(f"{_shown(config, view)} is current")
        return 0

    view.parent.mkdir(parents=True, exist_ok=True)
    view.write_text(render(state, load_next_up(config.path("priority_path"))), encoding="utf-8")
    print(f"wrote {_shown(config, view)} — {len(state)} ideas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
