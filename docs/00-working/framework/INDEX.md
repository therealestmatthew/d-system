# Framework Documentation Index

**Status:** Initial structure complete. Templates and agent workflows defined. Ready for analysis and iteration.

---

## What's Been Created

### ✓ Directory Structure
```
docs/framework/
├── 01-overview/          (to be filled)
├── 02-workflows/         (to be filled)
├── 03-governance/        (to be filled)
├── 04-templates/         (to be filled)
├── 05-schemas/           (9 files created)
│   ├── github-issue-idea.template.md
│   ├── github-pr.template.md
│   ├── session-record.template.md
│   ├── requirement.template.md
│   ├── plan.template.md
│   └── (+ schema.json files, to be created)
├── 06-analysis/          (1 guide, 5 analysis files TBD)
│   └── agent-workflows.md (complete)
├── README.md             (complete)
└── INDEX.md              (this file)
```

### ✓ Templates Created

| File | Purpose | Status |
|---|---|---|
| `github-issue-idea.template.md` | GitHub Issue template for ideas | ✓ Complete |
| `github-pr.template.md` | PR template for phase completion | ✓ Complete |
| `session-record.template.md` | Session record format | ✓ Complete |
| `requirement.template.md` | REQ document format | ✓ Complete |
| `plan.template.md` | PLAN document format | ✓ Complete |
| `requirement.schema.json` | JSON Schema validation | ○ To create |
| `plan.schema.json` | JSON Schema validation | ○ To create |
| `phase.schema.json` | Phase definition schema | ○ To create |
| `session-record.schema.json` | Session record schema | ○ To create |

### ✓ Agent Workflow Specifications

5 complete agent workflow specifications in `06-analysis/agent-workflows.md`:

1. **Pattern Extraction Agent** — Extract generalizable patterns from d-system
2. **Governance Effectiveness Analyzer** — Analyze which governance mechanisms actually help
3. **Session Documentation Quality Analyzer** — Improve session record template
4. **Decision Capture Efficiency Analyzer** — Measure decision-making efficiency
5. **Protocol Enhancement Proposer** — Suggest improvements to close/checkpoint

Each workflow includes:
- Purpose and scope
- Detailed agent instructions (copy-paste ready)
- Analysis questions
- Output format specification
- Success criteria
- Expected deliverables

---

## Next Steps (Priority Order)

### Phase 1: Run Analysis Agents (Priority 1)

**Goal:** Extract patterns and recommendations from d-system

**Agents to run (in parallel recommended):**

1. **Pattern Extraction Agent** 
   - Read: AGENTS.md, CLAUDE.md, GOV-*.md, ADRs, session records
   - Output: `06-analysis/extracted-patterns.md`
   - Est. time: 2 hours
   - Critical for: Understanding what's generalizable vs. d-system-specific

2. **Governance Effectiveness Analyzer**
   - Read: Governance docs, incident records, validation code
   - Output: `06-analysis/governance-effectiveness-study.md`
   - Est. time: 2 hours
   - Critical for: Deciding what to keep, skip, automate

3. **Session Documentation Quality Analyzer** *(Start after #1 completes)*
   - Read: 10+ session records, current template
   - Output: `06-analysis/session-documentation-quality.md`
   - Est. time: 2 hours
   - Critical for: Improving template

4. **Decision Capture Efficiency Analyzer** *(Parallel with #3)*
   - Read: ADRs, GOV-003, session decisions
   - Output: `06-analysis/decision-capture-efficiency.md`
   - Est. time: 2 hours
   - Critical for: Streamlining decision-making

5. **Protocol Enhancement Proposer** *(Start after #3 completes)*
   - Read: Checkpoint skill, session-close command, enhancement suggestions
   - Output: `06-analysis/recommended-enhancements.md`
   - Est. time: 1-2 hours
   - Critical for: Better handoff between sessions

### Phase 2: Create JSON Schemas (Priority 2)

**Goal:** Validation schemas for requirement, plan, session record, phase

**Files to create:**
- `05-schemas/requirement.schema.json`
- `05-schemas/plan.schema.json`
- `05-schemas/phase.schema.json`
- `05-schemas/session-record.schema.json`

**Why:** 
- Validate documents before they're used
- Enable tooling (auto-complete, validation in editors)
- Ensure consistency across repos

**Est. effort:** 2-3 hours (use template.md files as reference)

### Phase 3: Write Workflow Documentation (Priority 2)

**Goal:** Create detailed, reusable workflow guides

**Files to create in `02-workflows/`:**
- `multi-developer-workflow.md` — Complete parallel workflow (from earlier document you requested)
- `planning-workflow.md` — Ideation → Requirements → Plans → Phases
- `execution-workflow.md` — Claim → Work → Integrate
- `concurrent-coordination.md` — Race handling, conflict resolution
- `agent-deployment-checklist.md` — How to deploy agents on this framework

**Source material:** Use extracted patterns + existing d-system knowledge

**Est. effort:** 3-4 hours

### Phase 4: Create Governance Reference Docs (Priority 3)

**Goal:** Generalized governance protocols (not d-system-specific)

**Files to create in `03-governance/`:**
- `governance-overview.md` — Why governance matters, principles
- `backlog-system.md` — Phase queue + claiming
- `claim-protocol.md` — How to avoid work collisions
- `worktree-protocol.md` — Why isolated checkouts matter
- `conflict-resolution.md` — Handling git conflicts, code duplication
- `session-close-protocol.md` — End-of-phase handoff

**Source material:** GOV-*.md files, AGENTS.md, analysis results

**Est. effort:** 3-4 hours

### Phase 5: Create Overview & Principles (Priority 3)

**Goal:** Philosophy and core ideas

**Files to create in `01-overview/`:**
- `framework-intro.md` — What this framework is, why it exists
- `principles.md` — Core principles (no assumptions, clear protocols, auditable decisions)
- `scalability-patterns.md` — How the model scales from 1 to 100+ developers

**Est. effort:** 2 hours

### Phase 6: Create Starter Templates (Priority 3)

**Goal:** Templates for new repos to copy

**Files to create in `04-templates/`:**
- `CLAUDE.md.template` — Project orientation template
- `README.md.template` — Quickstart template
- `backlog.yaml.template` — Initial backlog structure
- `codes-reserved.yaml.template` — Code allocation tracking
- `.claude-commands-session-start.md.template` — Automated setup
- `.claude-commands-session-close.md.template` — Automated closeout

**Est. effort:** 2-3 hours

### Phase 7: Test on New Hackathon Repo (Priority 1 after Phase 1)

**Goal:** Validate framework on real usage

**Steps:**
1. Copy templates to new hackathon repo
2. Run initial planning session (ideation → requirements → plans)
3. Create first phases
4. Have developers claim and work
5. Capture what works, what needs improvement

**Output:** Session record documenting framework usability

**Timeline:** Parallel with Phase 2-5

---

## Analysis Workflow Execution

### How to Run the Agents

```bash
# Copy these prompts and run them with Claude Code agents

# Agent 1: Pattern Extraction
# → Create new agent session
# → Paste Workflow 1 instructions from agent-workflows.md
# → Agent reads d-system docs
# → Outputs: 06-analysis/extracted-patterns.md

# Agent 2: Governance Effectiveness
# → Parallel with Agent 1
# → Outputs: 06-analysis/governance-effectiveness-study.md

# Agent 3: Session Documentation
# → Start after Agent 1
# → Outputs: 06-analysis/session-documentation-quality.md

# Agent 4: Decision Efficiency
# → Parallel with Agent 3
# → Outputs: 06-analysis/decision-capture-efficiency.md

# Agent 5: Protocol Enhancements
# → Start after Agent 3
# → Outputs: 06-analysis/recommended-enhancements.md
```

### Timeline & Parallelism

**Optimal execution (minimizes total time):**

```
Time 0:00 — Start Agents 1 + 2 (parallel, ~2 hours each)
Time 2:00 — Start Agents 3 + 4 (parallel, while 1+2 finish)
Time 4:00 — Start Agent 5 (after 3 completes)
Time 5:30 — All analysis complete
         — Review findings + prioritize improvements
         — Begin Phase 2 (schemas) in parallel with Phase 3+ (docs)
```

---

## Key Documents to Read/Reference

### For Understanding the Framework Concept
- `README.md` — Overview and philosophy
- `01-overview/principles.md` (once created) — Core ideas

### For Implementing a New Repo
- `04-templates/*.template` — Copy these files
- `02-workflows/multi-developer-workflow.md` — Follow these steps
- `03-governance/*.md` — Understand the rules

### For Extracting Patterns
- `06-analysis/agent-workflows.md` — Run these agents
- d-system `AGENTS.md`, `GOV-*.md` — Source material

### For Improving the Framework
- `06-analysis/*.md` (once complete) — Analysis results
- d-system session records — Evidence of what works

---

## Framework Principles (TL;DR)

1. **No magic** — Every rule has a reason
2. **Scalable** — Works for 1 dev, 5, 50, or 100 agents
3. **Auditable** — Decisions in git history + records, not emails
4. **Automatable** — Steps are explicit enough for agents to execute
5. **Portable** — Copy to new repo, customize 3 files, start working

---

## Estimated Timeline to Full Framework

| Phase | Effort | Timeline | Blockers |
|---|---|---|---|
| Phase 1 (Analysis agents) | 5-6 hours | Day 1 (parallel) | None |
| Phase 2 (JSON schemas) | 2-3 hours | Day 1-2 | Need Phase 1 analysis |
| Phase 3 (Workflows) | 3-4 hours | Day 2 | Need Phase 1 patterns |
| Phase 4 (Governance docs) | 3-4 hours | Day 2-3 | Need Phase 1 effectiveness study |
| Phase 5 (Overview/principles) | 2 hours | Day 3 | Need Phase 1-4 foundation |
| Phase 6 (Starter templates) | 2-3 hours | Day 3 | Need Phases 3-5 |
| **Total (if parallel)** | **~15 hours** | **3 days** | — |

**Recommended approach:**
- Day 1: Run all 5 analysis agents in parallel (5-6 hours)
- Day 2: Phases 2-4 in parallel (8-10 hours)
- Day 3: Phases 5-6 + polish (4-5 hours)
- **Total: 3 days to full framework**

---

## Success Metrics

**Status: NOT met. This document previously marked these complete; that was false.**

An independent review on 2026-09-19 found this file self-certifying eight success metrics as done
while its own file tree showed most of the structure still `(TBD)`. Four of the eight planned
sections are empty. What exists is a skeleton plus five templates and one agent-specification file —
not a framework a team could pick up and use.

- [ ] README explains the philosophy clearly
- [ ] Templates are usable by humans and agents
- [ ] Agent workflows are detailed enough to execute without clarification
- [ ] Analysis documents surface actionable improvements
- [ ] Governance docs clearly state why each rule exists
- [ ] Workflow docs can be followed step-by-step
- [ ] Framework successfully applied to new repo (hackathon)
- [ ] Session record captures lessons for next repo

The governed successor to this staging area is `PLAN-040` and `PLAN-041`, with eight phases queued
as `phase-fwt-*` and `phase-fwa-*`. Treat those as authoritative and this directory as notes.
