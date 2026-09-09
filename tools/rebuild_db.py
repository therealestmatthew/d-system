#!/usr/bin/env python3
"""Rebuild DuckDB from entity JSON files and brain/ Markdown memories.

Run after editing any source files:
    uv run python tools/rebuild_db.py

Every source file is validated first. The rebuild drops every table before it inserts
anything, so a file that fails halfway through leaves an empty database rather than the
one it replaced; validating up front means a bad source file costs nothing.

Entity content (projects, people, commitments, tasks, ...) is read from
`D_SYSTEM_DATA_ROOT` if set, else the tracked `_data/` — see `data_root()` in
`src/db/source_validation.py` and ADR-009. `tags.json`, `ideas.jsonl` and `brain/` are
shared structure, not portfolio content, and are always read from the tracked tree.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import duckdb
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.ideas import fold as fold_ideas  # noqa: E402
from src.db.ideas import identity as idea_identity  # noqa: E402
from src.db.source_validation import (  # noqa: E402
    data_root,
    format_errors,
    split_front_matter,
    validate_sources,
)

ROOT = Path(__file__).parent.parent
SCHEMA_SQL = ROOT / "sql" / "001_schema.sql"
CAPTURE_VIEWS_SQL = ROOT / "sql" / "003_capture_views.sql"

VIEWS_DROP_ORDER = [
    "unfiled",
    "project_last_touched",
    "project_activity",
]

TABLES_DROP_ORDER = [
    "idea_annotations",
    "idea_links",
    "ideas",
    "idea_events",
    "memories",
    "development_events",
    "waiting_on",
    "decisions",
    "interactions",
    "tasks",
    "commitments",
    "project_tags",
    "project_people",
    "tags",
    "people",
    "projects",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _glob(directory: Path, pattern: str) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern))


def _parse_memory(path: Path, root: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter + Markdown body from a brain/ entry.

    Splitting is shared with the preflight so the two cannot disagree about what a
    readable entry is. By the time this runs the preflight has already rejected the
    unreadable ones, so None here means a file that appeared after validation.
    """
    split = split_front_matter(path.read_text(encoding="utf-8"))
    if split is None:
        return None
    meta: dict[str, Any] = yaml.safe_load(split[0]) or {}
    meta["content"] = split[1].strip()
    meta["file_path"] = str(path.relative_to(root))
    return meta


def _execute_sql_file(conn: duckdb.DuckDBPyConnection, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    clean = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("--")
    )
    for stmt in (s.strip() for s in clean.split(";") if s.strip()):
        conn.execute(stmt)


def rebuild(root: Path | None = None) -> None:
    root = ROOT if root is None else root
    # tags.json and ideas.jsonl are shared structure (ADR-009) and always read from the
    # tracked _data/. Entity content honours D_SYSTEM_DATA_ROOT via entities below.
    data = root / "_data"
    entities = data_root(root)
    brain = root / "brain"
    db_path = root / "data" / "d_system.duckdb"

    # Before mkdir and before connect: a failed validation must leave the filesystem
    # exactly as it found it, including not creating data/ on a first run.
    errors = validate_sources(root)
    if errors:
        print(f"Source validation failed — {len(errors)} problem(s), nothing written:")
        print(format_errors(errors))
        raise SystemExit(1)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db_path))

    # Full drop + recreate — deterministic rebuild. Views first: DuckDB refuses to drop
    # a table a view still references.
    for view in VIEWS_DROP_ORDER:
        conn.execute(f"DROP VIEW IF EXISTS {view}")
    for table in TABLES_DROP_ORDER:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    _execute_sql_file(conn, SCHEMA_SQL)
    _execute_sql_file(conn, CAPTURE_VIEWS_SQL)

    # --- Tags ---
    tags_path = data / "tags.json"
    if tags_path.exists():
        for tag in json.loads(tags_path.read_text(encoding="utf-8")):
            conn.execute(
                "INSERT INTO tags VALUES (?, ?, ?, ?, ?, ?)",
                [
                    tag["id"], tag["label"], tag["category"],
                    tag.get("description", ""),
                    tag.get("related", []),
                    tag.get("deprecated", False),
                ],
            )

    # --- Projects ---
    for path in _glob(entities / "projects", "*.json"):
        p = _load_json(path)
        conn.execute(
            "INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                p["id"], p["name"], p["status"], p["category"], p["type"],
                p.get("description", ""),
                p.get("tags", []),
                p.get("started"), p.get("target_date"), p.get("last_reviewed"),
                p.get("review_cadence"),
                p.get("notes", ""),
            ],
        )
        for tag_id in p.get("tags", []):
            conn.execute("INSERT INTO project_tags VALUES (?, ?)", [p["id"], tag_id])

    # --- People ---
    for path in _glob(entities / "people", "*.json"):
        person = _load_json(path)
        conn.execute(
            "INSERT INTO people VALUES (?, ?, ?, ?, ?, ?)",
            [
                person["id"], person["name"], person.get("role"),
                person.get("organization"), person.get("email"),
                person.get("notes", ""),
            ],
        )
        for project_id in person.get("projects", []):
            conn.execute(
                "INSERT INTO project_people VALUES (?, ?)",
                [project_id, person["id"]],
            )

    # --- Commitments ---
    for path in _glob(entities / "commitments", "*.json"):
        c = _load_json(path)
        conn.execute(
            "INSERT INTO commitments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                c["id"], c.get("project_id"), c["description"],
                c.get("promised_to"), c.get("due_date"),
                c.get("status", "open"), c.get("priority", "medium"),
                c["created"], c.get("completed"), c.get("notes", ""),
            ],
        )

    # --- Tasks (_data/tasks/) — first-class records, no longer unpacked from a
    # commitment's embedded array. sort_order has no source once tasks are independent
    # files, so it is always 0; nothing orders by it.
    for path in _glob(entities / "tasks", "*.json"):
        t = _load_json(path)
        conn.execute(
            "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                t["id"], t.get("commitment_id"), t.get("project_id"),
                t["description"], t.get("status", "open"), t.get("priority"),
                t.get("due_date"), t["created"], t.get("completed"),
                0, t.get("tags", []), t.get("notes", ""),
            ],
        )

    # --- Interactions ---
    for path in _glob(entities / "interactions", "*.json"):
        i = _load_json(path)
        conn.execute(
            "INSERT INTO interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                i["id"], i["date"], i["type"], i["summary"], i.get("project_id"),
                i.get("participants", []), i.get("participant_names", []),
                i.get("tags", []), i.get("notes", ""),
            ],
        )

    # --- Decisions ---
    for path in _glob(entities / "decisions", "*.json"):
        d = _load_json(path)
        conn.execute(
            "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                d["id"], d["date"], d["decision"], d["rationale"],
                d.get("project_id"), d.get("interaction_id"),
                d.get("decided_by", []), d.get("decided_by_names", []),
                d.get("alternatives", []), d.get("status", "active"),
                d.get("supersedes"), d.get("tags", []), d.get("notes", ""),
            ],
        )

    # --- Waiting-on (_data/waiting-on/) ---
    for path in _glob(entities / "waiting-on", "*.json"):
        w = _load_json(path)
        conn.execute(
            "INSERT INTO waiting_on VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                w["id"], w["description"], w.get("owed_by"), w.get("project_id"),
                w["requested"], w.get("due_date"), w["status"],
                w.get("last_chased"), w.get("received"), w.get("priority"),
                w.get("tags", []), w.get("notes", ""),
            ],
        )

    # --- Development events (_data/development-events/) ---
    for path in _glob(entities / "development-events", "*.json"):
        e = _load_json(path)
        conn.execute(
            "INSERT INTO development_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                e["id"], e["date"], e["type"], e["title"], e.get("description", ""),
                e.get("project_id"), e.get("provider"), e.get("credential"),
                e.get("hours"), e.get("tags", []), e.get("notes", ""),
            ],
        )

    # --- Ideas (_data/ideas.jsonl) ---
    #
    # idea_events is loaded in file order and kept in full; `ideas` is folded from it below.
    ideas_path = data / "ideas.jsonl"
    if ideas_path.exists():
        events = [
            json.loads(line)
            for line in ideas_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        counters: dict[str, int] = {}
        for event in events:
            idea = event["idea"]
            counters[idea] = counters.get(idea, 0) + 1
            # `title`/`body`/`text` are plain strings on the event that introduces them, but a
            # field_shape object on `amended` ({"set": ..., "value": ...}) — unwrap to the value
            # for the record, same as the effective fold does when it applies the amendment.
            # `target` is a plain string on `linked`, or a link_retraction shape on `amended`
            # ({"set": true, "value": null}) — unwrapping it the same way always yields None,
            # which is exactly what a retraction records.
            title = event.get("title")
            body = event.get("body")
            text = event.get("text")
            target = event.get("target")
            promoted_to = event.get("promoted_to")
            conn.execute(
                "INSERT INTO idea_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    idea, idea_identity(event), counters[idea], event["event"], event["at"],
                    title.get("value") if isinstance(title, dict) else title,
                    body.get("value") if isinstance(body, dict) else body,
                    event.get("from"), event.get("to"),
                    [promoted_to] if isinstance(promoted_to, str) else promoted_to,
                    event.get("amends"),
                    event.get("author"), event.get("kind"),
                    text.get("value") if isinstance(text, dict) else text,
                    event.get("type"),
                    target.get("value") if isinstance(target, dict) else target,
                ],
            )

        # Folded here, not read from source, with the same replay tools/append_idea.py
        # applies before deciding whether a transition is legal — writer and projection
        # cannot disagree about what state an idea is in. validate_sources() has already
        # run this same fold as part of the preflight above, so it cannot raise here.
        folded = fold_ideas(events)
        for idea, state in folded.items():
            conn.execute(
                "INSERT INTO ideas VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    idea, state["title"], state["body"], state["status"],
                    state["created"], state["updated"],
                    state["revisits"], state["promoted_to"],
                ],
            )
            for annotation in state["annotations"]:
                conn.execute(
                    "INSERT INTO idea_annotations VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        idea, annotation["eid"], annotation["author"], annotation["kind"],
                        annotation["text"], annotation["at"],
                    ],
                )
            for link in state["links"]:
                conn.execute(
                    "INSERT INTO idea_links VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        idea, link["eid"], link["type"], link["target"],
                        link["retracted"], link["at"],
                    ],
                )

    # --- Brain memories (brain/**/*.md) ---
    for path in sorted(brain.rglob("*.md")) if brain.exists() else []:
        if path.name == "index.md":
            continue
        mem = _parse_memory(path, root)
        if not mem or "id" not in mem:
            continue
        conn.execute(
            "INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                mem["id"], mem["title"], mem["type"],
                mem.get("tags", []),
                mem.get("systems", []),
                mem.get("source_model"),
                mem.get("project"),
                mem["created"],
                mem.get("updated"),
                mem.get("confidence", "medium"),
                mem.get("related", []),
                mem.get("scope", "global"),
                mem["content"],
                mem["file_path"],
            ],
        )

    conn.close()

    # Report
    conn2 = duckdb.connect(str(db_path))
    print(f"Rebuilt: {db_path}")
    for table in [
        "projects", "people", "tags", "commitments", "tasks",
        "interactions", "decisions", "waiting_on", "development_events",
        "memories", "ideas", "idea_events", "idea_annotations", "idea_links",
    ]:
        count = conn2.execute(f"SELECT count(*) FROM {table}").fetchone()[0]  # type: ignore[index]
        print(f"  {table}: {count} rows")
    conn2.close()


if __name__ == "__main__":
    rebuild()
