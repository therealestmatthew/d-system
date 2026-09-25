# Input for Gemini prompt G1: three-axis framework v3 (verbatim copy)

Copied on 2026-09-25 by the Prompt Planner session for `PROMPT-040` prompt G1. The originals are
gitignored (`_working/ideation/three-axis/v3/framework.md` and `report.md`), so a worktree cannot
see them. This file is an ungoverned staging copy (ADR-010). Do not edit it; it is a snapshot.

Paths inside the copied text such as `../v2/report.md`, `v3/stats.json` and `classification.jsonl`
point at gitignored files that are not in the repository. Treat any figure they are cited for as
given by this text; you cannot open them.

---

# Part 1: framework.md

## Knowledge-state classification framework, v3 (draft for review)

Status: draft with the owner's rulings of 2026-09-24 (§6), by Ideation. It is not governed. ARCH-005 (Idea node classification) remains
the governed vocabulary until `phase-idg-01` accepts it; §7 lists the edits ARCH-005 would need to match
this draft. Nothing here changes a tracked file.

**Sources.** Every change from ARCH-005 names its source:

- **[Gemini]**: Gemini's feedback, pasted by the owner and relayed by Session Manager on 2026-09-24.
  Because the owner forwarded it, it is treated as the owner's current direction.
- **[v2]**: Ideation's v2 classification of 452 ideas (`../v2/report.md`, `../v2/stats.json`).
- **[arch]**: `research/architecture/architecture.md` §2-§3 and §8, the page
  `_public/d-system-architecture.html` §02, and `research/architecture/transition_vocabulary.md`. The
  transition names SUPERSEDE, DEPRECATE and RETIRE are defined in the last of these (lines 112-114);
  architecture.md defines only SUPERSEDE (§4.2, line 149). Review finding R1.
- **[owner]**: an owner ruling relayed by Session Manager.

Where a proposal conflicts with another source, the conflict is stated in §6 and left for the owner.
None is resolved silently.

### 1. Scope: what gets classified

**Classification applies to knowledge records.** A record that only groups, tests or points at other
records is not a knowledge state [v2: 21 such records had no ontological value and 17 no lifecycle
value]. v3 therefore adds a **record kind**, decided first:

| Record kind | Definition | Rule | Example |
|---|---|---|---|
| `knowledge` | States, asks for, or records something about the domain | Everything else | 000442 |
| `collection` | Exists to group other records so they surface together (umbrella, anchor, batch) | Its stated purpose is to group other records: the title or the body calls it an anchor, an umbrella or a shared parent, or the body is mainly a list of other records. A record that bundles several findings of its own is not a collection (see O6) | 000050 ("Umbrella idea for...", in the body), 000385 |
| `fixture` | Test or rehearsal data with no domain content | It says it is a placeholder, test or rehearsal | 000088, 000103 |
| `reference` | A pointer to an external source kept for later, with no claim or ask of its own | Its body is essentially a link or a citation | 000282 |

Only `knowledge` records take values on O, E, L and T. The other three kinds carry no axis values and
are not outliers [v2, and recommendation D in `../report.md`]. This is a new construct that ARCH-005
does not have (conflict C5).

### 2. Axis O: Ontological (what is this record's subject?)

Decision rule: **the subject is the thing that the record's observation is about, or that its ask
would change.**

| Value | Definition | Decision rule | Example | Source |
|---|---|---|---|---|
| Concept / Mental Model | A theoretical construct, principle, paradigm or classification | The subject is an idea about how to think, not a thing that exists or runs | 000061 (the three-axis taxonomy) | ARCH-005 |
| Artifact / Entity | A concrete output or entity: a file, schema, tool, system, dataset, commit | A fix or build would change a file, a schema, code or data | 000442 (the agent manifest) | ARCH-005 |
| Process / Workflow | A sequence of steps: how something is done, who does what, in what order | A fix would change the order, the steps or the hand-offs, whatever files implement them | 000405 (the completion-edit sequence) | ARCH-005 |
| Event | A distinct occurrence in time | The occurrence itself is the subject, and nothing persistent is claimed or changed | 000076 (a question raised on 2026-09-10) | ARCH-005 |
| **Actor / Agent** | Who acts: a human role, stakeholder group or autonomous agent, with its remit and authority | The record is about who does something, with what authority or remit, rather than the file that defines it | 000062 (a pure classification agent), 000332 (a Documenter role) | [Gemini] |
| **Metric / Standard** | A quantitative measure or threshold that governs something: SLA, KPI, benchmark, budget, cap | The subject is the measure or the threshold itself | 000434 (which agent-run metrics to capture), 000008 (which metrics to derive from the idea log) | [Gemini] |

Tie-breaks:

- **O1. Artifact vs Process** (unstable in v2: 11 of the 13 O disagreements) [v2]. Ask what the fix or
  ask would edit. Editing a file's content, a schema, code or data is **Artifact**. Changing the
  steps, their order or who performs them is **Process**, even when the steps live in a file.
  - If the record names a specific file as defective, it is Artifact.
  - If it names a step that is missing or out of order, it is Process.
  - If the title names both, the subject is the thing the record's observation measures or counts.
    For example, 000442 counts files, so it is Artifact.
  - If nothing is measured, it is Process.
- **O2. Actor vs Artifact** (owner ruling C7). An agent type (`.claude/agents/*.md`) is **Actor**, and so
  is a record about its remit, its role or its definition file's content. For example, 000306 covers
  drifted agent definitions. Tooling that generates, indexes or lists agent files is **Artifact**. For
  example, 000442 covers the manifest's coverage.
- **O3. Metric vs Artifact or Process.** **Metric** applies when the number or threshold is the
  subject. When the subject is the tool that computes it or the step that checks it, use Artifact or
  Process. For example, 000071 (a command that reports metrics) is Artifact, and 000434 (which metrics
  exist) is Metric.
- **O5. Actor vs Process** (review finding R5). Ask what the fix or ask would change. Adding, removing
  or re-scoping a role, its remit or its authority is **Actor**. Changing the steps an existing role
  performs is **Process**. For example, 000332 proposes a new role, so it is Actor.
- **O6. A bundle of unrelated findings** (review finding R7). A record holding several unrelated findings
  of its own is `knowledge` with `decompose: true`. O is the value all its parts share, otherwise the
  value of the finding named first in the title. A knowledge record never has a blank O (C1). For
  example, 000286 holds three follow-ups.
- **O4. Event.** An incident that evidences a lasting defect is evidence, not the subject. Classify the
  defective thing [v2: Event fell from 46 to 1 once this rule applied].

### 3. Axis E: Epistemic (what is the truth status of what the record asserts?)

| Value | Definition | Decision rule | Example | Source |
|---|---|---|---|---|
| Axiom / Ground Truth | A claim accepted as verified within its stated scope | The record reports something observed, measured, reproduced or confirmed | 000442 (1 of 15 agent files in the manifest) | ARCH-005, wording per [arch] |
| Hypothesis / Assumption | An untested theory, prediction or premise that needs validation | The record **explicitly** asserts a belief or prediction as a claim | 000430 (model variety "would greatly benefit" planning) | ARCH-005 |
| Anti-Pattern / Falsified Concept | A disproven theory, failed approach or known dead end | The record says an approach was shown wrong or failed on its merits | 000220 (a counting method shown to bias results) | ARCH-005 |
| **Not Applicable / Agnostic** | The record asserts no verifiable truth claim | It only asks, proposes, instructs or questions, or names a thing without claiming anything about it | 000431 (a question), 000429 (a named tool to look at) | [Gemini]; replaces [owner]'s "blank" (C1) |

Tie-breaks:

- **E1. A proposal that cites a fact as motivation** (the main E disagreement in v2). Classify what the
  record **asks or asserts as its point**. If the point is the observation ("X is broken"), it is
  Axiom. If the point is the ask and the fact is background, it is N/A.

  Proxy (review finding R4): the point is what the **title** states. A title that states a defect, a
  count or a fact is Axiom. A title that is an imperative, a proposal or a question is N/A. For
  example, 000325's title proposes a fix, so it is N/A. This narrows the disagreement but does not
  remove it; §8 gives the expected residual.
- **E2. A verified symptom with a guessed cause.** Use Axiom, and name the guessed part in the reason.
  E is one value per record (see C6 for claim-level E).
- **E4. An Insight asserts its observation** (owner ruling, 2026-09-25). When L is Retrospective
  Insight, E is **Axiom**. If the observation itself is hedged ("observed, not demonstrated",
  "probably", "unconfirmed" applied to the finding itself), E is **Hypothesis**. E4 overrides E1 for
  Insights. It removes the dependence of E on how the title is phrased, which the v3 run exposed in 32
  Insights with imperative titles.
- **E3. Scope and time.** ARCH-005 says an Axiom is "immutable". A defect verified at a commit is an
  Axiom *as of* that commit, and T (§5) carries the time dependence. When the defect is later fixed,
  the record does not become Anti-Pattern: it was never falsified [arch §2.2 open issue]. See C4.

### 4. Axis L: Lifecycle (where is the record in the arc from thought to reviewed work?)

| Value | Definition | Decision rule | Example | Source |
|---|---|---|---|---|
| Generative Seed | A raw or developing idea, before commitment | A proposal or question with no owner commitment, whatever its detail | 000437 | ARCH-005 |
| Strategic Directive | A committed goal or plan that sets a direction | The owner has committed: a ruling, a promotion to a plan, or "we will" / "must" / "non-negotiable" in the owner's words | 000166 (a migration stated as non-negotiable) | ARCH-005 |
| Operational Task | One executable action with a clear done-state | A single action whose completion can be checked, with no design choice left | 000443 (add a "proposed" ADR status) | ARCH-005 |
| Retrospective Insight | A post-execution observation: a gap, technical debt, or newly realized context | It reports something found about work that already exists or already ran | 000405 | ARCH-005 |
| **Active / Evergreen** | A standing record in force outside execution: a policy, principle, master data or reference kept current | It states a rule, principle or standing structure to be followed or consulted, not something to execute once | 000435 (capture every owner decision), 000285 (a standing worktree exception) | [Gemini] |
| **Deprecated / Archived** | A record kept for audit after it was superseded, retired or withdrawn | The record's subject has been retired or superseded (L5). Set by a later event in the log, and the earlier L value stays in history | No clean example in the idea log. 000353 is a superseded *record*, which is a disposition, not this value (C2) | [Gemini] |

Tie-breaks:

- **Order of the L rules** (review finding R2b). Apply L3 before L1. A commitment worded as a standing
  rule ("every", "always", "from now on", "must" applied to all future cases) is Evergreen.
  Only then does L1's commitment test decide between Seed and Directive.
- **L1. Seed vs Directive** (unstable in v2) [v2]. Two counts describe this, and they are different
  measures (review finding R6):
  - 82 ideas that v1 called Seeds are Directives in v2. This is a v1-to-v2 comparison computed in the
    session and not stored in `stats.json`.
  - 70 v2 records carry Directive + Seed. A clear goal is not a commitment. Directive requires owner commitment evidence in the record:
  a ruling, a promotion, "we will", "must" or "non-negotiable". Otherwise the record is a Seed, however
  specific it is.

  A relayed owner imperative to produce a named deliverable ("Write the requirements, plan and
  phases", 000365) counts as commitment. An imperative to investigate or explore does not. Expect a
  residual disagreement (R4).
- **L2. Seed vs Task.** A Task has one action and a checkable done-state, with no open design choice.
  If the record lists options or questions, it is a Seed.
- **L3. Directive vs Evergreen.** A Directive is to be carried out, and then it is done. Evergreen stays
  in force indefinitely: a standing rule, a principle, or a reference kept current. "From now on, every
  X" is Evergreen, and "build X" is Directive.
- **L4. An observation with a remedy** (186 of the 202 v2 Insights) [v2]. L is Insight. Record the
  remedy as `L_remedy`, with the value `task` (one concrete fix) or `seed` (the remedy is open), so the
  record can be split at capture. This replaces v2's general "second value". `L_remedy` is a
  decomposition marker, not a second lifecycle state (conflict C3).
- **L5. Deprecated / Archived** (owner ruling, confirming Session Manager's reading in C2). Use it
  when the record's **subject** has been retired or superseded, for example a record describing a
  mechanism that has since been retired and is kept for audit. The idea record's own disposition
  (`discarded`, or superseded by another idea) is not an axis value, and a superseded or discarded
  record keeps its own L value. A record *about* something stale that is still in use (for example
  000381, stale lines in CLAUDE.md) is an Insight.

### 5. Axis T: Temporal validity (fourth axis, adopted by the owner)

Source: [arch §2.2 open issue] ("temporal validity should likely be represented separately from
epistemic status"); [v2] (65% of ideas are time-bound, including 200 of 202 Insights). Not proposed by
Gemini.

| Value | Definition | Decision rule | Example |
|---|---|---|---|
| As-of | True of a point or interval: a state at a commit, a count on a date, a condition later work changes | The record names or implies an observation time, and a later change would make it untrue without falsifying it | 000442 |
| Standing | True or relevant without a time bound | No observation time; a principle, a want or a standing rule | 000393 |

**Independence (review finding R3).** In v2, T is close to a function of L:

| L | As-of | Standing |
|---|---|---|
| Insight | 200 | 2 |
| Seed | 6 | 72 |
| Directive | 45 | 53 |
| Task | 37 | 20 |

For Insights and Seeds, T mostly restates L. It carries independent information only for Directives
and Tasks, and for any record whose truth expires (E3). T is proposed because it records a different
fact, whether a statement is valid now or was valid then. That fact is needed so that a fixed defect
can be marked no longer current without being falsified. It is not proposed because the data shows
statistical independence. **Owner ruling, 2026-09-24:** T is adopted as a full fourth axis on every knowledge record.

T records only whether the record is time-bound. The interval itself, `observed_at` and `valid_until`,
is data that a schema would need. A classifier cannot supply it (C4).

### 6. Conflicts, stated and not resolved

**Owner rulings, 2026-09-24, relayed by Session Manager (they resolve C1-C7 and L5):**

- **C1, resolved:** N/A applies to E only. A record that fits no O or L value gets a record kind (§1),
  not a blank. PLAN-029 §2's "blank with a reason" is superseded for E. For O and L, record kinds cover
  the non-knowledge records. A knowledge record has a value on every axis.
- **C2, resolved:** see below. L5 is restated to apply to the subject, as confirmed by the owner.
- **C3, resolved:** widen L in ARCH-005. Rename the axis "Lifecycle" and widen its definition to cover
  steady-state (Evergreen) and retired (Deprecated) records.
- **C4, resolved:** Axiom becomes "a claim accepted as verified within its stated scope". T carries
  when the claim held.
- **C5, resolved:** record kinds accepted (knowledge, collection, fixture, reference). Only knowledge
  records are classified on the axes.
- **C6, resolved as drafted:** E stays on the record. E on claims is left to 000454 and `phase-idg-01`.
- **C7, resolved:** agent types (`.claude/agents/*.md`) are Actor / Agent, not Artifact (O2).
- **T, resolved:** adopted as a full fourth axis on every knowledge record.
- **E4, adopted (2026-09-25):** an Insight's E is Axiom unless the insight is hedged (§3).

The original conflict statements follow, kept for the record.

- **C1. E: blank vs N/A.** On 2026-09-24 the owner ruled "leave it blank right now if none align"
  (000454, and the v2 re-run). The owner then forwarded Gemini's explicit N/A/Agnostic, with its reason
  that blanks break query logic. This draft treats **N/A as the current direction** and records the
  change. PLAN-029 §2 rules each axis *optional, with a reason for a blank*. N/A replaces the blank on
  E, but PLAN-029 §2 still governs O and L unless it is amended. **Owner decision:** does N/A supersede
  PLAN-029 §2 for E only, or for every axis, with record kinds (§1) covering the rest?
- **C2. RESOLVED: Deprecated/Archived does not duplicate `discarded` or `supersedes`.**
  Owner ruling, 2026-09-24, relayed by Session Manager, verbatim: "No, it does not duplicate. Ideas are
  discarded if we recognize they have no value to what we are trying to build and superseded if we
  propose a better or more detailed idea that explains more effectively. The epistemic classification has
  entirely to do with the truth state of a particular value. We could discard or supersede an idea and
  that is mutually exclusive to if we hold it to be true or later revise that it was not valid."

  The owner's definitions:
  - **discard**: "no value to what we are trying to build";
  - **supersede**: "we propose a better or more detailed idea that explains more effectively".

  **Ruled:** these dispositions of an idea record are independent of its epistemic value. The owner
  also noted that, because the log is append-only, a move to Deprecated/Archived is a recorded
  transition, not a mutation.

  *Session Manager's reading, not a ruling:* the same independence holds for L's Deprecated/Archived.
  It describes the lifecycle of the thing the idea is about, while discarded and superseded describe
  the idea record's disposition.

  Consequence for this draft, **pending the owner's confirmation of the SM reading**: under that reading, L5 needs restating. L5 currently makes
  Deprecated a property of the record ("the record itself says it is superseded"), which is the
  disposition the owner has placed outside the axes. Restated, Deprecated applies when the record's
  **subject** is retired or superseded, for example an idea about a retired mechanism kept for audit.
  A superseded idea record keeps its own L value. Flagged for the owner with the re-run.

- **C3. The L value set.** Adding Evergreen and Deprecated makes L a mixed axis:
  - four stages of an execution arc (ARCH-005 calls it "Execution / temporal");
  - one steady state (Evergreen);
  - one terminal state (Deprecated).

  architecture.md §2.3 describes L as "where it is in its evolution" and says the lifecycle "is not
  assumed to be strictly linear". Evergreen and Deprecated fit that description. They do not fit
  ARCH-005's "arc from raw thought to executed and reviewed work". **Owner decision:** widen L's
  definition in ARCH-005, or split out a separate "standing/retired" axis.
- **C4. T vs E's "immutable Axiom".** ARCH-005 defines Axiom as "a verified, immutable fact". Under T,
  most Axioms in this log (199 of 223 in v2) are As-of: verified at a time, and not immutable.
  **Owner decision:** reword Axiom to architecture.md's "accepted as verified within the applicable
  scope" (this draft's wording), and let T carry time.
- **C5. Record kind (§1) is new.** Neither ARCH-005 nor Gemini proposes it. It comes from v2's 21
  records with no ontological value. Gemini's N/A on E would cover their E, but not their O or L. Using
  Evergreen for references (000282) was considered and rejected: a saved link is not a policy kept in
  force. **Owner decision:** accept record kinds, or classify these records as `knowledge` with N/A or
  none values.
- **C6. Where E belongs.** v2 found E almost two-valued on idea records: 223 Axioms (observations) and
  218 asks, with only 10 Hypotheses. The claims that carry real epistemic weight sit inside ideas: a
  symptom, a guessed cause, a predicted benefit. This draft keeps E on the record, as ARCH-005 and
  Gemini do, and adds tie-break E1. Placing E on claims is a larger design change, left for 000454 and
  `phase-idg-01`.
- **C7. Actor/Agent overlaps Artifact** in this repository, because agents are files. Tie-break O2
  settles single cases. The owner may prefer Actor to cover only humans and roles, with agents staying
  Artifacts.

### 7. Edits ARCH-005 would need to match this draft (for phase-idg-01; not made)

| ARCH-005 location | Edit |
|---|---|
| Axis 1 table | Add rows **Actor / Agent** and **Metric / Standard** with §2's definitions |
| Axis 2 table | Add row **Not Applicable / Agnostic**. Reword Axiom from "a verified, immutable fact" to "a claim accepted as verified within its stated scope" (C4) |
| Axis 3 heading "Execution / temporal (the lifecycle stage)" | Rename to "Lifecycle"; widen the definition to cover steady-state and retired records (C3) |
| Axis 3 table | Add **Active / Evergreen** and **Deprecated / Archived** (subject retired or superseded; L5). It is not a record disposition (C2) |
| New section | Axis 4, **Temporal validity** (As-of, Standing) (§5), adopted |
| New section | **Record kind** (knowledge, collection, fixture, reference) (§1), accepted |
| New section | The tie-break rules O1-O6, E1-E4 and L1-L5, the L rule order, and a `decompose` marker for bundled records (O6) |
| Open questions: "Does every idea need a value on every axis?" | Replace with the answer from C1: every knowledge record has a value on all four axes; E may be N/A; non-knowledge records carry a record kind and no axis values |
| Axis 1 table, Actor / Agent row | State that agent types (`.claude/agents/*.md`) are Actor / Agent (C7) |
| **PLAN-029 §2** ("Each axis is optional, and a blank axis must carry a reason") | Amend: E is never blank (N/A / Agnostic replaces a blank); O, L and T are required on knowledge records; records that fit no O or L value carry a record kind (collection, fixture, reference) instead of a blank. The reason field stays per axis |
| Schema implication (for PLAN-029 G01) | Fields `record_kind`, `ontological`, `epistemic`, `lifecycle`, `lifecycle_remedy`, `temporal`, plus a per-axis confidence and reason if the classification agent writes them. The field names are for phase-idg-01 to choose |

### 8. Adversarial review

**Reviewer.** `partition-adversary` (read-only), 2026-09-24. It was given this file, ARCH-005,
architecture.md §2, §3 and §8, and `../v2/report.md`. It was not given Ideation's rationale. It checked
every claim against the files and the idea log. Its verdict: "not close to internally consistent enough
to promote". Every finding below is fixed or given a disposition. No finding was rejected.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| R1 | blocking | C2 attributed SUPERSEDE, DEPRECATE and RETIRE to architecture.md §3 and §8. architecture.md defines only SUPERSEDE, in §4.2 line 149 | **Fixed.** C2 was already rewritten as resolved by the owner's ruling, and that wording no longer makes this claim. The sources list now cites `transition_vocabulary.md` lines 112-114 for DEPRECATE and RETIRE. The ARCH-005 edit list no longer says "reached only by a transition" |
| R2a | blocking | 000050 fails the `collection` rule: "umbrella" is in its body, not its title | **Fixed.** The rule now tests the stated purpose, from the title or the body |
| R2b | blocking | 000435 contains "must", so L1 makes it a Directive, yet it is the Evergreen example | **Fixed.** L3 is applied before L1, and a standing-rule commitment is Evergreen. 000435 stays the Evergreen example |
| R2c | blocking | 000442's title names a defective file and a missing check, so O1's title fallback cannot decide it. It was also the wrong example for O2 | **Fixed.** O1's fallback is now the thing the observation measures (Artifact for 000442). O2's example is now 000306 |
| R2d | blocking | 000409 (a baseline guard) is Artifact or Process under O3, not Metric | **Fixed.** Replaced by 000008 |
| R3 | major | T is close to a function of L: 99% of Insights are As-of and 92% of Seeds are Standing. §5 treated this correlation as support | **Accepted.** §5 now shows the cross-tab and says T is proposed for update semantics, not for statistical independence. It also offers the owner the option of a field set only when T diverges from L |
| R4 | major | E1 and L1 are judgement calls, not mechanical rules (000325, 000365, 000275) | **Partly fixed.** E1 now uses the title as a proxy for the point. L1 counts a relayed owner imperative to produce a named deliverable as commitment. **Conceded:** residual disagreement remains, and the v3 re-run's agreement sample will measure it. v2's rates were E 89% and L 84% |
| R5 | major | No rule decided Actor vs Process (000332) | **Fixed.** Added O5 |
| R6 | minor | "82" disagreed with stats.json's 70 Directive + Seed pairs | **Clarified.** Both are right and measure different things: 82 is v1 Seed → v2 Directive moves, computed in the session, and 70 is the count of v2 pairs. L1 now states both |
| R7 | minor | A record bundling three findings (000286) fits neither `collection` nor two O values | **Fixed.** Added O6, which sets a `decompose: true` marker and O as the value its parts share |

**The reviewer's own view on direction:** "the underlying instincts (a record-kind escape valve, Actor
and Metric as real subjects in this corpus, E's redundancy with L) are [not] wrong". Its concern was
that the rules did not do what the document claimed. The fixes above target that concern. The v3
re-run's agreement sample is the test of whether they worked.

---

# Part 2: report.md

## Three-axis classification, v3 (final: framework v3, the owner's rulings, and E4)

This run classifies every idea against `framework.md`. That is the framework after Gemini's additions,
the adversarial review, the owner's rulings of 2026-09-24 (C1-C7, L5, T), and rule E4 (2026-09-25). It
supersedes v1 and v2.

**Owner ruling, 2026-09-25:** the finished framework, the edit list (§6) and `classification.jsonl` go
to `phase-idg-01` as inputs. idg-01 makes the ARCH-005, PLAN-029 §2 and schema changes. The backfill
phases append the rows. §6 is written to be used without the rest of this report.

### 1. Files and coverage

| File | What |
|---|---|
| `v3/classification.jsonl` | **The appendable output.** 454 rows, one per idea (§6.5 gives the contract) |
| `v3/framework.md` | The framework: rules §1-§5, owner rulings §6, adversarial review §8 |
| `v3/report.md` | This report. §6 is the builder's specification |
| `v3/stats.json` | Every figure here, including the agreement sample and `e4_changed` |
| `v3/merge_v3.py` | The deterministic merge, including E4. Re-running it reproduces the jsonl from `raw/` |
| `v3/instructions.md`, `v3/batches/`, `v3/raw/`, `v3/agreement-sample.jsonl`, `v3/agents.tsv`, `v3/run-meta.json` | Classifier instructions, inputs, verbatim outputs and run metadata |

Coverage: 454 ideas (000001-000454) at dev `a864603`, in nine batches. Each id was classified exactly
once, with 0 missing, 0 duplicated and 0 validation errors.

### 2. Agreement (independent classifier on the 45 ids ending in 5)

| Field | v3 | v2 | Remaining disagreements |
|---|---|---|---|
| record_kind | **45/45 (100%)** | — | none |
| E (E4 applied to both runs) | **44/45 (98%)** | 89% | 000165 (Seed vs Insight on L, which changes E under E4) |
| L_remedy | **43/45 (96%)** | 93% | 000165, 000415 (Task vs Seed) |
| T | **40/45 (89%)** | 80% | Directives and asks tied to a dated event (000115, 000235, 000365, 000445) |
| L | **39/45 (87%)** | 84% | Seed vs Task on specified components (000175, 000185, 000275); Seed vs Directive (000115); Directive vs Evergreen (000425) |
| O | **38/45 (84%)** | 71% | Artifact vs Process (000155, 000235, 000365), Concept vs Artifact (000135, 000165), Process vs Concept (000245), Artifact vs Metric (000295) |

### 3. Counts (after E4)

**Record kind:** 434 knowledge, 15 collection, 4 fixture, 1 reference.

- Collections: 000050-000052, 000054, 000056-000058, 000060, 000078, 000170, 000230, 000251, 000299,
  000347, 000385.
- Fixtures: 000088, 000090, 000102, 000103.
- Reference: 000282.

Knowledge records, by axis:

| O | n | E | n | L | n | T | n |
|---|---|---|---|---|---|---|---|
| Artifact / Entity | 278 | Not Applicable / Agnostic | 255 | Generative Seed | 198 | Standing | 255 |
| Process / Workflow | 92 | Axiom / Ground Truth | 176 | Retrospective Insight | 172 | As-of | 179 |
| Actor / Agent | 32 | Hypothesis / Assumption | 3 | Operational Task | 30 | | |
| Concept / Mental Model | 30 | Anti-Pattern / Falsified Concept | 0 | Strategic Directive | 28 | | |
| Metric / Standard | 2 | | | Active / Evergreen | 6 | | |
| Event | 0 | | | Deprecated / Archived | 0 | | |

- **E4** changed 32 rows: 31 N/A → Axiom, and 000095 N/A → Hypothesis (its race was "observed, not
  demonstrated"). Every changed row carries `"E4"` in its `rules` field.
- **L_remedy** on the 172 Insights: Seed 117, Task 55.
- **decompose** (O6) is set on 000009, 000014, 000019, 000086, 000157, 000286, 000380 and 000382.

### 4. Remaining outliers

1. **No knowledge record lacks a value.** The v3 value set covers the whole idea log.
2. **Five values are unused or nearly unused:** Event (0), Anti-Pattern (0), Deprecated / Archived (0),
   Metric / Standard (2) and Hypothesis (3).
   - For Deprecated this is expected: under L5, no idea's subject has been retired.
   - For the others, ideas are asks and observations, not incidents or claims.
   - All five will matter for other record types, such as ADRs, memories and research findings.
3. **E and T are almost functions of L.**
   - E: all 172 Insights are Axiom or Hypothesis (by E4), and 197 of the 198 Seeds are N/A.
   - T: 197 of the 198 Seeds are Standing, and 171 of the 172 Insights are As-of.
   - Independent information appears only on Directives (3 of 28 As-of) and Tasks (4 of 30).
   - The owner adopted T for update semantics (framework §5). The schema should not treat E or T as
     independent evidence alongside L.
4. **8 records need decomposing (O6).** These are the candidates for `phase-idg-05` (000065).
5. **Residual disagreement (§2):** about 13-16% on O and L. The owner may accept medium confidence here
   or have `phase-idg-02`'s agent revisit these judgements.

### 5. What changed from v2

| Axis | Same as v2 | Main moves | Cause |
|---|---|---|---|
| O | 309 of 434 | Process → Artifact 56; Artifact → Actor 24; Artifact → Process 8; Process → Actor 8 | O1's fallback; C7 (agent types are Actors) |
| E | 363 of 434 | Axiom → N/A 53; N/A → Axiom 7; Hypothesis → N/A 6 | E1: proposals that only cite a fact as motivation are N/A. E4 kept the Insights at Axiom |
| L | 277 of 434 | Directive → Seed 80; Insight → Seed 22; Task → Seed 22; Task → Directive 7 | L1 requires evidence of owner commitment, which reverses v2's rule-3 drift |
| T | 323 of 434 | — | L's changes carry through |
| none (v2) | — | 20 records became collection, fixture or reference | C5 |

---

### 6. Builder's specification for phase-idg-01 (self-contained)

#### 6.1 Inputs

- `_working/ideation/three-axis/v3/framework.md` (the full rules)
- this section
- `_working/ideation/three-axis/v3/classification.jsonl` (the rows to append)

All three are gitignored. idg-01 should copy what it needs into governed documents and should not
reference them from tracked files.

#### 6.2 The vocabulary

Exact value names, in ARCH-005's spelling, with the owner's additions.

**Record kind** (decided first; only `knowledge` records carry axis values):

| Value | Definition |
|---|---|
| knowledge | States, asks for, or records something about the domain |
| collection | Exists to group other records, stated in its title or body (anchor, umbrella, shared parent), or its body is mainly a list of other records. A record that bundles several findings of its own is `knowledge` with `decompose` set |
| fixture | Test or rehearsal data with no domain content |
| reference | A pointer to an external source kept for later, with no claim or ask of its own |

**Axis O, Ontological (what is the record's subject?).** The subject is the thing its observation is
about, or that its ask would change.

| Value | Definition |
|---|---|
| Concept / Mental Model | A theoretical construct, principle, paradigm or classification |
| Artifact / Entity | A concrete output or entity: a file, schema, tool, system, dataset, commit |
| Process / Workflow | A sequence of steps: how something is done, who does what, in what order |
| Event | A distinct occurrence in time, as the subject itself |
| Actor / Agent | Who acts: a human role, stakeholder group or autonomous agent, with its remit and authority. Agent types (`.claude/agents/*.md`) are Actor / Agent |
| Metric / Standard | A quantitative measure or threshold that governs something: SLA, KPI, benchmark, budget, cap |

**Axis E, Epistemic (truth status of what the record asserts).**

| Value | Definition |
|---|---|
| Axiom / Ground Truth | A claim accepted as verified within its stated scope |
| Hypothesis / Assumption | An untested theory, prediction or premise that needs validation |
| Anti-Pattern / Falsified Concept | A disproven theory, failed approach or known dead end |
| Not Applicable / Agnostic | The record asserts no verifiable truth claim (an ask, proposal, instruction, question, or a named thing) |

**Axis L, Lifecycle.** Where the record sits in its evolution, including steady-state and retired
records.

| Value | Definition |
|---|---|
| Generative Seed | A raw or developing idea, before owner commitment |
| Strategic Directive | A committed goal or plan that sets a direction |
| Operational Task | One executable action with a clear done-state |
| Retrospective Insight | A post-execution observation: a gap, technical debt, or newly realized context |
| Active / Evergreen | A standing record in force outside execution: a policy, principle, master data or reference kept current |
| Deprecated / Archived | The record's **subject** has been retired or superseded, and the record is kept for audit. This is not the idea record's own disposition |

`lifecycle_remedy` applies only when L is Retrospective Insight. Its value is Operational Task (one
concrete fix named) or Generative Seed (the remedy is left open).

**Axis T, Temporal validity.**

| Value | Definition |
|---|---|
| As-of | True of a point or interval; later change makes it untrue without falsifying it |
| Standing | True or relevant without a time bound |

**Dispositions are not axis values** (owner, 2026-09-24):

- **discard:** "no value to what we are trying to build";
- **supersede:** "a better or more detailed idea that explains more effectively".

Both are independent of every axis.

#### 6.3 Required values

- Every `knowledge` record has one value on O, E, L and T. E may be Not Applicable. No axis is blank.
- `collection`, `fixture` and `reference` records have no axis values.
- A reason is kept per axis.

#### 6.4 Tie-break rules

These are the rules a classifier or the `phase-idg-02` agent applies, in this order: record kind
first, and L3 before L1.

- **O1, Artifact vs Process.** Editing a file, schema, code or data is Artifact. Changing steps,
  their order or who performs them is Process. If the title names both, pick the thing the
  observation measures or counts. If nothing is measured, Process.
- **O2, Actor vs Artifact.** Agent types and their remit or definition are Actor. Tooling that
  generates, indexes or lists agent files is Artifact.
- **O3, Metric vs Artifact or Process.** Metric only when the number or threshold is the subject. The
  tool that computes it, or the step that checks it, is Artifact or Process.
- **O4, Event.** An incident that evidences a lasting defect is evidence. Classify the defective thing.
- **O5, Actor vs Process.** Adding, removing or re-scoping a role is Actor. Changing an existing
  role's steps is Process.
- **O6, a bundle of unrelated findings.** The record is `knowledge` with `decompose: true`. O is the
  shared value, otherwise the value of the first finding named in the title.
- **E1, the record's point.** Classify what the record asks or asserts as its point, using the title
  as the proxy. A defect, count or fact in the title is Axiom. An imperative, proposal or question is
  Not Applicable.
- **E2, a verified symptom with a guessed cause.** Axiom; the reason names the guessed part.
- **E3, scope and time.** An Axiom verified at a point in time stays an Axiom. T carries its time
  bound. A fixed defect was never falsified.
- **E4, an Insight asserts its observation.** If L is Retrospective Insight, E is Axiom, or Hypothesis
  when the observation itself is hedged. E4 overrides E1.
- **L3, Directive vs Evergreen (applied before L1).** A standing rule ("every", "always", "from now
  on", "must" applied to all future cases) is Evergreen. "Build X" is Directive.
- **L1, Seed vs Directive.** Directive requires evidence of owner commitment in the record: a ruling,
  a promotion, "we will", "must", "non-negotiable", or a relayed owner imperative to produce a named
  deliverable. An imperative to investigate or explore is not commitment.
- **L2, Seed vs Task.** Task is one action with a checkable done-state and no open choice. If the
  record lists options or questions, it is a Seed.
- **L4, an observation with a remedy.** L is Insight, and `lifecycle_remedy` is Task or Seed.
- **L5, Deprecated.** Only when the record's subject is retired or superseded. A record about
  something stale that is still in use is an Insight.

#### 6.5 Edits to make

**ARCH-005 (Idea node classification):**

1. **Axis 1 table.** Add Actor / Agent and Metric / Standard (§6.2), and state that agent types are
   Actor / Agent.
2. **Axis 2 table.**
   - Add Not Applicable / Agnostic.
   - Reword Axiom from "a verified, immutable fact" to "a claim accepted as verified within its stated
     scope".
3. **Axis 3.**
   - Rename the heading from "Execution / temporal (the lifecycle stage)" to "Lifecycle".
   - Widen its definition to cover steady-state and retired records.
   - Add Active / Evergreen and Deprecated / Archived, with the subject-retired meaning.
   - Add `lifecycle_remedy`.
4. **New section:** Axis 4, Temporal validity (As-of, Standing), required on every knowledge record.
5. **New section:** Record kind (knowledge, collection, fixture, reference). Only knowledge records
   carry axis values.
6. **New section:** the tie-break rules O1-O6, E1-E4 and L1-L5 with their order (§6.4), and the
   `decompose` marker.
7. **Open questions.** Replace "Does every idea need a value on every axis?" with §6.3.
8. **Dispositions.** State that discard and supersede are dispositions of the idea record,
   independent of every axis, quoting the owner's definitions (§6.2).

**PLAN-029 §2 ("Each axis is optional, and a blank axis must carry a reason"):**

9. Replace it with §6.3: E is never blank (Not Applicable replaces a blank); O, L and T are required
   on knowledge records; non-knowledge records carry a record kind instead of axis values; a reason is
   kept per axis.

**Schema.** idg-01 chooses the field names. The fields needed are:

- a record kind;
- the four axes;
- a lifecycle remedy (Insights only);
- a decompose flag;
- a confidence and a reason per axis;
- a list of the tie-break rules applied;
- provenance: who classified, and when.

#### 6.6 Backfill contract for `classification.jsonl`

Each line is one idea, with these keys:

- `idea`: the six-digit id.
- `record_kind`.
- `O`, `E`, `L`, `L_remedy`, `T`: exact §6.2 names, or null on non-knowledge rows. `L_remedy` is null
  unless L is Insight.
- `decompose`: boolean.
- `confidence`: `{O, E, L, T}`, each `high`, `medium` or `low`. null on non-knowledge rows.
- `reason`: `{O, E, L, T}`.
- `rules`: the list of tie-break ids applied, which includes `E4` where E4 changed E.
- `outlier`: always null in this run.
- `classified_at`: `2026-09-24`.
- `classified_by`: the agent type and model alias, the framework version and the merger.
- `source_eid`: the idea's latest event id at dev `a864603`.

To append:

1. For each row, compare `source_eid` with the idea's current latest eid.
   - If they differ, the idea changed after classification: re-classify it, do not append.
   - Ideas 000455 and later are not in the file.
2. Write through the sanctioned writer only, once the schema accepts the fields.

Rows are reproducible: re-running `merge_v3.py` rebuilds the file from `raw/`, including E4, which is
deterministic (`E4_HEDGED = {"000095"}`).
