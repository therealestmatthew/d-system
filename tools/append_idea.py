#!/usr/bin/env python3
"""The only sanctioned writer for `_data/ideas.jsonl`.

Ideas are an append-only event log. Nothing in it is ever edited, so a malformed line is
permanent — there is no correction path, only a longer history containing the mistake.
That is the whole reason this script exists instead of a convention: an agent formatting
its own entries will eventually format one wrongly.

The caller supplies prose. This script generates the identifier, the timestamp and the
event shape, validates the result against `schemas/idea.schema.json`, and appends it.

**There is deliberately no way to supply a timestamp.** The migration that needed one used
a separate tool which was deleted once it had run (see PLAN-016); an override living here
permanently would be one flag away from anyone reading --help, and a log whose times can be
chosen is not evidence of anything. The `at` parameters below are internal, reachable only
by import, and the CLI exposes no option that reaches them.

Usage:
    uv run python tools/append_idea.py add --title "..." --body "..."
    uv run python tools/append_idea.py add --title "..."     # body on stdin
    uv run python tools/append_idea.py add --file idea.md    # title = first line, rest = body
    uv run python tools/append_idea.py add                   # same, but from stdin
    uv run python tools/append_idea.py status 000007 reviewing
    uv run python tools/append_idea.py status 000007 promoted --promoted-to PLAN-016
    uv run python tools/append_idea.py status 000007 delivered --doc PLAN-016 --commit 0f142ce
    uv run python tools/append_idea.py status 000007 resolved --phase phase-idg-01
    uv run python tools/append_idea.py revisit 000007
    uv run python tools/append_idea.py amend 000007 --title "corrected title"
    uv run python tools/append_idea.py amend 000007 --body "corrected body"
    uv run python tools/append_idea.py annotate 000007 --author repository-owner --kind note \
        --text "..."
    uv run python tools/append_idea.py amend-annotation 000007 <eid> --text "corrected text"
    uv run python tools/append_idea.py link 000007 --type relates_to --target 000003
    uv run python tools/append_idea.py link 000007 --type relates_to --target-code PLAN-029
    uv run python tools/append_idea.py retract-link 000007 <eid>
    uv run python tools/append_idea.py classify 000007 --author agent-x --file classification.json

**`amend` corrects the idea's `created` event rather than rewriting it** — nothing in an
append-only log can be rewritten. It always targets that idea's `created` event by identity,
never a position, so the correction survives a rebase or a merge that interleaves two
branches' appended lines. Amending the same idea twice appends two corrections that both
survive (`src.db.ideas` merges a chain of amendments rather than keeping only the latest).
Title and body are the only amendable fields, and neither can be cleared — every idea must
have both.

**`status` into `delivered`, `resolved` or `absorbed` needs at least one pointer** — `--doc`,
`--phase` or `--commit`, each repeatable — naming where the delivery happened. Each must
resolve: a document code the governance registry holds, a phase id in the backlog, or a commit
in this repository's history. `promoted` is not terminal; it moves on to `delivered`.

**`annotate` adds a note, finding, assessment or lineage; it is permitted on every idea,
terminal included** — it extends the record, not the state machine (`PLAN-017.04`). A non-owner
`--author` (an agent) is restricted to `--kind finding`, so the owner's own voice in the log
stays unambiguous. `amend-annotation` corrects one annotation's text by its own `eid`
(printed when it was written); it never touches the others.

**`link` asserts a typed, one-directional edge to another idea** — `extends`, `supersedes`,
`relates_to` or `component_of` — and never mutates it afterward. `--target-code` points an
`extends` or `relates_to` edge at a governed document instead; the code must exist.
`retract-link` is the one legal amendment: it clears the target by the link's own `eid`, so the
retraction is recorded rather than the edge being silently repointed or deleted. An `extends`
cycle or a `supersedes` edge whose target is not `discarded` is flagged to stderr, never
refused — capture always wins.

**`classify` records an idea's ARCH-005 record kind and axis values** (ADR-024), read as a JSON
object from `--file` or stdin, so reasons never pass through a shell argument. The latest
classification wins; an earlier one stays in the log. Any author may classify.

**`--title`/`--body` pass prose through the calling shell as quoted arguments.** Prose
containing a backtick or `$(` is not safe there — idea 000019 was corrupted exactly this
way, by a double-quoted `--body` whose command substitution the shell evaluated before this
script ever saw the text. `--file` (or plain stdin) never puts prose in a shell argument at
all: the first line of the file/stream is the title, everything after it is the body. Prefer
it for anything longer than a short, plain-text title.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "_data" / "ideas.jsonl"
SCHEMA = ROOT / "schemas" / "idea.schema.json"

sys.path.insert(0, str(ROOT))

from src.db.ideas import (  # noqa: E402
    ANNOTATION_KINDS,
    CLASSIFICATION_FIELDS,
    CLOSING_STATES,
    DOCUMENT_LINK_TYPES,
    LINK_TYPES,
    IdeaError,
    fold,
    identity,
    legal_transitions,
    link_diagnostics,
    load_events,
    new_eid,
)
from src.governance.__main__ import document_codes  # noqa: E402

POINTER_KINDS = ("doc", "phase", "commit")


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _validator() -> Draft7Validator:
    return Draft7Validator(_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)


def validate(event: dict[str, Any]) -> None:
    """Reject an event before it reaches the log, where it would be permanent."""
    errors = sorted(_validator().iter_errors(event), key=lambda e: list(e.absolute_path))
    if errors:
        detail = "; ".join(
            f"{'.'.join(str(p) for p in e.absolute_path) or 'event'}: {e.message}"
            for e in errors
        )
        raise IdeaError(f"refusing to append an invalid event — {detail}")


def split_title_and_body(text: str) -> tuple[str, str]:
    """The safe input shape: first line is the title, the rest is the body.

    Used by both `--file` and bare stdin, so a file and a piped stream are read identically.
    """
    title, _, body = text.partition("\n")
    if not body.strip():
        raise IdeaError(
            "expected a title on the first line and the body after it — got no body"
        )
    return title.strip(), body.strip()


def _now() -> str:
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _next_id(state: dict[str, dict[str, Any]]) -> str:
    return f"{max((int(k) for k in state), default=0) + 1:06d}"


def _require(state: dict[str, dict[str, Any]], idea: str) -> dict[str, Any]:
    if idea not in state:
        raise IdeaError(f"no idea {idea} in the log")
    return state[idea]


def _phase_ids(root: Path) -> set[str]:
    backlog = yaml.safe_load((root / "docs" / "09-backlog" / "backlog.yaml").read_text("utf-8"))
    return {item["id"] for item in backlog["items"]}


def _is_commit(value: str, root: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{value}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def resolve_pointers(pointers: list[dict[str, str]], root: Path = ROOT) -> None:
    """Refuse a pointer that names nothing: a terminal state with a dangling reference is an
    assertion, which is what the pointer exists to prevent (GOV-003, 2026-09-22)."""
    codes: set[str] | None = None
    phases: set[str] | None = None
    for pointer in pointers:
        ((kind, value),) = pointer.items()
        if kind == "doc":
            codes = document_codes(root) if codes is None else codes
            if value not in codes:
                raise IdeaError(f"pointer doc {value!r} is not a governed document code")
        elif kind == "phase":
            phases = _phase_ids(root) if phases is None else phases
            if value not in phases:
                raise IdeaError(f"pointer phase {value!r} is not a phase in the backlog")
        elif not _is_commit(value, root):
            raise IdeaError(f"pointer commit {value!r} is not a commit in this repository")


def build_created(idea: str, title: str, body: str, at: str, eid: str) -> dict[str, Any]:
    return {"idea": idea, "event": "created", "at": at, "eid": eid, "title": title, "body": body}


def build_status(
    idea: str, source: str, target: str, at: str, eid: str,
    promoted_to: list[str] | None = None,
    closes_with: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "idea": idea, "event": "status", "at": at, "eid": eid, "from": source, "to": target,
    }
    if promoted_to is not None:
        event["promoted_to"] = promoted_to
    if closes_with is not None:
        event["closes_with"] = closes_with
    return event


def build_revisited(idea: str, at: str, eid: str) -> dict[str, Any]:
    return {"idea": idea, "event": "revisited", "at": at, "eid": eid}


def build_amended(
    idea: str, amends: str, at: str, eid: str,
    title: str | None = None, body: str | None = None, text: str | None = None,
    retract_target: bool = False, retract_target_code: bool = False,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "idea": idea, "event": "amended", "at": at, "eid": eid, "amends": amends,
    }
    if title is not None:
        event["title"] = {"set": True, "value": title}
    if body is not None:
        event["body"] = {"set": True, "value": body}
    if text is not None:
        event["text"] = {"set": True, "value": text}
    if retract_target:
        event["target"] = {"set": True, "value": None}
    if retract_target_code:
        event["target_code"] = {"set": True, "value": None}
    return event


def build_annotated(
    idea: str, author: str, kind: str, text: str, at: str, eid: str
) -> dict[str, Any]:
    return {
        "idea": idea, "event": "annotated", "at": at, "eid": eid,
        "author": author, "kind": kind, "text": text,
    }


def build_linked(
    idea: str, type_: str, target: str | None, at: str, eid: str, target_code: str | None = None
) -> dict[str, Any]:
    event: dict[str, Any] = {"idea": idea, "event": "linked", "at": at, "eid": eid, "type": type_}
    if target is not None:
        event["target"] = target
    if target_code is not None:
        event["target_code"] = target_code
    return event


def build_classified(
    idea: str, author: str, classification: dict[str, Any], at: str, eid: str
) -> dict[str, Any]:
    return {"idea": idea, "event": "classified", "at": at, "eid": eid, "author": author,
            **classification}


def append(event: dict[str, Any], log: Path = LOG) -> None:
    """Validate, then append one line. Nothing already in the file is read or rewritten."""
    validate(event)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def _read_add_input(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve title and body from whichever input form the caller used.

    `--file` and bare stdin share `split_title_and_body`, so prose never has to pass
    through a shell argument to reach either route.
    """
    if args.file is not None and (args.title is not None or args.body is not None):
        raise IdeaError("--file replaces --title/--body; pass one input form, not both")
    if args.file is not None:
        try:
            text = args.file.read_text(encoding="utf-8")
        except OSError as exc:
            raise IdeaError(f"cannot read {args.file}: {exc}") from exc
        return split_title_and_body(text)
    if args.title is not None:
        body = args.body if args.body is not None else sys.stdin.read()
        if not body.strip():
            raise IdeaError("an idea needs a body — pass --body or provide one on stdin")
        return args.title, body
    if args.body is not None:
        raise IdeaError("--body needs --title alongside it, or use --file/stdin for both")
    return split_title_and_body(sys.stdin.read())


def add(title: str, body: str, log: Path = LOG) -> dict[str, Any]:
    state = fold(load_events(log))
    event = build_created(_next_id(state), title.strip(), body.strip(), _now(), new_eid())
    append(event, log)
    return event


def change_status(
    idea: str, target: str, promoted_to: list[str] | None = None, log: Path = LOG,
    closes_with: list[dict[str, str]] | None = None, root: Path = ROOT,
) -> dict[str, Any]:
    state = fold(load_events(log))
    current = _require(state, idea)
    source = current["status"]

    if source == "discarded" and current["revisits"] >= 1:
        raise IdeaError(
            f"idea {idea} was discarded after being revisited — that is permanent. "
            "An idea worth a third look is a new idea; record it separately."
        )
    if (source, target) not in legal_transitions():
        raise IdeaError(
            f"illegal transition for idea {idea}: {source} -> {target}. "
            f"Legal from {source}: "
            + (", ".join(sorted(t for f, t in legal_transitions() if f == source)) or "none")
        )
    if target == "promoted" and not promoted_to:
        raise IdeaError("--promoted-to is required when promoting: name what the idea became")
    if target in CLOSING_STATES:
        if not closes_with:
            raise IdeaError(
                f"a move to {target} needs a pointer — --doc, --phase or --commit — naming "
                "where the delivery happened"
            )
        resolve_pointers(closes_with, root)
    elif closes_with:
        raise IdeaError(f"a pointer belongs to delivered, resolved or absorbed, not {target}")

    event = build_status(idea, source, target, _now(), new_eid(), promoted_to, closes_with)
    append(event, log)
    return event


def revisit(idea: str, log: Path = LOG) -> dict[str, Any]:
    state = fold(load_events(log))
    current = _require(state, idea)

    if current["status"] != "discarded":
        raise IdeaError(
            f"idea {idea} is {current['status']}, not discarded — only a discarded idea "
            "is revisited"
        )
    if current["revisits"] >= 1:
        raise IdeaError(
            f"idea {idea} was discarded after already being revisited once — that discard is "
            "permanent, because once is the limit. Something worth revisiting twice needs "
            "recording as its own idea, where the second thought stays legible instead of "
            "being buried in the first one's history."
        )

    event = build_revisited(idea, _now(), new_eid())
    append(event, log)
    return event


def _created_event(events: list[dict[str, Any]], idea: str) -> dict[str, Any]:
    for event in events:
        if event["idea"] == idea and event["event"] == "created":
            return event
    raise IdeaError(f"no idea {idea} in the log")


def amend(
    idea: str, title: str | None = None, body: str | None = None, log: Path = LOG
) -> dict[str, Any]:
    """Correct `idea`'s `created` event without rewriting it.

    Always targets the `created` event by identity, however many times it has already been
    amended — a chain of corrections to the same target merges (`src.db.ideas.fold`), so this
    never needs to know which prior amendment, if any, last touched the field it is fixing.
    """
    if title is None and body is None:
        raise IdeaError("an amendment must correct at least one of --title or --body")
    events = load_events(log)
    target = _created_event(events, idea)
    event = build_amended(
        idea,
        identity(target),
        _now(),
        new_eid(),
        title.strip() if title is not None else None,
        body.strip() if body is not None else None,
    )
    validate(event)
    fold(events + [event])  # re-validates the whole history with this amendment included
    append(event, log)
    return event


def annotate(
    idea: str, author: str, kind: str, text: str, log: Path = LOG
) -> dict[str, Any]:
    """Add a note, finding or assessment to `idea` — permitted whatever its status.

    A non-owner `author` (an agent) is restricted to `kind: finding`, so the owner's own
    voice in the log stays unambiguous (`PLAN-017.04`, settled 2026-09-08).
    """
    state = fold(load_events(log))
    _require(state, idea)
    if kind not in ANNOTATION_KINDS:
        raise IdeaError(f"unknown annotation kind {kind!r} — expected one of {ANNOTATION_KINDS}")
    if author != "repository-owner" and kind != "finding":
        raise IdeaError(
            f"agent author {author!r} may only write kind=finding, not {kind!r} — "
            "note and assessment stay the owner's own voice"
        )
    event = build_annotated(idea, author, kind, text.strip(), _now(), new_eid())
    append(event, log)
    return event


def amend_annotation(idea: str, eid: str, text: str, log: Path = LOG) -> dict[str, Any]:
    """Correct one annotation's text by its own identity; the others are untouched."""
    events = load_events(log)
    state = fold(events)
    _require(state, idea)
    if not any(
        e["idea"] == idea and e["event"] == "annotated" and identity(e) == eid for e in events
    ):
        raise IdeaError(f"no annotation {eid!r} on idea {idea}")
    event = build_amended(idea, eid, _now(), new_eid(), text=text.strip())
    validate(event)
    fold(events + [event])
    append(event, log)
    return event


def link(
    idea: str, type_: str, target: str | None, log: Path = LOG,
    target_code: str | None = None, root: Path = ROOT,
) -> tuple[dict[str, Any], list[str]]:
    """Assert a typed edge from `idea` to another idea `target`, or to a document `target_code`.

    Never refused for a cycle or a stale supersession — those are fold-time diagnostics
    (`link_diagnostics`), returned alongside the appended event rather than blocking it
    (`ADR-010`'s capture-always-wins principle, extended to links).
    """
    events = load_events(log)
    state = fold(events)
    _require(state, idea)
    if type_ not in LINK_TYPES:
        raise IdeaError(f"unknown link type {type_!r} — expected one of {LINK_TYPES}")
    if (target is None) == (target_code is None):
        raise IdeaError("a link names exactly one of --target (an idea) or --target-code")
    if target_code is not None:
        if type_ not in DOCUMENT_LINK_TYPES:
            raise IdeaError(
                f"a {type_} link cannot point at a document — only {DOCUMENT_LINK_TYPES} can"
            )
        if target_code not in document_codes(root):
            raise IdeaError(f"link target {target_code!r} is not a governed document code")
    elif target == idea:
        raise IdeaError(f"idea {idea} cannot link to itself")
    elif target not in state:
        raise IdeaError(f"link target {target!r} is not a known idea")
    event = build_linked(idea, type_, target, _now(), new_eid(), target_code)
    validate(event)
    new_state = fold(events + [event])
    diagnostics = link_diagnostics(new_state).get(idea, [])
    append(event, log)
    return event, diagnostics


def retract_link(idea: str, eid: str, log: Path = LOG) -> dict[str, Any]:
    """Clear a link's target by its own identity — the one legal amendment to a link."""
    events = load_events(log)
    state = fold(events)
    _require(state, idea)
    linked = next(
        (e for e in events
         if e["idea"] == idea and e["event"] == "linked" and identity(e) == eid),
        None,
    )
    if linked is None:
        raise IdeaError(f"no link {eid!r} on idea {idea}")
    to_document = "target_code" in linked
    event = build_amended(
        idea, eid, _now(), new_eid(),
        retract_target=not to_document, retract_target_code=to_document,
    )
    validate(event)
    fold(events + [event])
    append(event, log)
    return event


def classify(
    idea: str, author: str, classification: dict[str, Any], log: Path = LOG
) -> dict[str, Any]:
    """Record `idea`'s ARCH-005 classification (ADR-024). The schema enforces its shape: a
    knowledge record carries a value, a reason and a confidence on each of the four axes, and
    any other record kind carries none."""
    state = fold(load_events(log))
    _require(state, idea)
    unknown = sorted(set(classification) - set(CLASSIFICATION_FIELDS))
    if unknown:
        raise IdeaError(
            f"not classification fields: {', '.join(unknown)} — expected some of "
            f"{', '.join(CLASSIFICATION_FIELDS)}"
        )
    event = build_classified(idea, author, classification, _now(), new_eid())
    append(event, log)
    return event


def _read_classification(path: Path | None) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8") if path is not None else sys.stdin.read()
    except OSError as exc:
        raise IdeaError(f"cannot read {path}: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IdeaError(f"the classification is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise IdeaError("the classification must be a JSON object")
    return data


def _pointers(args: argparse.Namespace) -> list[dict[str, str]] | None:
    pointers = [
        {kind: value} for kind in POINTER_KINDS for value in (getattr(args, kind) or [])
    ]
    return pointers or None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Append an event to the idea log. Timestamps are generated, never supplied."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("add", help="record a new idea")
    new.add_argument(
        "--title", help="one-line summary; omit to read title and body together (see --file)"
    )
    new.add_argument("--body", help="the idea in full; read from stdin when omitted")
    new.add_argument(
        "--file",
        type=Path,
        help=(
            "read the title (first line) and body (the rest) from a file — bypasses the "
            "shell entirely, so it is the safe route for prose that might contain "
            "backticks, $(...), quotes or newlines"
        ),
    )

    moved = sub.add_parser("status", help="move an idea's status")
    moved.add_argument("idea", help="six-digit idea id")
    moved.add_argument("to", choices=sorted({t for _, t in legal_transitions()}))
    moved.add_argument(
        "--promoted-to", nargs="+",
        help="one or more governed document codes, required when promoting",
    )
    for kind, what in (
        ("doc", "a governed document code"),
        ("phase", "a backlog phase id"),
        ("commit", "a commit hash in this repository"),
    ):
        moved.add_argument(
            f"--{kind}", action="append",
            help=f"{what} where the delivery happened; repeatable. delivered, resolved and "
            "absorbed need at least one pointer",
        )

    again = sub.add_parser("revisit", help="reopen a discarded idea; permitted once")
    again.add_argument("idea", help="six-digit idea id")

    corrected = sub.add_parser(
        "amend", help="correct an idea's title and/or body without rewriting it"
    )
    corrected.add_argument("idea", help="six-digit idea id")
    corrected.add_argument("--title", help="the corrected title")
    corrected.add_argument("--body", help="the corrected body")

    annotated = sub.add_parser(
        "annotate", help="add a note, finding, assessment or lineage; permitted on any idea"
    )
    annotated.add_argument("idea", help="six-digit idea id")
    annotated.add_argument("--author", required=True, help="repository-owner or an agent name")
    annotated.add_argument("--kind", required=True, choices=ANNOTATION_KINDS)
    annotated.add_argument("--text", required=True, help="the contribution itself")

    annotation_fix = sub.add_parser(
        "amend-annotation", help="correct one annotation's text by its own identity"
    )
    annotation_fix.add_argument("idea", help="six-digit idea id")
    annotation_fix.add_argument("eid", help="identity of the annotation to correct")
    annotation_fix.add_argument("--text", required=True, help="the corrected text")

    linked = sub.add_parser("link", help="assert a typed edge to another idea")
    linked.add_argument("idea", help="six-digit idea id")
    linked.add_argument("--type", required=True, dest="type_", choices=LINK_TYPES)
    linked_target = linked.add_mutually_exclusive_group(required=True)
    linked_target.add_argument("--target", help="six-digit idea id this edge points to")
    linked_target.add_argument(
        "--target-code",
        help="governed document code this edge points to; extends and relates_to only",
    )

    retracted = sub.add_parser(
        "retract-link", help="clear a link's target by its own identity — never repoint one"
    )
    retracted.add_argument("idea", help="six-digit idea id")
    retracted.add_argument("eid", help="identity of the link to retract")

    classified = sub.add_parser(
        "classify", help="record an idea's ARCH-005 record kind and axis values"
    )
    classified.add_argument("idea", help="six-digit idea id")
    classified.add_argument("--author", required=True, help="repository-owner or an agent name")
    classified.add_argument(
        "--file", type=Path,
        help="a JSON object of classification fields; read from stdin when omitted",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    diagnostics: list[str] = []
    try:
        if args.command == "add":
            title, body = _read_add_input(args)
            event = add(title, body, log=LOG)
        elif args.command == "status":
            event = change_status(
                args.idea, args.to, args.promoted_to, log=LOG, closes_with=_pointers(args)
            )
        elif args.command == "revisit":
            event = revisit(args.idea, log=LOG)
        elif args.command == "amend":
            event = amend(args.idea, args.title, args.body, log=LOG)
        elif args.command == "annotate":
            event = annotate(args.idea, args.author, args.kind, args.text, log=LOG)
        elif args.command == "amend-annotation":
            event = amend_annotation(args.idea, args.eid, args.text, log=LOG)
        elif args.command == "link":
            event, diagnostics = link(
                args.idea, args.type_, args.target, log=LOG, target_code=args.target_code
            )
        elif args.command == "classify":
            classification = _read_classification(args.file)
            event = classify(args.idea, args.author, classification, log=LOG)
        else:
            event = retract_link(args.idea, args.eid, log=LOG)
    except IdeaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"{event['event']} {event['idea']} at {event['at']}")
    for diagnostic in diagnostics:
        print(f"warning: {diagnostic}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
