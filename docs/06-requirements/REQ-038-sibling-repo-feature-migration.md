---
schema_version: 1
id: doc-sibling-repo-feature-migration-requirements
code: REQ-038
title: Sibling-repository feature migration requirements — the idea overlap pre-pass, the structuring-time sanitiser, the timeline entity, the write-back decision, the deferred run-cost fold, and the provenance and idea-capture rules for everything ported from life and autoclaude-api
kind: requirement
status: draft
owner: repository-owner
created: '2026-10-10'
updated: '2026-10-10'
systems: [sys-portfolio, sys-capture, sys-contracts, sys-projection, sys-api, sys-gov-docs, sys-auto-ledger]
depends_on: [doc-idea-staging, doc-structure-content-boundary, doc-capture-requirements, doc-idea-record-system, doc-realization-role-contracts, doc-broker-first-autonomous-operations]
---

# Sibling-repository feature migration requirements

Observable statements for what d-system takes from two sibling repositories the owner also holds,
`life` and `autoclaude-api`, and for how everything else those repositories offered is kept
visible without being built. The plan that delivers them is
[PLAN-053](../01-plans/PLAN-053-sibling-repo-feature-migration.md).

## Observed problem and scope

On 2026-10-10 the owner asked for a review of `life` and `autoclaude-api` and a proposal of what
could be integrated into d-system. Three read-only surveys and one adversarial review were run
in that session; the session record names them. What they established, each checked in the
repositories themselves:

1. **`autoclaude-api` holds tested code d-system has reimplemented partially or not at all.**
   A title-token overlap function (`scout/dedup/overlap.py`, 50 lines, 12 tests in
   `tests/unit/test_dedup_overlap.py`), a text sanitiser (`sanitize_text` in `scout/_security.py`,
   17 tests in `tests/unit/test_security.py`), a thread-log cost rollup (`scout/report/`), a
   budget cap (`scout/reviewer/budget.py`), an audited write-back layer (`web/apps/api/writes/`),
   a proposal state machine, a golden-set evaluation harness, a hash-diff index sync, markdown
   timelines, engagement templates and static-export profiles. `pyproject.toml` line 7 declares
   the project `Proprietary`; there is no upstream licence file. Both repositories are the
   owner's, so copying needs the owner's say-so and a recorded source commit, nothing more.
2. **`life` holds conventions and one design, no code to port.** 14 commits, two stdlib scripts
   (159 lines), no tests, no application code. Its memory promotion ladder, bootstrap prompt,
   read-when orientation table, hook installation and voice-capture design are inputs to work
   d-system has already queued, not deliverables of their own.
3. **The idea log has no measured overlap signal.** The triage agent
   (`agent-workflows/idea-triage-agent.md`, step 2) skims every other idea's title by reading, and
   `ADR-010` forbids any dedup at entry. A deterministic pre-pass is permitted downstream
   ("Detecting overlap is a downstream pass, not a gate") and does not exist.
4. **Captured text reaches agents unsanitised.** `src/capture/raw.py` stores every capture
   verbatim, as `REQ-002` R1 and R2 require, and nothing between `src/capture/structure.py`'s
   `load_raw` and the structuring agent removes hidden Unicode or control characters.
5. **Two of the adversary's blockers removed the two ledger-based ports.** `_data/runs.jsonl` does
   not exist in this checkout (`ls _data/` lists commitments, ideas.jsonl, people, projects,
   tags.json, tasks, workbench) and `schemas/run.schema.json` has no `model` field and
   `additionalProperties: false`, so the cost rollup has nothing to read. The budget cap
   contradicts the owner's ruling of 2026-10-06 on `phase-irs-11` (tokens only, per run, fail
   closed, no cap value). Both are recorded as ideas, and the cost fold is a deferred phase.
6. **"Reverses the single-writer rule" was wrong.** No such rule exists as one sentence. What
   exists is a sanctioned writer per append-only log (`OPS-005`, `OPS-022`, `OPS-023`), the broker
   (`ADR-022`), and the backlog lock table in `AGENTS.md`. Whether the workbench may write to
   tracked files at all is a decision for the owner, so it is a decision phase here, not a build.
7. **The consulting half has no dated view.** Projects, people, commitments and tasks exist as
   entities; nothing holds a milestone or a date range that refers to one of them.

Scope: the four deliverables that survived adversarial review (the overlap pre-pass, the
sanitiser, the timeline entity with its route, the write-back decision), one deferred deliverable
(the run-cost fold), and the two cross-cutting rules (provenance on every ported unit, and an idea
for every proposal that is not built). Everything else the surveys proposed is in the idea log,
triaged, with a finding naming the phase it belongs to.

## Observable requirements and verification

"Baseline" below means the branch this plan was cut from, `dev` at the commit the session record
names.

| Id | Requirement | Verification |
|---|---|---|
| R01 | A tool `tools/idea_overlap.py <idea-id>` prints, for the named idea, every other idea in the folded log whose title-token Jaccard similarity with it is at least 0.6, one per line as `<id> <score> <title>`, highest score first, reading the log only through `src.db.ideas.fold`. With no candidate it prints one line saying so and exits 0. Two runs on the same log print byte-identical output. | A test builds a four-idea log in a temporary directory where two titles share most tokens and two do not, runs the tool against it, and asserts exactly one candidate line with its score, and the no-candidate line for an idea with none. The same test runs the tool twice and asserts identical stdout. An unknown id exits non-zero with a message naming it. |
| R02 | The tool writes nothing: no idea event, no file, no change to `docs/00-working/ideas.md`. | The test records the SHA-256 of `_data/ideas.jsonl` before and after a run and asserts equality, and asserts the temporary directory holds no new file. |
| R03 | The triage driver (`agent-workflows/idea-triage.md`) runs the tool for each idea it dispatches and hands its output to the triage role inside the dispatch. When the tool exits non-zero or is missing, the driver dispatches without it and writes the line `overlap pre-pass unavailable` with the tool's last stderr line into the dispatch, and the role's finding repeats that line. The role's contract (`agent-workflows/idea-triage-agent.md`) tells it to cite the measured candidates when present and to keep proposing links only where it is confident, and `GOV-014`'s Triage inputs name the pre-pass output as an advisory third input. The generated files under `.claude/`, `.codex/` and `.agents/` are regenerated from these sources. The workflow still moves no idea past `triaged`. | `uv run pytest test/test_agent_workflows.py` passes, which fails when a generated file differs from its source. A grep of both workflow sources finds `idea_overlap.py`, and a grep of the driver finds `overlap pre-pass unavailable`. A grep of `GOV-014` finds the pre-pass in the Triage inputs. A grep of the driver finds no status value other than `triaged` after a `status` verb. |
| R04 | The structuring agent reads a capture through one command, `tools/capture.py show <capture-id>`, which prints the capture's content with every character of Unicode categories Cf (zero-width characters, bidirectional controls, the byte-order mark) and Cc other than newline and tab removed and outer whitespace stripped, with no Unicode normalisation and no collapsing of spaces or tabs. The raw capture record on disk is byte-identical before and after. In `src/capture/structure.py`, a quote is resolved against that same sanitised view and its provenance `start` and `end` are mapped back to the raw record's offsets, so `REQ-002` R6 still locates the supporting text in the raw capture even when the quote spans a removed character. | A test writes a raw capture whose content holds U+200B, U+202E, U+FEFF, NUL, U+0007 and U+000D beside a newline, a tab, two consecutive spaces and a precomposed e-acute; `show` prints none of the six and keeps the newline, the tab, both spaces and the e-acute byte for byte; the raw file's SHA-256 is unchanged. A proposal whose quote spans the removed U+200B stages with offsets that cover the removed character in the raw content (the case that fails before this phase); a capture with nothing to remove yields the same offsets as before (control). `uv run pytest test/test_capture_contracts.py test/test_capture_intake.py test/test_capture_routing.py test/test_capture_promotion.py` passes, which fails if R1, R2 or R6 of `REQ-002` is broken. |
| R05 | The sanitiser is a module in d-system's own source, `src/capture/sanitize.py`, adapted from `sanitize_text` in `autoclaude-api` `scout/_security.py`, with a header comment naming the source repository, path and commit and the three source behaviours it drops: NFC normalisation, collapsing runs of spaces and tabs, and keeping carriage return. It exposes `sanitize(text)` and `sanitize_with_map(text)`, the second returning the sanitised text and a list mapping each of its indexes to the raw index. It imports nothing outside the standard library. | A grep of the function's module finds the header with a 40-character commit hash. A test reads the module's import lines and asserts every imported name is in `sys.stdlib_module_names`. |
| R06 | A `timeline` entity exists as `schemas/timeline.schema.json`: an id matching `^tl-[0-9]+`, a title, an optional description, and an `entries` list where each entry has an id, a title, a `kind` of `milestone` or `span`, a `start` date, an `end` date required when `kind` is `span` and absent otherwise, an optional `ref` naming an entity type (`project`, `commitment` or `person`) and id, and optional notes. `additionalProperties` is false at both levels. | `uv run pytest test/test_schemas.py` passes with new valid and invalid fixtures: a span without `end` is rejected, a milestone with `end` is rejected, a `kind` of `event` is rejected, and an unknown `ref` type is rejected (the cases that must fail). |
| R07 | `tools/rebuild_db.py` loads every `<data root>/timelines/*.json` into DuckDB tables `timelines` and `timeline_entries`, defined in `sql/001_schema.sql`, honouring `D_SYSTEM_DATA_ROOT` exactly as the other entities do. The tracked fictional set holds at least one timeline with at least one milestone and one span. | `uv run python tools/rebuild_db.py` then `SELECT count(*) FROM timeline_entries` returns at least 2. With `D_SYSTEM_DATA_ROOT` pointing at a temporary root holding one timeline with one entry, the same count returns 1 (control that the data root is honoured). `uv run pytest test/test_rebuild.py` passes. |
| R08 | An entry whose `ref` names an id that does not exist in the same data root fails source validation at rebuild with a message naming the timeline, the entry and the missing id, and nothing is loaded. | A test in `test/test_source_validation.py` writes a timeline with a `ref` to `p-999` in a root with no such project and asserts rebuild raises with that id in the message (the case that must fail). The same timeline with a `ref` to an existing project loads (control). |
| R09 | The API serves `GET /api/v1/timelines` (every timeline, entries sorted by `start`) and `GET /api/v1/timelines/{id}` (one timeline, 404 for an unknown id), registered in `src/api/__init__.py` under the same `D_SYSTEM_DEMO_TERMINAL=1` gate and loopback-bind check as the workbench read routes (`ADR-015`), with a Pydantic response model under `src/models/`. With the projection file missing or lacking the table, the route responds 503 naming `tools/rebuild_db.py` and creates no file. The route adds no write, no subprocess, no environment variable and no new process, port or credential. | A FastAPI `TestClient` test, with `src.db.connection.DB_PATH` pointed at a projection built in a temporary directory, asserts the list, the sorted order, the single lookup, the 404, the 503 with the projection absent and no `data/` directory created (the cases that must fail), and that the path is absent with the gate unset. `grep -nE "subprocess|os\.environ|INSERT|UPDATE|DELETE" src/api/routes/timelines.py` prints nothing. `uv run ruff check src/ test/ tools/` and `uv run mypy src/` are clean. |
| R10 | An ADR in `docs/04-decisions/` records whether the workbench may write to tracked files (governed documents, `backlog.yaml`, the JSON entities) and, if so, through what mechanism. It carries context, the decision, at least three alternatives (keep per-log sanctioned writers only; the audited write-back pattern from `autoclaude-api` `web/apps/api/writes/`: path safety, atomic write, optimistic lock on file hash with 409, pending-then-commit audit row; the broker as the single write gate per `ADR-022`), consequences and a revisit trigger. Its status is `draft` until the owner accepts it; the phase that writes it builds nothing. | `uv run python -m src.governance` exits 0 with the ADR present. A grep finds the five sections and the three alternatives. `git diff --stat` for the phase shows no change under `src/`, `ts/` or `tools/`. |
| R11 | `schemas/run.schema.json` gains optional `model`, `cache_creation_input_tokens` and `cache_read_input_tokens` fields on the `usage` object, and a tool `tools/run_cost_report.py` folds a run ledger into a deterministic markdown rollup of tokens by run, role, model and day. This requirement is deferred until idea `000349` is ruled and a ledger with recorded events exists. | Deferred: `phase-mig-06` carries `resume_when`. When resumed: a test folds a fixture ledger of two runs and asserts the rollup's totals and that two runs print byte-identical output; a ledger event with a `usage` field the schema does not list is rejected by `uv run pytest test/test_schemas.py`. |
| R12 | Every code unit ported or adapted from either repository carries, in its first comment block, the source repository name, the source path and the source commit hash, and names any source behaviour it drops, and the plan records that both repositories are proprietary and owner-controlled with no upstream licence. | A grep over `tools/idea_overlap.py` and the sanitiser's module finds `autoclaude-api`, a path and a 40-character hash. A grep of `PLAN-053` finds `Proprietary`. |
| R13 | Every proposal from the surveys that this plan does not deliver is in `_data/ideas.jsonl` as an idea whose body opens with `[agent-proposed by Session Manager - migration planning]`, with at least one `finding` annotation naming the existing phase, plan or idea it belongs to, and status `triaged`. | `uv run python -c "from src.db.ideas import load_events, fold; ..."` lists ids `000673` to `000688`, as the session record `SESS-2026-10-10-01` names them, with status `triaged` and one or more findings each. `uv run python -m src.governance` exits 0, which fails if `docs/00-working/ideas.md` is stale. |

## What each requirement is not

- R01 does not change how an idea is recorded, declined or merged. `ADR-010` stands: an entry is
  never refused for overlap, and the tool runs after the append, never before it.
- R01 does not tune the threshold. 0.6 is the source's constant
  (`scout/dedup/engine.py`, `JACCARD_THRESHOLD`); the score is printed so the triage role and the
  owner can see what 0.6 means on idea titles, which are shorter than catalog titles. Changing it
  is a later judgement (plan open question 2).
- R03 does not give the triage role any new authority. It still proposes links and promotions as
  text and writes only a finding.
- R04 does not touch the raw capture or the inbox file, and adds only the `show` subcommand to
  the capture CLI (`tools/capture.py`). It changes only what the structuring agent reads and how a
  quote is located.
- R04 does not strip characters inside structured fields after structuring, does not normalise
  Unicode (no NFC or NFKC), and does not change the owner-facing review text in
  `src/capture/review.py`, which the owner reads, not an agent.
- R04 removes U+200D (zero-width joiner, category Cf), so an emoji sequence joined by it is
  split in the sanitised view. The raw record keeps it.
- R06 to R09 do not add a workbench panel, a chart or an HTML page for timelines. They add the
  entity, its projection and a read route; a view is later work.
- R09 does not mount the route on the default binding. The projection can hold the owner's real
  portfolio under `D_SYSTEM_DATA_ROOT`, so the route sits behind `ADR-015`'s one gate and one
  binding, like every workbench read route.
- R10 does not build any writer. If the owner accepts an alternative that builds one, that is a
  new requirement and plan.
- R11 does not decide which ledger is canonical. That is idea `000349`'s ruling.
- R12 does not require the source tests to be copied verbatim. Each ported unit gets tests written
  against d-system's fixtures; the source tests are read for the cases they cover.
- R13 does not promote, link or discard any idea. Those moves are the owner's (`PLAN-016`).
- Nothing here changes `AGENTS.md` or `CLAUDE.md`.

## Accepted decisions

None by the owner yet. The owner's ask of 2026-10-10 was to review the two repositories, run an
adversarial review of the proposal, capture and triage the ideas, write the plan with its phases
and reviews, and open a pull request to `dev`. The gates that plan's protocol names (G2 partition
acceptance, G3 plan approval, G4 integration) all ride on that pull request.
