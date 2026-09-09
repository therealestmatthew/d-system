#!/usr/bin/env python3
"""Load relevant brain memories into a formatted context block for any AI model.

Output is plain Markdown — paste into Claude, GPT-4o, Gemini, or any other model.

Usage:
    uv run python tools/load_context.py --query "DuckDB connection pattern"
    uv run python tools/load_context.py --project example-project
    uv run python tools/load_context.py --type procedure
    uv run python tools/load_context.py --tags python,frameworks
    uv run python tools/load_context.py --system sys-backlog
    uv run python tools/load_context.py --query "memory" --type concept --limit 5
    uv run python tools/load_context.py --all
"""

from __future__ import annotations

import argparse
import textwrap
from datetime import date
from pathlib import Path

import duckdb

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "d_system.duckdb"


def build_where(
    query: str | None,
    project: str | None,
    mem_type: str | None,
    tags: list[str],
    system: str | None = None,
) -> tuple[str, list[object]]:
    clauses: list[str] = []
    params: list[object] = []

    if query:
        clauses.append("(LOWER(title) LIKE LOWER(?) OR LOWER(content) LIKE LOWER(?))")
        pattern = f"%{query}%"
        params.extend([pattern, pattern])

    if project:
        clauses.append("(project_id = ? OR project_id IS NULL)")
        params.append(project)

    if mem_type:
        clauses.append("type = ?")
        params.append(mem_type)

    for tag in tags:
        clauses.append("list_contains(tags, ?)")
        params.append(tag)

    if system:
        clauses.append("list_contains(systems, ?)")
        params.append(system)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params


def format_memory(row: tuple) -> str:  # type: ignore[type-arg]
    id_, title, type_, confidence, project_id, created, content, file_path = row
    scope_line = f"project:{project_id}" if project_id else "global"
    header = f"### [{type_.upper()}] {title}"
    meta = f"*id:{id_} | {scope_line} | confidence:{confidence} | {file_path}*"
    body = textwrap.indent(content.strip(), "  ")
    return f"{header}\n{meta}\n\n{body}"


def load(
    query: str | None = None,
    project: str | None = None,
    mem_type: str | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
    all_memories: bool = False,
    system: str | None = None,
) -> str:
    if not DB_PATH.exists():
        return "Database not found. Run: uv run python tools/rebuild_db.py"

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    if all_memories:
        where, params = "", []
    else:
        where, params = build_where(query, project, mem_type, tags or [], system)

    sql = f"""
        SELECT id, title, type, confidence, project_id, created, content, file_path
        FROM memories
        {where}
        ORDER BY
            CASE confidence WHEN 'high' THEN 0 WHEN 'medium' THEN 1 WHEN 'low' THEN 2 ELSE 3 END,
            created DESC
        LIMIT {limit}
    """
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    if not rows:
        return "No memories matched the query."

    parts = [
        "## Loaded Context — d-system Brain",
        f"*Retrieved: {len(rows)} {'memory' if len(rows) == 1 else 'memories'} | {date.today()}*",
        f"*Query: query={query!r} project={project!r} type={mem_type!r} "
        f"tags={tags} system={system!r}*",
        "---",
    ]
    parts.extend(format_memory(r) for r in rows)
    parts.append("---\n*End of loaded context*")
    return "\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load brain memories as AI context")
    parser.add_argument("--query", "-q", help="Keyword search across title and content")
    parser.add_argument("--project", "-p", help="Filter by project ID (also includes globals)")
    parser.add_argument("--type", "-t", dest="mem_type",
                        choices=["concept", "entity", "procedure", "episode", "decision"],
                        help="Filter by memory type")
    parser.add_argument("--tags", help="Comma-separated tag IDs to filter by")
    parser.add_argument("--system", "-s", help="Filter by system ID from systems.yaml")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Max memories to return")
    parser.add_argument("--all", dest="all_memories", action="store_true",
                        help="Return all memories (ignores other filters)")
    args = parser.parse_args()

    tag_list = [t.strip() for t in args.tags.split(",")] if args.tags else []

    result = load(
        query=args.query,
        project=args.project,
        mem_type=args.mem_type,
        tags=tag_list,
        limit=args.limit,
        all_memories=args.all_memories,
        system=args.system,
    )
    print(result)


if __name__ == "__main__":
    main()
