---
schema_version: 1
id: doc-session-idea-triage-agent
code: SESS-2026-09-08-18
title: Build the idea triage agent
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-09'
systems: [sys-portfolio, sys-memory-agents]
depends_on: [doc-idea-record-system]
---

# Build the idea triage agent

## Phase

`phase-idea-02` — Build the idea triage agent.

## Verification

```
uv run pytest
```
395 passed, 2 warnings

```
uv run python -m src.governance
```
Governance OK: 16 systems, 105 documents, 13 memories, 101 backlog phases

## Acceptance

- The agent writes only through the tool from phase-idea-01, using the finding-kind annotated
  event phase-idea-08 adds — **Met**. `.claude/agents/idea-triage.md` writes exclusively via
  `tools/append_idea.py annotate --author agent-idea-triage --kind finding`; confirmed by three
  real runs against `_data/ideas.jsonl` (ideas `000046`, `000047`, `000048`), each producing
  exactly one `annotated`/`kind: finding` event before the idea moved to `triaged`.
- It never advances an idea beyond triaged; owner judgement is not automated — **Met**.
  `.claude/commands/idea-triage.md` calls `status <id> triaged` and nothing further; the
  subagent's own instructions forbid calling `status`, `revisit`, `amend` or `link` at all. All
  three triaged ideas (`000046`, `000047`, `000048`) stopped at `triaged` in the log. The one
  `promoted` transition made this session (idea `000007`, backfilled to `PLAN-016`) was an
  explicit, separate owner-directed action on a pre-existing idea, not something the triage
  agent performed or was asked to perform automatically.
- An overlap it finds is recorded on the entry as a finding annotation, never used to decline
  or merge one — **Met**. All three findings recorded overlap in prose; no idea was declined or
  merged. Extended this session, at the owner's direction, with two proposal mechanisms that
  still never execute: `PROPOSED LINK:` (idea-to-idea overlap) and `PROPOSED PROMOTION:` (an
  idea's ask already fully delivered elsewhere) — both are lines in the finding text for the
  owner to act on by hand; the subagent is explicitly forbidden from calling `link` or
  `status ... promoted` itself.

## Backlog

- `status`: `active`
- `next_action`: All three acceptance conditions verified `Met` against real triage runs
  (`000046`, `000047`, `000048`) and the current file content. No further work is required for
  this phase's own scope; a full sweep of the remaining ~44 open ideas is explicitly out of
  scope for this phase (see `## Left undone`).
- `completion_evidence`: `.claude/agents/idea-triage.md`, `.claude/commands/idea-triage.md`,
  `_data/ideas.jsonl` (annotated/status events for `000046`, `000047`, `000048`, and the
  `000007` backfill).
- `result`: Built, exercised against three real ideas end-to-end, extended with owner-directed
  link and promotion proposals, tree green.

## Unresolved

None for this phase's own acceptance. Broader follow-ups are recorded in `## Left undone`
below, not as blockers to this phase.

## Review

Independent sub-agent review, fresh context, no access to this session's conclusions. Ran
`git diff the commit “Claim phase-idea-02 for agent-claude”..HEAD` / `git log the commit “Claim phase-idea-02 for agent-claude”..HEAD`, its own `uv run pytest`, and inspected
`_data/ideas.jsonl` directly rather than trusting any record's claims. Verbatim:

> **Verification run:** `uv run pytest` → 395 passed, 0 failed (2 unrelated deprecation
> warnings). Full suite, own run, not trusted from any record.
>
> **Diff reviewed:** `git diff the commit “Claim phase-idea-02 for agent-claude”..HEAD` / `git log the commit “Claim phase-idea-02 for agent-claude”..HEAD` — 9 commits, 6 files
> touched. New deliverables are exactly `.claude/agents/idea-triage.md` (111 lines) and
> `.claude/commands/idea-triage.md` (77 lines); everything else in `.claude/` (`idea.md`,
> `session-close.md`, `backlog.md`, `settings.local.json`, `scheduled_tasks.lock`,
> `checkpoint/SKILL.md`) predates this range. No stray files under `.claude/`.
>
> ### Condition 1 — writes only via the finding-kind annotated event (phase-idea-08's addition)
>
> **Met.** `ANNOTATION_KINDS = ("note", "finding", "assessment")` and the `kind: finding`
> schema entry were added in commit “phase-idea-08: annotations and typed relationships” (phase-idea-08), which lands earlier in this
> same session's history than phase-idea-02's own commits — so the dependency is real, not
> just claimed. The agent file's own "How you write the finding" section shows exactly one
> write path: `tools/append_idea.py annotate <id> --author agent-idea-triage --kind finding
> --text "$(cat ...)"`. In the actual log (`_data/ideas.jsonl`), ideas `000046`, `000047`,
> `000048` each carry exactly one `annotated` event with `"kind": "finding"`,
> `"author": "agent-idea-triage"` — matching the instructed shape exactly, no other event type
> authored by that agent name anywhere in the file.
>
> ### Condition 2 — never advances an idea beyond `triaged`
>
> **Met.** Per-idea event tally for 000046/000047/000048: 3 `created`, 3 `annotated`, 3
> `status` (each `open`→`triaged`, written by the *driver* command per its own instructions,
> not the subagent), 1 `linked`. No `status ... reviewing`, `promoted`, or `discarded` event
> traces back to the triage runs. The one `status: promoted` in the range belongs to idea
> `000007` and was done by `agent-claude` (the main session), not `agent-idea-triage` —
> confirmed by commit “phase-idea-02: propose promotions; backfill 000007's own promotion”'s message, which is explicit that this is a deliberate
> backfill outside the triage agent's own execution, and the agent definition explicitly
> forbids calling `status ... promoted` even for a promotion it proposes. Caveat noted below
> on how this prohibition is enforced.
>
> ### Condition 3 — overlap recorded as a finding annotation, never used to decline or merge
>
> **Met.** The 000046/000047 findings both surface the same overlap (explicit mutual textual
> cross-reference) but only as prose plus a `PROPOSED LINK:` line — no `linked` event was
> written by the subagent itself. The one `linked` event that does exist (`000046
> --relates_to--> 000047`, no author field — the schema/tool gives `linked` events no author
> field at all) is dated `23:22:33`, after both triage findings (`23:12:14`/`23:12:24`) and
> matches commit “Link 000046/047, record 000049, triage 000048”'s message: "Wrote the relates_to link... (owner-approved, not
> agent-asserted)" — i.e., asserted separately by the owner-directed main session, not inside
> the subagent dispatch. Both agent definitions (`.claude/agents/idea-triage.md`) explicitly
> forbid the agent from ever calling `link` or concluding an idea should be declined/merged
> from an overlap.
>
> ### Distinction check (idea 000007 promotion, 000046↔000047 link)
>
> Confirmed via commit messages and event ordering that both actions were explicit, separate
> owner-directed calls to `tools/append_idea.py status`/`link`, not output of the
> `idea-triage` subagent's own execution:
> - the commit “phase-idea-02: propose promotions; backfill 000007's own promotion” ("propose promotions; backfill 000007's own promotion") — 000007's
>   `status: promoted` and its accompanying finding are authored `agent-claude`, and the
>   annotation text itself says "Backfilled promotion."
> - the commit “Link 000046/047, record 000049, triage 000048” ("Link 000046/047...") — commit body states "(owner-approved, not
>   agent-asserted)."
>
> Neither the `status` nor `linked` schema carries an `author` field, so this can't be
> confirmed by field inspection alone — the confirmation rests on commit messages plus
> timing/sequencing, which is corroborating but not cryptographic proof of provenance.
>
> ### Other findings — gaps and concerns
>
> 1. **Enforcement is instructional, not technical.** The subagent's tool grant is
>    `Read, Grep, Bash` — `Bash` is unrestricted, so nothing stops it from literally invoking
>    `tools/append_idea.py status/link` itself; the boundary lives entirely in the prompt's
>    "What you must never do" section, not in a tool-permission wall. This session's actual
>    runs stayed within bounds (verified above), but the acceptance criteria are enforced by
>    written instruction discipline, not by a hard technical constraint. Worth flagging, not
>    necessarily worth blocking on, since `phase-idea-01`'s writer script
>    (`tools/append_idea.py`) does independently validate transitions and would refuse an
>    illegal one.
> 2. **No automated test coverage added for the new agent/command markdown files** —
>    expected, since they're prompt definitions rather than importable code, and the existing
>    395-test suite is unaffected/unrelated to this change. Verification here is necessarily
>    behavioral (inspecting the actual log), which is what this review did.
> 3. **No discrepancies found** between what the two files say the agent/driver should do and
>    what the log actually shows they did, across the three triage runs (000046, 000047,
>    000048) reviewed in this session.
>
> **Overall: all three acceptance conditions are Met**, based on independent inspection of the
> diff, the agent/command definition text, the actual event log, and a fresh `pytest` run
> (395 passed).

## Decisions

- **Read post-processed idea state only, never raw `_data/ideas.jsonl`, except for
  idea-system analysis itself.** First draft of the triage agent read raw `created` events
  directly, missing amendments and other ideas' existing annotations/links. Corrected to
  `fold(load_events())` before the first real triage run. Saved as a standing memory
  (`idea-system-read-post-processed-only`) since this is exactly the kind of mistake likely to
  recur on future idea-system work.
- **`model: haiku`, `effort: medium`, `maxTurns: 15`** on the subagent, per owner direction —
  a scouting task doesn't need full-strength reasoning, and turn count is the one budget lever
  Claude Code subagent frontmatter actually exposes (confirmed via a dedicated lookup; token
  and wall-clock budgets require the Agent SDK, explicitly deferred to a later
  re-evaluation, not built here).
- **Overlaps are proposed, never auto-asserted.** Idea-to-idea overlap becomes a
  `PROPOSED LINK:` line in the finding text, not a written `linked` event, per `PLAN-017.04`'s
  "extraction may propose; only a written `linked` event asserts" — confirmed with the owner
  before building rather than assumed.
- **Extended to propose promotions too, at the owner's direction**, after backfilling idea
  `000007`'s missed promotion surfaced the gap: an idea whose actual ask is already fully
  delivered by an existing document had no way to flag that during triage. `PROPOSED
  PROMOTION:` mirrors `PROPOSED LINK:` — named a governed document code, never a bare phase
  id, matching what `--promoted-to` actually records — and carries a deliberately stricter bar
  (fully delivered, not merely related) so it doesn't collapse into a second, softer version of
  the link proposal.
- **Ideas cite id-first in conversation** (`000046 (idea planner agent)`), inverting `GOV-006`'s
  document convention (name-first, code in parentheses) — an idea's six-digit id is its actual
  lookup handle in the log, unlike a document code that doubles as a filename fragment. Added
  to `GOV-006` itself at the owner's direction, rather than left as an unwritten session
  convention.
- **Test fixtures were real ideas, not synthetic ones.** The owner asked for actual triage
  runs to exercise the agent, so two real ideas were recorded first (`000046`, `000047`,
  deliberately cross-referencing each other to test overlap detection), then a third
  (`000048`, the idea scribe agent) came from the owner mid-session. All three are genuine
  ideas worth having on record regardless of this phase, not disposable test data.

## Corrections

- Raw-vs-post-processed read bug (above) — caught and fixed before any real triage run used
  the flawed logic, so no bad finding was ever written from it.
- `docs/08-governance/catalog.md` went stale twice this session (after the initial claim
  commit, and again after the `GOV-006` edit) because catalog regeneration wasn't bundled into
  the same commit as the triggering change. Both caught by the governance check before
  proceeding, neither shipped broken.
- First `backlog.yaml` edit for this checkpoint used the session's `code` (`SESS-2026-09-08-18`)
  in the phase's `session:` field; the schema expects the document `id`
  (`doc-session-idea-triage-agent`). Caught immediately by `uv run python -m src.governance`
  and corrected before this record was finalized.

## Left undone

- **Token/wall-clock budget caps** remain undone by design — flagged as SDK-only and
  explicitly deferred to a later re-evaluation, not silently dropped.
- **A hard technical guarantee against a misdirected write is still unbuilt.** The two
  guardrails added in the addendum below (literal command handoff, independent verification)
  fix the actual root cause observed, but neither makes a wrong write structurally
  impossible the way a wrapper script would. Planned as `phase-idea-10`, `queued`, not
  started.
- **The full `PROPOSED LINK`/`PROPOSED PROMOTION` queue from the addendum sweep is unreviewed
  by the owner.** Recorded in `_working/idea-triage-followups.md` for a fresh session to work
  through in batches.

## Addendum — 2026-09-09, post-closure work

`phase-idea-02` reached `status: complete` above before this addendum was written. Everything
below happened in the same continuous session, on direct owner instruction, without a new
backlog phase being claimed for it — noted here as a process gap rather than papered over: this
work should probably have been claimed as its own phase before starting, and the pattern is
worth watching for in future sessions where "one more thing" keeps extending past a phase's
formal close.

**Branch audit.** `agent/phase-idea-03` and `chore/first-commit` were both fully merged into
`dev` with no live worktrees (`git merge-base --is-ancestor` confirmed both); deleted via safe
`git branch -d`. Only `dev` remains.

**Full triage sweep.** All 44 ideas open at the time (`000001`-`000045` minus already-promoted
`000007`/`000039`, plus `000049`) were triaged via repeated `idea-triage` dispatches, in
batches of 5-8 concurrent subagents. Zero ideas remain `open`; 47 `triaged`, 2 `promoted`. 33
`PROPOSED LINK` and 2 formally-written `PROPOSED PROMOTION` candidates were surfaced (plus one
looser promotion candidate in prose only, `000045` → `PLAN-001`, that didn't meet the written
line's stricter bar) — none executed; the full list is in
`_working/idea-triage-followups.md` for the owner to work through.

**`maxTurns` did not take effect this session.** Bumped `15` → `30` in the subagent's
frontmatter mid-sweep after two ideas (`000006`, `000009`) hit the cap with no write. A
controlled retry immediately after the edit still hit exactly 15 tool calls, mid-task,
repeatedly (`000010`, `000012`, `000013` each failed once more after the bump). Root cause
unconfirmed — most likely the subagent definition was cached from earlier in this session and
the harness does not hot-reload `.claude/agents/*.md` mid-session. Worked around by
constraining scope (≤2 grep calls, write as soon as reasonably confident) rather than relying
on a larger budget; every constrained retry succeeded in well under 15 calls. **Needs
confirming in a fresh session** whether `maxTurns: 30` is actually honored once the harness
reloads agent definitions from disk.

**A stale test fixture broke.** `test_ideas.py::test_time_in_each_state_is_queryable_without_
parsing_markdown` hardcoded synthetic events onto real idea `000001`, on the documented
assumption that "the real log has 19 created events and nothing else" for that idea. Triaging
`000001` gave it real `annotated`/`status` events, colliding with the fixture's hardcoded
`seq` values and breaking the test. Fixed by moving the fixture onto a fabricated idea id
(`999999`, never present in the real log) — permanently decoupled from any real idea's
accumulating events, not just a patch for today's state.

**A real data-integrity bug.** One subagent dispatch wrote idea `000012`'s finding text onto
idea `000014`'s annotation — held the right id in its prompt, retyped the wrong one when
constructing the `annotate` command by hand. Caught by systematically diffing every finding's
own idea-number cross-references against the idea it was actually recorded on, not by trusting
any subagent's self-report (three other apparent mismatches on the same check turned out to be
false positives — ideas legitimately discussing another idea first). Corrected via
`amend-annotation` (append-only log — the wrong text stays as a permanent, explained record of
the mistake rather than being deleted), with a fresh, correctly-scoped dispatch supplying the
real finding.

**Two guardrails added against a recurrence**, both markdown-only, no new infrastructure:
1. The driver (`.claude/commands/idea-triage.md`) now interpolates the exact `annotate`
   command — id already filled in — into each dispatch prompt; the subagent runs it verbatim
   rather than reconstructing it from memory. This targets the actual root cause: the
   corruption happened at the retyping step, not from a design flaw in what the command should
   contain.
2. Both the subagent (before reporting success) and the driver (before advancing status)
   independently read back the newest annotation for the target id and check it doesn't open
   by naming a different idea's number as its own subject. Two checkers, neither trusting the
   other's report.

**A harder technical guarantee was investigated, not built.** Two options exist beyond the
Claude Code subagent frontmatter (`name`/`description`/`tools`/`model`/`effort`/`maxTurns` —
confirmed to be the complete set; no argument-validation or parameter-injection field):
- **A wrapper script.** The driver writes a fresh, per-dispatch file containing the pinned
  target id before each dispatch; the subagent is restricted to calling a thin wrapper
  (`tools/triage_annotate.sh <pin-file> <text-file>`) that reads the id from that file — never
  from an argument the agent supplies — so the agent has no path to write to the wrong id even
  if confused. One shared agent definition and one shared script still serve every idea; only
  the disposable pin-file changes per dispatch, created and discarded like the existing
  temp finding-text files. This is the strongest option achievable without the Agent SDK.
- **A `PreToolUse` hook.** Verified (not assumed) via a dedicated lookup: Claude Code hooks can
  block a Bash call (exit code 2), fire inside subagent execution, and the payload carries
  `agent_id`/`agent_type` distinguishing which dispatch is calling. But command-pattern
  matching is documented as "best-effort" (shell variable expansion isn't resolved for the
  hook), and correlating a hook's `agent_id` to "what id was this dispatch scoped to" requires
  the driver to write a correlation file in the narrow window between the Agent tool call
  returning its `agent_id` and the subagent's first tool call — a real race condition, not a
  solved problem.

Scoped as `phase-idea-10` (`queued`) rather than built now — genuinely new surface area (a new
script, a new file convention, a testing story for the pin-file mechanism) that deserves the
same plan-before-implementing treatment as any other non-trivial change, not a reflex patch
appended to an already-closed phase.
