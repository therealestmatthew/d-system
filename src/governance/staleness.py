"""Compare committed generated files with their renderings, without writing either.

`docs/08-governance/catalog.md` and `docs/00-working/ideas.md` are views: the first rendered by
`--catalog` from the document register and the backlog, the second by
`tools/generate_ideas_md.py` from the idea log. A write that changes a source and not its view
leaves the trunk red on a test while the governance check still passes — the failure recorded in
ideas 000405, 000406 and 000198 (REQ-028 R01, R02; PLAN-045 D3).

These checks only compare and report. Regeneration stays with `--catalog` and
`tools/generate_ideas_md.py`.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml  # type: ignore[import-untyped]

from src.db.ideas import fold, load_events

CATALOG = "docs/08-governance/catalog.md"
IDEAS_MD = "docs/00-working/ideas.md"
IDEAS_LOG = "_data/ideas.jsonl"
IDEAS_PRIORITY = "docs/00-working/ideas-priority.yaml"


def _read(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.is_file() else None


def catalog_errors(root: Path, rendered: str) -> list[str]:
    """One error naming the catalog when the committed file differs from `rendered`.

    `rendered` is `render_catalog`'s output; `write_catalog` stores it with exactly one trailing
    newline, so the comparison applies the same convention.
    """
    expected = rendered.rstrip("\n") + "\n"
    committed = _read(root / CATALOG)
    if committed == expected:
        return []
    state = "is missing" if committed is None else "differs from the rendered catalog"
    return [
        f"{CATALOG}: {state}; regenerate it with "
        "`uv run python -m src.governance --catalog` and commit the result"
    ]


def _ideas_renderer(root: Path) -> ModuleType:
    """Import `tools/generate_ideas_md.py` by path — `tools/` is not a package."""
    name = "generate_ideas_md"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, root / "tools" / f"{name}.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load tools/{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def render_ideas_md(root: Path, renderer: ModuleType | None = None) -> str:
    """What `tools/generate_ideas_md.py` would write, from `root`'s log and priority queue."""
    renderer = renderer or _ideas_renderer(root)
    state = fold(load_events(root / IDEAS_LOG))
    priority: dict[str, Any] = {}
    text = _read(root / IDEAS_PRIORITY)
    if text is not None:
        priority = yaml.safe_load(text) or {}
    rendered: str = renderer.render(state, list(priority.get("next_up", [])))
    return rendered


def ideas_md_errors(root: Path, renderer: ModuleType | None = None) -> list[str]:
    """One error naming `ideas.md` when it differs from the rendering of the idea log."""
    committed = _read(root / IDEAS_MD)
    if committed == render_ideas_md(root, renderer):
        return []
    state = "is missing" if committed is None else "differs from the rendered idea log"
    return [
        f"{IDEAS_MD}: {state}; regenerate it with "
        "`uv run python tools/generate_ideas_md.py` and commit the result"
    ]
