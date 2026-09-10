#!/usr/bin/env python3
"""Prepare and restore the demo stage around a rehearsal or the live run (`PROMPT-017`).

Two explicit subcommands, both idempotent on a second consecutive run:

    uv run python tools/demo_reset.py prepare
    uv run python tools/demo_reset.py restore

`prepare` sets the stage: it regenerates the overview outputs (`tools/generate_overview.py`),
clears the demo scratch directory this tool owns (`_public/demo-scratch/` — see "What
`prepare` clears" below), PARKS the pre-built overview skill
(`.claude/skills/d-system-overview/` moves to `.claude/skills/_parked/d-system-overview/`, a
location this tool owns), and SEEDS the fallback audience idea through
`tools/append_idea.py`'s sanctioned `add()` — but only if an idea carrying the fallback seed's
exact title is not already present in the folded idea state, so a second `prepare` seeds no
duplicate.

`restore` is the fallback and post-segment action the runbook invokes by name: it puts the
parked pre-built skill back in place and regenerates the overview outputs from current data.
A second `restore` finds the skill already in place and reports that rather than erroring.

**Contract: "pre-built state" means the pre-built SKILL is back in place.** The overview page
is always regenerated from current data, which grows as ideas are appended — the idea log is
append-only, so byte-identical pre-rehearsal page output is deliberately NOT the contract
(PLAN-021's afterlife decision keeps demo-recorded ideas as real work, and the page reflecting
them is intended behavior). `restore` never claims to reproduce pre-rehearsal page bytes.

**What `prepare` clears.** `_public/demo-scratch/` is the one directory this tool treats as
demo scratch state: reserved for ephemeral artifacts a rehearsal or the live run might drop
(nothing else in the repository writes there today, which is deliberate — it exists so a
future demo-run artifact has one tool-owned location guaranteed to start clean, rather than
`prepare`'s scratch-clearing step being a promise nothing checks). `prepare` removes it and
recreates it empty every run.

**Hard limits, enforced in code, not left as a comment.** Every filesystem create, move or
delete this tool performs passes through `_guard()`, which refuses a path inside
`_data/ideas.jsonl`, anything under `docs/`, `_private/`, `.agents/`, `.codex/`, `AGENTS.md` or
`CLAUDE.md` — even if it would otherwise fall inside this run's allowlist — and separately
refuses any path outside the allowlist the caller supplies. The only idea-log access this tool
ever makes is appending through `tools/append_idea.py`'s `add()`; it never opens
`_data/ideas.jsonl` for writing itself, and never rewrites or deletes a line already there.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.db.ideas import fold, load_events  # noqa: E402

#: Hard-forbidden paths, always resolved against the real repository root regardless of what
#: a caller's allowlist says. `_guard()` checks every mutating call against these first.
FORBIDDEN_PATHS: tuple[Path, ...] = (
    ROOT / "_data" / "ideas.jsonl",
    ROOT / "docs",
    ROOT / "_private",
    ROOT / ".agents",
    ROOT / ".codex",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
)

#: The fallback audience idea's title IS its label — there is no tag field on an idea
#: (`schemas/idea.schema.json`), so `prepare` checks the folded state for an idea whose
#: effective title matches this constant exactly before seeding another one.
FALLBACK_SEED_TITLE = "Demo fallback: audience idea seeded by tools/demo_reset.py"

FALLBACK_SEED_BODY = (
    "Seeded by `tools/demo_reset.py prepare` so the live-rebuild segment (REQ-006 R09) always "
    "has an idea to triage even if the audience does not supply one live. Labelled as the "
    "fallback seed by this exact title — `prepare` checks the folded idea state for this title "
    "before appending, so re-running `prepare` never seeds a duplicate. Real work per "
    "PLAN-021's afterlife decision: not reverted after the demo."
)


class DemoResetError(Exception):
    """A refusal this tool prints without a traceback — a blocked path or a broken precondition."""


@dataclasses.dataclass(frozen=True)
class Paths:
    """Every filesystem location `prepare`/`restore` read or write.

    Defaults are the real repository locations; every field is overridable so tests exercise
    the same code path against a temporary tree instead of the tracked idea log, skill
    directory or generated overview page.
    """

    root: Path = ROOT
    idea_log: Path = ROOT / "_data" / "ideas.jsonl"
    skill_dir: Path = ROOT / ".claude" / "skills" / "d-system-overview"
    parked_skill_dir: Path = ROOT / ".claude" / "skills" / "_parked" / "d-system-overview"
    scratch_dir: Path = ROOT / "_public" / "demo-scratch"
    overview_out: Path = ROOT / "_public" / "overview" / "index.html"
    generate_overview_script: Path = ROOT / "tools" / "generate_overview.py"
    append_idea_script: Path = ROOT / "tools" / "append_idea.py"

    def allowed_roots(self) -> tuple[Path, ...]:
        """Every location this run of the tool is permitted to create, move or delete."""
        return (
            self.skill_dir,
            self.parked_skill_dir,
            self.scratch_dir,
            self.overview_out.parent,
        )


@dataclasses.dataclass(frozen=True)
class PrepareReport:
    overview_regenerated: bool
    scratch_cleared: bool
    skill_park: str  # "parked" | "already parked"
    idea_seed: str  # "seeded" | "already seeded"


@dataclasses.dataclass(frozen=True)
class RestoreReport:
    skill_restore: str  # "restored" | "already in place"
    overview_regenerated: bool


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _guard(path: Path, allowed_roots: Sequence[Path]) -> Path:
    """Refuse any path this tool would create, move or delete unless it clears both checks.

    First, unconditionally: the path may not be, or contain, or be contained by, any of
    `FORBIDDEN_PATHS` — real repository locations this tool may never touch, regardless of
    what `allowed_roots` says. Second: the path must fall inside at least one of the caller's
    `allowed_roots`. Every mutating filesystem call in this module goes through here before it
    acts, so the allowlist is enforced in code rather than trusted from a comment.
    """
    resolved = path.resolve()
    for forbidden in FORBIDDEN_PATHS:
        forbidden_resolved = forbidden.resolve()
        if _is_within(resolved, forbidden_resolved) or _is_within(forbidden_resolved, resolved):
            raise DemoResetError(
                f"refusing to touch {path} — inside or containing the hard-forbidden path "
                f"{forbidden}, which tools/demo_reset.py may never create, move or delete"
            )
    if not any(_is_within(resolved, root.resolve()) for root in allowed_roots):
        allowed_text = ", ".join(str(root) for root in allowed_roots)
        raise DemoResetError(
            f"refusing to touch {path} — outside tools/demo_reset.py's allowlist ({allowed_text})"
        )
    return resolved


def _load_module(name: str, path: Path) -> ModuleType:
    """Import a `tools/` script by path — `tools/` is not a package."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _clear_scratch(paths: Paths) -> None:
    """Recreate `paths.scratch_dir` empty — the whole of `prepare`'s scratch-clearing step."""
    _guard(paths.scratch_dir, paths.allowed_roots())
    if paths.scratch_dir.exists():
        shutil.rmtree(paths.scratch_dir)
    paths.scratch_dir.mkdir(parents=True, exist_ok=True)


def _park_skill(paths: Paths) -> str:
    """Move the pre-built skill aside. Idempotent: a second call reports it already parked."""
    _guard(paths.skill_dir, paths.allowed_roots())
    _guard(paths.parked_skill_dir, paths.allowed_roots())
    skill_exists = paths.skill_dir.exists()
    parked_exists = paths.parked_skill_dir.exists()
    if skill_exists and not parked_exists:
        paths.parked_skill_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(paths.skill_dir), str(paths.parked_skill_dir))
        return "parked"
    if parked_exists and not skill_exists:
        return "already parked"
    if skill_exists and parked_exists:
        raise DemoResetError(
            f"both {paths.skill_dir} and {paths.parked_skill_dir} exist — ambiguous park "
            "state; resolve by hand before running prepare again"
        )
    raise DemoResetError(
        f"neither {paths.skill_dir} nor {paths.parked_skill_dir} exists — nothing to park and "
        "nothing already parked; the overview skill is missing"
    )


def _unpark_skill(paths: Paths) -> str:
    """Move the parked skill back. Idempotent: a second call reports it already in place."""
    _guard(paths.skill_dir, paths.allowed_roots())
    _guard(paths.parked_skill_dir, paths.allowed_roots())
    skill_exists = paths.skill_dir.exists()
    parked_exists = paths.parked_skill_dir.exists()
    if parked_exists and not skill_exists:
        paths.skill_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(paths.parked_skill_dir), str(paths.skill_dir))
        return "restored"
    if skill_exists and not parked_exists:
        return "already in place"
    if skill_exists and parked_exists:
        raise DemoResetError(
            f"both {paths.skill_dir} and {paths.parked_skill_dir} exist — ambiguous park "
            "state; resolve by hand before running restore again"
        )
    raise DemoResetError(
        f"neither {paths.skill_dir} nor {paths.parked_skill_dir} exists — nothing in place and "
        "nothing parked to restore"
    )


def _seed_fallback_idea(paths: Paths) -> str:
    """Append the fallback audience idea unless its title is already in the folded state."""
    state = fold(load_events(paths.idea_log))
    titles = {info["title"] for info in state.values()}
    if FALLBACK_SEED_TITLE in titles:
        return "already seeded"
    append_idea = _load_module("demo_reset_append_idea", paths.append_idea_script)
    append_idea.add(FALLBACK_SEED_TITLE, FALLBACK_SEED_BODY, log=paths.idea_log)
    return "seeded"


def _regenerate_overview(paths: Paths) -> None:
    """Run `tools/generate_overview.py` fresh against current data."""
    _guard(paths.overview_out, paths.allowed_roots())
    paths.overview_out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(paths.generate_overview_script), "--out", str(paths.overview_out)],
        cwd=paths.root,
        capture_output=True,
        check=True,
    )


def prepare(paths: Paths = Paths()) -> PrepareReport:
    """Regenerate overview outputs, clear scratch state, park the skill, seed the fallback idea."""
    _regenerate_overview(paths)
    _clear_scratch(paths)
    skill_status = _park_skill(paths)
    idea_status = _seed_fallback_idea(paths)
    return PrepareReport(
        overview_regenerated=True,
        scratch_cleared=True,
        skill_park=skill_status,
        idea_seed=idea_status,
    )


def restore(paths: Paths = Paths()) -> RestoreReport:
    """Put the parked pre-built skill back and regenerate overview outputs from current data."""
    skill_status = _unpark_skill(paths)
    _regenerate_overview(paths)
    return RestoreReport(skill_restore=skill_status, overview_regenerated=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo_reset.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "prepare",
        help=(
            "regenerate overview outputs, clear _public/demo-scratch/, park the pre-built "
            "overview skill, and seed the fallback audience idea if it is not already present"
        ),
    )
    sub.add_parser(
        "restore",
        help=(
            "put the parked pre-built overview skill back in place and regenerate overview "
            "outputs from current data"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "prepare":
            report = prepare()
            print(f"overview regenerated -> {Paths().overview_out}")
            print(f"scratch cleared -> {Paths().scratch_dir}")
            print(f"skill: {report.skill_park}")
            print(f"fallback idea: {report.idea_seed}")
        else:
            report = restore()
            print(f"skill: {report.skill_restore}")
            print(f"overview regenerated -> {Paths().overview_out}")
    except DemoResetError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc)
        print(f"tools/generate_overview.py failed: {detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
