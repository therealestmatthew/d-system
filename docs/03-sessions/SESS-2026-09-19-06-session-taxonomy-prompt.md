---
schema_version: 1
id: doc-session-session-taxonomy-prompt
code: SESS-2026-09-19-06
title: Session-taxonomy investigation prompt drafting
kind: session
status: active
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems: [sys-governance, sys-fw-analysis-sessions]
depends_on: []
---

# Session-taxonomy investigation prompt drafting

## Phase

Unclaimed — owner-directed work, no backlog phase. `session-taxonomy-prompt` — draft a
self-contained investigation prompt that classifies the kinds of Claude Code sessions run in
this repository, for later execution in a fresh session.

## Verification

```
$ uv run python -m src.governance
Governance OK: 35 systems, 293 documents, 26 memories, 286 backlog phases

$ uv run pytest
638 passed, 2 warnings

$ uv run python tools/check_no_private_content.py   # with this session's changes staged
check_no_private_content: OK (730 tracked files, 31 identifiers checked)
```

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

1. Clarifying questions were asked through AskUserQuestion before the prompt was drafted — Met:
   a four-question batch (evidence base, purpose, scope, runner) ran first and its answers shaped
   the prompt.
2. A self-contained investigation prompt exists under `docs/00-working/`, covering sub-agent
   investigation of session evidence and discovery of undocumented session types — Met:
   `docs/00-working/PROMPT-session-taxonomy-investigation.md` was written and iterated through
   the session. (It was later superseded the same day by the owner's separate adversarial-review
   session, which split it into `PROMPT-session-taxonomy-part1-theory.md` and
   `PROMPT-session-taxonomy-part2-evidence.md`; the original now stands as a stub pointing at
   them. Those two files belong to that session, not this one.)
3. The prompt's transcript handling is a deterministic reduction design grounded in the verified
   structure of real transcript files — Met: the JSONL record shapes were probed directly
   (real-prompt scarcity among `user` records, sidecar `ai-title`/`last-prompt` records,
   tool-use histograms) and the three-stage pipeline written from those observations.
4. The prompt includes the instruction to register the analysis engine rather than leave it in a
   scratchpad — Met: a "Register the engine, not just the findings" section routes it through
   `tools/append_idea.py` and an owner decision on permanent placement.
5. The prompt separates a portable session-type core from the d-system binding and is structured
   theory-first with a hard stop for the owner's review before empirical analysis — Met: both
   were added at the owner's direction and survive in the split successors.
6. Adversarial-review text for a fresh session was delivered in conversation — Met: delivered
   twice (initial and updated ten-surface version); the owner ran it, and the split in condition
   2 is its recorded outcome.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.

## Unresolved

- This session ran in the primary checkout on `dev` rather than a worktree. AGENTS.md requires a
  worktree for every session including documentation-only work; the session began as
  conversational Q&A and the requirement was not revisited when it started producing files. The
  work product is untracked files under the ungoverned `docs/00-working/`, so no tracked state
  was touched outside this record, but the record should say so rather than leave it implied.
- The investigation itself has not run. Part 1 (theory) awaits a fresh session; Part 2 runs only
  on the owner's explicit go after they ponder Part 1's output.

## Review

Independent sub-agent review (fresh, non-fork), findings pasted verbatim:

**1. AskUserQuestion clarification before drafting — Unverifiable from repo state.** As expected: conversations leave no repository trace. Nothing on disk contradicts it, and the prompts themselves institutionalize the practice (both parts instruct batched AskUserQuestion use), but that is authorship style, not evidence the questions were asked. Recording it as claimed-but-unverifiable is the honest reading.

**2. Self-contained prompt under docs/00-working/ — Holds, matching the superseded-stub account exactly.** On disk: `docs/00-working/PROMPT-session-taxonomy-investigation.md` is a 16-line stub dated 2026-09-19 explicitly saying it was split after an adversarial review; `PROMPT-session-taxonomy-part1-theory.md` (185 lines) and `PROMPT-session-taxonomy-part2-evidence.md` (238 lines) exist untracked. Every substance element the owner asked for survives in the split pair: sub-agent investigation of session evidence (Part 2 Stage 2: adjudication, blind anti-confirmation sample, record cross-check, session-record sweep, tooling sweep, portability attack, with agent-hygiene rules); undocumented-type discovery (Part 1's seed-taxonomy item (c) and Part 2 deliverable section 5); deterministic transcript reduction (Part 2 Stage 0/1, "no agent opens a raw .jsonl whole"); engine registration (Part 2's "Register the engine, not just the findings", routed through `tools/append_idea.py` with placement as an owner decision); portable core vs d-system binding (Part 1 consumer 6 plus Part 2 deliverable sections 2–3 and the portability-attack agent); theory-first hard stop (Part 1's "Stop there. Deliver the document, then halt and give the owner the floor"; Part 2 gates on an explicit go and refuses to run without the theory file). This is also a fair reading of the owner's five instructions, including instruction 4 (portable generalizations) and instruction 5 (theory-first with pondering time).

**3. Deterministic reduction grounded in verified transcript structure — Holds.** Spot-checked the prompt's empirical claims against the real corpus: 105 top-level `.jsonl` files (claimed ~105); 170MiB of top-level transcripts (claimed ~177MB decimal — same quantity); 707M total project dir (matching the owner's "700+MB"); 748 subagent transcripts (claimed ~744, plausibly grown since); 2 worktree project dirs exist as claimed; 19 distinct top-level `.type` values observed, all 19 named in the prompt's enumeration (claimed "~21" — the only figure that runs slightly high, and the prompt hedges it); exactly 2 degenerate no-user-record files at 1405 and 1770 bytes (claimed "~2 crash stubs, ~1.4KB"). This is genuinely probed structure, not invented.

**4. Engine-registration instruction — Holds.** Matches the record's description (append_idea.py, owner decides permanent placement, script-not-outputs).

**5. Portable core / d-system split and theory-first hard stop — Holds.** Both present and structural, not decorative (Part 1 even forbids reading Part 2 so the theory cannot be shaped to the measurement).

**6. Adversarial-review text delivered — Conversation-only, but corroborated.** The stub's own text ("split in two on 2026-09-19, after an adversarial review") and the review-fix list folded into Part 2 (privacy guard, blind sampling, fuzzy matching, marker-absence rule, portability attack) are exactly the artifacts an executed adversarial review would leave. The split files' existence corroborates the claimed outcome; the delivery of the review text itself is unverifiable from repo state.

**Verification gates rerun:** governance → `Governance OK: 35 systems, 293 documents, 26 memories, 286 backlog phases` (the record's originally pasted line said 292 — captured before this record itself was registered in the catalog; corrected after the review flagged it); pytest → `638 passed, 2 warnings` — matches; private-content check → `check_no_private_content: OK (730 tracked files, 31 identifiers checked)` — matches.

**Untouched-elsewhere check:** staged changes are only the session record (new) and catalog.md (one added row plus the count line). Untracked files are the three PROMPT-session-taxonomy* files plus files all present in the pre-session snapshot. Nothing unrecorded was touched.

**Discrepancies:** (1) governance count drift, minor and self-caused, corrected above; (2) subagent-transcript count "~744" vs actual 748 — within the tilde, not a discrepancy; (3) the record candidly self-reports the worktree-rule violation under Unresolved; the reviewer confirms the stated blast radius is accurate.

**Verdict: Pass.** Conditions 2–5 hold on direct inspection; conditions 1 and 6 are unverifiable from repo state but uncontradicted, with 6 partially corroborated by the stub/split structure. The acceptance conditions are a fair restatement of the owner's five instructions. All three verification gates pass on rerun; the only record-vs-reality discrepancy was the stale 292-vs-293 governance line, cosmetic and self-caused. Nothing was changed by the review.

## Decisions

- The investigation's evidence base is all three sources — curated session records, raw
  transcripts, and the repo's tooling/governance surface — per the owner's answer to the opening
  question batch; scope is this repo's sessions only, run later in a fresh session.
- Transcript volume is handled by deterministic code, not agent reading: a Stage 0 reduction
  script (manifest, prompts-only files, behavior signatures), a Stage 1 mechanical
  pre-classification, and agent judgment only on the residue. The owner prompted this
  restructure by asking for a deterministic extraction system; probing real transcripts showed
  only 17 of 220 `user` records in the largest file were actual owner prompts, which settled it.
- The signature vocabulary is derived from the repo's registered tooling (tools/, commands,
  skills, agents) rather than hand-picked markers, so Stage 0 contains no interpretation.
- The engine gets registered, not abandoned: the executing session must capture an idea via
  `tools/append_idea.py` proposing promotion to `tools/` plus an OPS doc, and ask the owner
  where the engine and prompt live permanently.
- The taxonomy carries two layers — a portable core (types defined without reference to any
  d-system artifact) and a d-system binding — because the owner directed that the results
  generalize to any repo. Type existence is the portable claim; frequency stays local.
- The investigation runs theory-first with a hard stop: Part 1 proposes the theoretical set and
  halts for the owner to ponder; Part 2's empirical pass runs only on their explicit go. Owner
  directed; it also makes Part 2 a test of registered predictions rather than curve-fitting.
- The prompt stays untracked under `docs/00-working/` per the owner's instruction; this session
  commits only its session record and the regenerated catalog.

## Corrections

- The first draft's Stage 0 hand-picked workflow markers (`append_idea.py`, `git worktree`, …)
  from this assistant's judgment. The owner's question "how will it identify the signatures?"
  exposed that as a guess; it was replaced with the repo-derived vocabulary rule.
- The original design had sub-agents grepping raw JSONL directly; the owner's push for a
  deterministic system was correct and the design was rebuilt around Stage 0. Recorded as a
  correction, not a refinement: the first design spent agent context on work a script does
  better.

## Left undone

- Part 1 (theory) and Part 2 (empirical) have not run. The owner runs Part 1 in a fresh session
  from `PROMPT-session-taxonomy-part1-theory.md`, ponders its output, then gates Part 2.
- No idea was appended for scheduling the Part 1 session — the prompt files themselves carry the
  work forward and the owner is sequencing it by hand. If they want it in the idea queue for a
  planning session, that capture is one `tools/append_idea.py` call away.
- The superseded stub `PROMPT-session-taxonomy-investigation.md` is left in place as a pointer;
  deleting it is the owner's call once the split files are the settled form.
