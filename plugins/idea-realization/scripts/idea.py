# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""The only sanctioned writer for the idea log.

Ideas are an append-only event log. Nothing in it is ever edited, so a malformed line is
permanent — there is no correction path, only a longer history containing the mistake.
That is the whole reason this script exists instead of a convention: an agent formatting
its own entries will eventually format one wrongly.

The caller supplies prose. This script generates the identifier, the timestamp and the
event shape, validates the result against the plugin's ``schemas/idea.schema.json``, and
appends it.

**There is deliberately no way to supply a timestamp.** A log whose times can be chosen is
not evidence of anything. The ``at`` values below are generated internally and the CLI
exposes no option that reaches them.

Usage (every subcommand also takes ``--root``, ``--ideas-path``, ``--docs-root``,
``--backlog-path`` and ``--exempt-files``):

    idea.py add --file idea.md          # title = first line, rest = body
    idea.py add                         # same, from stdin
    idea.py add --title "..." --body "..."
    idea.py status <id> reviewing
    idea.py status <id> promoted --promoted-to <document code>
    idea.py status <id> delivered --doc <document code> --commit <hash>
    idea.py revisit <id>
    idea.py amend <id> --title "corrected title"
    idea.py annotate <id> --author repository-owner --kind note --file note.txt
    idea.py amend-annotation <id> <eid> --file corrected.txt
    idea.py link <id> --type relates_to --target <other id>
    idea.py link <id> --type relates_to --target-code <document code>
    idea.py retract-link <id> <eid>
    idea.py classify <id> --author <name> --file classification.json
    idea.py list [--status open]        # read-only: id, status and effective title
    idea.py show <id>                   # read-only: one idea's folded state as JSON

**``amend`` corrects the idea's ``created`` event rather than rewriting it** — nothing in an
append-only log can be rewritten. It always targets that idea's ``created`` event by identity,
never a position, so the correction survives a rebase or a merge that interleaves two
branches' appended lines. Amending the same idea twice appends two corrections that both
survive (the fold merges a chain of amendments rather than keeping only the latest). Title
and body are the only amendable fields, and neither can be cleared — every idea must have
both.

**``status`` into ``delivered``, ``resolved`` or ``absorbed`` needs at least one pointer** —
``--doc``, ``--phase`` or ``--commit``, each repeatable — naming where the delivery happened.
Each must resolve: a code carried by a governed document under the document root, a phase id
in the backlog, or a commit in the repository's history. ``promoted`` is not terminal; it
moves on to ``delivered``.

**``annotate`` adds a note, finding, assessment or lineage; it is permitted on every idea,
terminal included** — it extends the record, not the state machine. A non-owner ``--author``
(an agent) is restricted to ``--kind finding``, so the owner's own voice in the log stays
unambiguous. ``amend-annotation`` corrects one annotation's text by its own ``eid`` (printed
when it was written); it never touches the others.

**``link`` asserts a typed, one-directional edge to another idea** — ``extends``,
``supersedes``, ``relates_to`` or ``component_of`` — and never mutates it afterward.
``--target-code`` points an ``extends`` or ``relates_to`` edge at a governed document instead;
the code must exist. ``retract-link`` is the one legal amendment: it clears the target by the
link's own ``eid``, so the retraction is recorded rather than the edge being silently repointed
or deleted. An ``extends`` cycle or a ``supersedes`` edge whose target is not ``discarded`` is
flagged to stderr, never refused — capture always wins.

**``classify`` records an idea's record kind and axis values**, read as a JSON object from
``--file`` or stdin, so reasons never pass through a shell argument. The latest classification
wins; an earlier one stays in the log. Any author may classify.

**Prose never belongs in a shell argument.** A ``--title``, ``--body`` or ``--text`` containing a
backtick or ``$(`` is evaluated by the calling shell before this script sees it, and the log
keeps whatever the shell produced. ``--file`` (or plain stdin) never puts prose in a shell
argument at all. Prefer it for anything longer than a short, plain-text title.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import paths
import yaml  # type: ignore[import-untyped]
from ideas import (
    ANNOTATION_KINDS,
    CLASSIFICATION_FIELDS,
    CLOSING_STATES,
    DOCUMENT_LINK_TYPES,
    LINK_TYPES,
    OWNER,
    SCHEMA,
    IdeaError,
    fold,
    identity,
    legal_transitions,
    link_diagnostics,
    load_events,
    new_eid,
)
from jsonschema import Draft7Validator  # type: ignore[import-untyped]

POINTER_KINDS = ("doc", "phase", "commit")
PATH_KEYS = ("ideas_path", "docs_root", "backlog_path", "exempt_files")


def _validator() -> Draft7Validator:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return Draft7Validator(schema, format_checker=Draft7Validator.FORMAT_CHECKER)


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


# --- What a pointer or a document link may name --------------------------------------------


def _front_matter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    loaded = yaml.safe_load(text[4:end])
    return loaded if isinstance(loaded, dict) else {}


def document_codes(docs_root: Path, exempt: tuple[Path, ...] = ()) -> set[str]:
    """Every `code` a Markdown file under `docs_root` declares in its front matter.

    A file whose front matter does not parse is skipped here; the document check is what
    reports it. Exempt files carry no front matter by definition and are not read.
    """
    skipped = {path.resolve() for path in exempt}
    codes: set[str] = set()
    if not docs_root.is_dir():
        return codes
    for path in sorted(docs_root.rglob("*.md")):
        if path.resolve() in skipped:
            continue
        try:
            meta = _front_matter(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            continue
        if isinstance(meta.get("code"), str):
            codes.add(meta["code"])
    return codes


def phase_ids(backlog: Path) -> set[str]:
    """Every phase id in the backlog; a missing or empty backlog has none."""
    if not backlog.is_file():
        return set()
    data = yaml.safe_load(backlog.read_text(encoding="utf-8")) or {}
    return {item["id"] for item in data.get("items") or [] if isinstance(item, dict)}


def _is_commit(value: str, root: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{value}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def resolve_pointers(pointers: list[dict[str, str]], config: paths.Config) -> None:
    """Refuse a pointer that names nothing: a terminal state with a dangling reference is an
    assertion, which is what the pointer exists to prevent."""
    codes: set[str] | None = None
    phases: set[str] | None = None
    for pointer in pointers:
        ((kind, value),) = pointer.items()
        if kind == "doc":
            codes = _codes(config) if codes is None else codes
            if value not in codes:
                raise IdeaError(f"pointer doc {value!r} is not a governed document code")
        elif kind == "phase":
            phases = phase_ids(config.path("backlog_path")) if phases is None else phases
            if value not in phases:
                raise IdeaError(f"pointer phase {value!r} is not a phase in the backlog")
        elif not _is_commit(value, config.root):
            raise IdeaError(f"pointer commit {value!r} is not a commit in this repository")


def _codes(config: paths.Config) -> set[str]:
    return document_codes(config.path("docs_root"), tuple(config.paths("exempt_files")))


# --- Event shapes ---------------------------------------------------------------------------


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


def append(event: dict[str, Any], log: Path) -> None:
    """Validate, then append one line. Nothing already in the file is read or rewritten."""
    validate(event)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


# --- Operations -----------------------------------------------------------------------------


def add(title: str, body: str, log: Path) -> dict[str, Any]:
    state = fold(load_events(log))
    event = build_created(_next_id(state), title.strip(), body.strip(), _now(), new_eid())
    append(event, log)
    return event


def change_status(
    idea: str, target: str, promoted_to: list[str] | None = None, *, log: Path,
    closes_with: list[dict[str, str]] | None = None, config: paths.Config | None = None,
) -> dict[str, Any]:
    state = fold(load_events(log))
    current = _require(state, idea)
    source = current["status"]
    transitions = legal_transitions()

    if source == "discarded" and current["revisits"] >= 1:
        raise IdeaError(
            f"idea {idea} was discarded after being revisited — that is permanent. "
            "An idea worth a third look is a new idea; record it separately."
        )
    if (source, target) not in transitions:
        raise IdeaError(
            f"illegal transition for idea {idea}: {source} -> {target}. "
            f"Legal from {source}: "
            + (", ".join(sorted(t for f, t in transitions if f == source)) or "none")
        )
    if target == "promoted" and not promoted_to:
        raise IdeaError("--promoted-to is required when promoting: name what the idea became")
    if target in CLOSING_STATES:
        if not closes_with:
            raise IdeaError(
                f"a move to {target} needs a pointer — --doc, --phase or --commit — naming "
                "where the delivery happened"
            )
        resolve_pointers(closes_with, config or paths.resolve())
    elif closes_with:
        raise IdeaError(f"a pointer belongs to delivered, resolved or absorbed, not {target}")

    event = build_status(idea, source, target, _now(), new_eid(), promoted_to, closes_with)
    append(event, log)
    return event


def revisit(idea: str, log: Path) -> dict[str, Any]:
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
    idea: str, title: str | None = None, body: str | None = None, *, log: Path
) -> dict[str, Any]:
    """Correct `idea`'s `created` event without rewriting it.

    Always targets the `created` event by identity, however many times it has already been
    amended — a chain of corrections to the same target merges in the fold, so this never
    needs to know which prior amendment, if any, last touched the field it is fixing.
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


def annotate(idea: str, author: str, kind: str, text: str, log: Path) -> dict[str, Any]:
    """Add a note, finding, assessment or lineage to `idea` — permitted whatever its status.

    A non-owner `author` (an agent) is restricted to `kind: finding`, so the owner's own
    voice in the log stays unambiguous.
    """
    state = fold(load_events(log))
    _require(state, idea)
    if kind not in ANNOTATION_KINDS:
        raise IdeaError(f"unknown annotation kind {kind!r} — expected one of {ANNOTATION_KINDS}")
    if author != OWNER and kind != "finding":
        raise IdeaError(
            f"agent author {author!r} may only write kind=finding, not {kind!r} — "
            "note, assessment and lineage stay the owner's own voice"
        )
    event = build_annotated(idea, author, kind, text.strip(), _now(), new_eid())
    append(event, log)
    return event


def amend_annotation(idea: str, eid: str, text: str, log: Path) -> dict[str, Any]:
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
    idea: str, type_: str, target: str | None, *, log: Path,
    target_code: str | None = None, config: paths.Config | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Assert a typed edge from `idea` to another idea `target`, or to a document `target_code`.

    Never refused for a cycle or a stale supersession — those are fold-time diagnostics
    (`link_diagnostics`), returned alongside the appended event rather than blocking it:
    capture always wins, for links as for ideas.
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
        if target_code not in _codes(config or paths.resolve()):
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


def retract_link(idea: str, eid: str, log: Path) -> dict[str, Any]:
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
    idea: str, author: str, classification: dict[str, Any], log: Path
) -> dict[str, Any]:
    """Record `idea`'s classification. The schema enforces its shape: a knowledge record
    carries a value, a reason and a confidence on each of the four axes, and any other record
    kind carries none."""
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


# --- Command line ---------------------------------------------------------------------------


def _read_text(path: Path | None) -> str:
    try:
        return path.read_text(encoding="utf-8") if path is not None else sys.stdin.read()
    except OSError as exc:
        raise IdeaError(f"cannot read {path}: {exc}") from exc


def _read_add_input(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve title and body from whichever input form the caller used.

    `--file` and bare stdin share `split_title_and_body`, so prose never has to pass
    through a shell argument to reach either route.
    """
    if args.file is not None and (args.title is not None or args.body is not None):
        raise IdeaError("--file replaces --title/--body; pass one input form, not both")
    if args.file is not None:
        return split_title_and_body(_read_text(args.file))
    if args.title is not None:
        body = args.body if args.body is not None else sys.stdin.read()
        if not body.strip():
            raise IdeaError("an idea needs a body — pass --body or provide one on stdin")
        return args.title, body
    if args.body is not None:
        raise IdeaError("--body needs --title alongside it, or use --file/stdin for both")
    return split_title_and_body(sys.stdin.read())


def _read_annotation_text(args: argparse.Namespace) -> str:
    """`--text` or `--file`, exactly one; the file route keeps prose out of the shell."""
    if (args.text is None) == (args.file is None):
        raise IdeaError("pass exactly one of --text or --file")
    text: str = args.text if args.text is not None else _read_text(args.file)
    if not text.strip():
        raise IdeaError("an annotation needs text")
    return text


def _read_classification(path: Path | None) -> dict[str, Any]:
    try:
        data = json.loads(_read_text(path))
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


def list_ideas(log: Path, status: str | None = None) -> list[str]:
    """One line per idea, in id order: id, status and effective title."""
    state = fold(load_events(log))
    return [
        f"{idea} | {entry['status']} | {entry['title']}"
        for idea, entry in sorted(state.items())
        if status is None or entry["status"] == status
    ]


def _parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    paths.add_arguments(common, PATH_KEYS)
    parser = argparse.ArgumentParser(
        description="Append an event to the idea log. Timestamps are generated, never supplied."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def command(name: str, help_text: str) -> argparse.ArgumentParser:
        return sub.add_parser(name, help=help_text, parents=[common])

    new = command("add", "record a new idea")
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

    moved = command("status", "move an idea's status")
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

    again = command("revisit", "reopen a discarded idea; permitted once")
    again.add_argument("idea", help="six-digit idea id")

    corrected = command("amend", "correct an idea's title and/or body without rewriting it")
    corrected.add_argument("idea", help="six-digit idea id")
    corrected.add_argument("--title", help="the corrected title")
    corrected.add_argument("--body", help="the corrected body")

    annotated = command(
        "annotate", "add a note, finding, assessment or lineage; permitted on any idea"
    )
    annotated.add_argument("idea", help="six-digit idea id")
    annotated.add_argument("--author", required=True, help=f"{OWNER} or an agent name")
    annotated.add_argument("--kind", required=True, choices=ANNOTATION_KINDS)
    annotated.add_argument("--text", help="the contribution itself, for short plain text")
    annotated.add_argument("--file", type=Path, help="read the contribution from a file")

    annotation_fix = command(
        "amend-annotation", "correct one annotation's text by its own identity"
    )
    annotation_fix.add_argument("idea", help="six-digit idea id")
    annotation_fix.add_argument("eid", help="identity of the annotation to correct")
    annotation_fix.add_argument("--text", help="the corrected text, for short plain text")
    annotation_fix.add_argument("--file", type=Path, help="read the corrected text from a file")

    linked = command("link", "assert a typed edge to another idea")
    linked.add_argument("idea", help="six-digit idea id")
    linked.add_argument("--type", required=True, dest="type_", choices=LINK_TYPES)
    linked_target = linked.add_mutually_exclusive_group(required=True)
    linked_target.add_argument("--target", help="six-digit idea id this edge points to")
    linked_target.add_argument(
        "--target-code",
        help="governed document code this edge points to; extends and relates_to only",
    )

    retracted = command(
        "retract-link", "clear a link's target by its own identity — never repoint one"
    )
    retracted.add_argument("idea", help="six-digit idea id")
    retracted.add_argument("eid", help="identity of the link to retract")

    classified = command("classify", "record an idea's record kind and axis values")
    classified.add_argument("idea", help="six-digit idea id")
    classified.add_argument("--author", required=True, help=f"{OWNER} or an agent name")
    classified.add_argument(
        "--file", type=Path,
        help="a JSON object of classification fields; read from stdin when omitted",
    )

    listed = command("list", "print every idea's id, status and effective title; writes nothing")
    listed.add_argument("--status", help="only ideas in this status")

    shown = command("show", "print one idea's folded state as JSON; writes nothing")
    shown.add_argument("idea", help="six-digit idea id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = paths.resolve(args)
    log = config.path("ideas_path")
    diagnostics: list[str] = []
    try:
        if args.command == "list":
            for line in list_ideas(log, args.status):
                print(line)
            return 0
        if args.command == "show":
            state = fold(load_events(log))
            print(json.dumps(_require(state, args.idea), ensure_ascii=False, indent=2))
            return 0
        if args.command == "add":
            title, body = _read_add_input(args)
            event = add(title, body, log)
        elif args.command == "status":
            event = change_status(
                args.idea, args.to, args.promoted_to, log=log, closes_with=_pointers(args),
                config=config,
            )
        elif args.command == "revisit":
            event = revisit(args.idea, log)
        elif args.command == "amend":
            event = amend(args.idea, args.title, args.body, log=log)
        elif args.command == "annotate":
            event = annotate(args.idea, args.author, args.kind, _read_annotation_text(args), log)
        elif args.command == "amend-annotation":
            event = amend_annotation(args.idea, args.eid, _read_annotation_text(args), log)
        elif args.command == "link":
            event, diagnostics = link(
                args.idea, args.type_, args.target, log=log, target_code=args.target_code,
                config=config,
            )
        elif args.command == "classify":
            classification = _read_classification(args.file)
            event = classify(args.idea, args.author, classification, log)
        else:
            event = retract_link(args.idea, args.eid, log)
    except IdeaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"{event['event']} {event['idea']} at {event['at']} eid {event['eid']}")
    for diagnostic in diagnostics:
        print(f"warning: {diagnostic}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
