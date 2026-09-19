# Agent Workflows for Framework Extraction & Analysis

This document specifies the agent workflows that extract and generalize patterns from the d-system repository, turning concrete examples into reusable framework components.

---

## Workflow 1: Pattern Extraction Agent

**Purpose:** Read d-system governance, workflows, and decision records. Extract patterns that are reusable across any multi-developer repo.

**Scope:** What to analyze
- `AGENTS.md` — Multi-agent concurrency rules
- `CLAUDE.md` — Project orientation structure
- `docs/08-governance/GOV-*.md` — Governance protocols (GOV-001, GOV-003, GOV-006)
- `docs/01-plans/PLAN-*.md` — Planning patterns
- `docs/04-decisions/ADR-*.md` — Architecture decision patterns
- `docs/03-sessions/SESS-*.md` — Session record patterns (5-10 examples)

**Agent Instructions:**

```markdown
# Extract Generalizable Patterns from d-system

Read the documents listed above. Your goal is to identify patterns that are:
1. Repeated in multiple documents (appears in 2+ places)
2. Applicable to ANY multi-developer repo (not d-system-specific)
3. Worth encoding as a best practice or principle

## What to Look For

### Concurrency Patterns
- How does d-system prevent collisions between parallel developers?
- What's the lock mechanism? (backlog.yaml claims)
- How are worktrees used? Why is isolation important?
- How are code conflicts handled? (file-based vs. git-based coordination)

### Decision Patterns
- How are big decisions made? (ADRs, GOV-003 entries)
- Who decides? (team lead, consensus, data-driven?)
- How is rationale recorded? (why is this important?)
- How long do decisions take? (are there decisions that should have been made faster?)

### Documentation Patterns
- What makes a good session record? (what fields are always captured?)
- What makes a good plan? (how detailed? how much tech detail?)
- What makes a good requirement? (observable, testable?)
- What documents are essential vs. nice-to-have?

### Workflow Patterns
- What steps are always taken before coding? (ideation, planning, approval)
- What steps always happen after coding? (testing, session record, integration)
- What's the minimal viable workflow for a hackathon? (skip what?)
- Where do people get stuck? (what procedures are confusing?)

### Coordination Patterns
- How does the team know what to work on? (backlog queue, claiming, next_up)
- How are conflicts resolved? (who decides? how is it recorded?)
- What happens when two people claim the same phase? (race handling)
- How does the team handoff between sessions? (session records, action items)

## Output Format

Create `06-analysis/extracted-patterns.md` with this structure:

### Pattern: [Name]

**Where it appears:** List 2+ documents that use this pattern  
**Concrete example:** Copy snippet from d-system  
**Generalized form:** How to apply this to any repo (repo-agnostic)  
**Why it works:** What problem does it solve? What's the benefit?  
**Tradeoff:** What cost does it have? (overhead, complexity, learning curve?)  
**When to use:** Every repo? Hackathons only? Always?  

---

## Examples to Extract

Example 1: Backlog-based claim system
- Appears in: AGENTS.md, concurrent-work-protocol (implied)
- Generalizes to: How to prevent work collision without external services

Example 2: Worktree isolation
- Appears in: AGENTS.md, GOV-003 incident reports
- Generalizes to: Why separate checkouts, how to set up safely

Example 3: Session records capturing decisions
- Appears in: SESS-*.md files, GOV-006
- Generalizes to: What to capture at end of work, what questions to ask

---

## Deliverable

File: `docs/framework/06-analysis/extracted-patterns.md`

Target: 10-15 patterns extracted, each 150-300 words.

## Notes for Agent

- **Be specific**: Use actual examples from d-system files
- **Generalize**: Remove d-system-specific details (e.g., "DuckDB" → "database", "Claude" → "agent framework")
- **Justify**: Every pattern should have a "why" — what problem does it solve?
- **Question assumptions**: If d-system does something, ask "is this always necessary, or just for this project?"
```

**Expected Output:**
- File: `06-analysis/extracted-patterns.md` 
- Length: ~4000-6000 words (10-15 patterns)
- Quality: Specific examples + generalizable principles

**Success Criteria:**
- [ ] ≥10 distinct patterns identified
- [ ] Each pattern has concrete example from d-system
- [ ] Each pattern has generalized form applicable to new repo
- [ ] Each pattern has rationale (why it matters)

---

## Workflow 2: Governance Effectiveness Analyzer

**Purpose:** Analyze which governance mechanisms in d-system actually solve problems vs. add overhead.

**Scope:** What to analyze
- `AGENTS.md` — Multi-agent rules, validation checks
- `docs/08-governance/GOV-001.md` — Documentation governance
- `docs/08-governance/GOV-003.md` — Incident records and resolutions
- `docs/08-governance/GOV-006.md` — Conversation guidelines
- `src/governance/` — Validation code (what does the validator check?)
- `docs/03-sessions/SESS-*.md` — Evidence of what worked/didn't

**Agent Instructions:**

```markdown
# Analyze Governance Effectiveness in d-system

Your goal is to determine which governance mechanisms are:
- CRITICAL: Prevent major issues; can't skip them
- IMPORTANT: Solve real problems; worth the overhead
- NICE-TO-HAVE: Improves quality but adds overhead; optional
- SKIP-FOR-HACKATHONS: Too slow/bureaucratic for short bursts

## For Each Governance Mechanism

### Identify it
- What rule/check/protocol is this?
- Where is it documented? (AGENTS.md section, GOV-NNN, code file)

### Problem it solves
- What issue was this created to prevent?
- Link to GOV-003 entry if there's an incident that caused it

### Cost / Overhead
- How much friction does it add? (time, complexity, learning curve)
- Can it be automated? (validator, CI check, script)
- Can developers forget/skip it?

### Evidence of effectiveness
- Are there incidents that prove this prevents problems?
- Do sessions mention this as helpful or frustrating?
- Has this mechanism prevented a real collision?

### Recommendation
- CRITICAL / IMPORTANT / NICE-TO-HAVE / SKIP-FOR-HACKATHONS?
- If IMPORTANT or SKIP: explain tradeoff clearly
- For new teams: mention if they should keep it

## Mechanisms to Analyze

Examples (not exhaustive):
- Phase claiming on backlog.yaml (prevents work conflicts)
- Governance validation before commit (uv run python -m src.governance)
- Worktree requirement (every session in separate checkout)
- Session records capturing decisions/action items
- Ideas log for scope management
- ADR requirement for tech decisions
- Code allocation system (preventing duplicate REQ-001, PLAN-002, etc.)

## Output Format

Create `06-analysis/governance-effectiveness-study.md` with this structure:

### Mechanism: [Name]

**Problem it solves:** 2-3 sentence description  
**Documented in:** AGENTS.md section X, GOV-003 entry Y  
**Overhead:** Time to run, learning curve, can automate?  
**Incident evidence:** GOV-003 dates when this prevented/would have prevented issues  
**Session impact:** Do session records mention this as helpful/frustrating?  
**Recommendation:** CRITICAL / IMPORTANT / NICE-TO-HAVE / SKIP-FOR-HACKATHONS  
**Rationale:** Why this classification? What's the reasoning?  

---

## Examples

Example 1: Phase claiming on backlog.yaml
- Problem: Multiple developers claiming same work
- Overhead: 2 minutes (edit + commit + push)
- Evidence: GOV-003 2026-09-06 entry (two agents claimed ADR-007)
- Recommendation: CRITICAL (enables parallelism without external service)

Example 2: Governance validation (uv run python -m src.governance)
- Problem: Invalid claims, undeclared system dependencies
- Overhead: 10 seconds per use, must run before every commit
- Evidence: Catches conflicts before they become merge nightmares
- Recommendation: IMPORTANT (automate in pre-commit hook)

Example 3: ADR requirement for all design decisions
- Problem: Decisions get re-litigated, rationale is lost
- Overhead: 30 minutes per decision record
- Evidence: Session records reference ADRs constantly
- Recommendation: IMPORTANT (but can defer until post-hackathon)
```

**Expected Output:**
- File: `06-analysis/governance-effectiveness-study.md`
- Length: ~3000-4000 words (10-15 mechanisms)
- Includes: Overhead analysis, incident evidence, recommendations

**Success Criteria:**
- [ ] ≥10 governance mechanisms analyzed
- [ ] Each has clear problem statement
- [ ] Each has overhead estimate
- [ ] Each has incident evidence or explanation
- [ ] Each has CRITICAL/IMPORTANT/SKIP recommendation

---

## Workflow 3: Session Documentation Quality Analyzer

**Purpose:** Analyze existing session records to find patterns, inefficiencies, and improvement opportunities.

**Scope:** What to analyze
- `docs/03-sessions/SESS-*.md` — All session records (read 10+ examples)
- Session record template (once created) — Compare reality to template

**Agent Instructions:**

```markdown
# Analyze Session Documentation Quality

Read 10+ session records from docs/03-sessions/. Your goal is to understand:
1. What information is ALWAYS captured (essential)
2. What information is sometimes missing (should be required)
3. What format makes session records most useful (for the next developer)
4. What inefficiencies exist (extra fields, confusing structure)
5. What improvements would help next agent (better templates, clearer format)

## For Each Session Record, Note

- **Title quality**: Is it clear what work was done?
- **Acceptance criteria**: Clearly stated? Verified? All checked?
- **Test results**: Output captured? Or just "tests pass"?
- **New requirements discovered**: Tracked as ideas? Or mentioned in prose?
- **Blockers**: Clear description of what's stuck? What's next?
- **Decisions made**: Explained? Or just mentioned?
- **Evidence files**: Listed? Do they still exist?
- **Notes quality**: Helpful for next developer? Or vague?
- **Time taken**: Estimated vs actual? Track for better planning?

## Analysis Questions

1. **What's essential**: Fields that appear in 80%+ of records?
2. **What's optional**: Fields that appear sometimes, could be omitted?
3. **What's missing**: Information that SHOULD be captured but isn't?
4. **What's confusing**: Structure that makes reading hard?
5. **What could improve efficiency**: Better format, templates, automation?

## Patterns to Look For

- Do sessions mention the same blocker repeatedly? (need better prevention)
- Are new requirements always captured? (or do they get lost?)
- Are decisions explained, or just stated? (why matters for future readers)
- Do sessions reference previous session records? (institutional memory?)
- What makes a "good" session record vs "okay" one? (quality indicators)

## Output Format

Create `06-analysis/session-documentation-quality.md` with sections:

### Session Record Analysis Summary
- Reviewed X session records
- Found Y patterns, Z inefficiencies, W improvement opportunities

### What's Working Well (Keep It)
- Field/pattern that appears consistently and is useful
- Why it's valuable (example of how it was used)

### What's Missing (Add It)
- Information that should be captured
- Where it would go in the template
- Example of why it matters

### What's Unclear (Improve It)
- Confusing field or section
- How to make it clearer
- Better wording or examples

### Recommended Template Changes
- Change 1: Move X section before Y (better flow)
- Change 2: Add new field Z (needed for handoff)
- Change 3: Make X field required (currently optional)

### Efficiency Recommendations
- Automate field X (can derive from git)
- Provide checkboxes for Y (easier than prose)
- Link to Z template (reference common sections)
```

**Expected Output:**
- File: `06-analysis/session-documentation-quality.md`
- Length: ~2000-3000 words
- Includes: Analysis, patterns, template improvement recommendations

**Success Criteria:**
- [ ] 10+ session records analyzed
- [ ] 3+ patterns identified (recurring issues/decisions)
- [ ] 3+ template improvements proposed
- [ ] Clear rationale for each recommendation

---

## Workflow 4: Decision Capture Efficiency Analyzer

**Purpose:** Measure how efficiently decisions are being made and recorded.

**Scope:** What to analyze
- `docs/04-decisions/ADR-*.md` — Architecture decision records
- `docs/08-governance/GOV-003.md` — Backlog decisions with incidents
- `docs/03-sessions/SESS-*.md` — Decisions mentioned in sessions

**Agent Instructions:**

```markdown
# Analyze Decision Capture Efficiency

Your goal is to understand:
1. How quickly are decisions made? (latency from problem → decision)
2. Are decision makers the right people? (authority, expertise)
3. Is the rationale clear? (can someone understand WHY months later?)
4. Are decisions reversible? (can we undo if wrong?)
5. What slows down decision-making?

## For Each Decision, Measure

- **Latency**: When was decision needed? When was it made? Gap = latency
- **Visibility**: Who knew about it before it was finalized?
- **Authority**: Who decided? Right person for this decision?
- **Reversibility**: Could this be undone? At what cost?
- **Record quality**: Would someone understand the rationale 6 months later?

## Decision Categories

Categorize each decision:
- **Technology**: Framework choice, library selection, architecture
- **Process**: How we work, governance rules, protocols
- **Scope**: What's in MVP, what's deferred, what's out
- **Design**: System design, API contract, data model

## Questions to Answer

1. **Which category has highest latency?** (needs faster decision process)
2. **Are process decisions documented well?** (or buried in emails/Slack?)
3. **Have any decisions been reversed?** (why? indicates unclear rationale)
4. **What decisions should have been made sooner?** (what slowed them?)
5. **Are there undocumented decisions?** (people are doing things not written down)

## Output Format

Create `06-analysis/decision-capture-efficiency.md`:

### Decision Efficiency Summary
- Analyzed X decisions
- Average latency: Y days (too slow? just right?)
- Record quality: Z% have clear rationale

### By Decision Category

#### Technology Decisions
- Average latency: X days
- Record quality: Y% have clear rationale
- Recommendation: (improve timing, clarity, authority?)

#### Process Decisions
- Average latency: X days
- Common issue: (decisions not documented? reversed?)
- Recommendation: (improve communication, recording, governance?)

### Specific Inefficiencies Found
- Decision A took too long because: (blocked on resource, unclear authority, etc.)
- Decision B wasn't documented, causing: (confusion, re-litigated later)
- Decision C was reversed because: (new info, better option found)

### Recommendations for Improvement
- Recommendation 1: How to make tech decisions faster (e.g., better design docs upfront)
- Recommendation 2: How to document process decisions immediately (e.g., record in meeting notes)
- Recommendation 3: How to clarify decision authority (e.g., clear decision-maker roles)
```

**Expected Output:**
- File: `06-analysis/decision-capture-efficiency.md`
- Length: ~2000 words
- Includes: Efficiency metrics, category analysis, improvement recommendations

**Success Criteria:**
- [ ] 10+ decisions analyzed
- [ ] Latency measured for each category
- [ ] 3-5 efficiency problems identified
- [ ] Actionable recommendations proposed

---

## Workflow 5: Protocol Enhancement Proposer

**Purpose:** Propose improvements to session close/checkpoint protocols based on actual usage patterns.

**Scope:** What to analyze
- `.claude/skills/checkpoint/SKILL.md` (if exists) — Checkpoint skill definition
- `.claude/commands/session-close.md` (if exists) — Session close command
- `docs/08-governance/GOV-003.md` — Decisions about session closing
- `docs/03-sessions/SESS-*.md` — Evidence of what works/doesn't

**Agent Instructions:**

```markdown
# Propose Session Close/Checkpoint Protocol Enhancements

Your goal is to make the session close and checkpoint processes:
1. More efficient (less manual work)
2. Clearer (agents understand what to do)
3. More complete (nothing gets forgotten)
4. More automatable (fewer manual steps)

## Questions to Answer

1. **Is the checkpoint/close process clear?** 
   - Can an agent follow it without asking for help?
   - Are the steps in the right order?

2. **Are all required artifacts captured?**
   - Nothing important gets forgotten?
   - Nothing extraneous is recorded?

3. **Is there redundancy?**
   - Are there overlapping steps?
   - Could some steps be combined?

4. **What could be automated?**
   - Collect test output automatically?
   - Track time automatically?
   - Validate files exist automatically?

5. **What confuses agents?**
   - Session records mention confusion about X?
   - Agents ask questions about Y?
   - Handoff notes mention "remember to do Z"?

## Analysis Format

For checkpoint skill:
- Current steps: List what checkpoint does today
- Problems: What could improve?
- Proposed changes: Specific recommendations
- Impact: What improves? Any new risks?

For session-close command:
- Current workflow: What's the procedure?
- Friction points: Where do agents get stuck?
- Proposed changes: Better order? New sub-steps? Removed steps?
- Owner authority: Should this stay owner-only? Why/why not?

## Output Format

Create `06-analysis/recommended-enhancements.md`:

### Session Close Efficiency

**Current Process:**
1. Run verification commands
2. Capture output
3. Write session record
4. Release _tmpagent/ claims
5. Update backlog.yaml
6. Commit and push
7. Open PR
8. Message team lead

**Problems Identified:**
- Step 3 is time-consuming (good format is unclear)
- Step 4 is error-prone (agents forget claims)
- No check that acceptance criteria are actually met
- No verification that files in completion_evidence actually exist

**Recommendations:**
- Recommendation 1: Provide session record template with required fields → 20% faster
- Recommendation 2: Add script to release all claims automatically → eliminates forgetting
- Recommendation 3: Add validation that completion_evidence files exist → catches errors early

### Checkpoint Skill Enhancements

**Current Capability:**
- Runs verification commands
- Captures output
- Writes session record (not complete)
- Never marks complete (intentional)

**Improvement Proposals:**
- Proposal 1: Auto-collect test output and coverage reports (more complete)
- Proposal 2: Timestamp session record creation (track actual session duration)
- Proposal 3: Provide checklist view (easier to follow than prose)

### Authority & Governance

**Current rule:** Only team lead can invoke `/session-close`  
**Proposal:** Should this stay owner-only? → YES, because (rationale)  
**Alternative:** Allow coordinator role → (pros/cons)
```

**Expected Output:**
- File: `06-analysis/recommended-enhancements.md`
- Length: ~2000-2500 words
- Includes: Efficiency analysis, specific proposals, implementation effort estimates

**Success Criteria:**
- [ ] Checkpoint skill analyzed thoroughly
- [ ] Session-close command analyzed thoroughly
- [ ] 5-10 concrete enhancement proposals
- [ ] Each proposal includes problem, solution, impact
- [ ] Effort estimates for each enhancement

---

## Running These Workflows

### Sequential vs. Parallel

These workflows are **independent**. Run them in parallel if possible:
- Workflow 1 (patterns) and Workflow 2 (governance) can run together
- Workflow 3 (session quality) and Workflow 4 (decisions) can run together
- Workflow 5 (enhancements) depends on input from 3, so run after 3 completes

### Timeline

- **Parallel 1+2:** 2-3 hours (pattern + governance analysis)
- **Parallel 3+4:** 2-3 hours (session quality + decision efficiency)
- **Sequential 5:** 1-2 hours (enhancements, after 3)
- **Total:** 3-5 hours for full analysis suite

### Output Organization

All outputs go in `docs/framework/06-analysis/`:
- `extracted-patterns.md` (from Workflow 1)
- `governance-effectiveness-study.md` (from Workflow 2)
- `session-documentation-quality.md` (from Workflow 3)
- `decision-capture-efficiency.md` (from Workflow 4)
- `recommended-enhancements.md` (from Workflow 5)

### Next Steps After Analysis

1. **Review findings** — Team lead reads all 5 analysis documents
2. **Prioritize** — Which improvements are most valuable?
3. **Implement** — Create new templates, update governance docs, update protocols
4. **Test** — Try framework on new repo, iterate based on real usage
5. **Document** — Finalize framework, add examples from new repo

