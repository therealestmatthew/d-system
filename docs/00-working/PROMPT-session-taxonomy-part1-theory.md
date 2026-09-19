# Prompt: Session-type taxonomy — Part 1 (theoretical model)

Paste everything below the line into a fresh Claude Code session opened in `/code/d-system`.

This is the first of two prompts. Part 2 (the empirical test) exists as a separate document the
owner hands over later; **do not read it** — `docs/00-working/PROMPT-session-taxonomy-part2-evidence.md`
is off-limits to this session. The separation is deliberate: the theory must be written without
knowledge of how it will be measured, so it cannot be shaped to fit the measurement.

---

## Mission

Propose a theoretical classification of the kinds of sessions the owner runs with Claude Code in
this repository — from first principles and the repo's visible surface, **before any evidence is
examined**. A later empirical phase will test this theory against ~108 raw transcripts and ~119
session records; you will not see that phase's design, and you read no transcripts here.

The taxonomy has six consumers, and each shapes what a session type's profile must record:

1. **Tooling design** — which types deserve their own skill / command / agent setup, the way
   phase work already has `/session-start` and `/session-close`.
2. **Governance and records** — which types need session records, worktrees, and backlog claims,
   and which are legitimately exempt.
3. **Descriptive understanding** — which types actually occur, and roughly how often (the
   empirical phase answers this; the theory predicts it).
4. **Orchestration design** — the orchestrator session variants and their boundaries (e.g. one
   that runs plan phases parallelized into action chains vs. one that orchestrates ideation,
   triage, and idea partitioning).
5. **CLAUDE.md / AGENTS.md revamp** — the owner intends to redesign both files, with CLAUDE.md
   treated as the primary agent's entry document. The taxonomy should feed *identification
   logic*: "a session that looks like X follows protocol Y" rules that turn today's prose
   governance into recognizable patterns and skill triggers. The owner's design notes from a
   Gemini conversation are Appendix A below; treat them as design input to evaluate against
   first principles, not as decided policy.
6. **A portable session-type model** — the taxonomy's core must generalize beyond this repo: a
   claim about what kinds of Claude Code sessions exist anywhere, usable to design any repo's
   entry documents and tooling. The deliverable keeps two layers cleanly separated: a *portable
   core* (types defined only by signals any repo exhibits — the intent of the first prompt,
   read/write posture, delegation structure, the kind of artifact produced) and a *d-system
   binding* (how each type manifests here: which local skills, records, and governance
   obligations attach). A type whose definition cannot be stated without naming a d-system
   artifact is not portable — it goes in the binding layer, and the portable layer records the
   generic type it instantiates. Related local context: the backlog's portable-framework phases
   and the framework-generalization session record
   (`docs/03-sessions/SESS-2026-09-19-05-framework-generalization-and-concurrency.md`) — read
   for alignment, not as constraints on the model.

The deliverable is a working document, not a governed one, and not an edit to CLAUDE.md or
AGENTS.md. **Do not modify CLAUDE.md or AGENTS.md under any circumstances** — that rule is
absolute in this repo.

## Session setup

This is a read-only investigation whose only output is an untracked file in `docs/00-working/`.
At the start, ask the owner (AskUserQuestion) whether to run it as an unclaimed ad-hoc session or
under the full `/session-start` claim-and-worktree protocol; do not assume either.

## Inputs — and what is out of bounds

**Allowed inputs:**

- The owner's seed taxonomy below.
- First-principles reasoning about agentic work: what dimensions distinguish sessions (intent of
  the first prompt, read/write posture, delegation structure, artifact produced, governance
  weight), and what a complete set looks like.
- The repo's tooling and governance surface: `.claude/skills/`, `.claude/commands/`,
  `.claude/agents/`, `.agents/skills/`, `docs/08-governance/` (GOV-* and OPS-* docs),
  `docs/09-backlog/backlog.yaml` + README. The tooling built so far implies types the owner
  already found worth supporting; governance docs imply obligations that attach to types.
- The repo's existing governed session-type work, from `phase-ses-01`: the per-type
  obligations requirement (`REQ-023`) and the type-declaration and lifecycle decision
  (`ADR-020`). Prior art to build on, extend, or depart from — not a constraint. Where the
  proposed taxonomy differs from REQ-023's set, say so explicitly and give the reason; the
  empirical phase will test both.
- Appendix A.
- At most a skim of session-record *titles* (`ls docs/03-sessions/`) for orientation.

**Out of bounds:** raw transcripts in `~/.claude/projects/`, the *contents* of session records,
and the Part 2 prompt. The theory's value to the later test depends on it being registered before
the evidence is seen.

## Seed taxonomy (owner's braindump — extend and structure it, don't just confirm it)

- One-off questions (ask about something, no repo change)
- Idea capture sessions
- Planning sessions (requirements, plans, backlog phases)
- Direct coding sessions (executing a plan phase, no sub-agents)
- Orchestrator sessions, possibly several kinds:
  - phase-execution orchestrators (parallelized plan phases sequenced into action chains)
  - ideation/triage/partitioning orchestrators

Your job is to (a) validate, split, or merge these on theoretical grounds, (b) propose types the
seed list plausibly misses, and (c) propose types that may not yet occur but would be useful to
define — e.g. maintenance/audit sessions, governance-revision sessions, retrospective sessions,
demo/rehearsal sessions, literature-review sessions. Mark each type as seed-derived, inferred
from the tooling surface, or proposed-novel.

## Predictions must be falsifiable — this is the core requirement

For each proposed type, state predictions about what its sessions should look like in evidence,
**bound to observables** and registered before any evidence is seen. Each type's predictions must
name:

1. **First-prompt signature** — what the opening prompt's intent and phrasing look like, in
   generic terms (portable core) and in this repo's terms (binding layer: specific commands,
   phrases, or skills that would open such a session).
2. **Activity signature** — expected read/write posture (read-only? which top-level directories
   get written: `docs/01-plans/` vs `src/` vs `_data/`?), expected delegation (sub-agents or
   none, and of what kind), expected tool mix in coarse terms.
3. **Artifact** — what the session leaves behind (a document, code, ideas appended, a record,
   nothing).
4. **At least one disconfirming observation** — something that, if seen in a session of this
   type, would count *against* the type's definition as drawn. A prediction nothing could
   contradict is not a prediction; rewrite it until it excludes something.
5. **Expected frequency band** — rare / occasional / common, so the empirical phase can score
   surprises in both directions.

## Deliverable

One untracked document; commit nothing: `docs/00-working/session-types-theory.md` — the proposed
theoretical taxonomy: the distinguishing dimensions, the proposed portable types (each with
definition, generic entry signals, and the falsifiable predictions above), the expected d-system
binding per type, an initial reading of Appendix A against the proposed model, and the open
questions the owner should ponder before the empirical phase.

**Stop there.** Deliver the document, then halt and give the owner the floor. Do not begin any
transcript or session-record analysis in the same breath, under any banner — including
"orientation" or "spot-checking a prediction". The owner may revise the model, run an adversarial
review on it, or let it sit. The empirical phase proceeds only on their explicit go, in a later
session, with its own prompt.

## Conduct

- Follow GOV-006 reporting style: name things then cite codes; paste the output that carries
  information; corrections stated plainly.
- If the owner voices any new want mid-session, capture it immediately via
  `tools/append_idea.py` per GOV-006.
- Ask questions via AskUserQuestion, batched, at the point the work reaches them; state
  assumptions that can wait and surface them at the end.

## Appendix A — Owner's CLAUDE.md design notes (from a Gemini conversation)

Design input. Evaluate against first principles and the repo's surface; do not treat as decided
policy.

### The behavioral spine (Karpathy's 4 rules)

Behavioral posture over technical specifics:

1. **Think before coding (no silent assumptions)** — if a prompt is ambiguous or has multiple
   interpretations, stop, name what is confusing, and ask. Do not guess intent.
2. **Simplicity first (no over-engineering)** — the minimum code required for the immediate
   problem. No speculative features, no "just in case" flexibility, no abstractions for
   single-use code.
3. **Surgical changes (no orthogonal edits)** — touch only the lines the request needs. No
   formatting adjacent code, no refactoring what isn't broken; match existing style.
4. **Explicit verification (goal-driven execution)** — define success criteria upfront, loop
   until verified, run the relevant tests and check terminal output before claiming done.

### Core values over rigid rules

Rigid rules break when context shifts; values let the model make correct tradeoffs.
Bad (rigid): "Keep responses short. Avoid over-engineering. No comments unless asked."
Good (value-driven): "Clarity matters more than brevity when something is genuinely complex. If
a comment states what the code already shows, cut it; if it explains a tradeoff or a non-obvious
decision, keep it."

### The modern root CLAUDE.md structure

Lean (under 50 lines); a behavioral router, not a mini-wiki:

- **Core values & posture** — the behavioral rules above.
- **Context map** — pointers to where specific architectural/database documents live ("read
  docs/ARCHITECTURE.md before touching the database").
- **Verification commands** — exact, non-interactive CLI commands so the agent never hangs in
  the terminal.
- **Global gotchas** — only the 1–2 massive, repo-breaking landmines.

### Path-scoped rules and the phase split

`.claude/rules/` files carry YAML frontmatter with glob patterns (`paths: - "src/**/*.ts"`);
when Claude touches a matching file the rules are deterministically injected. The vulnerability:
loading is deterministic but late — a plan drawn up before any file is opened is made blind to
path-specific constraints. The hybrid fix splits context by execution phase:

- **Phase 1, planning (root CLAUDE.md)** — loads unconditionally at session start: high-level
  architecture, tech-stack boundaries, core values needed before deciding what to touch.
- **Phase 2, execution (`.claude/rules/`)** — loads via glob matching: granular, syntax-level
  constraints that only matter once code is being typed.
