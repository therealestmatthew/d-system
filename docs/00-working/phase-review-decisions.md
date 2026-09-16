# Queued phase review — decisions for the owner

This document consolidates the 55 decision entries accumulated across the queued phase review of
`PROMPT-035` — eight pass-2 groups (A through H) critiquing 23 queued phases from `phase-irs-03`
onward, plus one adversarial pass-3 sweep — into 46 live decisions plus one resolved question.
Duplicate questions raised by more than one group, or by one group against more than one phase for
the same underlying reason, are merged below into a single entry naming every phase and group
involved. The top-ranked decisions from this list were put to the owner in session on 2026-09-16;
the remainder wait for a dedicated sitting.

## How to use this

Entries are ranked by how much the answer redirects downstream work — a decision that changes what
several phases build, or that blocks a phase from being claimed at all, outranks a wording choice.
Each entry carries a recommendation (where one of the reviewing groups proposed one) and its
evidence anchor in the group critique files. Deciding one entry does not require deciding any
other unless the entry says so.

## Decisions

### 1. Gate 3 ratification flow claimed by three phases at once
Affects: `phase-irs-04`, `phase-irs-07`, `phase-irs-14`
Raised by: group C
Decision needed: does `phase-irs-07` still build a standalone Gate 3 ratification mechanism (owner
ratifies/amends/rejects, decision recorded, twice-rejected escalation), given `phase-irs-04`'s
`gate` CLI verb and `phase-irs-14`'s decision-verb implementation now appear to cover the same
interrupt-and-decision machinery, and the orchestrator design's own list of backlog changes never
mentions `phase-irs-07`?
Options: narrow `phase-irs-07` to the mapping agent and proposal-artifact format only, dropping the
ratification bullet and deferring all decision-recording to `phase-irs-04`'s `gate` verb / keep
`phase-irs-07`'s flow as an explicitly-interim, standalone mechanism that `-04`/`-14` later absorb.
Recommended: narrow `phase-irs-07` — the orchestrator design already centralizes decision recording
there, and a second implementation duplicates it silently.
Evidence: C.md § question: The "Gate 3 ratification flow" appears to be claimed by three phases at once

### 2. Does the idea planner need to ship pre-decomposed plans?
Affects: `phase-idg-12`, `phase-irs-05`, `phase-irs-06`, `phase-irs-07`
Raised by: group F
Decision needed: `ARCH-006` (written one day after `REQ-014`) names `phase-idg-12`'s planner as
drafting requirement-plus-plan "decomposed to minimum scope," and names its downstream check
(`phase-irs-05/06/07`, which already assume the wider duty) — but neither `REQ-014` nor
`phase-idg-12`'s own scope mention decomposition or sizing at all.
Options: widen `phase-idg-12`'s scope/acceptance to require decomposed output now / leave as-is and
send `ARCH-006` back for a correcting edit instead.
Recommended: widen now — the downstream dependents already assume the wider duty, and shipping the
narrower one first means redoing the agent's contract later.
Evidence: F.md § question: does this phase's scope match the "minimum-scope" duty a newer document already assigns it?

### 3. Rename the colliding decision-schema filename
Affects: `phase-irs-04`
Raised by: group A
Decision needed: `phase-irs-04`'s scope names `schemas/decision.schema.json` for its gate-decision
inbox, but that filename already belongs to an unrelated, wired-in entity schema (a DuckDB table,
a `phase-cap-02` deliverable). The plan document `PLAN-039.01` names the same colliding path, so
whichever fix is chosen needs the plan document corrected to match.
Options: rename to `schemas/gate-decision.schema.json` / `_data/gate-decisions.jsonl` / keep the
name and disambiguate with a discriminator field.
Recommended: rename — the collision is with a filename, not a concept, and a backlog-only fix would
leave the phase contradicting its own plan document.
Evidence: A.md § question: schemas/decision.schema.json is already a different, load-bearing entity schema; A.md § question: PLAN-039.01 names the same colliding schema path as phase-irs-04

### 4. Prose-only role contracts, or stub agent skeletons too?
Affects: `phase-irs-03`, `phase-irs-05`, `phase-irs-07`, `phase-irs-08`, `phase-irs-09`, `phase-idg-12`
Raised by: group B
Decision needed: for the seven pipeline roles with no existing `.claude/agents/*.md` file, does
`phase-irs-03` write only a prose contract document that later building phases must conform to, or
also create a stub agent-definition skeleton (tools, model, never-do baked in) that those phases
edit into a working agent?
Options: prose-only contracts under `docs/08-governance/` / stub skeletons for every role too.
Recommended: prose-only — the source document's own phrase is "written contract," not "agent
scaffold," and skeleton drift before the real design lands is a cost with no offsetting benefit.
This is the owner's call since it changes what "done" means for this phase materially.
Evidence: B.md § question: does this phase author new `.claude/agents/*.md` files, or only prose contracts?

### 5. `sys-governance` collision blocks a claimed parallel front
Affects: `phase-idg-08`, `phase-idg-10`, `phase-idg-11` (and `PLAN-029`, the document making the
contradicted claim)
Raised by: group F
Decision needed: `systems: [sys-governance]` on all three phases makes them mechanically mutually
exclusive under the disjoint-systems rule, contradicting `PLAN-029:192-196`'s claim that these
three (plus `phase-idg-01` and `phase-idg-06`) are "the widest genuinely parallel front" in that
programme. Is serializing the three acceptable, or should `sys-governance` be split into
finer-grained ids?
Options: accept serialization and correct `PLAN-029`'s parallel-front claim / split `sys-governance`
in `systems.yaml` into finer-grained ids.
Recommended: flagged to the owner rather than guessed — splitting a registry entry used by many
phases outside this programme is a bigger call than the reviewing group could make unilaterally.
Evidence: F.md § question: systems: [sys-governance] blocks the parallel front PLAN-029 itself claims; F.md § Out of scope: phase-idg-08 shares the exact same systems/deliverables collision; F.md § Out of scope: PLAN-029's parallel-front claim itself needs correcting

### 6. Reword "park as blocked" to match the propose-then-observe ruling
Affects: `phase-irs-08`
Raised by: group C
Decision needed: the orchestrator design's round-4 ruling has the daemon propose changes for a
human to commit, never write dev state directly. `phase-irs-08`'s current wording — "park a
twice-rejected unit as blocked" — reads as the daemon writing the blocked status itself.
Options: reword scope to "propose the park (blocked edit, `blocked_reason`, `resume_when`) for
human commit," with the matching verification-language amendment / leave as-is and trust the
executing agent to infer the safer reading.
Recommended: reword — a precedent verification amendment already exists elsewhere in this plan for
exactly this kind of design change, and leaving this one silent invites the direct-write behavior
the round-4 ruling forbids.
Evidence: C.md § question: "Park a twice-rejected unit as blocked" contradicts the propose-then-observe ruling

### 7. Is `phase-irs-04`'s one-session budget realistic?
Affects: `phase-irs-04`, `phase-irs-11`, `phase-irs-13`, `phase-irs-14`, `phase-irs-15`
Raised by: groups A and B
Decision needed: `phase-irs-04` is sized at `session_budget: 1` against a large scope — the full
four-run-kind orchestrator skeleton, a tracked run ledger and decision inbox with two new schemas
and two sanctioned writers (each needing its own operations document), attended-only dispatch
gating, and the daemon's lock-contention/stale-lock-recovery test surface, which the design
document itself says "gets its own narrow tests." Four other queued phases depend on this phase
landing correctly.
Options: accept the size as-is / split the daemon process model (lock, signal handling,
start/stop/status) into a follow-on phase.
Recommended: no recommendation from either group — this is a sizing call for the owner, but the
risk it flags propagates directly into every phase that depends on `phase-irs-04`.
Evidence: A.md § question: is one session realistic for this phase's actual breadth?; B.md § is phase-irs-04's session_budget: 1 realistic against its own specified scope?

### 8. Which source decides the phase-fit heuristic?
Affects: `phase-irs-05`, `phase-idg-10`
Raised by: group C
Decision needed: `phase-irs-05` (the phase-fit procedure and agent) currently instructs itself to
derive its size heuristic from two different sources at once — an acceptance bullet and
`depends_on: phase-idg-10` pointing at the plan-quality standard, and its own `next_action` text,
which already commits to sourcing the heuristic from historical `session_budget` data across
completed phases. These could yield different fit heuristics.
Options: drop the acceptance bullet and, if nothing else needs it, the `phase-idg-10` dependency,
sourcing the fit test purely from `session_budget` history / keep the dependency and have
`phase-idg-10`'s standard extended to cover phase-level sizing.
Recommended: the former — `next_action` already committed to the `session_budget`-history approach,
and `phase-idg-10`'s real scope never touches phase sizing.
Evidence: C.md § question: Acceptance bullet cites a standard that does not cover what it is cited for

### 9. `phase-agx-09` doesn't build the mechanism `phase-irs-04` is told to consume
Affects: `phase-agx-09`, `phase-irs-04`
Raised by: group C
Decision needed: the plan's boundary table says `phase-irs-04` consumes a stale-claim/orphaned-
worktree recovery mechanism that `phase-agx-09` is supposed to build — but `phase-agx-09`'s actual
backlog scope is only a documentation/architecture essay, with no deliverable that is a runnable,
consumable mechanism. As written, `phase-irs-04` depends on something `phase-agx-09` never commits
to producing.
Options: none proposed in the source finding — flagged for whoever owns `phase-agx-09`/`phase-irs-04`.
Recommended: no recommendation given; this is a scope-ownership gap between two phases outside this
review's 23-phase scope.
Evidence: C.md § question: phase-agx-09's actual scope does not match what PLAN-039's boundary table says it owns

### 10. Widen `phase-irs-13`'s missing dependency edges
Affects: `phase-irs-13`, `phase-irs-11`, `phase-irs-06`, `phase-irs-07`
Raised by: groups B and C
Decision needed: `phase-irs-13` builds the gate queue but its `depends_on` names only
`phase-irs-04`. Group B flagged the missing edge to `phase-irs-11` (whose budget-park item kind the
renderer needs to know about); group C flagged the missing edges to `phase-irs-06`/`phase-irs-07`
(whose output — proposal, adversarial findings, evidence — is exactly the content the queue
renders). Pass 3's sweep found the plan document's own coverage table lists `phase-irs-04` only,
so the missing `-06`/`-07` edges match the plan as written; if they're needed, the plan's table
needs the same correction — still the owner's call, not a backlog slip.
Options: add `phase-irs-11`, `phase-irs-06` and `phase-irs-07` to `depends_on` (and correct the
plan's table to match, if the owner agrees) / leave as `phase-irs-04` only, treating "generic
ledger-entry rendering" as an explicit, if currently unstated, design constraint.
Recommended: add the edges — without them, the renderer is built against a guessed shape and a
rendering gap for budget-parked items.
Evidence: B.md § question: should depends_on include phase-irs-11?; C.md § question: phase-irs-13 builds the gate queue without depending on the phases that produce its content; pass3.md § Questions resolved by this sweep (partial)

### 11. Does `phase-irs-13` duplicate or extend `phase-irs-04`'s status verb?
Affects: `phase-irs-13`, `phase-irs-04`
Raised by: group B
Decision needed: is `phase-irs-13` a new presentation layer (e.g. a workbench panel) over the same
underlying queue `phase-irs-04`'s `status` verb already assembles, or does it own the real
decision-ready assembly (evidence digestion, adversarial-findings packaging), making `phase-irs-04`'s
`status` verb only a bare operational table for the daemon operator? The answer changes this phase's
actual size.
Options: `phase-irs-13` is purely a `ts/` presentation layer, changing nothing in `src/`'s assembly
logic / `phase-irs-13` owns the real assembly and `phase-irs-04`'s `status` verb is CLI-only.
Recommended: the latter — `phase-irs-04`'s own deliverables list no `ts/` at all, so whatever it
renders cannot be the owner-facing surface the requirements have in mind.
Evidence: B.md § question: does this phase duplicate or extend phase-irs-04's status verb?

### 12. Sibling agent-building phases missing a `depends_on` edge to `phase-irs-03`
Affects: `phase-irs-05`, `phase-irs-07`, `phase-irs-08`, `phase-irs-09`, `phase-idg-12`, `phase-irs-03`
Raised by: group B
Decision needed: each of these five phases builds the actual agent for a role `phase-irs-03`
contracts, but none lists `phase-irs-03` in its own `depends_on`. Without the edge, a contracted
agent could be built and merged before its binding never-do contract exists, making the
requirement's stated verification ("grep role contracts for the reservation") vacuous at ship time.
Options: none proposed in the source finding — this is a missing edge on the five phases' side.
Recommended: add `phase-irs-03` to all five phases' `depends_on`.
Evidence: B.md § question: sibling phases that build a contracted role's agent do not depend on phase-irs-03

### 13. Does `phase-agx-03`'s store expose a stable recording contract?
Affects: `phase-agx-03`, `phase-irs-10`
Raised by: group G
Decision needed: `phase-irs-10` requires the anti-pattern store's "own recording contract" to be
used "unchanged," but `phase-agx-03` (which builds that store) never requires the store to expose a
documented contract at all. Group D separately confirmed the `phase-agx-03`/`phase-irs-10`
deliverable seam is clean — but that check assumed a contract exists to stay stable, which is not
guaranteed as `phase-agx-03` is currently written.
Options: leave `phase-agx-03` as-is and let `phase-irs-10` reverse-engineer the store's shape when
it runs (risks building the "second store or parallel format" its own acceptance forbids) / require
`phase-agx-03` to name and document its recording contract explicitly.
Recommended: require the contract — stating it once while building the store is far cheaper than a
later phase inferring it from code and risking divergence.
Evidence: G.md § Out of scope: phase-irs-10 requires "the store's own recording contract... unchanged," but phase-agx-03 never requires the store to expose one; D.md § question: does this phase collide with phase-agx-03 on who "builds" the store?

### 14. What does "amend PLAN-025" actually require `phase-irs-02` to change?
Affects: `phase-irs-02`, `phase-part-03`
Raised by: groups D and H
Decision needed: two open facets of one question. (i) Does "amend PLAN-025" mean restructuring the
partition skill's own three gates down to fewer gates, or only batching their presentation into one
owner sitting at the orchestrator level? (ii) The three gate-stops are actually enforced by
`.claude/skills/partition-ideas/SKILL.md` (built by `phase-part-03`), not by the prompt pack or the
plan document — yet `phase-irs-02`'s `deliverables` never name that skill path, so if the answer to
(i) requires any behavioral change, no phase currently owns editing the skill's gate logic.
Options: presentation-batching only, narrowing the scope line and dropping the implied structural
edit, with no deliverables change needed / a real structural edit to `PLAN-025`'s gate count,
requiring a `docs/06-requirements/` deliverable and a REQ-009 amendment, plus widening
`phase-irs-02`'s deliverables to include the skill path.
Recommended: presentation-batching — the architecture document already describes this as
pipeline-level consolidation "where the material allows," not a rewrite of the skill's own gate
count — but if any behavioral change is intended at all, `deliverables` still needs the skill path
named, or the prose amendment and the skill's actual code risk drifting apart with nothing
reconciling them.
Evidence: D.md § question: does "amend PLAN-025" mean removing gates, or batching their presentation?; H.md § Out of scope: phase-irs-02's deliverables never name the workflow it must actually amend

### 15. "Stages 3 through 7" reads as license to duplicate peer-owned scope
Affects: `phase-irs-14`
Raised by: group A
Decision needed: the scope bullet "implement the batch graph covering stages 3 through 7" could be
read as writing the phase-fit, review and mapping logic inline — duplicating `phase-irs-05`/`-06`/
`-07`'s own scope — when the acceptance criteria in fact never require real stage-4/5/6/7 behavior.
Options: reword the scope bullet to state explicitly that stages 4/6/7 are stub/pass-through nodes
dispatched by role contract / leave as written and trust the acceptance bullets to constrain
behavior.
Recommended: reword — the wrong reading duplicates three other phases' work.
Evidence: A.md § question: "covering stages 3 through 7" reads as building peer-owned stage logic

### 16. The "partition record" `phase-irs-14` consumes is not a defined artifact
Affects: `phase-irs-14`, `phase-part-03`
Raised by: group A
Decision needed: `phase-irs-14`'s G2 node consumes "the partition record," but no concrete schema
or file location for it exists anywhere in the governing plans or architecture documents. The one
thing that exists — `phase-part-03`'s markdown output — is not machine-readable.
Options: a fixture/test-only partition proposal is enough to prove the graph mechanics, with a real
markdown-to-record bridge left to whichever (currently unscoped) phase wires `phase-part-03` in /
add a scope bullet defining a structured partition-record artifact plus a `phase-part-03`
dependency.
Recommended: flagged for the owner rather than guessed — the two readings produce very different
amounts of work.
Evidence: A.md § question: the "partition record" this phase's G2 node consumes is not a defined artifact

### 17. `phase-auto-04` has no `depends_on` edge onto the `P4` phases it needs
Affects: `phase-auto-04`, `phase-agx-01`, `phase-agx-05`
Raised by: group E
Decision needed: the plan's "should run after `P4`" guidance for `phase-auto-04` — unlike the hard
`depends_on` edge `phase-auto-06` gets onto `phase-agx-07` — is not a `depends_on` edge, so nothing
currently stops `phase-auto-04` (the run ledger) from being claimed and built before any
`phase-agx-*` phase completes, despite the plan's own claim that building it first means guessing.
Options: none proposed in the source finding — flagged since as written nothing enforces the
guidance.
Recommended: no recommendation given; a claim-blocking gap the owner should close.
Evidence: E.md § question: phase-auto-04 (the run ledger) has no depends_on edge onto P4, despite the plan's own claim that building it first means guessing

### 18. Should this programme register its own `sys-*` id?
Affects: `phase-auto-01`, `phase-auto-02`, `phase-auto-03`, `phase-auto-04`, `phase-auto-05`
Raised by: group E
Decision needed: `phase-auto-03` and `phase-auto-04` (outside group E) both declare
`systems: [sys-api]`, which the disjoint-systems rule would treat as a collision despite the plan's
claim they run in parallel. Should `phase-auto-01` register one or more new `sys-*` ids for this
programme's components instead of reusing `sys-api`?
Options: keep `sys-api`/`sys-governance` for every phase in the programme and accept `-03`/`-04` in
fact serialize, or amend the plan's concurrency claim / have `phase-auto-01` register new `sys-*`
id(s) (e.g. `sys-agent-ops`) and have `-02` through `-05` each declare a distinct id.
Recommended: register new ids — it's the only option consistent with both the plan's stated
concurrency and the repository's convention for new components.
Evidence: E.md § question: should this programme register its own sys-* id instead of overloading sys-api; E.md § question: phase-auto-03 and phase-auto-04 both declare systems: [sys-api], which ADR-003's disjoint-systems rule would reject as concurrent

### 19. Build a synthetic gate node to prove `phase-irs-04`'s resume mechanism
Affects: `phase-irs-04`
Raised by: group A
Decision needed: `phase-irs-04`'s acceptance (R17) requires a killed run to resume at its gate, but
the only graph this phase actually builds (intake, Stage 2) has no interrupt gate at all.
Options: build a synthetic, test-only gate node exercised by fixtures / narrow this phase's
acceptance to drop the "resumes at its gate" claim.
Recommended: the synthetic fixture — it's the only way this phase's own acceptance bullet is
checkable by its own graph.
Evidence: A.md § question: no gate exists in the one graph this phase actually ships

### 20. `phase-auto-03`/`phase-auto-04`'s identical `systems` declarations contradict the plan's parallel claim
Affects: `phase-auto-03`, `phase-auto-04`
Raised by: group E
Decision needed: as declared, these two phases directly contradict the plan's own claim that they
run in parallel under the disjoint-systems rule (see decision 18 above, which this resolves once
`phase-auto-01` registers new ids).
Options: none proposed in the source finding — flagged for whoever owns these two phases.
Recommended: resolved by decision 18's outcome.
Evidence: E.md § question: phase-auto-03 and phase-auto-04 both declare systems: [sys-api], which ADR-003's disjoint-systems rule would reject as concurrent — contradicting the plan's own claim that they run in parallel

### 21. Add missing PLAN-039.01 §6 hand-off duties to `phase-irs-08`'s scope
Affects: `phase-irs-08`
Raised by: group C
Decision needed: the orchestrator design's unit-run hand-off duties (session record written, every
`_tmpagent/` claim released, `git rebase dev`, a green governance check and `uv run pytest`, with
the G4 gate presenting that output) belong to "the unit run" — exactly what `phase-irs-08`
implements — but no `phase-irs-*` phase currently claims them in its own scope.
Options: add them explicitly to `phase-irs-08`'s scope / leave them unassigned across the fifteen
`phase-irs-*` phases.
Recommended: add them here — leaving them out means the executing agent has to invent this from the
design document alone rather than from its own phase's scope.
Evidence: C.md § question: Missing unit-run hand-off duties from PLAN-039.01 §6

### 22. Does "returning split phases into review" require calling `phase-irs-06`?
Affects: `phase-irs-05`, `phase-irs-06`
Raised by: group C
Decision needed: does "returning split phases into the three-altitude review" mean an end-to-end
call into `phase-irs-06`'s procedure (needing an added `depends_on: phase-irs-06` edge, not
currently present), or a status-marking action that needs no such edge?
Options: end-to-end call into `phase-irs-06`, requiring the added edge / status-marking only,
stated explicitly in scope.
Recommended: status-marking only — the plan's phase table lists `-05` and `-06` as both gating
only on `phase-idg-10`, independently of each other, which favours this reading.
Evidence: C.md § question: Does "returning split phases into review" require invoking phase-irs-06, or only marking them for it?

### 23. Commit the single-adversary-to-trio seam now, or defer it?
Affects: `phase-irs-06`, `phase-agx-11`, `phase-agx-12`
Raised by: group C
Decision needed: should `phase-irs-06` specify the single-adversary-to-trio "adoption seam"
concretely now — guessing at a shape `phase-agx-11`/`-12` haven't committed to — or commit only to
running a single adversary and leave the seam design to whichever phase lands second?
Options: build a narrow, minimal seam now (one verdict-in/findings-out call), accepting rework
risk / defer any seam commitment, stating the swap is `phase-agx-11/12`'s integration duty.
Recommended: defer — `phase-agx-11`/`-12` are themselves unbuilt, and over-specifying an interface
against an unbuilt pair invites the exact rework the seam was meant to avoid.
Evidence: C.md § question: The engine "adoption seam" has no stated contract to build against

### 24. Is `phase-auto-02`'s one-session budget realistic before `phase-auto-01`'s shape ruling?
Affects: `phase-auto-02`, `phase-auto-01`
Raised by: group E
Decision needed: `phase-auto-02`'s `session_budget: 1` may be unrealistic if `phase-auto-01` rules
for the full-policy shape (capability taxonomy, real approval workflow, audit trail, plus the
pending-approval action surface) rather than the smaller permissive-default shape.
Options: leave `session_budget: 1` and accept it may slip / have `phase-auto-01`'s ruling
explicitly weigh `phase-auto-02`'s session budget as a factor.
Recommended: leave for now — sizing before the ruling exists would be guessing.
Evidence: E.md § question: is one session realistic, and does it depend on phase-auto-01's ruling

### 25. Is `phase-irs-12`'s one-session budget realistic for a full trace, nine forced failures, and a new metrics tool?
Affects: `phase-irs-12`
Raised by: group D
Decision needed: this phase must run a full end-to-end trace, force nine separate stage-class
failures, and build and run a new deterministic metrics tool twice, all before its acceptance can
be checked, at `session_budget: 1`.
Options: leave as one phase and accept the risk it under-runs / split into a trace-and-metrics
phase and a separate forced-failure-drill phase / raise `session_budget` to 2 and keep the scope as
one unit.
Recommended: raise to 2 — the forced failures are most realistic when triggered against the same
real idea's run rather than a second, separately staged run.
Evidence: D.md § question: is one session enough for a full trace, nine forced failures, and a new metrics tool?

### 26. Reserve document codes now for three bare `docs/08-governance/` deliverables
Affects: `phase-idg-08`, `phase-idg-10`, `phase-idg-11`
Raised by: group F
Decision needed: each phase's deliverable is a bare `docs/08-governance/` directory rather than a
specific reserved filename. The proposed fix (reserve the code now under `GOV-005`, narrow the
deliverable) could not be applied by the reviewing group — the permission system blocked the edit
to `codes.yaml`'s `reserved` list. Should an agent with the needed authority reserve `GOV-010`
(`phase-idg-10`), `ADR-019`/`GOV-011` (`phase-idg-11`, successor to `ADR-010`), and whatever code
`phase-idg-08` needs, narrowing each deliverable to the specific filename?
Options: reserve the codes and narrow the three deliverables as proposed / leave the bare
directories and accept the deliverable-collision risk between the three phases.
Recommended: reserve — `GOV-005` exists precisely for this case; the only obstacle was a permission
grant this pass didn't have.
Evidence: F.md § fix: reserve document codes now and narrow the docs/08-governance/ deliverable; F.md § fix: same bare-directory deliverable collision as phase-idg-10; F.md § Out of scope: phase-idg-08 shares the exact same systems/deliverables collision

### 27. Does the anti-pattern store's recurrence detection need to reach all four capture destinations?
Affects: `phase-agx-03`
Raised by: group G
Decision needed: should the store's recurrence detection (R06) reach anti-patterns the
`log-anti-patterns` skill routes to `GOV-003`, `_data/ideas.jsonl`, or session records too, or is
it deliberately scoped to the "standing habit" class that lands in `brain/procedures/` only?
Options: scope to `brain/procedures/`-classified entries only / index across all four destinations
the skill can write to.
Recommended: index across all four — the requirement says "anti-patterns are stored" without
qualifying by destination, and a store blind to three of four capture paths will look like it
works while missing most future recurrences.
Evidence: G.md § question: Does the store cover only brain/procedures/-classified anti-patterns, or all four destinations the capture skill can write to?

### 28. Which `brain/procedures/` entries count as anti-patterns to ingest?
Affects: `phase-agx-03`
Raised by: group G
Decision needed: should the store ingest every file under `brain/procedures/` — including plain
how-to guides such as `add-new-project.md` or `session-close-with-no-active-phase.md` — or only the
subset that is actually anti-pattern-shaped?
Options: ingest the whole directory uniformly / name the qualifying subset explicitly.
Recommended: name the subset — both the governing plan and requirement cite only
`runtime-behavior-needs-runtime-evidence.md` (and, by the same logic,
`scope-dispatches-to-the-turn-budget.md`) as the verified "already exists" material.
Evidence: G.md § question: Which brain/procedures/ entries count as anti-patterns to ingest?

### 29. Does the "starter catalog" require writing three new procedure entries?
Affects: `phase-agx-03`
Raised by: group G
Decision needed: does "populate from the 2026-09-11 starter catalog" mean only the two items
already recorded as procedures, or does it require this phase to also write `brain/procedures/`
entries for three other anti-patterns named only in prose (idea `000138`) before counting them?
Options: count only the two already-recorded items / extract and record all five now.
Recommended: extract all five, per the requirement's own wording ("populated from what already
exists rather than started empty") — but this materially expands the phase's scope to include
authoring three new procedure entries.
Evidence: G.md § question: What counts as "the 2026-09-11 starter catalog," and is it a discrete artifact or prose to be extracted?

### 30. Should `phase-irs-11`'s OPS documentation land in `phase-irs-04` or `phase-irs-11`?
Affects: `phase-irs-04`, `phase-irs-11`
Raised by: group B
Decision needed: is the raise-cap/clear-switch operator procedure entirely `phase-irs-04`'s
documentation to write (since the halt/resume verbs ship there), or does `phase-irs-11`, which
builds the actual park/resume enforcement, need to amend that same OPS document once the
enforcement exists?
Options: `phase-irs-04`'s OPS doc covers it fully, `phase-irs-11` adds nothing to docs /
`phase-irs-11` amends the doc with the enforcement's actual behavior once it exists.
Recommended: the former — the verbs and their doc are one unit shipped together.
Evidence: B.md § question: does this phase need a docs/08-governance/ deliverable?

### 31. Should `phase-irs-13`'s `systems` list include a workbench id?
Affects: `phase-irs-13`
Raised by: group B
Decision needed: once decision 11 above settles where the gate-queue surface lives, does
`phase-irs-13`'s `systems` list gain a `sys-wb-*` entry so the governance conflicts rule can detect
a collision with a concurrent workbench-editing session?
Options: yes, whichever `sys-wb-*` id the chosen panel/host uses / no, if the surface is thin
enough that it touches no file under an existing `sys-wb-*` id's declared paths.
Recommended: yes — without it the conflicts rule is silently blind to a real collision.
Evidence: B.md § question: should systems include a workbench id if the surface lands there?

### 32. `phase-idg-11`: build the promoted-plan location on `GOV-005` reservations, or a separate mechanism?
Affects: `phase-idg-11`
Raised by: group F
Decision needed: the phase's acceptance states allocating a code before the draft exists "would
waste codes on drafts that never land," but `GOV-005` already provides a reservation mechanism for
exactly this case, removable without ever burning the number.
Options: build on `GOV-005` reservations, defining only the physical draft location and the
abandoned-draft case on top of them / design a separate mechanism.
Recommended: build on reservations — a second mechanism solving an already-solved problem
duplicates governance machinery for no stated benefit.
Evidence: F.md § question: does R18's "would waste codes" framing account for the existing reservation mechanism?

### 33. Is a mechanical grep check needed for `phase-irs-03`'s role-contract acceptance?
Affects: `phase-irs-03`
Raised by: group B
Decision needed: is a human read-through of the role contracts the intended verification for this
phase's acceptance bullets 1 and 2, or should a mechanical grep-based check be added, and against
what exact pattern?
Options: leave as owner/validator diff review, add no command / add a mechanical grep for the seven
reserved-action phrases across `.claude/agents/*.md` and `docs/08-governance/*contract*`.
Recommended: leave as a read-review — grepping natural language for "the owner-reserved list" is
brittle and would give false confidence.
Evidence: B.md § question: are acceptance bullets 1 and 2 checkable by the listed verification command?

### 34. Should the plan-quality standard reconcile with the generic document template?
Affects: `phase-idg-10`
Raised by: group F
Decision needed: should the new plan-quality standard supersede or rewrite the generic document
template (`templates/governance/document.md`, used by every document kind), extend it, or stand
beside it as a plan-specific layer the template still gates entry to?
Options: rewrite the template / layer a plan-specific standard beside it.
Recommended: layer beside it with an explicit cross-reference — rewriting the template touches
every document kind and is a larger change than "audit the plan corpus."
Evidence: F.md § question: does the standard reconcile with the existing generic template?

### 35. Should the plan-quality standard also cover requirement documents?
Affects: `phase-idg-10`, `phase-idg-12`
Raised by: group F
Decision needed: `phase-idg-10`'s scope is limited to `docs/01-plans/`, but `phase-idg-12`'s planner
drafts "the paired requirement" alongside the plan whenever the idea implies observable behavior —
and nothing this phase produces gives that later conformance check anything to check the
requirement document against.
Options: broaden now to also name what a good requirement document looks like / defer requirement-
document quality explicitly out of scope for now.
Recommended: broaden now — `phase-idg-12` depends on this phase's output and will need it the
moment it drafts a real requirement, not later.
Evidence: F.md § question: does the standard need to cover requirement documents too?

### 36. Should the flag file allow the stopgap tool to check the kill switch now?
Affects: `phase-irs-01`
Raised by: group B
Decision needed: should `phase-irs-01`'s dispatch hook check the `_working/orchestrator-halt` flag
file (a stat-only check, no dependency on later daemon code) before dispatching, so the kill
switch's "all pipeline dispatch" claim is actually true from day one — or is the stopgap
deliberately exempt until the daemon absorbs it?
Options: add the flag check now — cheap, closes the literal reading of the requirement / leave it
exempt and narrow the requirement's scope note to "all dispatch through the orchestrator."
Recommended: no default recommendation — this is a real definitional choice about whether the
interim tool counts as "the pipeline" for kill-switch purposes, not a mechanical one.
Evidence: B.md § question: does the kill switch apply to the stopgap tool?

### 37. Should `phase-irs-15`'s `systems` list add `sys-portfolio`?
Affects: `phase-irs-15`
Raised by: group A
Decision needed: should `phase-irs-15`'s `systems` list add `sys-portfolio` to match `phase-irs-09`'s
precedent, since its acceptance test exercises real idea-log writes end to end even though the
write path itself belongs to `phase-irs-09`'s already-sanctioned writer?
Options: leave as `sys-realization` only / add `sys-portfolio` for consistency with `-09`.
Recommended: leave as-is, but flagged because the inconsistency with its own dependency's system
list was not visibly a deliberate choice.
Evidence: A.md § question: should systems include sys-portfolio, matching phase-irs-09's precedent?

### 38. Two `phase-idg-10` acceptance bullets have no mechanical verification
Affects: `phase-idg-10`
Raised by: group F
Decision needed: two acceptance bullets ("every judgement names plans from the corpus on both
sides"; "names a section list a later plan can be checked against mechanically") have no
verification command that can check them — the only listed verification checks document
front-matter/schema validity, not prose content.
Options: leave as owner/reviewer read-check / add a minimal grep-based self-check once the
document's real heading text is known.
Recommended: leave as a read-check for now and revisit only if `phase-idg-12` (which must grep this
document) finds it unworkable.
Evidence: F.md § question: two acceptance bullets have no verification command that can check them

### 39. `src/db/ideas.py` has no home in `systems.yaml`
Affects: `phase-idg-01` (registry gap predates this phase)
Raised by: group F
Decision needed: `sys-portfolio`'s registry entry lists `tools/append_idea.py` and
`tools/generate_ideas_md.py` but not `src/db/ideas.py`, even though `sys-portfolio`'s own
description covers the append-only idea log and `src/db/ideas.py` implements `fold()` for it.
Options: none proposed in the source finding — flagged so it isn't rediscovered as if it were new.
Recommended: whoever maintains `systems.yaml` should add the missing entry.
Evidence: F.md § Out of scope: src/db/ideas.py has no home in systems.yaml

### 40. Should `phase-irs-05`'s R11 gate-arithmetic check get a free synthetic test now?
Affects: `phase-part-03`
Raised by: group H
Decision needed: R11, unlike R06 (needs two real dated documents) and R13 (needs a real dispatch to
measure), can be verified for free with a fabricated partition document and manifest. Should this
phase run that synthetic check before closing, or is a single deferred story for R06/R11/R13
together the intent regardless of R11's lower cost?
Options: add the free synthetic checklist test (fabricate a partition doc missing one id, confirm
the gate step catches it and names the id) to this phase's acceptance and verification / defer R11
along with R06 and R13 uniformly to the first real sweep.
Recommended: add it now — the requirement already specifies the exact fabricated-input test and it
costs nothing this phase isn't already spending.
Evidence: H.md § question: Should R11's gate-arithmetic check get a free synthetic test in this phase rather than being deferred with R06/R13?

### 41. What date stamps a same-day partition document?
Affects: `phase-part-03`
Raised by: group H
Decision needed: the dated filename convention (`docs/00-working/idea-partition-<YYYY-MM-DD>.md`)
is invented by this phase's own scope line, but nothing says whether the date is the corpus-build
date or the synthesis-completion date, or how a second same-day invocation collides.
Options: stamp by the corpus's build date and refuse/suffix on a same-day collision / stamp by
synthesis-completion date and allow same-day overwrite with a printed warning.
Recommended: stamp by corpus build date — the traceability point ("a partition document can be
traced to the slice it was built from") reads most naturally against the corpus date.
Evidence: H.md § question: What date stamps docs/00-working/idea-partition-<YYYY-MM-DD>.md when a sweep spans, or collides on, a calendar day?

### 42. Does the design need to state the broker's relationship to `AGENTS.md`'s convention-enforced rules?
Affects: `phase-auto-01`
Raised by: group E
Decision needed: does the design need to state explicitly whether the capability broker is meant to
eventually mechanically enforce `AGENTS.md`'s own convention-enforced rules (merge-locally-never-
push, confidentiality), or whether those stay a separate, still-convention-enforced concern?
Options: the design states these rules are out of scope for this programme and remain
convention-enforced / the design names them as future capability-set candidates.
Recommended: state them out of scope for this phase — `phase-auto-02`'s example capabilities
already don't include those two, but the design should say so rather than leave it implicit.
Evidence: E.md § question: does the design need to state the broker's relationship to AGENTS.md's existing convention-enforced rules

### 43. Does "returned to queued with reasoning attached" require editing `backlog.yaml`?
Affects: `phase-auto-01`
Raised by: group E
Decision needed: does the acceptance phrase require editing the deferred phase's own `next_action`/
scope text in `backlog.yaml`, or is recording the reasoning in the ADR alone sufficient?
Options: reasoning lives only in the ADR, phases unchanged / reasoning is also written into the
deferred phase's `next_action`, requiring `docs/09-backlog/` in deliverables.
Recommended: ADR-only — it needs no deliverables change and matches how decision phases already
operate elsewhere in this backlog.
Evidence: E.md § question: does "returned to queued with reasoning attached" require editing backlog.yaml

### 44. Two `phase-idg-10` acceptance bullets have no verification command — is a read-check enough?
Affects: `phase-idg-10`
Raised by: group F
Decision needed: (duplicate framing of decision 38 above at the source level — retained separately
because it names a different remedy timing.) Is a manual read at session-close sufficient for the
two unverifiable acceptance bullets, or should a mechanical spot-check be added now?
Options: leave as owner/reviewer read-check / add a minimal grep-based self-check.
Recommended: leave as a read-check for this phase.
Evidence: F.md § question: two acceptance bullets have no verification command that can check them

### 45. `PLAN-039`'s phase table still lists R01 against `phase-irs-02` alone
Affects: `phase-irs-02`
Raised by: group D
Decision needed: does the plan's requirement-coverage table correctly attribute R01 (all five gate
categories) to `phase-irs-02`, when this phase's scope only touches G2's partition sub-structure?
Options: leave as-is and treat it as a plan documentation slip, out of this phase's control /
narrow this phase's requirement attribution to R08 only, since R01 more properly belongs to
`phase-irs-04`.
Recommended: narrow the attribution if a later pass touches the plan's table — this phase's own
acceptance criteria only ever reference G2.
Evidence: D.md § question: PLAN-039's requirement-coverage table over-attributes R01 to this phase

### 46. `phase-idg-12`'s new `phase-dgov-01` prerequisite is missing from the front queue
Affects: `phase-idg-12`, `phase-dgov-01`
Raised by: the pass-3 orchestrator sweep
Decision needed: should `phase-dgov-01` be woven into `next_up` immediately before `phase-idg-12`,
now that `phase-idg-12` declares it as a dependency? `readiness()` ignores `next_up` (it only checks
`depends_on`), so nothing is broken at claim time — this is a queue-visibility gap, not a
correctness bug: an agent working strictly down the front queue would reach `phase-idg-12`, find it
`waiting`, and see no prerequisite queued ahead of it.
Options: weave `phase-dgov-01` into `next_up` between `phase-idg-11` and `phase-idg-12` / leave
`next_up` as-is and let `phase-dgov-01` be claimed from the general ready pool.
Recommended: weave it in — the same operation was already performed for the gate phases, and
without it the front queue's stated purpose (resolving this batch's dependencies in visible order)
is false for this one edge. Not applied during the review itself: editing `next_up` is outside this
session's authority grant under `PROMPT-035`.
Evidence: pass3.md § F: phase-idg-12's new prerequisite is missing from the front queue

## Resolved during the run

### `phase-idg-11`'s dependency on `phase-idg-10`
Resolved because: pass 3's adversarial sweep confirmed `phase-idg-11`'s scope and acceptance never
mention the plan-quality standard. `REQ-014` keeps R17 (the standard, owned by `phase-idg-10`) and
R18 (the storage location, owned by `phase-idg-11`) as two independent rows; R20, the row that
actually ties a draft to R17's standard, is scoped to `phase-idg-12`, which already, correctly,
depends on `phase-idg-10`. `depends_on: []` on `phase-idg-11` is correct as written; no edge was
missing.
Evidence: pass3.md § Questions resolved by this sweep
