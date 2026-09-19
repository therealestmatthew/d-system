# Prompt: Session-type taxonomy — Part 3 (record quality and templates)

Paste everything below the line into a fresh Claude Code session opened in `/code/d-system`,
**only after Part 2's taxonomy has been delivered and the owner has given an explicit go.**

Registration note: this prompt is executed by **phase-fwa-03** (session and decision record form
critique, PLAN-041, serving 000276), which depends on the taxonomy's empirical phase
(`phase-tax-02`); its proposed schema feeds **phase-fwt-04** (session-record document schema,
PLAN-040, serving 000277). It is not a phase of the taxonomy plan itself.

Required inputs — stop and tell the owner if either is missing:

- `docs/00-working/session-taxonomy.md` (Part 2's evidence-tested taxonomy)
- `_private/analysis/session-taxonomy/record-structure.tsv` (Part 2's per-record structural
  facts: sections vs contract, length, deviations, front-matter completeness)

---

## Mission

Serve two open ideas, which this phase exists to close out with a concrete proposal:

- **000276** (session-record quality analysis) — how session records are actually written:
  structure, length, signal-to-noise, whether each required field earns its place. Are the
  records carrying unnecessary information? Too verbose? Missing information that needs to be
  captured?
- **000277** (session-documentation template and schema) — restructure the checkpoint and
  session-close outputs as templates populated with key fields, backed by an authoritative
  schema, covering the fields downstream consumers need: decisions, new requirements, deferred
  items, action items, verification output, completion evidence.

Related context to honor, not re-solve: **000275** (sub-agent extraction of decisions buried in
record prose — a template that makes extraction mechanical serves it), **000237** (checkpoint
and session-close must cover unclaimed sessions — the template must have an unclaimed branch),
and **000267** (schema-govern every durable object — the schema proposed here should follow
that pattern). 000276 also names *decision records*; that half is out of this phase's scope —
note it in the deliverable as remaining open on the idea.

This is a proposal phase. **Change nothing that is governed:** no edits to
`.claude/commands/session-close.md` (owner-only command), no edits to the checkpoint skill —
note that `.claude/skills/checkpoint/SKILL.md` is generated from `agent-workflows/`, so any
accepted change lands in the source, not the generated file. And never CLAUDE.md or AGENTS.md.

## Session setup

At the start, ask the owner (AskUserQuestion) whether to run as an unclaimed ad-hoc session or
under the full `/session-start` protocol; do not assume either.

## Evidence and method

1. **The prose contract as it stands.** Read `.claude/skills/checkpoint/SKILL.md` (the record
   contract: front matter plus `Phase` / `Verification` / `Acceptance` / `Backlog` /
   `Unresolved`) and `.claude/commands/session-close.md` (the close sections: `Review` /
   `Decisions` / `Corrections` / `Left undone`). This is the de facto template; the question is
   whether it is the right one, not whether one exists.
2. **How records deviate in practice.** Analyze `record-structure.tsv` — deviation rates per
   section, length distribution, non-contract sections that keep appearing (recurring
   inventions like `Outcome` / `Evidence` / `What this session produced` are demand signals for
   fields the contract lacks, not just noncompliance). Read a handful of the outlier SESS files
   directly — they are curated, tracked documents; whole-file reads are fine here.
3. **Field-by-field audit, per consumer.** For every contract field and every recurring
   invented section, ask who consumes it: the owner reviewing a session, extraction agents
   (000275), governance gates (`/session-close`'s acceptance check), future audits, the
   CLAUDE.md revamp. A field no consumer reads is a candidate to cut; information a consumer
   needs that lives in narrative prose is a candidate to become a structured field. Use Part
   2's taxonomy: which fields are universal, and which only make sense for certain session
   types (a question session has no acceptance conditions; an orchestrator session has
   delegation to account for).
4. **Verbosity findings need evidence.** "Too verbose" is a claim about specific sections in
   specific records — cite record and section, and say what a bounded version would keep.

## Deliverable

One document at the executing phase's declared deliverable path,
`docs/00-working/framework/06-analysis/session-protocol-enhancements.md` (phase-fwa-03,
REQ-025 R03) — cite idea 000276 and the batch anchor 000281 in it:

1. **Field verdicts** — per contract field and recurring invented section: keep / cut /
   restructure / add, each with the consumer it serves and the evidence (deviation counts,
   examples).
2. **Proposed template(s)** — the populated-fields structure for checkpoint output and the
   session-close additions: a markdown skeleton with each field's type, whether required, and
   its bounded format (e.g. verification output capped to the failing lines plus counts).
   State explicitly whether one template with per-type optional blocks or per-type variants
   fits the taxonomy better, and why.
3. **Proposed schema** — machine-readable (JSON Schema, matching `schemas/`' existing pattern
   per 000267), validating front matter and section presence, with the unclaimed-session
   branch (000237) covered.
4. **Adoption path** — what changes in `agent-workflows/` (checkpoint source) and
   `session-close.md` if the owner accepts, as a described diff, not an applied one; and how
   existing records are treated (grandfathered vs migrated — recommend, don't decide).
5. **Open questions for the owner** — batched, few, and only ones that change the design.

## Conduct

- Follow GOV-006 reporting style: name things then cite codes; ideas id-first (`000276
  (session-record quality analysis)`); paste the output that carries information.
- If the owner voices any new want mid-session, capture it immediately via
  `tools/append_idea.py` per GOV-006.
- Ask questions via AskUserQuestion, batched, at the point the work reaches them; state
  assumptions that can wait and surface them at the end.
