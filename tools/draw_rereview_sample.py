#!/usr/bin/env python3
"""Draw the phases whose passed build reviews are re-reviewed, by a recorded seed.

The re-review sampler (REQ-030 R07, PLAN-047 D6). It reads the build-review verdict records under
`docs/08-governance/reviews/verdicts/` and the earlier draws under
`docs/08-governance/reviews/draws/`, and considers every gating verdict no earlier draw has
considered. Shadow verdicts (`gating: false`) are never considered. From those it draws:

- every passed review of a phase that a gating review rejected before it passed;
- one in ten of the other passed reviews, rounded up, chosen by the seed.

For each drawn phase it lists every reviewer type with a verdict record for that phase, gating or
shadow; none of them may re-review it. The draw is printed and written to
`docs/08-governance/reviews/draws/<draw_id>.json` with its seed and the verdicts it considered, so
the next draw starts after them.

    uv run python tools/draw_rereview_sample.py                 # draw with a fresh seed
    uv run python tools/draw_rereview_sample.py --seed 4021     # draw with a chosen seed
    uv run python tools/draw_rereview_sample.py --dry-run       # print the draw, write nothing
    uv run python tools/draw_rereview_sample.py --replay 2026-10-02-01

`--replay` re-runs a recorded draw from its own seed and considered list and compares the drawn
phases, verdicts and reasons with the record, so anyone can confirm the sample was not chosen by
hand. It writes nothing.

Exit codes: 0 when the draw was made (or there was nothing new to draw), or a replay matched; 1
when a replay differs from its record; 2 when a verdict or draw record is invalid, or a replay
names an unknown draw.

See REQ-030 R05 and R07 and PLAN-047 D4 and D6 (docs/01-plans/PLAN-047-reviewer-contract.md),
phase-asr-03.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import secrets
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator  # type: ignore[import-untyped]
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent

SCHEMA = Path("schemas") / "review-verdict.schema.json"
REVIEWS = Path("docs") / "08-governance" / "reviews"
VERDICTS = REVIEWS / "verdicts"
DRAWS = REVIEWS / "draws"
RATE = 10  # one in RATE passed gating reviews, rounded up
SEED_BOUND = 2**32


class Refused(Exception):
    """A record cannot be read, so no draw is made."""


@dataclass(frozen=True)
class Drawn:
    phase: str
    verdict_id: str
    reason: str
    excluded_reviewer_types: tuple[str, ...]

    def as_record(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "verdict_id": self.verdict_id,
            "reason": self.reason,
            "excluded_reviewer_types": list(self.excluded_reviewer_types),
        }


def _validator(root: Path, pointer: str) -> Draft7Validator:
    schema = json.loads((root / SCHEMA).read_text(encoding="utf-8"))
    registry: Registry[Any] = Registry().with_resource(
        schema["$id"], Resource.from_contents(schema)
    )
    return Draft7Validator(
        {"$ref": f"{schema['$id']}#{pointer}"},
        registry=registry,
        format_checker=Draft7Validator.FORMAT_CHECKER,
    )


def load_records(
    root: Path, directory: Path, pointer: str, id_field: str
) -> list[dict[str, Any]]:
    """Every record in the directory, each validated and named by its own id."""
    validator = _validator(root, pointer)
    records = []
    for path in sorted((root / directory).glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise Refused(f"{path.relative_to(root)}: not readable JSON: {exc}") from exc
        errors = sorted(error.message for error in validator.iter_errors(record))
        if errors:
            raise Refused(f"{path.relative_to(root)}: {errors[0]}")
        if record[id_field] != path.stem:
            raise Refused(
                f"{path.relative_to(root)}: {id_field} {record[id_field]!r} is not the filename"
            )
        records.append(record)
    return records


def load_verdicts(root: Path) -> list[dict[str, Any]]:
    return load_records(root, VERDICTS, "", "verdict_id")


def load_draws(root: Path) -> list[dict[str, Any]]:
    return load_records(root, DRAWS, "/definitions/draw", "draw_id")


def unconsidered(
    verdicts: Sequence[dict[str, Any]], draws: Sequence[dict[str, Any]]
) -> list[str]:
    """The gating verdicts no earlier draw has considered, sorted by verdict_id."""
    seen = {verdict_id for d in draws for verdict_id in d["considered"]}
    return sorted(v["verdict_id"] for v in verdicts if v["gating"] and v["verdict_id"] not in seen)


def draw(verdicts: Sequence[dict[str, Any]], considered: Sequence[str], seed: int) -> list[Drawn]:
    """The sample from the considered gating verdicts: deterministic for a given seed."""
    gating = {v["verdict_id"]: v for v in verdicts if v["gating"]}
    unknown = sorted(set(considered) - set(gating))
    if unknown:
        raise Refused(f"not a gating verdict record: {', '.join(unknown)}")

    def rejected_before(passed: dict[str, Any]) -> bool:
        return any(
            v["phase"] == passed["phase"]
            and v["verdict"] == "reject"
            and v["date"] <= passed["date"]
            for v in gating.values()
        )

    passes = sorted(vid for vid in considered if gating[vid]["verdict"] == "pass")
    always = [vid for vid in passes if rejected_before(gating[vid])]
    rest = [vid for vid in passes if vid not in always]
    chosen = random.Random(seed).sample(rest, math.ceil(len(rest) / RATE))

    reasons = {vid: "rejected-before-pass" for vid in always}
    reasons.update({vid: "one-in-ten" for vid in chosen})
    drawn = []
    for vid in sorted(reasons):
        phase = gating[vid]["phase"]
        excluded = sorted({v["reviewer"]["type"] for v in verdicts if v["phase"] == phase})
        drawn.append(Drawn(phase, vid, reasons[vid], tuple(excluded)))
    return drawn


def next_draw_id(draws: Sequence[dict[str, Any]], today: str) -> str:
    used = [d["draw_id"] for d in draws if d["draw_id"].startswith(f"{today}-")]
    return f"{today}-{len(used) + 1:02d}"


def _print(record: dict[str, Any], passed: int) -> None:
    considered = len(record["considered"])
    print(
        f"Draw {record['draw_id']}  seed {record['seed']}  "
        f"considered {considered} gating verdicts ({passed} passed)"
    )
    if not record["sample"]:
        print("Nothing drawn.")
    for entry in record["sample"]:
        excluded = ", ".join(entry["excluded_reviewer_types"])
        print(f"  {entry['phase']}  {entry['verdict_id']}  {entry['reason']}  not by: {excluded}")


def _replay(verdicts: list[dict[str, Any]], draws: list[dict[str, Any]], draw_id: str) -> int:
    recorded = next((d for d in draws if d["draw_id"] == draw_id), None)
    if recorded is None:
        raise Refused(f"no draw record {draw_id}")
    again = draw(verdicts, recorded["considered"], recorded["seed"])
    expected = [(e["phase"], e["verdict_id"], e["reason"]) for e in recorded["sample"]]
    actual = [(d.phase, d.verdict_id, d.reason) for d in again]
    if actual == expected:
        print(f"Draw {draw_id} replays: seed {recorded['seed']} gives the recorded {len(actual)}.")
        return 0
    print(f"Draw {draw_id} does not replay from seed {recorded['seed']}.")
    print(f"  recorded: {expected}")
    print(f"  replayed: {actual}")
    return 1


def main(argv: Sequence[str] | None = None, root: Path = ROOT, today: str | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Draw the phases whose passed build reviews are re-reviewed (REQ-030 R07)."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--seed", type=int, help="the seed for the one-in-ten draw; a fresh one if omitted"
    )
    group.add_argument("--replay", metavar="DRAW_ID", help="re-run a recorded draw and compare it")
    parser.add_argument("--dry-run", action="store_true", help="print the draw and write nothing")
    args = parser.parse_args(argv)
    if args.seed is not None and not 0 <= args.seed < SEED_BOUND:
        parser.error(f"--seed must be from 0 to {SEED_BOUND - 1}")

    try:
        verdicts = load_verdicts(root)
        draws = load_draws(root)
        if args.replay:
            return _replay(verdicts, draws, args.replay)

        considered = unconsidered(verdicts, draws)
        if not considered:
            print("No gating verdicts since the last draw; nothing drawn and nothing written.")
            return 0
        seed = args.seed if args.seed is not None else secrets.randbelow(SEED_BOUND)
        day = today or date.today().isoformat()
        record = {
            "draw_id": next_draw_id(draws, day),
            "date": day,
            "seed": seed,
            "rate": RATE,
            "considered": considered,
            "sample": [d.as_record() for d in draw(verdicts, considered, seed)],
        }
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2

    errors = [e.message for e in _validator(root, "/definitions/draw").iter_errors(record)]
    if errors:  # a defect in this tool, not in the records
        raise AssertionError(f"draw record does not match its schema: {errors[0]}")
    passed = sum(1 for v in verdicts if v["verdict_id"] in considered and v["verdict"] == "pass")
    _print(record, passed)
    if args.dry_run:
        print("Dry run: nothing written.")
        return 0
    path = root / DRAWS / f"{record['draw_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
