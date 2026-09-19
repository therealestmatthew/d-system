---
schema_version: 1
id: doc-session-session-taxonomy-theory
code: SESS-2026-09-19-07
title: Session-type taxonomy Part 1 — theoretical model with falsifiable predictions
kind: session
status: active
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems: [sys-governance]
depends_on: [doc-session-taxonomy-investigation]
---

# Session-type taxonomy Part 1 — theoretical model with falsifiable predictions

## Phase

`phase-tax-01` — Session-type taxonomy Part 1: theoretical model with falsifiable predictions.

## Verification

**1. `uv run python -m src.governance`**

```
Governance OK: 35 systems, 295 documents, 26 memories, 288 backlog phases
```

**2. "Read session-types-theory.md and confirm every proposed type carries the five prediction
elements and at least one disconfirming observation."**

Prose verification, performed mechanically rather than by eye so the result is reproducible. A
script split the document on its `#### ` type headings and checked each block for all five labelled
elements. Thirteen type blocks were found and every one carried all five:

```
Type blocks found: 13
  A1 — Inquiry                     OK
  A2 — Capture                     OK
  A3 — Exploration                 OK
  B1 — Specification               OK
  B2 — Adjudication                OK
  B3 — Construction                OK
  B4 — Repair                      OK
  B5 — Capability                  OK
  B6 — Governance                  OK
  C1 — Orchestration               OK
  C2 — Investigation               OK
  C3 — Retrospective               OK
  C4 — Rehearsal                   OK

REQ-023 reconciliation section present: True
ALL FIVE ELEMENTS ON EVERY TYPE: True
```

Element 4 of the five *is* the disconfirming observation, so the second half of the condition is
covered by the same check. Each is a single named observation, not a list, and each was written to
exclude something specific — several predict the type's own collapse into a neighbouring type.

**3. `uv run python tools/check_no_private_content.py` (changes staged)** — not in the phase's
verification list; run anyway because the session commits a tracked document.

```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (737 tracked files, 0 identifiers checked)
```

**Recorded as a partial result, not a pass.** The identifier list is derived from
`_private/portfolio/`, which is gitignored and therefore absent from this worktree, so the run
checked **0 identifiers** — the path check ran, the content check did not. The same command in the
primary checkout checks 31 identifiers. The definitive staged run belongs in the primary checkout at
integration.

## Acceptance

- **REQ-026 R01 holds** — **Met.** `docs/00-working/session-types-theory.md` exists; verification 2
  shows all thirteen proposed types carrying all five prediction elements, and the REQ-023
  reconciliation section present (§6, "Reconciliation with REQ-023 and ADR-020", which states three
  departures with reasons).
- **REQ-026 R02 holds** — **Met.** The inputs and exclusions are named in `## Inputs and exclusions`
  below, which is this record's attestation.

## Backlog

`phase-tax-01` remains `status: active`, `agent: agent-tax`.

`next_action`: Owner reviews `docs/00-working/session-types-theory.md`. Part 2 (`phase-tax-02`)
proceeds only on their explicit go, in a separate session, per the Part 1 prompt's hard stop.

`next_up` unchanged — the phase is not complete and only `/session-close` may make it so.

## Inputs and exclusions

Recorded here because `REQ-026` R02's verification asks this record for exactly it.

**Inputs actually used:**

- The Part 1 prompt, `docs/00-working/PROMPT-session-taxonomy-part1-theory.md`, including the owner's
  seed taxonomy and Appendix A (the Gemini CLAUDE.md design notes).
- The plan (`PLAN-042`) and its requirements (`REQ-026`).
- `AGENTS.md` and `CLAUDE.md` — read, not edited.
- Prior art named by the prompt: the per-type obligations requirement (`REQ-023`) and the
  type-declaration and lifecycle decision (`ADR-020`), both in full.
- The tooling surface, by listing and by front-matter description only: `.claude/skills/`,
  `.claude/commands/`, `.claude/agents/`, `.agents/skills/`. Also confirmed that `.claude/rules/`
  does not exist, which §7 of the deliverable relies on.
- The governance surface: `docs/08-governance/` directory listing; `GOV-003` (headings, plus the
  completion-gate and coordinator-completion entries in full), `GOV-006`, `GOV-007`, `GOV-008`,
  `GOV-009`, `GOV-013`, `GOV-014`, `GOV-015` (opening sections), and `systems.yaml` (ids only).
- `docs/09-backlog/backlog.yaml` (the `phase-tax-01` and `phase-tax-02` entries, the `next_up` list,
  and the `--ready` report) and `docs/09-backlog/README.md` (the full track table).
- Line counts of `CLAUDE.md` (210) and `AGENTS.md` (330), used in §7's evaluation of Appendix A's
  50-line target.

**Attestation of exclusions:**

- **No raw transcript was read.** Nothing under `~/.claude/projects/` was opened, listed or searched
  at any point in this session.
- **No session-record contents were read.** The only contact with `docs/03-sessions/` was a
  directory listing of filenames, which the prompt permits ("at most a skim of session-record
  *titles*"). No `SESS-*.md` file was opened.
- **`SESS-2026-09-19-05-framework-generalization-and-concurrency.md` was not read**, although the
  Part 1 prompt's Mission section names it as a "read for alignment" input. That line contradicts
  `REQ-026` R02, the phase scope and the owner's session instruction, all three of which exclude
  session-record contents. The conflict was put to the owner at orientation and they ruled the
  exclusion wins. The deliverable's portable layer was built from the backlog track table and the
  tooling surface instead.
- **The Part 2 prompt was not read.** `docs/00-working/PROMPT-session-taxonomy-part2-evidence.md`
  was never opened. It appears in this session only as a filename in directory listings of
  `docs/00-working/`.
- No `_private/` path was read or written.

## Decisions taken at orientation

Three questions were put to the owner before the claim, and all three were answered:

1. **Claim the phase** rather than run unclaimed — yes.
2. **What "commit nothing" means.** The prompt's Deliverable section says "One untracked document;
   commit nothing", but `docs/00-working/` is tracked, the phase declares the file as a deliverable,
   and R02 requires a session record. The owner ruled the theory document and the session record are
   both committed on `agent/phase-tax-01`, reading "commit nothing" as "create no governed policy" —
   which matches `PLAN-042`'s own statement that "nothing here creates governed policy".
3. **The SESS-2026-09-19-05 conflict** — resolved as recorded under exclusions above.

## Unresolved

- **The deliverable's §8 carries five open questions for the owner**, ordered by how much each would
  change the model. The first is load-bearing for `phase-tax-02`'s design: if the empirical phase
  classifies one session to exactly one type, every prediction phrased as "common as a segment,
  uncommon as a session" becomes untestable as written. That decision is the owner's and was not
  made here.
- **The Part 1 prompt's Session-setup step was not executed as written.** It instructs the session
  to ask the owner whether to run unclaimed or under `/session-start`. The owner's invocation had
  already directed the full claim-and-worktree protocol, so re-asking would have been a question
  whose answer was already given. Recorded because the prompt is the phase's method and this is a
  departure from it.
- **The staged private-content check has not had a conclusive run** — see verification 3. It checked
  0 identifiers in the worktree. The deliverable is abstract prose about session types and names no
  person, client or portfolio record, so the risk is low; the check is nonetheless owed a real run
  in the primary checkout.
- **`phase-lit-07` holds a stale claim.** The `--ready` report at session start flagged it as
  `agent-lit` with "no evidence: no agent/<phase-id> branch found". It locks `sys-research` and did
  not collide with this phase, so it did not block the claim. Noted for whoever runs the
  claim-recovery procedure (`phase-conc-04`).
- The branch is **not integrated**. `git diff dev..agent/phase-tax-01` shows the two commits.
