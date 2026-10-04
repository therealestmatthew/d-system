# Series arc

The series follows an idea's path through the system, in the order the pipeline runs it, and ends
with the release of the IRE. Each stage is about one week at five posts a week. Sources are listed
per stage; [pillars.md](pillars.md) gives the post types that fill each week.

The pipeline itself is specified in the idea realization system architecture (`ARCH-006`): nine
stages and five owner gates. The arc groups those nine stages into posts a reader can follow, and
adds the coordination and guard work that sits around them.

## Stages

### 1. Origin

What D-System is, why the owner built it, and what the IRE will be.

- An idea realization engine: it carries an idea from capture to delivered, governed work, with the
  owner deciding at explicit gates (`README.md`, `CLAUDE.md` "Project Purpose").
- Model-agnostic in practice: Claude, OpenAI and Gemini models work in the repository (`README.md`).
- The first architecture decisions are dated 2026-09-05 (`ADR-001` file-based governance, `ADR-002`
  session backlog, `ADR-003` multi-agent concurrency).
- The history was squashed before the first push so that no confidential data from the earlier
  tree could reach the remote (`GOV-003`, "History is squashed, not filtered"; `ADR-009`).

### 2. Capture

How an idea enters the system and why the log can never be edited.

- `_data/ideas.jsonl` is an append-only event log; `tools/append_idea.py` is its only writer, and
  there is deliberately no way to supply a timestamp.
- Raw capture is stored verbatim before any interpretation runs (`ADR-007`).
- The ungoverned staging area for parked ideas (`ADR-010`), and why heavy schemas produced
  documents that existed only to satisfy the schema.
- Current state is computed by folding the events (`src/db/ideas.py`, `fold()`).

### 3. Triage and partition

How hundreds of ideas become a small number of tracks.

- One triage agent per idea writes a finding annotation and moves the idea to `triaged`
  (`.claude/agents/idea-triage.md`).
- The partition sweep (`PLAN-025`, `REQ-009`, `.claude/skills/partition-ideas/`): an analyst
  proposes groups, an adversary attacks them, the owner rules at a gate.
- The 2026-09-23 partition: 371 of 383 triaged ideas in 87 groups under 12 tracks; two independent
  runs, one of which never read the triage findings (`docs/00-working/idea-partition-2026-09-23.md`).

### 4. Planning and adversarial review

How a track becomes an approved plan, and what review finds.

- Five gates as five categories of decision, not five interruptions (`ARCH-006`).
- "A stage with no failure path is a defect" (`ARCH-006`, the nine-stage table).
- The three-altitude review procedure (`GOV-018`) and the plan standard (`GOV-010`).
- The recorded review findings: 100 findings across 12 dispositioned reviews, 18 of them blockers
  (`docs/08-governance/reviews/`).

### 5. Backlog, claims and multi-session coordination

How several agent sessions work on one repository without overwriting each other.

- The backlog as a lock table: a claim on the integration branch, `max_active`, declared systems
  (`docs/09-backlog/backlog.yaml`, `ADR-003`, `AGENTS.md`).
- Every session works in its own git worktree, and why the documentation-only exception was
  withdrawn on 2026-09-12 (`GOV-003`).
- The collisions ledger: the same document code issued twice, the same idea id allocated twice,
  and an idea-log collision that produced no git conflict at all (`GOV-003`, "Concurrency
  collisions").
- The session roles and message protocol: Session Manager, Builders, `TURN?`, `READY` (`GOV-017`).
- On 2026-09-22, 46 of 74 ready phases were blocked by one active claim because they shared its
  system (`GOV-017`).

### 6. Deterministic guards

The checks that run on every commit, and the failures that produced each one.

- The pre-commit hook: the private-content check, then the governance check; never `--no-verify`
  (`tools/git-hooks/pre-commit`).
- The private-content check, whose identifier list is derived at run time and never written to a
  tracked file (`tools/check_no_private_content.py`, `ADR-009`).
- Governance checks for catalog drift, code reservations, containment and silent status regressions
  (`src/governance/`).
- "A check that cannot fail is not a check" and the other procedures in `brain/procedures/`.

### 7. Engine pages

What the system shows about itself.

- Deterministic HTML pages generated from the repository's own records: pipeline overview, idea
  funnel and ledger, backlog and batch graph (`tools/generate_engine_pages.py`, `_public/engine/`).
- "Every number on a page names its source"; two runs on one commit give identical bytes.

### 8. The IRE

The portable form and the release.

- The `idea-realization` Claude Code plugin: agents, skills, scripts, schemas and templates that
  carry the pipeline into any git repository (`plugins/idea-realization/`).
- A test forbids repository-specific instances in the plugin, so it ships the mechanism without
  this repository's history (`test/test_no_source_references.py`).
- What is planned and not yet built: the end-to-end orchestrator (`PLAN-039`, `ADR-018`).
- The release posts are written when the owner sets the release; this arc does not fix a date.

## Later-stage formats

The first weeks use text, diagrams and written image briefs. Later posts add two formats.

### Animations and short videos

Used where the point is a sequence that a still image cannot show: an idea moving through the
stages, two sessions racing for one identifier, a check failing and blocking a commit. Candidate
posts, in arc order:

| Stage | Animation |
|---|---|
| 2 | Events appended one by one, and the folded state of one idea changing with each |
| 5 | Two sessions allocating the same idea id from logs that differ by one commit |
| 6 | A commit blocked by the pre-commit hook, the fix, and the commit passing |
| 8 | The plugin installed into an empty repository and the first idea captured |

The repository holds no earlier animation or video work to build on (no `.gif`, `.mp4`, `.webm` or
recording files are tracked), so the production method is open; [image-style.md](image-style.md)
lists the options.

### Shared reference files

People post their `CLAUDE.md` and similar files because readers can copy them. Candidates from this
repository, each shared as a sanitised copy under the confidentiality rules in
[README.md](README.md):

| File | What a reader gets | Preparation |
|---|---|---|
| `plugins/idea-realization/templates/CLAUDE.md` and `AGENTS.md` | The working agreement in its portable form | Already free of repository instances by test; read once more before posting |
| `docs/08-governance/GOV-006-conversation-guidelines.md` | How agents report to the owner | Short; examples use phase codes only |
| One `brain/procedures/` entry, e.g. `a-check-that-cannot-fail-is-not-a-check.md` | A correction written so the next model reads it | Check the incident text for anything beyond phase codes |
| One agent definition, e.g. `.claude/agents/partition-adversary.md` | A real adversarial reviewer prompt | Remove repository-specific "never touch" paths |

This repository's own `CLAUDE.md` and `AGENTS.md` describe the private portfolio boundary and a past
private-content incident; they are posted only after a line-by-line review by the owner, if at all.
