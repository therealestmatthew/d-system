---
schema_version: 1
id: doc-idea-realization-plugin-absolutes-trace
code: PLAN-048.10
title: Idea-realization plugin — trace table for the governance documents as absolutes, part one
kind: plan
status: approved
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-plugin-absolutes]
depends_on: [doc-idea-realization-plugin-absolute-documents]
parent: doc-idea-realization-plugin
---

# Trace table: the governance documents as absolutes, part one

Child of [PLAN-048](PLAN-048-overview.md); written by `phase-plug-07` under
[PLAN-048.07](PLAN-048.07-absolute-documents.md). It maps every rule in the plugin's
`docs/protocol.md`, `docs/backlog-protocol.md`, `docs/document-codes.md` and `docs/reporting.md`
to the source passage it restates, lists the source rules that were not shipped and why, and
records the decision-ledger triage (family C) in full so `phase-plug-09` reads it for families E
and F instead of re-dispatching it. The plugin never cites this file (`REQ-031` R02).

## Context and scope

`REQ-031` R20 requires the plugin's governance documents to state current rules with no history,
with every still-standing rule of the decision ledger (`GOV-003`) inlined into the document it
amends, and a trace table in this repository. This file is that table for families A (core
protocol and codes: `GOV-001`, `GOV-002`, `GOV-005`, `AGENTS.md`), B (reporting: `GOV-006`) and C
(ledger triage: `GOV-003`, `GOV-004`). Families D, E and F are `PLAN-048.09`.

Source line numbers refer to the files as they stood on `dev` when `phase-plug-07` was claimed.
`P:` abbreviates `plugins/idea-realization/`.

## Design

Three analyst dispatches, one per family, each returned one-line absolutes with source lines and
the plugin mechanism behind each rule; the ledger triage ran first and its still-standing rules
were attached to family A's dispatch. Each rule id below (`A`, `B`, `C` prefixes; family B's
reporting rules use `R`) is the analyst's; the "Plugin location" column names the document and its
numbered section. Where the plugin's mechanism differs from the source, the plugin's version is the
rule and the row says so.

## Work and dependencies

1. Family C classified the ledger (section "Ledger triage").
2. Families A and B extracted the rules (sections "protocol.md" to "reporting.md").
3. The four plugin documents were written from the extractions; `P:test/test_no_history.py`
   guards `P:docs/` against history words.

## Ledger triage (family C, from GOV-003 and GOV-004)

Every dated entry of the decision ledger and every section of the initial coverage review,
classified as a still-standing rule (STANDING, with the rule id in the next table) or history
(dropped from the plugin). `phase-plug-09` reads this classification for families E and F.

### Classification

| # | Source | Entry | Class | Reason |
|---|---|---|---|---|
| 1 | GOV-003:17-22 | Schema-design reconciliation; project-party authority | HISTORY | Repository-specific schema decision |
| 2 | GOV-003:24-27 | Two uncommitted captures allocated overlapping idea ids | HISTORY | One-time; embedded rule is C26 |
| 3 | GOV-003:29-31 | Two reviews both used one ARCH code | HISTORY | One-time; embedded rule is C3a |
| 4 | GOV-003:33 | Authority: questionnaire answers | HISTORY | One-time authorization |
| 5 | GOV-003:37 | Row: delivery scope | HISTORY | One-time; principle already in AGENTS.md:168-169, GOV-002:17 |
| 6 | GOV-003:38 | Row: `project.stakeholders` authoritative | HISTORY | Repository-specific |
| 7 | GOV-003:39 | Row: global memory retrieval | HISTORY | Repository-specific product choice |
| 8 | GOV-003:40 | Row: page data authority | HISTORY | Repository-specific |
| 9 | GOV-003:41 | Row: runtime block validation | HISTORY | Repository-specific |
| 10 | GOV-003:42 | Row: memory writers | HISTORY | Repository-specific |
| 11 | GOV-003:43 | Row: Chronicle trigger manual | HISTORY | Repository-specific |
| 12 | GOV-003:44 | Row: embeddings deferred | HISTORY | Repository-specific |
| 13 | GOV-003:45 | Row: retrieval hints blended | HISTORY | Repository-specific |
| 14 | GOV-003:46 | Row: agents propose, owner resolves memory conflicts | HISTORY | Repository-specific (memory subsystem) |
| 15 | GOV-003:48-52 | Blended hint design | HISTORY | Repository-specific |
| 16 | GOV-003:54-56 | Delegated implementation choices | HISTORY | Repository-specific |
| 17 | GOV-003:58 | `--all` and limit semantics | HISTORY | Repository-specific |
| 18 | GOV-003:60-66 | Concurrency-collision ledger: when an entry is required | STANDING | C1 |
| 19 | GOV-003:70 | Collision row: double-claimed ADR code | HISTORY | One-time; embedded rule C3a; reservation now automated (GOV-005) |
| 20 | GOV-003:71 | Collision row: one idea id | HISTORY | One-time; embedded rule C3b |
| 21 | GOV-003:72 | Collision row: a run of idea ids | HISTORY | One-time; embedded rule C3b |
| 22 | GOV-003:74-77 | Ledger rows in the same diff; disjoint-phase source conflicts always recorded | STANDING | C1, C2 |
| 23 | GOV-003:79-83 | Choices after the capture definition session (intro) | HISTORY | One-time |
| 24 | GOV-003:85-98 | Signal track depends on capture | HISTORY | One-time ordering |
| 25 | GOV-003:100-106 | Solo agent on a docs-only phase works in the primary checkout | HISTORY | Superseded by GOV-003:330-334 |
| 26 | GOV-003:108-112 | A phase widened to lift the prohibition | HISTORY | One-time |
| 27 | GOV-003:114-116 | Resolution note | HISTORY | Superseded by GOV-003:330-334 |
| 28 | GOV-003:118-123 | Promoted records keep a source reference | HISTORY | Repository-specific (capture pipeline) |
| 29 | GOV-003:125-137 | Field-rename ownership; historical records keep old names | HISTORY | One-time; see open point U11 |
| 30 | GOV-003:139-143 | Widenings committed before the work | HISTORY | One-time; embedded rule C4 |
| 31 | GOV-003:145-148 | Contracts precede the source preflight | HISTORY | One-time ordering |
| 32 | GOV-003:150-157 | `waiting_on.owed_by` stays unprotected | HISTORY | Repository-specific product rule |
| 33 | GOV-003:159-165 | `tools/` joins the lint gate | HISTORY | One-time scope assignment; see U13 |
| 34 | GOV-003:167-172 | Contract tests and preflight agree about dates | HISTORY | One-time filing |
| 35 | GOV-003:176-180 | A phase drops a dependency | HISTORY | One-time |
| 36 | GOV-003:182-185 | Checkpoint is a skill; session-close owner-only | HISTORY | Owner-only half superseded by GOV-003:461-489; checkpoint half is C5 |
| 37 | GOV-003:187-190 | An agent never decides a session is over | HISTORY | Narrowed by GOV-003:482-489; residue is C6 |
| 38 | GOV-003:192-195 | One session record for both; checkpoint referenced from instruction files | STANDING | C7, C8 |
| 39 | GOV-003:197 | A phase depends on both | HISTORY | One-time |
| 40 | GOV-003:199-216 | History squashed; fallback withdrawn | HISTORY | One-time action |
| 41 | GOV-003:218-222 | Nothing kept "in history"; no tracked document cites a commit hash | STANDING | C9 (repository-specific; U3) |
| 42 | GOV-003:224-237 | Root plans folder retired | HISTORY | One-time; resulting fact in GOV-001:60 |
| 43 | GOV-003:239-249 | Demo track completes through its gate | HISTORY | Superseded by GOV-003:456-480 |
| 44 | GOV-003:251-259 | Demo track: what is bought and conceded | HISTORY | Superseded by GOV-003:482-489; checkpoint clause at 258 is C5 |
| 45 | GOV-003:261-272 | A phase inserted ahead of rehearsal | HISTORY | One-time |
| 46 | GOV-003:274-285 | Demo gate extends to the workbench track | HISTORY | Superseded by GOV-003:478-480 |
| 47 | GOV-003:287-293 | Owner-machine conditions for one phase | HISTORY | One-time, track-specific; see U9 |
| 48 | GOV-003:295 | Semantic provider and agentic refinement gates | HISTORY | Repository-specific |
| 49 | GOV-003:297 | Plans stay open until mapped phases complete or cancel | STANDING | C10 |
| 50 | GOV-003:299-309 | Workbench gate extended to two phases | HISTORY | Superseded by GOV-003:456-480 |
| 51 | GOV-003:311-321 | A deletion broke another phase's evidence | HISTORY | One-time resolution |
| 52 | GOV-003:322-326 | An evidence line retires with a deleted file | STANDING | C11 |
| 53 | GOV-003:330-342 | Every session works in a worktree | STANDING | C12 |
| 54 | GOV-003:344-363 | Why the earlier reasoning failed | HISTORY | Rationale |
| 55 | GOV-003:365-369 | Where the rule lives; instruction files owner-edited | STANDING | C13 |
| 56 | GOV-003:371-376 | Follow-up ideas | HISTORY | One-time |
| 57 | GOV-003:380-399 | Non-dispatch block carries no idempotency sentence | HISTORY | One-time amendment; embedded rule C14 |
| 58 | GOV-003:401-406 | Why the acceptance amendment was recorded | HISTORY | Rationale; see U7 |
| 59 | GOV-003:410-424 | Four programmes reframed | HISTORY | One-time, repository-specific |
| 60 | GOV-003:426-429 | Five-gate model pending | HISTORY | Repository-specific pending amendment (U8) |
| 61 | GOV-003:430-432 | session-close owner-invoked; `next_up` the owner's | STANDING (partial) | session-close half superseded by GOV-003:461-463; `next_up` half is C15 |
| 62 | GOV-003:436-454 | Queued-phase review session may edit unclaimed phases' lines | STANDING | C16 |
| 63 | GOV-003:458-465 | Coordinator completion; `next_up` reaffirmed | STANDING | C15, C17 |
| 64 | GOV-003:467-476 | Three completion conditions; completion commit after integration | STANDING | C17 |
| 65 | GOV-003:478-480 | Repository-wide and standing | STANDING | C17 |
| 66 | GOV-003:482-489 | What is bought; never complete on own judgement | STANDING | C6, C19 |
| 67 | GOV-003:491-500 | Batch approval covers the claim gate; questions first; stop conditions; blocker to an agent first | STANDING | C20-C23 |
| 68 | GOV-003:502-507 | The close command corrected | HISTORY | One-time edit |
| 69 | GOV-003:509-514 | Checkpoint does not contradict; only session-close completes | STANDING | C5 |
| 70 | GOV-003:516-518 | Why recorded | HISTORY | Rationale |
| 71 | GOV-003:520-556 | Generated ideas-and-backlog page kept | HISTORY | Repository-specific ruling; see U10 |
| 72 | GOV-003:560-571 | Lifecycle intro and a correction | HISTORY | Rationale and correction |
| 73 | GOV-003:573-589 | Three terminal states, each needing a pointer | STANDING | C24 |
| 74 | GOV-003:591-596 | `promoted` is non-terminal | STANDING | C25 |
| 75 | GOV-003:598-601 | One `delivered`, two paths into it | HISTORY | Repository-specific phase coordination |
| 76 | GOV-003:603-605 | Backfill by appending; a correction is a later event | STANDING | C26 |
| 77 | GOV-003:607-612 | Two ideas moved to resolved | HISTORY | One-time |
| 78 | GOV-003:614-619 | Backfill split into its own phase | HISTORY | One-time |
| 79 | GOV-003:621-624 | Work folded into another phase | HISTORY | One-time |
| 80 | GOV-003:626-630 | Propose, verify, ratify for the new states | STANDING | C27 |
| 81 | GOV-003:632-645 | Agent-written close announces itself and never blocks | STANDING | C28 |
| 82 | GOV-003:647-649 | Why recorded | HISTORY | Rationale |
| 83 | GOV-003:653-658 | Parallel sessions under a Session Manager (intro) | STANDING | C29 (conditional on GOV-017) |
| 84 | GOV-003:660-673 | Six departures from AGENTS.md | STANDING | C29, C30 (conditional; U5, U14) |
| 85 | GOV-003:675-676 | `max_active` value; system overlap bounds parallel work | HISTORY | Repository-specific value |
| 86 | GOV-003:678-680 | Why recorded | HISTORY | Rationale |
| 87 | GOV-003:684-686 | Batch opening pack (intro) | HISTORY | One-time |
| 88 | GOV-003:688-694 | Two phases reordered | HISTORY | One-time |
| 89 | GOV-003:696-702 | Authority process split into its own phase | HISTORY | One-time |
| 90 | GOV-003:704-710 | Acceptance narrowed; `proposed_by` field named | HISTORY | One-time; names the mechanism C28 needs |
| 91 | GOV-003:711-717 | Four review fixes | HISTORY | One-time |
| 92 | GOV-003:719-721 | A question left to a later phase | HISTORY | One-time |
| 93 | GOV-003:723-726 | Why recorded | HISTORY | Rationale |
| 94 | GOV-003:730-741 | Merge gate adds lint, type checks and the dirty-integration check | STANDING | C31, C32 |
| 95 | GOV-003:743-747 | "Neither departs from AGENTS.md"; why recorded | HISTORY | Rationale; contested (U4) |
| 96 | GOV-004:15-19 | Intro; snapshot; live command authoritative | HISTORY | Dated snapshot; the live-command rule is in GOV-001:26 |
| 97 | GOV-004:21-34 | Every open plan | HISTORY | Snapshot |
| 98 | GOV-004:36-44 | Source section audit | HISTORY | Repository-specific |
| 99 | GOV-004:46-64 | Audit findings and answers | HISTORY | Repository-specific mapping |
| 100 | GOV-004:66-70 | Release gates and scope boundary | HISTORY | Repository-specific; embedded rules C33, C34 |
| 101 | GOV-004:72-74 | Initial execution order; one active phase | HISTORY | Superseded by `max_active` (GOV-001:177, GOV-002:80) |
| 102 | GOV-004:76-86 | Capture validation results | HISTORY | Dated snapshot |

### Still-standing rules and where each was inlined

Every rule that amends the core protocol, the backlog protocol or the completion authority
appears in exactly one of the four documents written here. Rules for families D to F are listed
with the document `phase-plug-09` writes; the idea-system rules name the plugin file that already
carries them.

| Rule | Absolute rule | Source | Amends | Inlined in |
|---|---|---|---|---|
| C1 | A collision resolved by a real choice is recorded, with its reason, in the decision record in the same change. | GOV-003:62-66, 74 | AGENTS.md, GOV-002 | backlog-protocol.md §12 |
| C2 | A source-code conflict between phases declared disjoint always gets a decision-record entry. | GOV-003:74-76 | AGENTS.md | backlog-protocol.md §12 |
| C3a | A document code is free before merge and permanent after; whoever integrates second renumbers. | GOV-003:29-31, 70 | GOV-005 | document-codes.md §5 (backlog-protocol.md §12 points to it) |
| C3b | A collided idea id is yielded by whoever integrates second, re-appended through the writer under a new id; the log is never hand-edited. | GOV-003:71-72 | idea capture | Not in these four documents. P:skills/idea/SKILL.md carries the writer-only rule and P:scripts/ideas.py refuses a second `created` event for one id; the renumbering procedure is left to the idea documents (`phase-plug-09` or later) |
| C4 | Widening a phase's declarations is committed on the integration branch, and the check re-run, before the work. | GOV-003:139-140 | AGENTS.md | backlog-protocol.md §7 |
| C5 | Checkpoint records progress, is safe to repeat, and never completes a phase; only session-close does. | GOV-003:182-184, 258, 509-513 | AGENTS.md | backlog-protocol.md §9 |
| C6 | An agent never completes a phase on its own judgement that the work looks finished. | GOV-003:187-189, 488-489 | AGENTS.md | backlog-protocol.md §10 |
| C7 | Each session has one session record; checkpoint creates and updates it, session-close finalises it. | GOV-003:192-194 | GOV-002 | backlog-protocol.md §9 |
| C8 | The agent instruction files reference the checkpoint procedure. | GOV-003:194-195 | AGENTS.md | Not shipped: P:templates/AGENTS.md and P:templates/CLAUDE.md do not mention checkpoint |
| C9 | Nothing is preserved "in history"; no tracked document cites a commit hash. | GOV-003:218-222 | AGENTS.md | Not shipped: it follows from this repository's squashed history; a target repository's hashes resolve, and P:scripts/idea.py accepts a commit pointer |
| C10 | A plan stays open until every mapped phase is complete or cancelled with a reason. | GOV-003:297 | GOV-002 | backlog-protocol.md §5 |
| C11 | A deleted evidence file's line is removed with a decision-record entry in the same change. | GOV-003:322-325 | GOV-002 | backlog-protocol.md §10 |
| C12 | Every session works in its own worktree; only the claim and its catalog regeneration happen in the primary checkout. | GOV-003:330-342 | AGENTS.md, GOV-001, GOV-002 | protocol.md §11 |
| C13 | The instruction files change only with the owner's explicit approval; an agent that finds one wrong quotes, proposes and stops. | GOV-003:367-369 | AGENTS.md | protocol.md §3 |
| C14 | Every dispatched block of a prompt pack opens with the idempotency sentence; a block the coordinator performs is marked "not a dispatch". | GOV-003:384-398 | GOV-008 | prompt-packs.md (`phase-plug-09`) |
| C15 | Ranking `next_up` is the owner's; an agent only removes a phase in the change that completes it. | GOV-003:431-432, 464-465 | GOV-002 | backlog-protocol.md §4 |
| C16 | A queued-phase review session under an owner-approved pack may edit in-scope phases' lines, `updated` and the forced catalog regeneration only. | GOV-003:442-449 | AGENTS.md:265 | Not shipped: the plugin ships no queued-phase review pack, and P:skills/checkpoint/SKILL.md forbids touching other phases' lines. If `phase-plug-09` ships the pack, it belongs in plan-review.md |
| C17 | A phase is complete only when verification ran green, an independent adversarial review's findings are fixed or accepted, and the branch is integrated with the owner's approval; the completion edit follows integration. | GOV-003:467-480 | GOV-002, AGENTS.md:178-180 (stale; idea 000467) | backlog-protocol.md §10 |
| C18 | Integration needs the owner's explicit yes for every phase. | GOV-003:473-474, 485-486 | AGENTS.md | protocol.md §12 |
| C19 | The owner may run the close procedure afterwards as an audit of a completed phase. | GOV-003:483-485 | GOV-002 | Not shipped: P:skills/session-close/SKILL.md forbids re-running on a closed phase |
| C20 | An owner-approved batch naming its phases in build order is the claim approval for them; the numeric checks still run before each claim. | GOV-003:491-496 | session-start step 2, GOV-013 | coordinator.md (`phase-plug-09`) |
| C21 | Questions a per-phase claim gate would raise go to the owner as one batch before the first claim. | GOV-003:495-497 | GOV-013 | coordinator.md (`phase-plug-09`) |
| C22 | A coordinator stops mid-batch only on a genuinely wrong phase or an obstacle that survives resolution. | GOV-003:497-499 | GOV-013 | coordinator.md (`phase-plug-09`) |
| C23 | A blocker goes first to an agent; only an unresolved blocker reaches the owner, with findings attached. | GOV-003:499-500 | GOV-013 | coordinator.md (`phase-plug-09`) |
| C24 | An idea closes as `delivered`, `resolved` or `absorbed`, each with a pointer. | GOV-003:575-589 | idea schema | Already in P:docs/vocabulary.md (Statuses) and P:schemas/idea.schema.json |
| C25 | `promoted` is not terminal. | GOV-003:591-594 | idea schema | Already in P:docs/vocabulary.md (Statuses) |
| C26 | The idea log is append-only; a correction is a later event. | GOV-003:603-605, 24-27 | idea schema | Already in P:skills/idea/SKILL.md |
| C27 | An agent closes an idea into a terminal state only by proposing it with evidence; the owner ratifies in batch. | GOV-003:626-630 | idea protocol | Partial: the writer refuses an unresolvable pointer; no propose or ratify step exists. Left to the idea documents |
| C28 | An agent-written terminal state is marked as awaiting ratification and never blocks downstream work. | GOV-003:632-645 | idea protocol | Not shipped: no ratification marker exists in the plugin (nor yet in this repository) |
| C29 | Under a Session Manager: grants, relayed merge approval, assigned builds, batch-table turns. | GOV-003:660-669 | AGENTS.md (departures) | multi-session.md (`phase-plug-09`), as procedure; the plugin has no lock relay |
| C30 | No test run happens in the primary checkout. | GOV-003:670-673 | AGENTS.md | multi-session.md (`phase-plug-09`); conflicts with P:skills/backlog and P:skills/session-start, which run tests from the primary checkout (U5) |
| C31 | The post-rebase gate includes clean lint and type checks. | GOV-003:734-738 | GOV-017 | multi-session.md (`phase-plug-09`); the plugin is language-agnostic and its gate is "the check and the repository's tests" (P:skills/session-start/SKILL.md) |
| C32 | Before every fast-forward the primary checkout is confirmed clean; a peer's work is never stashed. | GOV-003:739-741 | AGENTS.md | backlog-protocol.md §11 (protocol.md §12 points to it); the dirty-integration hook script is not shipped |
| C33 | A deferred or blocked phase is released only by its resume condition. | GOV-004:68; GOV-003:297 | GOV-002 | backlog-protocol.md §3 |
| C34 | Approval authenticity, identifier permanence and evidence quality are human review responsibilities. | GOV-004:70 | GOV-001 | protocol.md §7 |

### Ledger points the triage could not settle

| Id | Point | Effect on this phase |
|---|---|---|
| U1 | AGENTS.md:178-180 and GOV-014:174-175 still say only the owner-invoked close completes a phase, against GOV-003:458-480 | None: the plugin follows C17 (`REQ-031` R15). Recorded as idea 000467 |
| U2 | Who accepts a review finding: GOV-003:472 does not say; P:skills/session-close says the owner | backlog-protocol.md §10 follows the plugin: accepted by the owner |
| U3 | No-commit-hash rule against commit-hash pointers for terminal ideas | C9 not shipped |
| U4 | Lint and type checks: repository-wide or multi-session only | Left to `phase-plug-09` (C31) |
| U5 | Tests in the primary checkout: multi-session only or any session | Left to `phase-plug-09` (C30) |
| U6 | GOV-002:127-129 cites a stale-claim recovery procedure that is not written | Not shipped (see not-shipped table). Recorded as idea 000468 |
| U7 | Acceptance amended after seeing the deliverable: rule or one case | Not carried |
| U8 | Five-gate model pending its phase | Not carried |
| U9 | Owner-machine conditions close only on the owner's results: general or one phase | Not carried |
| U10 | An idea carried by a phase is not also on the priority queue | Not carried; P:scripts/checks/ideas.py has a related rule |
| U11 | Historical records keep old names | Not carried |
| U12 | Stakeholders field migration | Repository-specific |
| U13 | `tools/` in the lint gate | Repository-specific |
| U14 | `max_active` value | Repository-specific; the plugin default is 1 |
| U15 | Checkpoint referenced from the templates | Same as C8 |
| U16 | "Squash" and "ratification" were proposed as standing rules; neither is one | C9, C28 |

## reporting.md (family B, from GOV-006)

| Rule | Rule as shipped | Source | Plugin location | Plugin mechanism |
|---|---|---|---|---|
| R1 | The working agreement governs the work; this document governs how it is reported. | GOV-006:17 | reporting.md, preamble | P:templates/AGENTS.md:1-5 |
| R2 | Lead with what a thing is; its code goes in parentheses as the lookup handle, never as the noun. | GOV-006:23 | reporting.md §Name things | conduct |
| R3 | Never make a bare phase id or document code the subject of a sentence; a code is a filename. | GOV-006:28-29 | reporting.md §Name things | conduct |
| R4 | First mention of a phase in a session carries a one-line gloss. | GOV-006:29-30 | reporting.md §Name things | conduct |
| R5 | Governed documents take the same form: title or role first, code in parentheses. | GOV-006:32-33 | reporting.md §Name things | conduct |
| R6 | Names are looked up: phase `title` in the backlog, document `title` in front matter, track prefixes in the tracks table where kept. | GOV-006:35-37 | reporting.md §Name things | P:schemas/backlog.schema.json (`title`); P:schemas/document.schema.json (`title`); P:docs/repository-layout.md:78-81. The source's "titles are in the catalog" is not carried: the plugin catalog has no title column (P:scripts/codes.py:300-308) |
| R7 | An idea is named id first, gloss in parentheses. | GOV-006:39-41 | reporting.md §Ideas are named id first | P:scripts/idea.py (six-digit ids) |
| R8 | The id-first form applies in prose, commit messages and finding annotations. | GOV-006:41-42 | reporting.md §Ideas are named id first | P:docs/vocabulary.md (`finding`) |
| R9 | Paste the real output when the number or message is the point. | GOV-006:46-47 | reporting.md §Show the output | conduct |
| R10 | Summarise a wall of passing checks. | GOV-006:47-48 | reporting.md §Show the output | conduct |
| R11 | A summary of a failure is not a result; the failure is. | GOV-006:48 | reporting.md §Show the output | conduct |
| R12 | A failing check is a result to record, not a step to retry, and is reported as it happened. | GOV-006:50-51 | reporting.md §Show the output | P:templates/AGENTS.md:65-66 |
| R13 | Ask when the answer changes what gets built, at the point the work reaches it. | GOV-006:55-56 | reporting.md §Do not block | P:templates/AGENTS.md:27-29 |
| R14 | Any other question is an assumption stated, the work continues, and it is listed at the end. | GOV-006:55-56 | reporting.md §Do not block | P:templates/AGENTS.md:28-29 |
| R15 | Ambiguity is flagged, not interrupted for. | GOV-006:59-60 | reporting.md §Do not block | conduct |
| R16 | A new ask outside the session's work is recorded at once through the idea writer. | GOV-006:64-66 | reporting.md §Capture new asks | P:skills/idea/SKILL.md |
| R17 | One idea per distinct ask. | GOV-006:66 | reporting.md §Capture new asks | P:skills/idea/SKILL.md |
| R18 | Each id is reported back from the writer's own output, never guessed. | GOV-006:66 | reporting.md §Capture new asks | P:scripts/idea.py (prints `created <id>`) |
| R19 | Never fold an ask into the active task or hold it in memory to the end. | GOV-006:66-67 | reporting.md §Capture new asks | conduct |
| R20 | The idea log is the capture path in every session and context. | GOV-006:68-69 | reporting.md §Capture new asks | P:skills/idea/SKILL.md |
| R21 | Record an ask as given; note an overlap in the body and leave it for triage. | GOV-006:69-70 (the record-as-given rule it cites, ADR-010:58-61) | reporting.md §Capture new asks | P:skills/idea/SKILL.md:40-42 |
| R22 | Asks for one future session are linked to a shared anchor idea and annotated there. | GOV-006:70-71 | reporting.md §Capture new asks | P:skills/idea/SKILL.md (`link`, `annotate`). The link type is left unspecified, as in the source |
| R23 | When the owner's correction is right, say so in one sentence and move on. | GOV-006:75 | reporting.md §Correction | P:templates/AGENTS.md:33 |
| R24 | Do not argue the point again or present a wrong call as partly right. | GOV-006:76 | reporting.md §Correction | conduct |
| R25 | A correction not stated as one leaves the owner unsure it was taken on board. | GOV-006:76-77 | reporting.md §Correction | conduct |

### GOV-006: not shipped or dropped

| Source | What | Why |
|---|---|---|
| GOV-006:17-18 | The document is imported into every session from `CLAUDE.md` | Not shipped: `P:templates/CLAUDE.md` carries no import of `docs/reporting.md`, and a target repository cannot portably import a file under the plugin root |
| GOV-006:18-19 | Keep this document short; add a rule only when its absence caused a misunderstanding | Dropped: a maintenance rule for this repository's copy, resting on the import cost above |
| GOV-006:25-26, 28, 32-33, 41 | Worked examples naming a phase, three document codes and an idea | Codes and ids (R02); the examples in the plugin use placeholders |
| GOV-006:35-37, 39, 66 | This repository's paths and `tools/append_idea.py` | Restated through the plugin's backlog, front matter and `idea` skill |
| GOV-006:50, 58-59 | "This extends AGENTS.md's rule"; "the principle ADR-007 applies" | Citations; the rules themselves are R12 and R15 |


## protocol.md (family A)

| Rule | Rule as extracted | Source | Plugin location | Plugin mechanism |
|---|---|---|---|---|
| A1 | What works is established by executable code plus observed verification. A plan's existence never establishes that its feature exists. | GOV-001:18, GOV-001:26, AGENTS.md:160 | protocol.md §1 | conduct |
| A2 | The schemas define the data shapes. The plugin's scripts validate against the plugin's own schemas; the copies in the repository are for reference only. | GOV-001:27 | protocol.md §1 | P:scripts/documents.py:117-122; P:docs/repository-layout.md:66-68 |
| A3 | The reason for an architectural choice is recorded in an accepted decision record (kind `adr`). | GOV-001:30, AGENTS.md:112 | protocol.md §1 | P:scripts/documents.py:61; P:templates/codes.yaml:18-23 |
| A4 | A plan states what might be built. Draft content is a proposal. | GOV-001:31 | protocol.md §1 | conduct; P:templates/plan.md |
| A5 | Who maintains a capability is given by the `owner` and `systems` of the systems registry. | GOV-001:32 | protocol.md §1 | P:schemas/systems.schema.json:16-28 |
| A6 | The owner's and the session's instructions, together with the working agreement, govern an agent. A plan never overrides them. | GOV-001:33 | protocol.md §1 | conduct; P:templates/AGENTS.md:3-5 |
| A7 | No service, scheduler or lock daemon runs. Versioned files plus the check are the whole mechanism. | GOV-001:159, GOV-001:194, GOV-002:178 | protocol.md §1 | P:scripts/check.py:21-45 |
| A8 | An owner key names an accountable role, not a person's approval. Git records authorship. An AI model is an author, never an owner. | GOV-001:35 | protocol.md §2 | P:schemas/systems.schema.json:16-28; P:templates/systems.yaml:2-4 |
| A9 | Every owner key a document or phase uses exists in the systems registry's owners map before it is used. | GOV-001:35, GOV-001:92 | protocol.md §2 | P:scripts/documents.py:260-261; P:scripts/backlog.py:190-191 |
| A10 | An agent id is a claim label, not an owner. The phase's `owner` stays accountable whichever agent executes it. | GOV-001:194-196 | protocol.md §2 | P:schemas/backlog.schema.json:113-117, 203-208 |
| A11 | The working agreement (`AGENTS.md`) governs how agents work. Framework orientation files (`CLAUDE.md`) say what the project is and where things live. Where the two disagree, the working agreement wins. | AGENTS.md:3-5, GOV-001:37 | protocol.md §3 | P:templates/AGENTS.md:3-5; P:templates/CLAUDE.md:9-12 |
| A12 | `CLAUDE.md` holds only pointers, the instructions an agent needs before anything else, and the few facts worth duplicating. Shared conventions live in the working agreement and are linked, not copied. **(plugin differs)** | GOV-001:37 | protocol.md §3 | P:templates/CLAUDE.md:5-7, 20-28 |
| C13 | The agent instruction files change only with the owner's explicit approval of that change. An agent that finds one wrong quotes the passage, proposes wording and stops. | AGENTS.md:9-22 | protocol.md §3 | P:templates/AGENTS.md:11-23; P:templates/CLAUDE.md:14-18 |
| A13 | Every governed document is one of nine kinds: plan, adr, architecture, requirement, prompt, session, walkthrough, operation, governance. | GOV-001:47-57 | protocol.md §4 | P:schemas/document.schema.json:41-56 |
| A14 | A document lives only under a location its series names in the code register, relative to the document root. | GOV-001:47-57, GOV-001:90 | protocol.md §4 | P:scripts/codes.py:164-168; P:templates/codes.yaml:5-59 |
| A15 | For any non-trivial change, a requirement document and a plan document are written before implementation code. Approving one plan does not exempt the next piece of work. | AGENTS.md:41-44 | protocol.md §4 | P:templates/AGENTS.md:35-39 |
| A16 | A plan carries these sections: context and scope, design, work and dependencies, acceptance and verification, out of scope, open questions. It adds requirement coverage when it depends on a requirement, and execution order when it names two or more phases. **(plugin differs)** | GOV-001:49 | protocol.md §4 | P:scripts/plan_check.py:36-47, 79-88; P:templates/plan.md:20-46; P:skills/plan-check/SKILL.md |
| A17 | A requirement states each observable requirement with its verification method, and what each requirement is not. | GOV-001:52, AGENTS.md:41-43 | protocol.md §4 | P:templates/requirement.md:20-32 |
| A18 | Every document body is nonempty. The body content of other kinds (a decision record's context, decision, alternatives, consequences and revisit trigger; an operation's trigger, command and recovery; and so on) is a reviewer's judgement. | GOV-001:50-57 | protocol.md §4 | P:scripts/documents.py:109-110; otherwise conduct |
| A19 | A decision record is written whenever a design choice is not obvious. | AGENTS.md:112 | protocol.md §4 | conduct |
| A20 | Every Markdown file under the document root is a governed document whose front matter satisfies the document schema, except the catalog and the files listed in `exempt_files`. Naming a file `README.md` does not exempt it. | GOV-001:64, GOV-001:155 | protocol.md §5 | P:scripts/documents.py:140-167; P:.claude-plugin/plugin.json:59-65 |
| A21 | Files outside the document root are not scanned. Durable scratch work is moved into a governed location before anything relies on it. | GOV-001:155 | protocol.md §5 | P:scripts/documents.py:146-153; conduct |
| A22 | Required fields are `schema_version, id, code, title, kind, status, owner, created, updated, systems, depends_on`. Optional fields are `parent, supersedes, review_after, completion_evidence`. Any other field fails. **(plugin differs: no `tags`)** | GOV-001:66-100, GOV-001:102 | protocol.md §5 | P:schemas/document.schema.json:5-18, 19-143 |
| A23 | `schema_version` is exactly `1`. | GOV-001:87 | protocol.md §5 | P:schemas/document.schema.json:20-23 |
| A24 | `id` is a `doc-` kebab id, unique across governed documents and independent of path. | GOV-001:88 | protocol.md §5 | P:schemas/document.schema.json:24-29; P:scripts/documents.py:321-323 |
| A25 | `code` comes from the kind's series, is unique and permanent, and prefixes the filename (see document-codes.md). | GOV-001:89 | protocol.md §5 | P:scripts/codes.py:198-241 |
| A26 | `status` is one the kind allows (section 6). | GOV-001:91 | protocol.md §5 | P:scripts/documents.py:57-67, 258-259 |
| A27 | `created` and `updated` are ISO dates with created ≤ updated ≤ today. Quoted and unquoted dates are both accepted. | GOV-001:93, GOV-001:102 | protocol.md §5 | P:schemas/document.schema.json:76-87; P:scripts/documents.py:74-77, 254-257 |
| A28 | `systems` holds unique, existing `sys-` ids and may be empty. | GOV-001:94 | protocol.md §5 | P:schemas/document.schema.json:88-98; P:scripts/documents.py:262-264 |
| A29 | `depends_on`, `supersedes` and `parent` name existing documents, never the document itself, and form no cycle. `depends_on` means a prerequisite, not a related topic. | GOV-001:95-97, GOV-001:60 | protocol.md §5 | P:scripts/documents.py:274-298 |
| A30 | `parent` is valid only between two plans. | GOV-001:96 | protocol.md §5 | P:scripts/documents.py:282-284 |
| A31 | Every `supersedes` target has status `superseded`, and every superseded document is named in some document's `supersedes`. | GOV-001:97 | protocol.md §5 | P:scripts/documents.py:285-291 |
| A32 | A complete document lists `completion_evidence`, and each entry is an existing repository-relative file. | GOV-001:98 | protocol.md §5 | P:scripts/documents.py:265-271 |
| A33 | `review_after` is an optional advisory date. | GOV-001:99 | protocol.md §5 | P:schemas/document.schema.json:127-132 (the overdue warning is not shipped) |
| A34 | These fail: duplicate YAML keys, a malformed or non-mapping header, delimiters not on their own lines, invalid dates, an empty body. | GOV-001:102 | protocol.md §5 | P:scripts/documents.py:80-93, 100-114 |
| A35 | Schema defaults are descriptive and are never written back into files. | GOV-001:102 | protocol.md §5 | conduct |
| A36 | The namespaces are distinct: `sys-` systems, `doc-` documents, `phase-` phases, `agent-` claim labels. | GOV-001:102 | protocol.md §5 | P:schemas/document.schema.json:28, 96; P:schemas/backlog.schema.json:76, 207 |
| A37 | A plan's statuses are draft, approved, active, complete, deprecated, superseded. | GOV-001:108-121 | protocol.md §6 | P:scripts/documents.py:60 |
| A38 | A decision record's statuses are draft, accepted, deprecated, superseded. | GOV-001:121 | protocol.md §6 | P:scripts/documents.py:61 |
| A39 | Every other kind's statuses are draft, active, deprecated, superseded. | GOV-001:121 | protocol.md §6 | P:scripts/documents.py:62-66 |
| A40 | A plan moves draft→approved when the owner accepts it and approved→active when implementation starts. It moves active→complete once acceptance and evidence are reviewed. It moves to deprecated from draft, approved or active when withdrawn, cancelled or abandoned, and to superseded from complete or deprecated once a replacement is linked. | GOV-001:108-119 | protocol.md §6 | conduct (the check validates the current state only: P:scripts/documents.py:258-259) |
| A41 | A draft is edited freely. An accepted decision is reversed by a new decision record whose `supersedes` names the old one, and the old record is kept. | GOV-001:121 | protocol.md §6 | P:scripts/documents.py:285-291; conduct |
| A42 | The owner approves a concrete diff. An `approved` or `accepted` status never manufactures approval. Completion means the acceptance criteria are met; a written plan or an empty evidence file does not count. | GOV-001:123, GOV-002:76 | protocol.md §6 | conduct |
| A43 | Before a document is accepted or activated: its facts are checked against the cited sources, proposed and current behaviour are separated, dependencies are resolved, and the check runs. | GOV-001:125 | protocol.md §6 | P:scripts/check.py; conduct |
| A44 | On completion, `completion_evidence` lists the implementation and verification files and the body summarises actual results. On cancellation the reason is kept. On replacement the old status and the new `supersedes` change in the same change. Several documents may each replace a stated portion of one. | GOV-001:125 | protocol.md §6 | P:scripts/documents.py:265-271, 285-291 |
| A45 | The check runs every installed feature's check and exits nonzero on any problem. It exits 0 before any hand-off. | GOV-001:18, AGENTS.md:47, AGENTS.md:157 | protocol.md §7 | P:scripts/check.py:5-8, 21-45 |
| A46 | Metadata shape, dates and unknown fields are enforced by the schemas. | GOV-001:144 | protocol.md §7 | P:schemas/document.schema.json; P:scripts/documents.py:125-130 |
| A47 | Ids, owners, and references to systems, documents and plans are enforced by the document scan. | GOV-001:145 | protocol.md §7 | P:scripts/documents.py:252-298 |
| A48 | Cycles in dependency, parent, supersession, system and phase graphs fail. | GOV-001:146 | protocol.md §7 | P:scripts/documents.py:170-189, 242-244, 292-298; P:scripts/backlog.py:249-256 |
| A49 | Overlapping or unclaimed concurrent active phases fail. | GOV-001:147 | protocol.md §7 | P:scripts/backlog.py:129-149 |
| A50 | Declared paths are repository-relative and never escape the repository. They never pass through `.git`, `.venv`, `node_modules` or a symlink. Symlinks under the document root are refused. Missing system and evidence paths fail. | GOV-001:149, GOV-001:157 | protocol.md §7 | P:scripts/checks/backlog.py:36-51; P:scripts/documents.py:153-164, 236-238, 267-271 |
| A51 | The check reads only the document root, its two registers, the backlog and git metadata, and loads schemas locally. A feature that was never set up has nothing to check. | GOV-001:157 | protocol.md §7 | P:scripts/documents.py:11-16, 117-122, 375-377; P:scripts/checks/backlog.py:87-88 |
| A52 | The backlog is checked only when the document tree is clean. | — (plugin) | protocol.md §7 | P:scripts/checks/backlog.py:102-104 |
| A53 | The owner's diff review decides what no mechanism can see: work outside a phase's declared systems or deliverables, and the accuracy of prose. | GOV-001:148, GOV-001:152, GOV-002:90 | protocol.md §7 | conduct |
| C34 | Approval authenticity, identifier permanence and evidence quality are human review responsibilities, not automated guarantees. | GOV-001:127, GOV-001:152, GOV-002:76, GOV-002:174 | protocol.md §7 | conduct (the checks cover current-state consistency only) |
| A54 | The systems registry holds the owners map plus one entry per independently changeable capability: `id, name, domain, status, owner, paths, depends_on, description`. It is not a portfolio or a per-file list. | GOV-001:131 | protocol.md §8 | P:schemas/systems.schema.json:16-114; P:templates/systems.yaml |
| A55 | `domain` groups systems and adds no second hierarchy. | GOV-001:131 | protocol.md §8 | P:schemas/systems.schema.json:57-68 |
| A56 | Maturity is implemented, scaffold, planned or retired, independent of document status. Implemented and scaffold systems list paths, and every listed path exists. | GOV-001:138 | protocol.md §8 | P:schemas/systems.schema.json:69-79; P:scripts/documents.py:234-238 |
| A57 | A system's `depends_on` names existing systems and is acyclic. It records current dependencies for implemented systems and intended ones for planned systems. A plan path is not implementation evidence. | GOV-001:138 | protocol.md §8 | P:scripts/documents.py:239-244; conduct |
| A58 | The registry changes only when a capability's responsibility, maturity, paths, owner or dependencies change. Maturity is reassessed when a plan completes. | GOV-001:159, AGENTS.md:159 | protocol.md §8 | conduct |
| A59 | A generated file is never edited by hand: its source is changed and it is regenerated. It is committed only when a check regenerates it and fails on any difference. | GOV-001:138, AGENTS.md:133 | protocol.md §9 | P:templates/AGENTS.md:51-55; P:templates/CLAUDE.md:27-28 |
| A60 | The catalog (`catalog.md` at the document root) lists every governed document's code, kind, status, owner and path. It lists every plan with its queued, active and complete phase counts and agents when a backlog exists, every held code with its state and reason, and a count per kind. | GOV-005:177 | protocol.md §9 | P:scripts/codes.py:279-353 |
| A61 | The catalog is regenerated and committed after any change to a governed document, the code register or the backlog. The check renders it in memory and fails when the committed file differs. **(plugin differs)** | GOV-005:177-183, AGENTS.md:155-156 | protocol.md §9 | P:scripts/documents.py:369-392; P:skills/catalog/SKILL.md:8-9 |
| A62 | The catalog command writes only when the document tree is clean, and prints the file it wrote and its document count. **(plugin differs)** | GOV-005:185-186 | protocol.md §9 | P:scripts/documents.py:408-426 |
| A63 | A conflict in a generated file is resolved by regenerating the file. | — (plugin) | protocol.md §9 | P:skills/session-start/SKILL.md:191 |
| A64 | The data root (`data_root`) holds the repository's data. Anything generated from it is regenerated, never edited. | GOV-001:28, GOV-001:39-41, AGENTS.md:133 | protocol.md §10 | P:templates/AGENTS.md:53-55; P:templates/CLAUDE.md:27-28 (a template placeholder only; no script reads a data root) |
| A65 | The confidential directory (`confidential_dir`) is never tracked. It is read or written only when the owner directs. | AGENTS.md:65-66, AGENTS.md:111 | protocol.md §10 | P:templates/AGENTS.md:43-44; P:templates/CLAUDE.md:25-26 |
| A66 | A confidential identifier is never written into a tracked file: not in code, a document, a commit message, or a record that describes the identifiers. | AGENTS.md:60-61 | protocol.md §10 | P:templates/AGENTS.md:45-46 (conduct; no scanner ships) |
| A67 | Structure is tracked and confidential content is not. The test for an unclear file is whether it would still be correct if a different person adopted the system. | GOV-001:41 | protocol.md §10 | conduct |
| A68 | A fresh clone, with nothing from the confidential directory, passes the check and the tests. | GOV-001:41 | protocol.md §10 | conduct |
| A69 | Pushing your own branch needs no approval. Backing up your own work is not publishing. | AGENTS.md:55-56, AGENTS.md:191-193 | protocol.md §10 | P:templates/AGENTS.md:47; P:skills/session-start/SKILL.md:149 |
| A70 | Pushed history is not rewritten. If it seems to need rewriting, the agent says so and stops. | AGENTS.md:70-71 | protocol.md §10 | conduct |
| C12 | Every session works in its own worktree on its own branch, whatever the work touches, and the primary checkout's branch is never switched. The only work in the primary checkout is the claim commit plus the catalog regeneration it forces, committed together. | AGENTS.md:220-236, GOV-001:183-190, GOV-002:168 | protocol.md §11 | P:templates/AGENTS.md:57-60; P:templates/CLAUDE.md:23-24; P:skills/session-start/SKILL.md:49-58, 203 |
| A71 | The branch is `agent/<phase-id>` and the worktree is `<worktree directory>/<phase-id>`. The worktree directory sits outside the repository, so no scan or test walks a second copy. | AGENTS.md:249-251, GOV-001:184-185 | protocol.md §11 | P:skills/session-start/SKILL.md:123-128; P:.claude-plugin/plugin.json:46-51; P:docs/repository-layout.md:37, 71-72 |
| A72 | Ignored directories (virtual environments, databases, `node_modules`) belong to one worktree. Each worktree creates its own and never links a peer's. | AGENTS.md:252-255 | protocol.md §11 | P:skills/session-start/SKILL.md:133-135 |
| A73 | Ignored content never travels through a merge, and removing a worktree destroys it. It is copied out by hand first. | AGENTS.md:256-258 | protocol.md §11 | P:skills/session-start/SKILL.md:137-138, 182 |
| A74 | A server started from a worktree uses a free port chosen explicitly. | AGENTS.md:259-260 | protocol.md §11 | P:skills/session-start/SKILL.md:134-135 |
| A75 | Diffs are narrow, one concern per commit, on the session's own branch only. | AGENTS.md:131, AGENTS.md:264 | protocol.md §11 | P:templates/AGENTS.md:64; P:skills/session-start/SKILL.md:146 |
| A76 | A session rebases onto the integration branch whenever a peer integrates, and never merges the integration branch in. | AGENTS.md:266-267 | protocol.md §11 | P:skills/session-start/SKILL.md:147-148 |
| C18 | Integration onto the integration branch needs the owner's explicit yes for every phase. A green branch is ready to integrate, not cleared to. | AGENTS.md:57-58, AGENTS.md:293-296 | protocol.md §12 | P:templates/AGENTS.md:48-49; P:templates/CLAUDE.md:22; P:skills/session-start/SKILL.md:165-167, 202 |
| A77 | A branch qualifies for integration only when the check and the tests pass after rebasing onto the current integration branch. A red rebase is never integrated. | GOV-001:191-192, GOV-002:170, AGENTS.md:287-290 | protocol.md §12 | P:skills/session-start/SKILL.md:159-161 |
| A78 | Integration is a fast-forward made from the primary checkout. A non-fast-forward means rebase again and re-run the check, never a merge commit. | AGENTS.md:297, AGENTS.md:301-308 | protocol.md §12 | P:skills/session-start/SKILL.md:176-184 |
| A79 | After integration the worktree is removed and the branch deleted. | AGENTS.md:185, AGENTS.md:303-304 | protocol.md §12 | P:skills/session-start/SKILL.md:178-179 |
| A80 | Without the owner's yes the branch stays unmerged and is reported ready for review, with `git diff <integration branch>..agent/<phase-id>`. | AGENTS.md:295-296 | protocol.md §12 | P:skills/session-start/SKILL.md:166-167 |
| A81 | A branch that fails after rebase is fixed on that branch against the current integration branch. A peer's commit is never reverted. | AGENTS.md:324-325 | protocol.md §12 | conduct |

## backlog-protocol.md (family A)

| Rule | Rule as extracted | Source | Plugin location | Plugin mechanism |
|---|---|---|---|---|
| B1 | The backlog is the execution record of every open plan. Each phase is one independently verifiable outcome that fits one focused session, including its checks and hand-off. Parent plans keep the design. | GOV-002:17, GOV-001:163-165, AGENTS.md:169 | backlog-protocol.md §1 | P:schemas/backlog.schema.json:1-5, 137-141; P:docs/repository-layout.md:47-49 |
| B2 | The backlog on the integration branch is the lock table, and the check is the lock check. | GOV-001:181-182, GOV-002:168, AGENTS.md:195-196 | backlog-protocol.md §1 | P:skills/session-start/SKILL.md:54; P:docs/repository-layout.md:47-49 |
| B3 | The backlog YAML is the only editable state. Reports are generated, never copied into a second board. | GOV-002:28 | backlog-protocol.md §1 | P:scripts/backlog.py:290 |
| B4 | `ready` prints `next_up` first, then priority and id. For each phase it shows readiness, prerequisites and a Conflicts column naming the active phases it would collide with; for each active claim it shows a stale-claim signal. `--all` adds every phase's details and the source-plan coverage table. It changes nothing. | GOV-002:21-28 | backlog-protocol.md §1 | P:scripts/checks/backlog.py:162-189; P:scripts/backlog.py:284-383; P:skills/backlog/SKILL.md:8-10, 41-43, 86 |
| B5 | The backlog's top-level fields are `schema_version` (1), `updated` (never in the future), optional `decision_record` (a governance or adr document), `max_active` (1–4, default 1), `next_up` and `items`. | GOV-002:39, GOV-002:80 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:6-47; P:scripts/backlog.py:174-175, 182-186 |
| B6 | A phase id is `phase-<track>-NN`. It is permanent and never renumbered. A new phase takes the next unused number in its track, chosen by hand. | GOV-002:34, GOV-002:148-150 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:72-77; P:docs/repository-layout.md:76-81 |
| B7 | `title` is one observable outcome. | GOV-002:35 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:78-82 |
| B8 | `plan` names one primary plan document. `sources` names every other governed source the phase covers. | GOV-002:36 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:83-100; P:scripts/backlog.py:195-206 |
| B9 | `systems` lists one or more existing `sys-` ids. `owner` is an existing owner key. | GOV-002:37 | backlog-protocol.md §2 | P:scripts/backlog.py:190-194; P:schemas/backlog.schema.json:101-117 |
| B10 | `priority` is 1 foundation, 2 capability, 3 composition or 4 conditional extension. | GOV-002:38 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:131-136 |
| B11 | `session_budget` is exactly 1. It is a review promise about scope, not a timing guarantee. | GOV-002:40 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:137-141 |
| B12 | Every `depends_on` prerequisite is complete before the phase is active or complete. There is no self-dependency and no cycle. | GOV-002:41, GOV-002:74 | backlog-protocol.md §2 | P:scripts/backlog.py:207-212, 249-256 |
| B13 | `scope` has at least one step. `acceptance` has at least two observable conditions. `verification` has at least one command or specific check, run and recorded during execution. | GOV-002:42-44 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:154-186 |
| B14 | `deliverables` lists expected repository paths that need not exist yet, refined during execution. | GOV-002:45 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:187-197; P:scripts/checks/backlog.py:39-51 |
| B15 | `next_action` is the first useful action or an exact resume instruction. | GOV-002:46 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:198-202 |
| B16 | `agent` is `agent-<name>` and names the branch `agent/<phase-id>`. It is required on every active phase while `max_active` exceeds 1. | GOV-002:48 | backlog-protocol.md §2 | P:schemas/backlog.schema.json:203-208; P:scripts/backlog.py:136-139 |
| B17 | `blocked_reason` is required on blocked, deferred and cancelled phases. `resume_when` is required on blocked and deferred phases. | GOV-002:49, GOV-002:178 | backlog-protocol.md §2 | P:scripts/backlog.py:217-222 |
| B18 | `session`, `completion_evidence` and `result` are required together for complete, and may be recorded while a phase is active or blocked. A released phase (queued, deferred, cancelled) carries none of them. | GOV-002:50, GOV-002:54 | backlog-protocol.md §2 | P:scripts/backlog.py:227-239 |
| B19 | `session` names a session or walkthrough document. | GOV-002:76 | backlog-protocol.md §2 | P:scripts/backlog.py:223-226 |
| B20 | Session-record and decision-record filenames in initial deliverables are illustrative. Source ids stay stable when a file moves. | GOV-002:52 | backlog-protocol.md §2 | conduct |
| B21 | A phase is queued, active, blocked, deferred, complete or cancelled. Readiness is derived: a queued phase is ready when every dependency is complete, and waiting otherwise. | GOV-002:47, GOV-002:58-74 | backlog-protocol.md §3 | P:schemas/backlog.schema.json:118-130; P:scripts/backlog.py:276-281 |
| B22 | Transitions: queued→active once prerequisites are complete; active→complete; queued or active→blocked on an external impediment; blocked→queued once the resume condition is met; queued→deferred; deferred→queued; active→queued with an exact hand-off; queued, blocked or deferred→cancelled when scope is withdrawn. | GOV-002:58-72 | backlog-protocol.md §3 | conduct, except the prerequisite rule (P:scripts/backlog.py:207-212) and leaving complete (B67) |
| B23 | Blocked and deferred are explicit decisions, not names for an unmet prerequisite. | GOV-002:74 | backlog-protocol.md §3 | conduct |
| B24 | A cancelled dependency never satisfies its dependents. The dependency graph is revised deliberately. | GOV-002:74 | backlog-protocol.md §3 | P:scripts/backlog.py:210-212, 279 |
| C33 | A deferred or blocked phase is released only by its recorded resume condition, never by elapsed time. | GOV-002:49, GOV-002:65, GOV-002:67, AGENTS.md:177 | backlog-protocol.md §3 | P:schemas/backlog.schema.json:214-218; P:scripts/backlog.py:220-222; P:skills/backlog/SKILL.md:53-55 |
| B25 | `agent` stays on active, blocked and complete phases, and is dropped on queued, deferred and cancelled ones. | GOV-002:88 | backlog-protocol.md §3 | P:scripts/backlog.py:21-23, 215-216 |
| B26 | The queue order is the `next_up` entries as listed, then priority, then id. Position in the file means nothing. | GOV-002:148-150 | backlog-protocol.md §4 | P:scripts/backlog.py:263-273 |
| B27 | Every `next_up` entry names an existing phase that is neither complete nor cancelled. | GOV-002:156-157 | backlog-protocol.md §4 | P:scripts/backlog.py:176-181 |
| C15 | Ranking the `next_up` front of the queue belongs to the owner. An agent may propose an order but never writes one. The only agent edit is removing a phase in the change that completes it. | GOV-002:152-158, AGENTS.md:175 | backlog-protocol.md §4 | P:skills/backlog/SKILL.md:49-51; P:skills/checkpoint/SKILL.md:122; P:skills/session-close/SKILL.md:107; P:scripts/backlog.py:176-181 |
| B28 | `next_up` stays short: it says what happens now, and priority says when. | GOV-002:153-154 | backlog-protocol.md §4 | conduct |
| B29 | The phase to take is the first ready phase in the rendered order, which is what "the next task" means. | GOV-002:160-161, AGENTS.md:36-40, AGENTS.md:172-174 | backlog-protocol.md §4 | P:skills/backlog/SKILL.md:45-51 |
| B30 | The phase's `scope`, `acceptance`, `verification` and `next_action` bound the work. | GOV-002:166, AGENTS.md:39-40 | backlog-protocol.md §4 | P:skills/backlog/SKILL.md:59-65 |
| B31 | Before implementing, the agent reads the open plans and the decision record, and finds existing phases before creating new ones. | GOV-002:134 | backlog-protocol.md §5 | conduct |
| B32 | Each plan is split into one-outcome phases with acceptance and dependencies. A shared prerequisite is one phase referenced by every source it serves. | GOV-002:135 | backlog-protocol.md §5 | conduct |
| B33 | Every draft, approved or active plan, overview or child, is covered by at least one non-cancelled phase through `plan` or `sources`. The phases are added in the same change as a new plan. | GOV-002:136, GOV-002:178, GOV-001:166, AGENTS.md:43, AGENTS.md:168 | backlog-protocol.md §5 | P:scripts/backlog.py:21, 198-203, 257-259 |
| B34 | Coverage is structural. A reference cannot prove every requirement was captured, so plan bodies are re-inspected whenever scope changes. | GOV-002:142 | backlog-protocol.md §5 | conduct |
| B35 | The check runs and coverage (`ready --all`) is inspected before product work. | GOV-002:138 | backlog-protocol.md §5 | P:scripts/backlog.py:349-358 |
| B36 | A plan's implementation start moves it from approved to active. | GOV-002:166 | backlog-protocol.md §5 | conduct |
| C10 | A plan stays open until every phase mapped to it is complete, or cancelled with a reason. Deferred phases keep it open. | GOV-002:174 | backlog-protocol.md §5 | P:scripts/backlog.py:204-206 |
| B37 | At plan closure, its acceptance criteria are reviewed, its completion evidence is recorded and its metadata is updated. | GOV-002:174 | backlog-protocol.md §5 | P:scripts/documents.py:265-271 |
| B38 | `max_active` bounds the number of simultaneously active phases. Raising it authorizes nothing by itself. | GOV-002:80, GOV-001:177 | backlog-protocol.md §6 | P:scripts/backlog.py:132-135; P:schemas/backlog.schema.json:29-35 |
| B39 | An agent holds at most one active phase and reuses the agent id it chose once. | GOV-001:179, GOV-002:88, AGENTS.md:198-199 | backlog-protocol.md §6 | P:scripts/backlog.py:136-141; P:skills/session-start/SKILL.md:98-99 |
| B40 | Orientation runs the check and the tests first. If either fails, nothing is claimed. | — (plugin) | backlog-protocol.md §6 | P:skills/backlog/SKILL.md:16-29; P:skills/session-start/SKILL.md:66-67 |
| B41 | The owner is asked before a claim is committed. An unanswered question is not a yes. | — (plugin) | backlog-protocol.md §6 | P:skills/session-start/SKILL.md:69-80 |
| B42 | A claim is one commit on the integration branch in the primary checkout. It holds this phase's `status: active` and `agent`, the backlog `updated` set to today, and the regenerated catalog, and nothing else. It is pushed before work begins. | GOV-001:181-183, GOV-002:168, AGENTS.md:204-205, AGENTS.md:228-232 | backlog-protocol.md §6 | P:skills/session-start/SKILL.md:87-116 |
| B43 | The primary checkout is brought up to date by a fast-forward pull and never switched. If it is not on the integration branch, the session stops and reports it. | AGENTS.md:200 (conflict) | backlog-protocol.md §6 | P:skills/session-start/SKILL.md:89-95 |
| B44 | The check runs before the claim is committed. It rejects overlap with an active peer's systems, deliverables or dependency chain, and a full `max_active`. A rejection means choosing different work, never waiting. | GOV-002:168, AGENTS.md:201-203, AGENTS.md:206-207 | backlog-protocol.md §6 | P:skills/session-start/SKILL.md:110-112; P:scripts/backlog.py:129-149 |
| B45 | If the claim push is rejected as non-fast-forward: `git pull --rebase`, re-run the check, and confirm the claim is still safe. | AGENTS.md:208-210 | backlog-protocol.md §6 | P:skills/session-start/SKILL.md:115-116 |
| B46 | A peer's claim is never edited. A session touches only its own phase's backlog lines and `updated`. | AGENTS.md:203, AGENTS.md:265 | backlog-protocol.md §6 | P:skills/session-start/SKILL.md:145; P:skills/checkpoint/SKILL.md:20-21 |
| B47 | Owner-directed work with no phase claims nothing and uses `agent/<slug>`. Its first report says it is unclaimed. A phase is never invented to have something to claim. | AGENTS.md:212-216 | backlog-protocol.md §6 | P:skills/session-start/SKILL.md:82-85; P:skills/checkpoint/SKILL.md:75-91 |
| B48 | No two active phases share a system. No declared deliverable path of one equals or contains one of the other's. Neither is a transitive prerequisite of the other. | GOV-001:177-179, GOV-002:80-86 | backlog-protocol.md §7 | P:scripts/backlog.py:92-149 |
| B49 | Work stays inside the declared systems and deliverables. The check cannot see edits outside them, so diff review confirms it. | GOV-002:90, AGENTS.md:261 | backlog-protocol.md §7 | conduct |
| C4 | Widening a phase's declared systems or deliverables is committed on the integration branch, and the check re-run, before the work that needs it, so peers see the wider lock first. | AGENTS.md:261-263 | backlog-protocol.md §7 | P:skills/session-start/SKILL.md:142-144 |
| B50 | Work on a system that `depends_on` a peer's active system treats the peer's contract as frozen at the branch point, and builds against the merged integration branch, never a peer's unmerged branch. | GOV-002:90, AGENTS.md:330-332 | backlog-protocol.md §7 | conduct |
| B51 | Each active claim shows one of `no`, `STALE: <signal>`, `no evidence: no agent/<phase-id> branch found`, or `no signal evaluated`. | GOV-002:94-104 | backlog-protocol.md §8 | P:scripts/backlog.py:68-89, 317-323 |
| B52 | There are two signals: no commit on `agent/<phase-id>` for more than 2 days, and no worktree checked out on that branch. | GOV-002:106-114 | backlog-protocol.md §8 | P:scripts/backlog.py:27, 30-65; P:scripts/checks/backlog.py:129-159 |
| B53 | A claim whose branch has no commits, including one whose branch does not follow `agent/<phase-id>`, reports no evidence and is never marked stale. | GOV-002:103, GOV-002:121-123 | backlog-protocol.md §8 | P:scripts/backlog.py:56-59, 86-87 |
| B54 | The signal is evidence for the owner, never proof. A long read or an external wait looks the same as abandonment, and a missing worktree read on another machine is no evidence. | GOV-002:116-123 | backlog-protocol.md §8 | P:scripts/backlog.py:42-54 |
| B55 | No script releases a claim. The report is an input to the owner's decision. | GOV-002:125-127 | backlog-protocol.md §8 | P:scripts/backlog.py:5-8, 53-54 |
| C7 | Each session has one session record. Checkpoint creates and updates it; session-close finalises it. | AGENTS.md:275, GOV-002:166 | backlog-protocol.md §9 | P:skills/checkpoint/SKILL.md:38-40, 98-100; P:skills/session-close/SKILL.md:8-9 |
| C5 | The checkpoint procedure records progress, is safe to repeat, and never marks a phase complete; only session-close does. | AGENTS.md:178-179 | backlog-protocol.md §9 | P:skills/checkpoint/SKILL.md:8-11, 15-17, 60-62; P:skills/session-start/SKILL.md:150 |
| B56 | The session record is `kind: session` with status `active`. Its code comes from the session series, with a date equal to `created`, and the file is named `<code>-<topic>.md`. Its sections are Phase, Verification, Acceptance, Backlog and Unresolved, and each checkpoint regenerates them from observed state. | AGENTS.md:275-278 | backlog-protocol.md §9 | P:skills/checkpoint/SKILL.md:36-73; P:scripts/codes.py:236-239 |
| B57 | Verification records the literal command and its literal output. A failure is never paraphrased into a pass. | AGENTS.md:273-274, GOV-002:44 | backlog-protocol.md §9 | P:skills/checkpoint/SKILL.md:66-68, 110-113 |
| B58 | Acceptance is judged one condition at a time from recorded evidence, as Met or Not met. | AGENTS.md:282 | backlog-protocol.md §9 | P:skills/checkpoint/SKILL.md:69-70, 114-115 |
| B59 | Checkpoint never runs worktree, rebase or remote commands, and never touches another phase's lines. | — (plugin) | backlog-protocol.md §9 | P:skills/checkpoint/SKILL.md:18-21 |
| B60 | Once a session is closed, its record is only added to, never rewritten. | GOV-001:127 | backlog-protocol.md §9 | P:skills/session-close/SKILL.md:50-51; conduct |
| C6 | An agent never completes a phase on its own judgement that the work looks finished. | AGENTS.md:180 | backlog-protocol.md §10 | P:skills/session-close/SKILL.md:13-14 |
| C17 | A phase may be marked complete only when all three conditions hold. The owner may do it, or a coordinator running session-close. (1) Every verification command ran green and its real output is in the session record. (2) An independent adversarial review of the diff against acceptance ran, and every finding is fixed or explicitly accepted by the owner. (3) The branch is integrated with the owner's approval. The completion edit is one small commit on the integration branch right after integration, together with the regenerated catalog. | AGENTS.md:176, AGENTS.md:271, AGENTS.md:284-286 (all superseded; see 4.1) | backlog-protocol.md §10 | P:skills/session-close/SKILL.md:11-28, 96-107, 129-130 |
| B61 | The review runs in a fresh agent that does not share the session's context, never a fork. It receives the phase's scope, acceptance and verification, the diff range and the record. Its findings are recorded verbatim, each with its disposition. | — (plugin; C17(2)) | backlog-protocol.md §10 | P:skills/session-close/SKILL.md:56-86 |
| B62 | Completion writes `session`, `completion_evidence` (existing files) and `result` (the actual verification and review outcome), keeps `agent`, and removes the phase from `next_up` in the same change. | AGENTS.md:175, AGENTS.md:284-286, GOV-002:158 | backlog-protocol.md §10 | P:skills/session-close/SKILL.md:104-107; P:scripts/backlog.py:227-231 |
| B63 | While any condition is unmet, the phase stays active, or queued if handed off, with `next_action` naming what remains. | AGENTS.md:282-283, GOV-002:170 | backlog-protocol.md §10 | P:skills/session-close/SKILL.md:25-28, 111-112 |
| B64 | An unclaimed session completes nothing. | — (plugin) | backlog-protocol.md §10 | P:skills/session-close/SKILL.md:109 |
| B65 | Close adds Review, Decisions, Corrections and Left undone to the record. | — (plugin) | backlog-protocol.md §10 | P:skills/session-close/SKILL.md:82-94 |
| C11 | Completion evidence lists files that existed when the phase closed. When a later phase's sanctioned scope deletes one, its evidence line is removed in the same change as a decision-record entry, never silently. | GOV-002:50, AGENTS.md:284 | backlog-protocol.md §10 | P:scripts/backlog.py:243-245 (a missing file fails); the decision-record entry is conduct (see 4.19) |
| B66 | Hand-off order: run verification, write the record, rebase and re-run the check and tests, confirm the primary checkout is clean, ask the owner. | AGENTS.md:271-296 | backlog-protocol.md §11 | P:skills/session-start/SKILL.md:152-170 |
| C32 | Before every fast-forward onto the integration branch the primary checkout is confirmed clean. A peer's uncommitted work is never stashed or forced around. | AGENTS.md:291-292 | backlog-protocol.md §11 | P:skills/session-start/SKILL.md:162-164 |
| B67 | An interrupted phase returns to queued with an exact `next_action`, clearing `agent`, `session`, `completion_evidence` and `result`, or goes to blocked with a reason. Its worktree is removed so no directory outlives the claim, and completion is never claimed. | GOV-002:170, AGENTS.md:282-283 | backlog-protocol.md §11 | P:skills/checkpoint/SKILL.md:116-121; worktree removal is conduct |
| B68 | A backlog conflict keeps both sides: the peer's phases verbatim, your own phase's edits, and `updated` set to today. It is never resolved with `--ours` or `--theirs`. | GOV-002:172, AGENTS.md:312-314 | backlog-protocol.md §12 | P:skills/session-start/SKILL.md:188-190 |
| C2 | A source-code conflict between phases declared disjoint always gets a decision-record entry, because it shows the declarations the concurrency check relies on are wrong. The declarations are fixed before either phase completes. | GOV-002:172, AGENTS.md:320-323 | backlog-protocol.md §12 | P:skills/session-start/SKILL.md:194-195; the entry is conduct |
| C1 | When resolving a collision needs a real choice (which phase yields, whether a boundary moves, whether a phase splits or widens its declarations, which implementation is kept), the decision and its reason go into the decision record in the same change. A commit message is not a record. A mechanical keep-both merge needs no entry. | GOV-002:172, AGENTS.md:326-329 | backlog-protocol.md §12 | P:skills/session-start/SKILL.md:196-197; P:schemas/backlog.schema.json:23-28 (optional; see 4.18) |
| B69 | A duplicate document code is resolved by renumbering (see C3a in document-codes.md). | AGENTS.md:315-317 | backlog-protocol.md §12 | cross-reference |
| B70 | IDs and completed evidence are kept, never deleted. | GOV-002:178 | backlog-protocol.md §13 | P:scripts/regression.py:44-46, 90-109 |
| B71 | A phase that leaves complete, or stays complete but loses `session`, `completion_evidence` or `result`, is an error against HEAD unless the same change adds a decision-record entry naming it. Against the integration branch the same finding is a warning. | — (plugin; see 4.20) | backlog-protocol.md §13 | P:scripts/regression.py:1-33, 49-51, 141-156, 195-210; P:scripts/checks/backlog.py:116-119 |
| B72 | Without a `decision_record` the regression check does not run, and the check says so. | — (plugin) | backlog-protocol.md §13 | P:scripts/checks/backlog.py:108-112 |
| B73 | A phase that exceeds one session is split into new ids, keeping its rationale, and dependents are rewired before work continues. A phase is never left labelled as one session when it is not. | GOV-002:170, AGENTS.md:177 | backlog-protocol.md §14 | conduct |
| B74 | A phase is cancelled only with a reason. A cancelled phase does not count toward plan coverage. | GOV-002:178 | backlog-protocol.md §14 | P:scripts/backlog.py:202-203, 217-219 |
| B75 | The backlog `updated` is kept current on substantive edits and is never a future date. | GOV-002:178, AGENTS.md:205 | backlog-protocol.md §14 | P:schemas/backlog.schema.json:17-22; P:scripts/backlog.py:174-175 |

## document-codes.md (family A)

| Rule | Rule as extracted | Source | Plugin location | Plugin mechanism |
|---|---|---|---|---|
| D1 | Every governed document carries a permanent code from its kind's series. The code prefixes the filename as `<code>-<slug>.md`. | GOV-005:17-18, GOV-005:49, GOV-001:89, AGENTS.md:151-153 | document-codes.md §1 | P:scripts/codes.py:187-188; P:schemas/document.schema.json:30-35 |
| D2 | The code register (`codes.yaml` at the document root) is the only source of truth for each series' prefix, kind, numbering and locations. | GOV-005:23-24 | document-codes.md §1 | P:schemas/codes.schema.json:23-27; P:templates/codes.yaml:1-4 |
| D3 | Default series: PLAN (`plans/`, counter, sub-codes), REQ (`requirements/`), ADR (`decisions/`), ARCH (`architecture/`), PROMPT (`prompts/`), OPS and GOV (`governance/`), all counters; SESS and WALK (`sessions/`), dated. **(plugin differs: paths)** | GOV-005:26-36 | document-codes.md §1 | P:templates/codes.yaml:5-59; P:docs/repository-layout.md:24-30 |
| D4 | The register has one series per kind, with no duplicate prefix or kind, and every kind covered. A dated series never allows sub-codes. A held code is never both reserved and retired, and is well-formed in a known series. | GOV-005:23 | document-codes.md §1 | P:scripts/codes.py:139-161 |
| D5 | A document fails if its kind has no series, its code belongs to another series, or its code uses the wrong numbering. | GOV-005:17 | document-codes.md §1 | P:scripts/codes.py:208-226 |
| D6 | A counter code reads `<SERIES>-NNN`, optionally with a sub-code `.NN`. A dated code reads `<SERIES>-YYYY-MM-DD-NN`, and its date equals the document's `created`. | GOV-005:38-39, AGENTS.md:277-278 | document-codes.md §1 | P:scripts/codes.py:35-38, 236-239 |
| D7 | A code is allocated with `next-code <kind> [--parent <plan id>]`, which prints one code. A code is never chosen by hand or from a directory listing, and the register is never edited to take one. | GOV-005:43-51, GOV-001:60, AGENTS.md:45-46, AGENTS.md:151-154 | document-codes.md §2 | P:skills/next-code/SKILL.md:8-12, 17-25; P:scripts/codes.py:383-411 |
| D8 | The next counter code is the highest number among documents, register reservations, retirements and pre-merge reservations, plus one. | GOV-005:53 | document-codes.md §2 | P:scripts/codes.py:80-88, 120-122 |
| D9 | The next sub-code is the parent's highest sub-code plus one. The parent holds a top-level code in a series that allows sub-codes. | GOV-005:54 | document-codes.md §2 | P:scripts/codes.py:124-136 |
| D10 | A dated code takes today's date and the highest same-day sequence plus one, and takes no parent. Dated series contend only within one date. **(plugin differs)** | GOV-005:54-55, GOV-005:171 | document-codes.md §2 | P:scripts/codes.py:113-118 |
| D11 | Allocation takes the code: computing it and holding it are one operation from a peer's point of view. | GOV-005:94-96 | document-codes.md §2 | P:scripts/codes.py:356-380 |
| D12 | Allocation runs only on a clean document tree. On failure nothing is reserved. | — (plugin) | document-codes.md §2 | P:scripts/codes.py:397-402; P:skills/next-code/SKILL.md:27-28 |
| D13 | A plan set lives in a folder named `<parent code>-<slug>` under the plan location. The overview holds the parent code. Each child holds a sub-code and a `parent` naming the overview. | GOV-005:60-62, GOV-001:60 | document-codes.md §3 | P:scripts/codes.py:189-192, 244-266 |
| D14 | A sub-code and `parent` imply each other. A sub-code without a parent fails; a child with a top-level code fails; the sub-code's stem must match the parent's code. | GOV-005:62-63 | document-codes.md §3 | P:scripts/codes.py:244-266 |
| D15 | An area folder sits at most one level inside a plan folder, carries a reader-facing name, and holds only sub-coded children. The overview stays at the plan folder's root. | GOV-005:65-70 | document-codes.md §3 | P:scripts/codes.py:176-194 |
| D16 | A flat plan folder is the default. An area folder is used only when the child list is too long to show its shape. | GOV-005:72-73 | document-codes.md §3 | conduct |
| D17 | A code for a planned, unwritten document (typically a phase deliverable) is reserved under `reserved`. Its `reason` names the planned document and any claiming phase. **(plugin differs: code and reason only)** | GOV-005:78-79 | document-codes.md §4 | P:schemas/codes.schema.json:88-95, 106-126 |
| D18 | Allocation skips a reserved code. A document using one fails until the same change removes the reservation. | GOV-005:79-81 | document-codes.md §4 | P:scripts/codes.py:80-88, 232-233 |
| D19 | A code whose document is deleted is retired under `retired`. A retired code is never reissued, and a document using one fails. | GOV-005:83-84 | document-codes.md §4 | P:scripts/codes.py:230-231; P:schemas/codes.schema.json:96-103 |
| D20 | Held codes appear in the catalog with their state and reason. | GOV-005:177 | document-codes.md §4 | P:scripts/codes.py:340-346 |
| D21 | Once a code reaches the integration branch it is never reused or renumbered. Superseded and deprecated documents keep their codes. Renaming the slug is allowed; changing the code is not. | GOV-005:88-90, GOV-001:89 | document-codes.md §5 | P:scripts/codes.py:227-231; conduct |
| C3a | A document code is free before merge and permanent after: whoever integrates second allocates again, renames the file and updates every reference. | GOV-005:167, AGENTS.md:315-317 | document-codes.md §5 | P:skills/session-start/SKILL.md:192-193; P:scripts/codes.py:227-228 |
| D22 | A duplicate code arises only between allocations on different machines, which share no git directory, or from a reservation that expired before its document was written. | GOV-005:162-165, AGENTS.md:317-319 | document-codes.md §5 | P:scripts/reservations.py:13-17, 55-58 |
| D23 | The register is the ledger and the check is the check. | GOV-005:167-169 | document-codes.md §5 | P:scripts/codes.py:198-241 |
| D24 | A register reservation is tracked, deliberate, lasts until its document is written and survives a clone. A pre-merge reservation is untracked, automatic, lasts minutes and is machine-local. The two are unrelated. | GOV-005:98-111 | document-codes.md §6 | P:schemas/codes.schema.json:88-95; P:scripts/reservations.py:5-17 |
| D25 | Each allocation creates one file named for the code under `<git common dir>/code-reservations/` with `O_CREAT \| O_EXCL`. Exactly one racer wins, and the loser tries the next candidate, up to 50 attempts. | GOV-005:115-117, GOV-005:119-120 | document-codes.md §6 | P:scripts/reservations.py:53, 65-80, 136-150; P:scripts/codes.py:40-42, 371-376 |
| D26 | The git common directory is shared by the primary checkout and every linked worktree, so peers see a reservation before any merge. A tracked file cannot provide that. | GOV-005:119-130 | document-codes.md §6 | P:scripts/reservations.py:7-17 |
| D27 | An empty or unreadable reservation still holds its code and expires by the file's modification time. **(plugin differs)** | GOV-005:117 | document-codes.md §6 | P:scripts/reservations.py:19-23, 83-96, 104-117 |
| D28 | Expiry after 14 days is the only automatic release. Allocation prunes expired reservations first. | GOV-005:134-136 | document-codes.md §6 | P:scripts/reservations.py:55-58, 120-133; P:scripts/codes.py:371 |
| D29 | `release-code <code>` releases a reservation for a document that will not be written. With no argument it lists reservations and their holders. | GOV-005:138-142 | document-codes.md §6 | P:scripts/reservations.py:153-164, 188-216; P:skills/next-code/SKILL.md:30-37 |
| D30 | A reservation is never released because its document exists. It stands until expiry at no cost, because allocation skips the code anyway. | GOV-005:144-156 | document-codes.md §6 | P:scripts/reservations.py:25-29 |

## Core protocol sources: not shipped


| Source (file:line) | Source rule, one line | Why not shipped |
|---|---|---|
| GOV-001:29 | Durable memory facts live in a memory store with provenance and confidence. | The plugin has no memory store or memory loader. |
| GOV-001:41-43 | Records resolve through a data-root environment variable, with a tracked fictional example set; taxonomy and process data always come from the tracked root. | No plugin script resolves a data root; `data_root` is only a template placeholder (P:templates/AGENTS.md:53). |
| GOV-001:58, 60 (memory sentences) | Memory types live in their own directories, and a memories folder is only a pointer. | No memory store. |
| GOV-001:64, GOV-001:104 | Memories satisfy a separate memory schema; memory project and related links resolve. | No memory schema ships (P:schemas/ has none). |
| GOV-001:99, GOV-001:150, GOV-001:159 | An overdue `review_after` produces a warning and is reviewed in a weekly habit. | The field is allowed (P:schemas/document.schema.json:127-132), but no script compares it to today. |
| GOV-001:100 | Optional `tags` from the data root's tags list. | The plugin schema has no `tags` field and rejects unknown fields (P:schemas/document.schema.json:5), and there is no tags taxonomy. |
| GOV-001:134-138, AGENTS.md:158 | An `--inventory` report of component maturity and open plans. | No inventory command. The catalog's plans table (P:scripts/codes.py:311-336) covers plans only. |
| GOV-001:144-153, GOV-001:157 (CI), GOV-002:178 ("in CI"), GOV-005:178 | Failures are CI failures, and CI runs the validator and diffs the catalog through a temporary file. | The plugin ships no CI. `check.py` sets an exit code and the catalog is compared in memory (P:scripts/documents.py:381-391). |
| GOV-001:157 | The checker never traverses the confidential tree and never opens the database directory. | Repository paths. The plugin scans only the document root (P:scripts/documents.py:146-153). |
| GOV-001:190 | A gitignored in-repository worktree directory guards against misplaced worktrees. | The scaffold changes `.gitignore` only for the staging directory (P:scripts/scaffold.py:118-122). |
| GOV-002:127-130 | An authorized recovery procedure releases a stale claim, using the signal as evidence. | No skill or script releases a claim (P:scripts/backlog.py:53-54). |
| AGENTS.md:61-64 | A private-content checker, run with changes staged, gates confidential identifiers. | The checker script is not shipped. Only the conduct rule A66 ships. |
| AGENTS.md:113-115 | Ideas not ready to be governed are parked in an ungoverned staging folder with no front matter. | Not shipped. The plugin captures ideas in its idea log; `staging_dir` holds partition drafts. |
| AGENTS.md:116-121 | Ephemeral working plans live in a gitignored folder and are never deleted without approval. | That directory is not shipped. |
| AGENTS.md:122-127, AGENTS.md:279-281 | Files that worktree agents must read live in a tracked shared-files folder with a claims ledger, and every claim is released at hand-off. | The shared-files ledger and its contract are not shipped. |
| AGENTS.md:161-164 | Every new tool ships with an operations document paired by filename and filled by a generator. | P:scripts/generate_tool_docs.py writes one tools reference. There is no pairing with operations documents. |
| AGENTS.md:297-299 | Before merging, a dirty-integration hook script must exit 0. | The hook is not shipped. The `git status --short` check in P:skills/session-start/SKILL.md:162 carries C32. |
| AGENTS.md:245-246, 252-255 (specific commands) | Each worktree syncs its dev extras and rebuilds its database. | Repository toolchain. The general rule ships as A72. |
| Ledger C8 | The agent instruction files reference the checkpoint procedure. | Neither P:templates/AGENTS.md nor P:templates/CLAUDE.md mentions checkpoint (confirmed by grep). |
| Ledger C19 | The owner may re-run the close procedure afterwards as an audit of a completed phase. | P:skills/session-close/SKILL.md:50-51 forbids re-running it on a phase that is already closed. |
| GOV-001:37 (criterion) | A duplicated fact qualifies only if not knowing it for one turn causes irreversible harm. | The plugin template states a looser test, "the few facts worth duplicating" (P:templates/CLAUDE.md:5-7). A12 carries the plugin wording. |


## Core protocol sources: dropped as history or repository-specific


| Source lines | What | Why |
|---|---|---|
| GOV-001:1-14, GOV-002:1-13, GOV-005:1-13 | The sources' own front matter | Metadata, not rules |
| GOV-001:20 | Links to the audit, the registry, the operations guide and the design decision | Repository documents |
| GOV-001:37 (last two sentences) | Memory editing and the proposed scribe monopoly | Repository-specific state |
| GOV-001:41 (plan and decision references), GOV-001:43 | A named sweep binding every phase; a named phase that moved the real records | History, phase and document codes |
| GOV-001:60 (middle sentence) | "All plans live under one folder; the root plans folder no longer exists", with its plan and decision references | History |
| GOV-001:66-83 | Example YAML with repository codes and dates | Content carried as A22–A36 |
| GOV-001:133-136, GOV-002:21-26, GOV-005:44-46, 141, 182-183, AGENTS.md:81-104, 241-247 | Repository command lines | The plugin's invocations live in its skills and in P:docs/tools.md |
| GOV-001:153 | Python and frontend CI jobs | Repository-specific |
| GOV-001:155 (named prompt file, `js/`, working and public folders) | Named exempt files and unscanned folders | Replaced by `exempt_files`, and scanning limited to the document root |
| GOV-001:157 (last sentence) | Protected-branch CI enforcement is host configuration | Repository host |
| GOV-001:163, 176 | One design decision "adds" a catalog, and another "amends" its single-active rule | History; the resulting rules are carried |
| GOV-001:169-172 | Exemptions for the backlog README and a raw answers file | Repository files. The plugin's backlog lives outside the document root by default. |
| GOV-001:189-190, AGENTS.md:238-239 | The documentation-only exception was withdrawn on a date | History; C12 carries the current rule |
| GOV-002:80 ("this repository sets 3") | The local `max_active` value | Repository setting; the plugin default is 1 |
| GOV-002:95, 110-112, 116, 126-130 | Phase and requirement references, the measured history behind the threshold, the test-file grep, the recovery procedure's origin | History and codes; the threshold value (2 days) is carried |
| GOV-002:140 | The initial capture of ten plans and the portfolio records | History |
| GOV-002:142 (capture-review link) | Link to the capture review | Repository document |
| GOV-002:144 | Empty heading "Start and end a session" | No content |
| GOV-002:161-162 | Without `next_up`, ties fall to the alphabetical order of track names | Rationale; B26 states the order |
| GOV-005:18-19, 169 | Links to design decisions | Codes |
| GOV-005:74 | A named plan as the worked example | Code |
| GOV-005:121-127 | Requirement reference; why the integration branch and the shared-files folder cannot hold reservations | Codes and repository specifics; D26 carries the reason |
| GOV-005:145-153 | A phase built and removed the release-on-existence mechanism | History; D30 carries the rule |
| GOV-005:158-162 | "What this replaces": the old register-reservation workaround | History |
| GOV-005:172-173 | Session records were renumbered twice before the mechanism existed | History |
| AGENTS.md:24-27 | Origin story of the never-edit rule | History |
| AGENTS.md:33-35 | Pointer to the repository's session-start command file | The plugin ships it as P:skills/session-start |
| AGENTS.md:51-54, 58-59, 64 (story), 67-69, 184-189 | Remote and squash history, which branch is the integration branch today, the idea to gate `main`, the confidentiality-sweep story, the move of the real records | History, names and codes |
| AGENTS.md:73-78, 106-111, 132-133, 139-146 | Stack, repository conventions, route and data rules, adding a domain entity | Repository-specific |
| AGENTS.md:135-137 | Pointer to the reporting guidelines | Carried by P:docs/reporting.md |
| AGENTS.md:170 | Read the named decision record | Generalised as `decision_record` (B31) |
| AGENTS.md:231 | Name of a repository test | The plugin check covers the same thing (P:scripts/documents.py:389-391) |
| AGENTS.md:299 | Reference to the operations guide | Code |


## Conflicts between the sources and the plugin, and how each was resolved


1. **Completion authority.** AGENTS.md:178-180 says only the owner-invoked review marks a phase complete. AGENTS.md:284-286 has the agent mark complete on its branch, before the rebase and before integration. C17 and P:skills/session-close/SKILL.md:13-28, 102-107 say otherwise: a coordinator marks complete after the owner-approved integration, on the integration branch. **C17 carried; both AGENTS.md passages dropped.**
2. **Switching the primary checkout.** AGENTS.md:200 says `git switch dev && git pull`, which contradicts AGENTS.md:220. **Resolved to the plugin:** confirm the checkout is on the integration branch, stop if not, then `git pull --ff-only` (session-start:89-95), as B43.
3. **Contents of the claim commit.** AGENTS.md:204-205 says it "changes nothing else", but AGENTS.md:230-232 has the catalog regeneration committed with the claim. **Resolved as claim plus catalog in one commit** (session-start:114; B42, C12).
4. **Branch naming.** GOV-001:181, 192 and GOV-002:168, 170 name the integration branch `main`; AGENTS.md names `dev`. **Resolved:** no branch is named anywhere; the rules say "the integration branch" (`integration_branch`, default `main`, P:.claude-plugin/plugin.json:40-45).
5. **Stale states.** GOV-002:94-96 says "three text states" but its table lists four. P:scripts/backlog.py:69 repeats "three" while returning four. **Four carried (B51).** The plugin docstring should be corrected separately.
6. **Dated code sequence.** GOV-005:54-55 says a dated code takes the "lowest unused sequence"; the plugin takes the highest plus one (codes.py:117-118). **Plugin carried (D10).**
7. **Allocation as a pure function.** GOV-005:55-56 says allocation is a pure function of committed state, which GOV-005:94-96 itself contradicts. **Resolved:** `next_code` is pure, and `allocate` takes and reserves the code (D8, D11).
8. **Register reservation fields.** GOV-005:79 records a reason and the claiming phase; the plugin's entry has only `code` and `reason`, and extra fields are rejected (codes.schema.json:106-126). **Plugin carried:** the phase goes inside `reason` (D17).
9. **Code locations.** GOV-005:26-36 and GOV-001:47-57 use this repository's numbered folders; the plugin uses `plans/`, `requirements/` and so on under the document root. **Plugin carried (D3, A14).**
10. **How the catalog is checked.** GOV-005:178 says CI regenerates into a temporary file and diffs; the plugin check renders in memory. GOV-005:185 says the command "also prints" the catalog; the plugin prints only the path and count. **Plugin carried (A61, A62).**
11. **Crash recovery for reservations.** GOV-005:117 says there is "nothing to repair after a crash". The plugin documents that an empty file left by a crash still holds its code and expires by modification time. **Plugin carried (D27).** These are consistent in effect.
12. **Duplicate-code cases.** AGENTS.md:317-319 names only different machines; GOV-005:162-165 adds an expired reservation. **Both carried (D22).**
13. **`tags`.** GOV-001:100 makes `tags` optional, but the plugin schema rejects the field. **Plugin carried:** `tags` is not a field (A22; not-shipped row).
14. **`review_after`.** GOV-001:99 promises an overdue warning; the plugin has none. **Field carried (A33), warning not shipped.**
15. **Plan sections.** GOV-001:49 lists outcome, scope, dependencies, steps, acceptance checks and open questions; plan_check requires six different sections plus two conditional ones. **Plugin carried (A16).**
16. **Session records.** GOV-001:127 says session records are append-only after review, while checkpoint regenerates sections 2–6 on every run. **Resolved:** checkpoint regenerates until close; after close the record is only added to (B60), backed by session-close:50-51.
17. **When the session record is created.** GOV-002:166 creates it at session start; the plugin creates it at the first checkpoint or at hand-off (session-start:158). **C7 carried without a timing claim.**
18. **C1 when no decision record is configured.** `decision_record` is optional (backlog.schema.json:23-28), and a fresh scaffold names none (scaffold.py:81), so C1, C2 and C11 then have nowhere to write. I did not invent a rule. **Open question for the owner:** should the scaffold seed a decision record, or should C1/C2/C11 say what happens without one?
19. **C11's mechanism is partial.** regression.py flags a complete phase only when `completion_evidence` becomes empty (regression.py:103). Removing one line of several is not caught; only the missing-file check forces the removal. **C11's entry requirement is marked conduct.**
20. **B71 and B40/B41 have no basis in the four sources.** They come from the plugin (regression.py, the backlog skill, session-start). They are carried because the plugin enforces them; each is marked "— (plugin)".
21. **Unenforced cap.** The schema's `max_active` maximum is 4 (backlog.schema.json:29-35); no source states one. **Plugin carried (B5).**
22. **Integration wording.** AGENTS.md:302 integrates with `git -C <primary checkout>`; the plugin runs the merge from the primary checkout. The same act, so **the plugin form is carried (A78).**
23. **Outside the three documents: history in a plugin comment.** P:scripts/backlog.py:25-26 reads "where this rule was first measured". Flagged in case the no-history test should cover script comments.
## Changes made while writing the plugin documents

The plugin documents follow the extractions above, with these differences:

- protocol.md §11 states C12 with the fast-forward that integrates a branch added to the work done
  in the primary checkout, because A78 and P:skills/session-start/SKILL.md §8 merge from there.
- protocol.md §12 points to backlog-protocol.md §11 for C32 instead of restating it, so the rule
  appears once.
- backlog-protocol.md §12 names the decision record as "the document the backlog's
  `decision_record` names", the wording of P:skills/session-start/SKILL.md. When no decision record
  is configured, C1, C2 and C11 have nowhere to write and the regression check does not run
  (B72); what should happen then is open (family A conflict 18).
- document-codes.md §2 adds the reason dated series exist (several sessions write those kinds at
  once), from P:scripts/codes.py's module docstring.
- reporting.md shows the id-first form with placeholders (`<id> (<short title>)`) rather than a
  real idea.
- The plugin's P:docs/vocabulary.md lost two history words under the owner's ruling for this
  phase: the `supersedes` link reads "takes the place of the target", and tie-break `O4` reads
  "An event that evidences a lasting defect", both with meaning unchanged.

## Acceptance and verification

As the `phase-plug-07` backlog entry states. A reviewer reads each row's source passage and the
named plugin section and finds the rule present; `P:test/test_no_history.py` and
`P:test/test_no_source_references.py` pass over `P:docs/`.

## Out of scope

Families D, E and F (`PLAN-048.09`); the orientation document and the surface audit; this
repository's own governance documents, whose contradictions found here are recorded as ideas
000467 and 000468.

## Open questions

- Family A conflict 18: whether the scaffold should seed a decision record, or the backlog
  protocol should say what C1, C2 and C11 require when none is configured.
- Family A conflict 23: P:scripts/backlog.py:25-26 carries a history comment ("where this rule was
  first measured") outside `docs/`, which `test_no_history.py` does not cover.
- GOV-006:17-18: nothing loads `docs/reporting.md` at session start in a target repository.
