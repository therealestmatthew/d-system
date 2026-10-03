---
schema_version: 1
id: doc-ops-draw-rereview-sample
code: OPS-030
title: Draw the passed build reviews to re-review, by a recorded seed
kind: operation
status: active
owner: repository-owner
created: '2026-10-02'
updated: '2026-10-02'
systems: [sys-gov-docs]
depends_on: [doc-reviewer-contract-requirements, doc-reviewer-contract, doc-three-altitude-review-procedure]
---

# Draw the passed build reviews to re-review, by a recorded seed

## Trigger

A passed build review is only as good as the reviewer that passed it. The sampler picks some
passed reviews to be checked again by a different reviewer type, so the owner learns how often a
pass was wrong (`REQ-030` R07, `PLAN-047` D6). The coordinator, today the Session Manager, runs
it. Because the count is rounded up, running it more often draws slightly more re-reviews in total.

## What it reads

**Verdict records**, one JSON file per build review under
`docs/08-governance/reviews/verdicts/`, named `<verdict_id>.json` and validated by
`schemas/review-verdict.schema.json` (`REQ-030` R05, `PLAN-047` D4). The coordinator writes each
one from the reviewer's reply without changing a finding, and the builder commits it unchanged on
the phase branch. A record holds the reviewer type and the sha256 of its agent definition, the
model, the phase, the reviewed commit, `pass` or `reject`, the findings, whether it gated the
merge or ran in shadow, the sha256 of the reviewer's raw reply, and an `outcomes` list. Outcomes
are appended later and never edited: `owner-overturned`, `defect-found-on-dev`, or
`sampled-rereview`, which also names the draw, the re-reviewer's type and its verdict.

**Earlier draws**, one JSON file per draw under `docs/08-governance/reviews/draws/`, validated by
the same schema's `definitions/draw`.

## What it draws

These rules are the owner's rulings of 2026-10-02:

1. **Only gating verdicts are considered**, and only those no earlier draw lists in its
   `considered`. A shadow verdict (`gating: false`) decided no merge and is never sampled. A
   sampled re-review is itself recorded with `gating: false`, because the merge it would decide
   has already happened. So re-reviews are never drawn for re-review again.
2. **Every phase rejected before it passed is drawn.** A passed gating verdict is drawn with
   reason `rejected-before-pass` when a gating verdict on the same phase, dated on or before the
   pass, is `reject`. That reject may have been considered by an earlier draw. A shadow reject
   does not count.
3. **One in ten of the other passes is drawn, rounded up**, chosen by the seed from those verdicts
   sorted by `verdict_id`, with reason `one-in-ten`. Three passes give one, eleven give two. A draw
   with at least one pass always draws at least one.
4. **For each drawn phase, the reviewer types that may not re-review it** are every type with a
   verdict record for that phase, gating or shadow.

Rejected verdicts are listed in `considered` but are never drawn themselves.

## Command

```bash
uv run python tools/draw_rereview_sample.py                       # draw, fresh seed, write the record
uv run python tools/draw_rereview_sample.py --seed <n>            # draw with a chosen seed
uv run python tools/draw_rereview_sample.py --dry-run [--seed <n>]  # print only
uv run python tools/draw_rereview_sample.py --replay <draw_id>    # re-run a recorded draw
```

Run it in a worktree on a branch, not in the primary checkout. A draw writes a tracked file, which
reaches `dev` by the usual merge (`GOV-017`). With no `--seed`, the tool picks a seed from
`0` to `2**32 - 1` and records it.

## Expected result

A draw prints its id, seed, the number of gating verdicts considered and how many passed, then one
line per drawn phase: the phase, the verdict drawn, the reason and the types that may not re-review
it. Unless `--dry-run` is given, it writes `docs/08-governance/reviews/draws/<draw_id>.json`, where
`draw_id` is the date and a two-digit counter for that date (`2026-10-09-01`).

When no gating verdict is new since the last draw, it prints that, writes nothing and exits 0.

Then, for each drawn phase, the coordinator dispatches a re-review by a dedicated type not in its
excluded list. It records the re-review as its own verdict record with `gating: false`, and
appends a `sampled-rereview` outcome to the drawn verdict record. The sample and its results go to
the owner, as `REQ-030` says. The sample does not replace the owner's own judgement.

`--replay <draw_id>` re-runs that draw from its recorded seed and `considered` list and compares
the drawn verdicts and reasons with the record. A match shows the sample came from the seed and
was not chosen. It does not compare the excluded types, because a later re-review adds its own
type to the phase's list.

| Exit | Meaning |
|---|---|
| 0 | The draw was made and printed (and written, unless `--dry-run`); or nothing was new; or a replay matched |
| 1 | A replay does not match its record. The two lists are printed |
| 2 | Refused: a verdict or draw record is not valid JSON, fails the schema, or is not named by its own id; a replay names an unknown draw; or the arguments are wrong (`--seed` with `--replay`, a seed outside the range) |

## Failure and recovery

- **Exit 2 naming a record.** The message gives the file and the first schema error. Fix the
  record on a branch, or, if it was committed unchanged from the coordinator's copy, raise it with
  the coordinator. Nothing is drawn until every record reads.
- **A replay does not match.** The draw record was edited after it was written, or the verdict
  records it considered changed in a way that alters the draw, such as a changed `verdict`, `date`
  or `gating`. Both are findings for the owner. Do not rewrite the draw to make it match.
- **A draw was made by mistake** (wrong branch, run twice). Before it merges, delete the file on
  the branch. After it merges, it stands. The verdicts it considered stay considered, and a second
  draw over them would let someone pick the result they prefer.

<!-- generated:tool-reference:start -->

### Reference: `tools/draw_rereview_sample.py`

Draw the phases whose passed build reviews are re-reviewed, by a recorded seed.

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

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--seed` | the seed for the one-in-ten draw; a fresh one if omitted |  |  |  |
| `--replay` | re-run a recorded draw and compare it |  |  |  |
| `--dry-run` | print the draw and write nothing |  |  |  |

Exit codes found in source: 0, 1, 2.

<!-- generated:tool-reference:end -->
