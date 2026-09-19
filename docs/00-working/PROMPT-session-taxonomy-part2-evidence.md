# Prompt: Session-type taxonomy — Part 2 (empirical test)

Paste everything below the line into a fresh Claude Code session opened in `/code/d-system`,
**only after the owner has reviewed Part 1's deliverable and given an explicit go.**

Required input: `docs/00-working/session-types-theory.md` (Part 1's registered theory). If it
does not exist, stop and tell the owner — this phase tests that theory; it cannot run without it.

---

## Mission

Test the registered theoretical taxonomy in `docs/00-working/session-types-theory.md` against
the evidence of what sessions actually ran in this repository. Because the theory and its
falsifiable predictions were registered before any evidence was seen, this phase is a test, not
curve-fitting: for each proposed type, does the evidence contain it, at the predicted signature?
The interesting outputs are the misfits — sessions no proposed type covers, proposed types the
evidence never shows, and predictions that fail in either direction (including frequency-band
surprises).

The six consumers of the final taxonomy, and the deliverable structure serving them, are listed
under Deliverable below. The deliverables are working documents, not governed ones, and not
edits to CLAUDE.md or AGENTS.md. **Do not modify CLAUDE.md or AGENTS.md under any
circumstances** — that rule is absolute in this repo.

## Session setup

At the start, ask the owner (AskUserQuestion) whether to run as an unclaimed ad-hoc session or
under the full `/session-start` claim-and-worktree protocol; do not assume either.

## Evidence base (three sources — all three are required)

1. **Curated session records**: `docs/03-sessions/SESS-*.md` (~119 files). The project's own
   framing: what each session was for, what it produced, how it closed.
2. **Raw transcripts**: top-level `*.jsonl` files in `~/.claude/projects/-code-d-system/`
   (~105 files, ~177MB) **and** in the sibling worktree project directories
   `~/.claude/projects/-code-d-system-worktrees-*/` (sessions launched inside worktrees are
   filed there — a handful of files, and exactly the direct-coding sessions the taxonomy cares
   about). Top-level files only: the *subdirectories* under each session id hold sub-agent
   transcripts (`<session-id>/subagents/agent-*.jsonl`, ~744 of them) and tool-result caches —
   they are **not** owner sessions and stay out of the corpus, but the *existence* of a
   session's `subagents/` directory is recorded as a strong orchestration marker.
3. **Repo tooling and governance surface**: `.claude/skills/`, `.claude/commands/`,
   `.claude/agents/`, `.agents/skills/`, `docs/08-governance/` (GOV-* and OPS-* docs),
   `docs/09-backlog/backlog.yaml` + README.

## Privacy guard (binding — read before writing any derived file)

Transcripts contain private content: tool results from sessions that touched
`_private/portfolio/`, and owner prompts that reference it (verified: 33 prompts across 24
transcripts mention that path, and prompts naming real clients or people are expected). The
standing rule applies: **never write a confidential identifier into a tracked file.**

- All derived outputs (the working directory below) go to `_private/analysis/session-taxonomy/`
  — inside the gitignored `_private/` boundary (ADR-009). Nowhere else. Not the scratchpad
  (they must outlive this session as input to the CLAUDE.md revamp), and never anywhere
  trackable.
- The two deliverable documents in `docs/00-working/` quote transcript content only in
  paraphrase or with private identifiers removed; when in doubt, cite the session id and leave
  the quote in `_private/analysis/`.
- The register-the-engine step at the end covers the **script only**, never the derived outputs.

## Cost and agent-hygiene rules (binding)

- **You are the orchestrator, tracker, and final judge only.** Delegate read-heavy work to
  deterministic code first and sub-agents second. You read the manifest, sub-agent reports, and
  ambiguous cases' derived files; you never read a raw transcript.
- **Deterministic reduction before any agent reads anything.** No agent, including you, opens a
  raw `.jsonl` whole. Median transcript ~1.45MB, max ~9.9MB, and mostly noise for this purpose:
  in the largest transcript, 8 of 220 `type:"user"` records are real owner prompts — the rest
  are `tool_result` payloads (~90% of bytes) and harness records. Stage 0 strips all of that
  mechanically.
- **Bounded scopes, no overlap.** Give each sub-agent an explicit file list. No sub-agent spawns
  sub-agents.
- **One judgment wave, then synthesize.** A second wave is justified only to resolve a specific
  conflict or gap the first wave surfaced, and say so when you launch it.
- **Reports, not dumps.** Every sub-agent returns a structured summary (classification +
  evidence lines), never raw file content. Cap each report's length in its prompt.
- Use the Explore agent type for read-only sweeps; use general-purpose only where Bash is needed.

## Stage 0 — deterministic reduction (a script, zero agents)

Write one Python script into your scratchpad and run it once over the corpus defined above,
emitting into `_private/analysis/session-taxonomy/`.

**Record shapes (verified against the full corpus, 2026-09-19; spot-check anyway):**

- The corpus parses cleanly (zero JSON parse errors as of verification), but wrap parsing
  per-line and count failures rather than crashing.
- Top-level `.type` has **~21 values**, not a handful. Substantive: `user`, `assistant`,
  `system`, `attachment`. Sidecars: `ai-title`, `last-prompt`, `mode`, `permission-mode`,
  `bridge-session`, `atis-latch`, `queue-operation`, `file-history-snapshot`/`-delta`,
  `agent-name`, `custom-title`, `pr-link`, `frame-link`, `relocated`,
  `artifact-comment-monitor`. Ignore types you don't recognize; log their names.
- Sidecars repeat per turn (a file can hold dozens of `ai-title` records) — take **last wins**.
  `ai-title` is missing entirely from ~22 of 105 files and `last-prompt` from ~12; emit empty
  columns, not errors. `mode`/`permission-mode`/`bridge-session` records carry no `timestamp`
  — derive first/last timestamps from records that have one.
- **Real owner prompts** are `type:"user"` records that are NOT `isMeta:true`, whose
  `.message.content` is either a string or a list containing `text` blocks (2 real prompts in
  the corpus carry images alongside text), **excluding**: `<command-name>` wrappers (extract
  these into their own manifest column — a session opening with `/session-start` is
  self-labeling), `<local-command-stdout>` records, and `[Request interrupted...]` markers.
  Census for calibration: ~12,800 `tool_result` echoes, ~1,237 real prose prompts, 227 command
  wrappers, 221 isMeta strings, 164 isMeta text-block lists (skill-body expansions — never
  owner prose), 39 stdout records.
- **`/clear` openers**: ~88 of the prompt-bearing files begin with a `/clear` command wrapper.
  Owner-confirmed convention: they clear after every session close, so **each file is a fresh,
  self-contained session** — skip the wrapper, never concatenate files. A file opening some
  other way (`resume`, bare continuation phrasing) is unusual; flag it for adjudication.
- **Degenerate sessions**: ~2 files contain no user records at all (crash stubs, ~1.4KB). Flag
  `degenerate` in the manifest; report them as a class; exclude them from Stage 1 rules.
- Substantive records carry `cwd`, `gitBranch`, and `sessionId` — use `gitBranch`/`cwd`
  directly as worktree/claim/branch evidence instead of grepping Bash strings.

**Outputs:**

1. `manifest.tsv` — one row per session: id, source project dir, ai-title (last), first/last
   timestamp, real-prompt count, opening command(s), first real prompt (first 200 chars),
   assistant-turn count, top tool names, Agent/Skill invocation counts, `gitBranch` values
   seen, has-`subagents/`-dir flag, degenerate flag, last-prompt. You read this yourself.
2. `prompts/<session-id>.md` — the real owner prompts only, in order, plus extracted command
   invocations marked as such. Tool results, thinking, meta records, and attachments dropped.
3. `signatures/<session-id>.tsv` — tool-use histogram, `subagent_type` of each Agent call,
   skills/commands invoked, files edited bucketed by top-level directory (`docs/01-plans/` vs
   `src/` vs `_data/` carry different meaning), and workflow-marker hits (below).

**Signature vocabulary — derive it, don't invent it.** Before extraction, the script
enumerates: script names in `tools/`, command names in `.claude/commands/`, skill names in
`.claude/skills/` and `.agents/skills/`, agent names in `.claude/agents/`, and a small fixed
set of git workflow strings. A session's signature records which registered names appear in its
Bash command strings, `Skill` calls, `subagent_type` fields, and written file paths. Stage 0
contains zero interpretation — it only counts occurrences of names the repo registers; all
meaning-assignment happens in Stage 1.

**Caveat the vocabulary honestly:** it is today's tool surface, and the corpus spans weeks in
which that surface changed. **A marker's absence is never evidence** — a session that predates
a tool could not have used it. Only marker *presence* may drive a rule.

Spot-check the script's output on three transcripts — one large, one small, and one that opens
with `/clear` — before trusting the run.

## Stage 1 — mechanical pre-classification (still deterministic)

A rule pass over the signatures assigns each session a *candidate* label plus confidence plus
the triggering evidence — e.g. Agent calls or a `subagents/` dir → orchestrator candidate;
Edit/Write-heavy with a claim/branch marker → direct coding; `append_idea.py` dominant →
capture; zero writes and non-degenerate → question/analysis; plan-doc writes without code →
planning. Rules key on marker presence only, per the absence caveat above. This is triage for
attention, not the taxonomy; expect it to be wrong at the margins, and record the rules in the
deliverable so they can be criticized.

## Stage 2 — agent judgment (derived files only — never raw JSONL)

1. **Adjudication** (1–2 agents): read `prompts/` files for low-confidence, conflicting,
   rule-defying, or unusual-opener sessions; assign and justify a label.
2. **Blind anti-confirmation sample** (1 agent): take a random sample from each *confident*
   class and hand the agent the `prompts/` files **without Stage 1's labels or rules**. It
   classifies blind against the theory's type definitions; you compare its answers to Stage 1's
   and treat every disagreement as a finding about the rules, not the agent.
3. **Record cross-check** (1 agent): reconcile `manifest.tsv` against `docs/03-sessions/SESS-*`.
   There is **no join key** — SESS front-matter carries no session UUID — so matching is fuzzy
   (dates, titles, topics, `gitBranch`). The agent reports match confidence per pairing. An
   unmatched item is a *lead to investigate*, not a finding: transcripts may be filed under a
   worktree project dir, and records may cover work done across machines or before the corpus
   window. Only after those explanations fail does a mismatch count as evidence of an
   undocumented type or a governance gap.
4. **Session-record sweep** (1–2 agents, split by date): per SESS file — stated purpose, work
   performed, sub-agent use, worktree/claim, proposed type label, as a table. The same agents
   also record structural facts per record, at no extra reading cost, into
   `_private/analysis/session-taxonomy/record-structure.tsv`: sections present vs the
   checkpoint contract (front matter plus `Phase` / `Verification` / `Acceptance` / `Backlog` /
   `Unresolved`, and session-close's `Review` / `Decisions` / `Corrections` / `Left undone`),
   line count, front-matter completeness, and any non-contract sections. This table is input to
   Part 3 (the record-quality and template phase serving 000276 and 000277) — collect it here,
   analyze it there.
5. **Tooling/governance sweep** (1 agent): map each skill, command, agent definition, and
   GOV/OPS doc to the session type(s) it serves; list governance obligations (worktree, claim,
   record, checkpoint) and which types they plausibly attach to; list tooling gaps.
6. **Portability attack** (1 agent): give it *only* the portable-core type definitions and
   entry signals from the draft deliverable — no d-system context, no repo access beyond that
   text. It flags every term that presupposes a backlog, a claim queue, an idea ledger, a
   session record, or any other artifact a generic repo lacks. Flagged terms move the type (or
   its signal) to the binding layer. This is the only portability test available from a
   one-repo corpus; say so in the deliverable.
7. **You**: score each Part 1 prediction (confirmed / disconfirmed / not testable — and why),
   reconcile labels across all of the above, build the final taxonomy, write the document. Keep
   the derived outputs in `_private/analysis/session-taxonomy/` — they are reusable input for
   the CLAUDE.md revamp; record that exact path in the deliverable.

## Deliverable

One untracked document; commit nothing: `docs/00-working/session-taxonomy.md` — the
evidence-tested taxonomy. Structure:

1. **Prediction scorecard** — every Part 1 prediction with its outcome and the evidence line
   that settled it. Disconfirmations lead.
2. **Portable taxonomy** — each type: name, one-line definition stated without reference to any
   d-system artifact, entry signals in generic terms (the identification logic for any repo's
   entry document), and whether it is observed / seed-confirmed / proposed. State the
   external-validity caveat honestly: the evidence is one user in one repo, so *existence* of a
   type is the portable claim; *frequency* is a local fact and stays in the binding layer. Note
   the portability-attack agent's verdicts.
3. **D-system binding, per type** — local entry signals (specific commands, phrases, skills),
   frequency with evidence counts, governance obligations that should attach (record? worktree?
   claim?), existing tooling that serves it, tooling gaps, and typical failure modes seen in
   evidence.
4. **Orchestrator variants** — the sub-classification of orchestration sessions, with boundary
   criteria between variants.
5. **Undocumented and proposed types** — what the evidence showed that the theory missed, and
   proposed-but-unobserved types with rationale.
6. **Inputs to the CLAUDE.md / AGENTS.md revamp** — a candidate "session identification"
   section: per type, the recognition rule and the protocol pointer it should route to.
   Proposals only; no edits to the governed files. Evaluate the Appendix A design notes (in the
   Part 1 prompt, `docs/00-working/PROMPT-session-taxonomy-part1-theory.md`) against the
   evidence: which ideas fit this repo (behavioral spine, lean router-style root file,
   path-scoped rules, planning-vs-execution phase split), which conflict with existing
   governance (the current CLAUDE.md's "what belongs in this file" section, the GOV-006
   import), and what the taxonomy adds that the notes lack — chiefly that this repo's routing
   dimension is *session type*, not just file path.
7. **Open questions for the owner** — batched, few, and only ones that change the design.

Also note in the deliverable that `record-structure.tsv` is ready for Part 3
(`docs/00-working/PROMPT-session-taxonomy-part3-record-templates.md`), which runs on the
owner's go after the taxonomy is accepted.

## Register the engine, not just the findings

The Stage 0/1 script and this prompt-pair's design are reusable infrastructure — the CLAUDE.md
revamp and any future usage audit will want to rerun them. Do not let the script die in a
scratchpad, and do not promote anything into governed space unilaterally:

1. Capture an idea via `tools/append_idea.py` proposing the **script** (never the derived
   outputs) be promoted to `tools/` with an OPS doc describing the derived layers, per this
   repo's pattern for sanctioned tooling. Confirm the id back to the owner.
2. In the deliverable's open-questions section, ask the owner where the engine and the two
   prompts should live permanently (tools/ + OPS doc, a prompt-pack under GOV-008, or stay in
   `docs/00-working/`). Their call, not yours.
3. Until then, the script stays in the scratchpad or alongside the derived outputs in
   `_private/analysis/session-taxonomy/`; record the location in the deliverable.

## Conduct

- Follow GOV-006 reporting style: name things then cite codes; paste the output that carries
  information; corrections stated plainly.
- If the owner voices any new want mid-session, capture it immediately via
  `tools/append_idea.py` per GOV-006.
- Ask questions via AskUserQuestion, batched, at the point the work reaches them; state
  assumptions that can wait and surface them at the end.
