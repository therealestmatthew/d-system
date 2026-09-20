---
schema_version: 1
id: doc-session-session-taxonomy-theory
code: SESS-2026-09-19-07
title: Session-type taxonomy Part 1 — theoretical model with falsifiable predictions
kind: session
status: active
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-20'
systems: [sys-governance]
depends_on: [doc-session-taxonomy-investigation]
---

# Session-type taxonomy Part 1 — theoretical model with falsifiable predictions

## Phase

`phase-tax-01` — Session-type taxonomy Part 1: theoretical model with falsifiable predictions.

## Verification

**1. `uv run python -m src.governance`**

```
Governance OK: 35 systems, 296 documents, 26 memories, 288 backlog phases
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
check_no_private_content: OK (738 tracked files, 0 identifiers checked)
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

`phase-tax-01` is `status: complete`, `agent: agent-tax`, closed through owner-invoked
`/session-close` on 2026-09-20 after the independent review recorded below returned both acceptance
conditions holding.

All three `GOV-003` completion conditions were met: every verification command ran green with real
output captured here; an independent, non-fork sub-agent reviewed the diff against acceptance and its
two findings were fixed; and the branch was integrated onto `dev` with the owner's explicit approval
("Commit and merge to dev") before this close.

Removed from `next_up`. `phase-tax-02` is now at the front of that queue and runs only on the owner's
explicit go.

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

**The exclusions above hold for this session without qualification.** One related event happened
after the theory was registered and is recorded here so no reader has to reconstruct it:

- **A post-registration provenance scout ran at the owner's direction**, after the theory document
  was written, verified and committed. A sub-agent read the ten most recent session records on
  `dev` and wrote its findings to `_working/session-provenance-scout-2026-09-19.md` (gitignored,
  ungoverned). It was instructed to return only a file path, a record count and any unreadable file
  — no finding, no quotation, no summary — and **this session did not read its output**. The owner
  reads the file directly.
- R02's guarantee is therefore intact in both halves: the theory was registered before any evidence
  was examined, and no session-record content entered this session's context at any point, before
  or after registration.

**The registration boundary**, which `phase-tax-02` may cite as the point the theory was frozen, is
the commit titled **"Deliver the session-type theory document (`phase-tax-01`)"** — the first of
the branch's five commits, and the only one that adds
`docs/00-working/session-types-theory.md`. It is identified by that title rather than by a hash on
purpose: this branch was rebased onto `dev` twice during the session and the hash changed both
times. `git log --diff-filter=A -- docs/00-working/session-types-theory.md` resolves it whatever
the hash turns out to be.

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
- **The staged private-content check has now had its conclusive run.** It checked 0 identifiers in
  the worktree, because the identifier list derives from gitignored `_private/portfolio/`, which no
  worktree carries. Run against the merged tree in the primary checkout it checked all 31 and
  passed: `check_no_private_content: OK (738 tracked files, 31 identifiers checked)`. Closed.
- **`phase-lit-07`'s stale claim was released by a peer.** The `--ready` report at session start
  flagged it as `agent-lit` with "no evidence: no agent/<phase-id> branch found". Commit `a69d8af`
  on `dev` released it while claiming `phase-lit-09`. No longer outstanding.
- **A document-code collision is live and belongs to another session.** `agent/lit-campaign`
  (`phase-lit-09`) holds `SESS-2026-09-19-07-literature-review-pass-3c.md` at commit `33ac6d5`,
  unmerged — the same code this record took. This branch integrated first, so `AGENTS.md`'s
  collision rule puts the renumbering on `phase-lit-09`: reallocate with `--next-code session`,
  rename the file, and update every reference including its own `backlog.yaml` `session:` field. It
  will also meet a `backlog.yaml` conflict that must keep both sides. Recorded here because nothing
  on `dev` will surface it until that branch tries to integrate.

## Review

Independent sub-agent review of the range `9bba035..b6d5af1` (five commits, four files) plus the
claim commit `7c3411b`, run at close under `/session-close` step 3. The reviewer started with no
context from this session, was given the phase's `scope`/`acceptance`/`verification` pasted in full,
and was instructed to decide from the diff and its own command runs rather than from this record's
claims. Its findings, condition by condition:

**Acceptance condition 1 (REQ-026 R01) — HOLDS.**

> Thirteen types, all five elements each — counted myself, not taken from the record. Splitting on
> `#### ` headings gives thirteen type blocks (A1–A3, B1–B6, C1–C4). [...] Exactly 13 of each, so no
> type is missing one and none double-counts. The disconfirmers are substantive rather than
> decorative — each names a specific observation that would collapse the type into a neighbour.
>
> The REQ-023 reconciliation is real. §6 runs to three numbered departures, each with a stated
> reason [...] That is departures-with-reasons as the scope requires, not a gesture at one.
>
> Layer separation holds against the prompt's own test. I grepped the entire portable core for local
> artifact names. [...] **No type's definition names a d-system artifact** — the prompt's stated test.
> [...] One minor observation, not a failure: A3's element 4 is the single place a portable-layer
> prediction element cites a local document (`REQ-023` R2's "must never"). The observable itself is
> generic; the local citation is a trailing consequence note.

**Acceptance condition 2 (REQ-026 R02) — HOLDS.**

> I attacked the attestation against the diff and could not break it. I searched the deliverable for
> any claim the declared inputs could not support — no `SESS-` code appears anywhere, no transcript
> or record count, no named past session, no assertion about actual session history. Every specific
> factual claim traces to a declared input, and I checked each one rather than assuming.
>
> Ordering corroborated independently of the record's testimony. The rebase rewrote committer dates,
> but author dates survive it: [...] The theory was committed **82 minutes before any session record
> was read**. That is git and filesystem evidence, not attestation, and it is the substance R02
> protects.
>
> On the disclosed sub-agent scout. The disclosure is honest and volunteered against interest —
> nothing in the tracked diff would have exposed it.

The reviewer raised one interpretive question it declined to resolve on its own authority, reproduced
here in full because it bears on Part 2 rather than on this phase:

> R02 says "the session that writes it reads no raw transcript and no session-record contents." A
> strict reading that counts a dispatched sub-agent as part of "the session" would make R02 fail. Two
> things argue against that reading. First, REQ-026 names sub-agents explicitly when it means them —
> R06 says "every sub-agent and the orchestrator read only derived files" — and R02 does not, so the
> omission reads as deliberate. Second, R02's verification clause is narrower still [...] and the
> record satisfies it on its face. Combined with the 82-minute ordering, I judge R02 holds. Flagging
> it because the requirement's author may want to tighten the wording for Part 2.

**Scope adherence — two departures, both disclosed; no undisclosed ones.** The reviewer confirmed the
Session-setup omission and the `SESS-2026-09-19-05` exclusion were both already recorded, and added
that the "commit nothing" reinterpretation is filed under orientation decisions rather than among the
departures, "which is the only reason it reads as less prominent than the other two". On the hard
stop: "The deliverable contains no transcript or session-record analysis under any banner — verified
by search, not by trusting the claim."

**Verification claims — all accurate.** The reviewer re-ran everything: governance matched this
record exactly; `638 passed, 2 warnings`; and it ran the private-content check in the primary
checkout itself, getting `OK (738 tracked files, 31 identifiers checked)`.

> The prediction was exact and the check genuinely passes. Declining to claim a pass on a run that
> checked nothing is the correct call.

**Nothing landed that should not have.** All four files justified; no backlog line outside
`phase-tax-01` edited; `AGENTS.md` and `CLAUDE.md` untouched across all six commits; the claim commit
contains only the claim and one catalog line; the phase was not self-completed.

**Discrepancies found — two, both bookkeeping, both now fixed.**

> 1. Record line 148: "the first of this branch's four commits." The branch has **five**. The
>    sentence was written in the fifth commit and did not count itself.
> 2. Record line 186: "The branch is not integrated [...] shows the two commits." Stale twice over.

Both were corrected in the same commit that added this section. The reviewer's verdict:

> Both acceptance conditions **HOLD**. [...] The record's substantive assertions survived every check
> I put to them — including the ones designed to break the R02 attestation. The work is sound. [...]
> The two stale lines above are the only defects I found, and both are bookkeeping in a record that
> was amended three times rather than any misstatement of the work.

## Decisions

**The three orientation decisions** are recorded above under their own heading; they were taken
before the claim and shaped everything after.

**Thirteen types rather than three.** The existing governed taxonomy (`REQ-023`) defines three and
states explicitly that a coordinator is not a fourth. The model departs from that, and the departure
is argued rather than asserted: `REQ-023` R1 forbids any session to decide its own completion while
`GOV-003`'s 2026-09-16 ruling lets a coordinator do exactly that, and two rules that contradict each
other cannot be governing the same type. The over-splitting risk this creates is registered as a
falsifiable condition in the deliverable's §10 — if more than four types fail their disconfirmer in
the direction of "this is a segment", the model should be rebuilt coarser.

**Convergence criterion as the generative dimension.** The model's central methodological bet is that
*how a session knows it is finished* separates types that write identical paths — Specification from
Investigation, Construction from Repair. This is what produces the concrete finding against
`ADR-020` Decision 3: its inference keys on write path, which is a proxy for object of work only, so
it merges exactly those pairs. `phase-tax-01` is itself the live counter-example, and finding it
required no transcript.

**The blind-scout arrangement**, mid-session, at the owner's direction. Asked to scout recent session
provenance while `REQ-026` R02 forbade this session to read session records, the choice was between
contaminating the session, deferring the answer, or dispatching a sub-agent that writes to a file and
returns only a pointer. The owner chose the third. It preserved both halves of R02 — the theory was
already frozen, and no record content entered this session's context — and the reviewer independently
corroborated the ordering from author dates rather than from the attestation.

**Identifying the registration boundary by commit title, not hash.** Two rebases onto `dev` rewrote
the theory commit's hash twice, invalidating a citation written into this record each time. The third
correction removed the dependency instead of repeating it, naming the commit by title and supplying
`git log --diff-filter=A -- docs/00-working/session-types-theory.md` as the resolver. The reviewer
confirmed it resolves uniquely.

## Corrections

**The commit-hash citation, twice.** Writing a hash into a file on the branch that hash belongs to
guarantees the citation breaks on rebase. It broke twice before the approach changed. The lesson is
general and worth carrying: a branch-local artifact must not be identified by a hash that the branch's
own integration can rewrite.

**Stale verification counts.** The record's captured output said `295 documents` and `737 tracked
files` — both true when run, both stale once the session record itself existed. Refreshed to `296`
and `738` before the merge. The checkpoint contract requires sections to reflect a run *now*, and a
figure that was honest when captured can still be wrong when read.

**Two stale lines the reviewer caught**, both fixed in this close: a commit count written in the
commit that changed it, and an "unmerged" note that outlived the merge.

## Left undone

**The deliverable's five open questions (§8) are unanswered by design** — they are the owner's to
settle. The first is load-bearing for `phase-tax-02`: if the empirical phase classifies one session to
exactly one type, every prediction phrased as "common as a segment, uncommon as a session" becomes
untestable as written, and `ADR-020` Decision 2 already asserts mid-flight type change is the common
case. Settling it before Part 2 starts is cheap; discovering it mid-scorecard is a redesign.

**R02's wording may want tightening for Part 2**, per the reviewer's flag above: R02 does not say
whether a dispatched sub-agent counts as "the session", where R06 addresses sub-agents explicitly.
This phase's conduct satisfies either reading on the evidence, so nothing here depends on it — but
Part 2 runs sub-agents by design and the ambiguity is cheaper to close now.

**No empirical work was begun**, which is the prompt's hard stop and not an omission. `phase-tax-02`
holds the Part 2 prompt and runs only on the owner's explicit go.

**The `phase-lit-09` code collision** is another session's to resolve; see `## Unresolved`.
