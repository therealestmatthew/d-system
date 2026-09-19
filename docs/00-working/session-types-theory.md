# Session types — a theoretical model with falsifiable predictions

Working document. Ungoverned staging under [ADR-010](../04-decisions/ADR-010-idea-staging.md); no
code, no front matter, no policy. Produced by `phase-tax-01` under the session-taxonomy
investigation plan (`PLAN-042`), against the observable requirements in `REQ-026` R01–R02.

**This document was written before any evidence was examined.** It reads no raw transcript and no
session-record contents. Its purpose is to be *wrong in specific, checkable ways* so that the
empirical phase (`phase-tax-02`) is a test rather than a description. Every type below carries an
observation that would count against it.

---

## 1. What the model has to do

Six consumers, each of which constrains the shape:

| Consumer | What it needs from a type |
|---|---|
| Tooling design | An entry signal specific enough to trigger a skill or command |
| Governance and records | An obligation profile — record, claim, worktree, gate — that differs between types |
| Descriptive understanding | A frequency prediction that can be wrong in both directions |
| Orchestration design | Boundary criteria separating orchestrator variants from each other and from the work |
| CLAUDE.md / AGENTS.md revamp | Identification logic: "a session that looks like X follows protocol Y" |
| A portable model | A definition stated without naming any local artifact |

The last one is the binding constraint. A type whose definition needs the word `backlog.yaml` is not
a portable type; it is a local *binding* of some portable type. The document keeps those two layers
physically separate: §4 defines the portable core, §5 binds each type to this repository.

### The discipline this document holds itself to

Predictions are bound to observables **intrinsic to a session** — the first user message, the paths
written, whether sub-agents were spawned, what survives the session. They are deliberately *not*
tuned to what any particular measurement pipeline can extract, because the Part 2 design has not
been read and must not be inferred. A prediction that turns out to be un-measurable is a real cost
and should be scored as "not testable", not quietly reinterpreted.

---

## 2. The dimensions that generate the types

Types are not enumerated from intuition. They fall out of six dimensions; a type is a region of this
space that has its own obligation profile *and* its own done-condition.

**D1 — Object of work.** What the session acts on. Five layers, ordered by how far they sit from the
product: the world outside the repository → the *intent* layer (what should be built) → the
*artifact* layer (what is built) → the *capability* layer (what the agent can do) → the *governing*
layer (the rules all work obeys). A sixth object sits orthogonal: the repository's own history.

**D2 — Commitment posture.** Does the output bind future sessions? *Non-binding* (an answer, a
parked note), *binding on acceptance* (a proposal awaiting a gate), *binding immediately* (merged
code, an active rule).

**D3 — Read/write posture.** Read-only, append-only, or mutating — and, when mutating, which
top-level directories.

**D4 — Delegation structure.** Solo; *fan-out* (one wave of sub-agents whose results the session
merges into its own context); or *coordinated* (a driver that dispatches many units serially and
deliberately holds almost none of their content).

**D5 — Convergence criterion.** How the session knows it is finished. *Externally specified* (a
done-condition existed before the session opened), *internally derived* (the session must construct
its own), or *open-ended* (finished when the human says so).

**D6 — Governance weight.** The obligations that attach: a durable record, a claim against
concurrent peers, an isolated workspace, a human gate before the output binds.

D5 is the dimension most often missed, and it does the most work below. Two sessions can write the
same files for the same reason and still be different types because one consumed a done-condition
and the other had to invent one. That difference predicts everything about how they go wrong.

---

## 3. Three families

The families are not decoration; each carries a single governance claim, which is the model's most
useful output for the CLAUDE.md revamp.

- **Family A — Non-committing.** Nothing in the repository is bound by the output. *Claim: needs no
  lock, no isolated workspace, and no durable record.*
- **Family B — Committing.** The output binds, immediately or on acceptance. *Claim: needs all
  three, plus a human gate proportional to reversibility.*
- **Family C — Second-order.** Work about work: driving it, checking it, or learning from it. *Claim:
  obligations are inherited from what it acts on, not from what it writes — which is why a single
  blanket rule misfits this family badly.*

---

## 4. The portable core — thirteen types

Each type carries: definition, generic entry signals, provenance (seed-derived / inferred from the
tooling surface / proposed-novel), and the five required prediction elements. Frequency bands are
defined numerically so that a surprise is scoreable in both directions:

| Band | Share of sessions |
|---|---|
| rare | under 3% |
| occasional | 3–12% |
| common | 12–30% |
| dominant | over 30% |

"Sessions" means transcripts, not records. The distinction matters and §6 makes a prediction out of
it.

---

### Family A — Non-committing

#### A1 — Inquiry
*Seed-derived ("one-off questions").*

**Definition.** The human wants to know something. The repository is a subject to be read, not an
object to be changed. Finishes when the question is answered.

**Entry signals (generic).** An interrogative opening: what / why / how / where is. No imperative
verb of change. Frequently a proper noun the human cannot resolve themselves.

1. **First-prompt signature.** A question, usually one sentence, with no deliverable named and no
   success condition stated. Often about an external fact (a library, a version, a product) or about
   the repository's own state ("what does X do", "why is Y failing").
2. **Activity signature.** Read-only. Search and read tools dominate; zero writes to tracked paths.
   No delegation, or at most a single read-only fan-out when the search space is wide. Short — the
   tool count should be low relative to every Family B type.
3. **Artifact.** Nothing on disk. The output is the reply.
4. **Disconfirming observation.** An Inquiry session that ends with a tracked-file write. If a large
   share of question-opened sessions mutate the repository, then "inquiry" is not a type but a
   *prelude* — the opening move of Construction or Repair — and should be modelled as a phase of
   those types instead.
5. **Frequency.** Common (12–30%).

**Subtypes worth distinguishing if evidence supports it:** *external* (the answer is outside the
repository), *explanatory* (the answer is in the repository), *diagnostic* (why did this fail) —
diagnostic is the one most likely to violate the disconfirmer, and if it does, it belongs to Repair.

---

#### A2 — Capture
*Seed-derived ("idea capture sessions").*

**Definition.** A thought is stored so it survives, and **deliberately not acted on**. The refusal to
act is the definition, not an accident of scope.

**Entry signals (generic).** A declarative want with no request to execute it: "note that…", "for
later", "don't do this now, just record it". Often several unrelated wants in one message.

1. **First-prompt signature.** Imperative to record rather than to build. Frequently plural and
   unrelated — capture batches cluster where planning does not.
2. **Activity signature.** Append-only, to exactly one store. One tool family, very few calls, no
   reads of the product surface. No delegation. The shortest sessions in the corpus.
3. **Artifact.** One or more appended records with identifiers, reported back.
4. **Disconfirming observation.** A capture session that also reads or writes anything the captured
   thought concerns. If capture consistently drags in orientation — reading the plan the idea
   relates to, checking whether it duplicates an existing one — then it is not a non-committing type
   and its obligation profile is wrong.
5. **Frequency.** Occasional (3–12%) as a *standalone* session; near-dominant as a *segment* inside
   other types. This split is itself the prediction: capture is common behaviour and an uncommon
   session.

---

#### A3 — Exploration
*Inferred from the tooling surface (`demo-skill-brainstorm`, `demo-cmd-rubber-duck`,
`demo-cmd-second-opinion`) and named by `REQ-023` as "brainstorming".*

**Definition.** An undecided question is shaped without being closed. Output is better-formed
thinking, not a commitment. Finishes when the human says it has gone far enough — the only type
whose convergence is genuinely open-ended (D5).

**Entry signals (generic).** "What are our options", "I'm not sure whether", "push back on this",
"help me think about". The absence of a named deliverable is the strongest signal.

1. **First-prompt signature.** A question with no single right answer, or an explicit request for
   options, objections or a second view. Long, discursive openings; the human supplies context
   rather than asking for it.
2. **Activity signature.** Read-heavy, write-nothing-governed. Many conversational turns relative to
   tool calls — the inverse of every Family B type. Delegation, when present, is adversarial
   (a reviewer or an objector), not productive.
3. **Artifact.** Usually nothing, or a note in ungoverned staging, or ideas appended at the end. Never
   a governed document written from inside the session.
4. **Disconfirming observation.** An exploration session that writes a requirement, plan or decision
   record. If that is common, then exploration does not exist as a separate type here — it is the
   opening phase of Specification, and `REQ-023` R2's "must never" is describing an aspiration rather
   than a practice.
5. **Frequency.** Occasional (3–12%). Predicted *lower* than intuition suggests, because exploration
   tends to be absorbed into the front of a specification session rather than run on its own.

---

### Family B — Committing

#### B1 — Specification
*Seed-derived ("planning sessions").*

**Definition.** The work ahead is made explicit: what will be built, in what order, and how anyone
will know it is done. Produces no product artifact. Binding on acceptance.

**Entry signals (generic).** "Plan", "spec out", "what would it take to", "write this up before we
build it". A named future capability plus an explicit or implicit "not yet".

1. **First-prompt signature.** Names a capability that does not exist and asks for its
   specification, sequencing, or decomposition. Usually carries scope words — "the whole", "all of",
   "everything under".
2. **Activity signature.** Mutating, confined to documentation and work-item paths; zero writes to
   product source. Heavy reads across existing specifications. Fan-out delegation is plausible (one
   wave of researchers or adversarial reviewers) but not coordination.
3. **Artifact.** One or more specification documents plus enumerated work items, each with a
   done-condition.
4. **Disconfirming observation.** A specification session that writes product source. Also
   disconfirming in the other direction: a specification session that produces documents carrying no
   enumerated work items with done-conditions — that would be Exploration wearing a document's
   clothes, and would mean the type's artifact prediction is describing a template, not a practice.
5. **Frequency.** Common (12–30%).

---

#### B2 — Adjudication
*Inferred from the tooling and governance surface — a distinct decision-record document kind exists,
and a standing decisions ledger is maintained separately from plans.*

**Definition.** An open choice is closed and the reason is made durable. The output *removes*
options; that is what separates it from Specification, which *adds* work.

**Entry signals (generic).** "Should we X or Y", "decide", "rule on", "settle", "we keep going back
and forth on". Two or more named alternatives already on the table.

1. **First-prompt signature.** Presents alternatives, or asks for a ruling on a question raised
   earlier. Frequently opens by referencing a prior session's unresolved item.
2. **Activity signature.** Read-heavy on prior decisions and constraints; a small, concentrated
   write. Delegation, when present, is adversarial — the argument against the leading option.
   Distinctly *fewer files touched* than Specification for a comparable session length.
3. **Artifact.** A decision record, or an entry appended to a decisions ledger, naming the chosen
   option, the rejected alternatives, and the reason.
4. **Disconfirming observation.** Every session that produces a decision record also produces a plan
   or requirement in the same session. If that holds, adjudication is a *section* of specification,
   not a type, and its separate obligation profile is unjustified.
5. **Frequency.** Occasional (3–12%).

---

#### B3 — Construction
*Seed-derived ("direct coding sessions").*

**Definition.** A specified unit of work is built and verified. The defining feature is D5: the
done-condition **existed before the session opened**. Construction consumes a specification; it does
not derive one.

**Entry signals (generic).** A work-item identifier, or "implement", "build", "execute" plus a
reference to something already written down.

1. **First-prompt signature.** Names a pre-existing unit of work by identifier, or points at a
   specification and says to build it. Rarely explains *why* — the why is in the document.
2. **Activity signature.** Mutating, in product source, tests and data paths. Edit and write tools
   dominate. Test-execution commands appear and are expected to appear *more than once* — the
   build-verify loop is the signature. Solo or a single fan-out wave of creators and validators.
3. **Artifact.** Product code and tests, a durable record of the session, and captured verification
   output.
4. **Disconfirming observation.** A construction session whose verification commands run exactly
   once and pass. That pattern means the loop never closed — the work was either trivial or the
   verification was performed for the record rather than for information — and it would undercut the
   claim that an externally-specified done-condition is what distinguishes this type.
5. **Frequency.** Dominant (over 30%) among sessions that carry a durable record; common (12–30%)
   across all sessions.

---

#### B4 — Repair
*Inferred from the tooling surface — a work track exists whose scope is explicitly named as defects,
distinct from the track that built the same product's features.*

**Definition.** Something that used to work, or was supposed to, does not. The session must
**derive its own done-condition** from the symptom. That is the whole difference from Construction,
and it is a difference in D5, not in D1.

**Entry signals (generic).** A symptom: an error message, a screenshot, "this is broken", "it stopped
doing X". No identifier, no specification, and frequently no reproduction steps.

1. **First-prompt signature.** Describes an observed wrong behaviour rather than a desired one. Often
   pasted output. The success condition is implicit — "make it stop" — and the session has to make it
   explicit before it can finish.
2. **Activity signature.** A read/execute-heavy opening (reproduce, locate) followed by a narrow
   mutation. The ratio of *reads before first write* is predicted to be markedly higher than in
   Construction — that ratio is the type's clearest quantitative fingerprint.
3. **Artifact.** A narrow diff, usually with a regression test, and often a captured note about the
   cause.
4. **Disconfirming observation.** Repair sessions that open with a work-item identifier and a
   pre-written verification list. If defects are consistently specified before being fixed, repair is
   not a separate type in this repository — it is Construction applied to a defect-shaped
   specification, and the D5 distinction collapses.
5. **Frequency.** Common (12–30%).

---

#### B5 — Capability
*Inferred from the tooling surface — a governance document exists that audits every agent-facing
file as a population in its own right.*

**Definition.** The object of work is what the agent itself can do: skills, commands, sub-agent
definitions, prompts. Distinguished from Construction by consumer, not by activity — the artifact is
consumed by an agent, not by a user of the product.

**Entry signals (generic).** "Make this a skill", "add a command for", "write an agent that", "this
keeps happening, automate it". Very often follows a manual sequence the human just performed.

1. **First-prompt signature.** Asks for a reusable affordance, and typically cites repetition as the
   reason. The strongest tell is a backward reference — "the thing we just did" — rather than a
   forward specification.
2. **Activity signature.** Mutating, confined to agent-configuration paths. Reads of existing
   definitions for format conformance dominate over reads of product source. Verification is weak or
   absent, because the artifact's correctness is only observable when a later session runs it.
3. **Artifact.** A new or amended agent-facing definition.
4. **Disconfirming observation.** Capability sessions that follow the full specify-then-build arc
   with a pre-written verification list, identically to Construction. If so, "capability" is a path
   predicate on Construction rather than a type, and its weak-verification prediction is simply false.
   The reverse also disconfirms: if capability work never appears as a session's *primary* purpose
   and is always a tail segment of another type, it is not a type either.
5. **Frequency.** Occasional (3–12%).

---

#### B6 — Governance
*Inferred from the governance surface — a numbered governance series exists, and the two top-level
instruction files carry an explicit, incident-justified rule reserving their edits to the owner.*

**Definition.** The rules that bind all future sessions change. Highest commitment posture in the
model: the output is binding immediately and is read by every subsequent session before it does
anything.

**Entry signals (generic).** "Add a rule", "this should be policy", "update the working agreement",
"from now on". The phrase "from now on" is close to a perfect entry signal — it is a request to bind
the future.

1. **First-prompt signature.** Proposes a standing rule, usually generalising from a single recent
   event. The generalisation is the tell, and it is also the failure mode: the distance between "do
   this once" and "do this always" is exactly where governance sessions go wrong.
2. **Activity signature.** Small mutations to instruction and governance paths, preceded by
   disproportionately heavy reading — the rule has to be checked against every rule it might
   contradict. Expected to show the highest *reads-per-line-written* ratio of any type.
3. **Artifact.** An amended or new governing document, and a durable record of why.
4. **Disconfirming observation.** A governance change that lands inside a diff whose stated purpose
   was something else. That is not merely a rule violation; it disconfirms the *type*, because it
   shows governance behaves as an opportunistic side-effect rather than a session with its own
   entry signal — which would mean the identification logic cannot key on the first prompt at all.
5. **Frequency.** Rare (under 3%).

---

### Family C — Second-order

#### C1 — Orchestration
*Seed-derived ("orchestrator sessions, possibly several kinds").*

**Definition.** A session that drives many units of work to completion through dispatched agents
while **deliberately holding almost none of their content**. The context posture is the definition.
An orchestrator that reads the work it dispatches is not orchestrating; it is doing the work with
extra steps.

**Entry signals (generic).** A plural target plus an instruction to run rather than to decide: "work
through all of", "run the next N", "dispatch these", "keep going until".

1. **First-prompt signature.** Names a set, a batch, or a queue — never a single unit — and either
   names or implies a stopping condition. Frequently pre-authorises a class of decision in advance,
   because stopping to ask per unit would defeat the design.
2. **Activity signature.** Delegation-dominant: sub-agent spawns are the highest-frequency tool
   family, and the orchestrator's own reads and writes are sparse and structural (queue state,
   integration, gates). The signature is a *low ratio of direct file edits to sub-agent dispatches*,
   sustained over a long session. Long wall-clock, low own-context growth.
3. **Artifact.** The union of its units' artifacts, plus queue-state transitions and integration
   commits it makes itself.
4. **Disconfirming observation.** An orchestration session whose own direct edits to work-product
   files exceed its dispatches. That means the context-offloading claim is false and the "type" is
   just a long Construction session that happened to use sub-agents.
5. **Frequency.** Rare to occasional (under 3% rising toward 3–12%) — *predicted to be rising over
   time*, which is a second, separately scoreable claim: orchestration should be near-absent early in
   the corpus and concentrated late.

**Variants, with boundary criteria.** The owner's seed list names two. The model proposes that the
correct discriminator is **what the orchestrator is allowed to close**, not what domain it works in:

| Variant | Units dispatched | What the orchestrator may close | Boundary test |
|---|---|---|---|
| **C1a — Execution orchestrator** | Pre-specified units of work with existing done-conditions | Individual units, under a gate | Every unit existed before the session opened |
| **C1b — Generative orchestrator** | Units it creates as it goes (triage, classification, partitioning) | Nothing — it only stages proposals | The set of units is not known at session start |
| **C1c — Pipeline orchestrator** | Stages of a single campaign, each consuming the last one's output | Stage boundaries only | Units are sequentially dependent, not parallel |

The owner's "ideation/triage/partitioning" orchestrator is C1b. The distinguishing prediction is that
**C1b never closes anything** — its outputs are proposals awaiting a human gate — whereas C1a's whole
point is closing units. If the evidence shows a triage orchestrator marking work complete, the
variant boundary is drawn in the wrong place and should be redrawn on domain after all.

---

#### C2 — Investigation
*Inferred from the governance surface — a research protocol exists as a governed document, an audit
of the full agent surface exists as another, and the work-item tracks include both a literature
review line and a standalone-explorations line.*

**Definition.** A question is answered by systematic evidence-gathering, and finishes when a
**declared scope has been covered** — not when the answer feels sufficient. Coverage-of-scope is the
convergence criterion and is what separates Investigation from Inquiry.

**Entry signals (generic).** "Audit", "review every", "survey", "investigate", "check whether X holds
across". A population word — every, all, each — is close to definitional.

1. **First-prompt signature.** Names a population or a scope and asks for a verdict across it, rather
   than asking one question. Frequently supplies a method or a frozen prompt to execute.
2. **Activity signature.** Read-dominant with one concentrated write at the end. Fan-out delegation is
   expected and is *read-only* — investigators, extractors, checkers that produce findings rather than
   changes. Long read phase, single-artifact write phase; the write is late and large.
3. **Artifact.** A findings document, frequently with a table that has one row per member of the
   population.
4. **Disconfirming observation.** An investigation that changes what it investigates in the same
   session. If audits routinely fix what they find, then investigation is not second-order — it is the
   opening phase of Repair, and its separate no-mutation obligation profile is wrong.
5. **Frequency.** Occasional (3–12%).

**Subtypes:** *audit* (population is enumerable inside the repository; every member gets a verdict),
*research* (population is external literature), *theory* (population is the space of possible models —
the session producing this document is one). The subtypes share a convergence criterion and differ
only in where the population lives, which is why they are one type.

---

#### C3 — Retrospective
*Inferred from the tooling surface — a skill exists for recording a mistake or near-miss where it
will be found again, routing it to a collisions ledger, a durable procedure note, or a record.*

**Definition.** The object is the repository's own history: what happened, and what should change
because of it. Distinguished from Investigation by object — Investigation examines the artifact or
the world; Retrospective examines *the process that produced them*.

**Entry signals (generic).** "That went wrong", "why did we end up doing that twice", "what should
we change so this doesn't recur", "log this".

1. **First-prompt signature.** References a past session or a past failure and asks what to change.
   Backward-looking with a forward ask — the compound is the signal.
2. **Activity signature.** Reads of records and history; a small append to a durable lessons store.
   Minimal tool variety. No product reads at all.
3. **Artifact.** An appended incident or procedure entry, and sometimes a proposed governance change
   — which, if made, changes the session's type to Governance from that point (see §7).
4. **Disconfirming observation.** No session's *primary* purpose is examining past sessions. If
   retrospection only ever appears as a closing paragraph inside another type, it is a section, not a
   session type, and the corresponding tooling should be a skill invoked from within other types
   rather than an entry point of its own.
5. **Frequency.** Rare (under 3%). This is the model's least confident prediction and the one most
   likely to be disconfirmed by absence.

---

#### C4 — Rehearsal
*Proposed-novel. Nothing in the tooling surface names it as a session type, though a runbook and
rehearsal work items exist.*

**Definition.** The system is **executed as a user would execute it**, to discover whether it works —
not to change it. The session's value is the list of things that stalled. Read-only on the
repository, read-write on the running system.

**Entry signals (generic).** "Walk through", "run it end to end", "pretend you're the user", "does
this actually work", a rehearsal or demo date mentioned.

1. **First-prompt signature.** Asks for an end-to-end run of something already built, usually under a
   named scenario or audience. Names no file.
2. **Activity signature.** Execution-dominant: process launches, navigation, screenshots. Almost no
   edits; reads confined to runbooks and entry points. Uniquely among all thirteen types, the tool mix
   is dominated by *driving the system* rather than by reading or writing it.
3. **Artifact.** A defect list, a corrected runbook, or nothing but a verbal verdict.
4. **Disconfirming observation.** Rehearsal never appears as a session's primary purpose — always as
   a closing segment of a construction session that built the thing being rehearsed. That would make
   it a phase, not a type. This is the most likely outcome and the type is proposed anyway, because
   its *absence* is itself a finding: a system whose end-to-end behaviour is only ever checked by the
   person who just built it has no independent verification step.
5. **Frequency.** Rare (under 3%).

---

## 5. The d-system binding

How each portable type manifests here. Nothing in this section belongs in the portable layer.

| Type | Opens with (local) | Writes (local) | Governance obligations today |
|---|---|---|---|
| A1 Inquiry | Bare question; `/demo-cmd-explain-this`, `/demo-cmd-teach-me` | Nothing | None. No claim, no worktree, no record |
| A2 Capture | `/idea`; any owner want voiced mid-session (`GOV-006`) | `_data/ideas.jsonl` via `tools/append_idea.py` | None beyond the sanctioned writer |
| A3 Exploration | `/demo-cmd-rubber-duck`, `/demo-cmd-second-opinion`, `demo-skill-brainstorm` | `docs/00-working/`, `_working/`, ideas | `REQ-023` R2: runs unclaimed, no governed document |
| B1 Specification | `/backlog`, `/session-start` on a `docs/0*`-deliverable phase | `docs/01-plans/`, `docs/06-requirements/`, `docs/09-backlog/backlog.yaml` | `REQ-023` R3; claim, worktree, record, `--next-code`, governance check |
| B2 Adjudication | "rule on", an open question carried forward | `docs/04-decisions/ADR-*`, `docs/08-governance/GOV-003` | Same as B1 today — the model argues this is wrong (§6) |
| B3 Construction | `/session-start <phase-id>` on a code-deliverable phase | `src/`, `ts/`, `test/`, `schemas/`, `sql/`, `_data/` | `REQ-023` R4; full protocol, `verification` list, `/session-close` |
| B4 Repair | Pasted error or defect description; `phase-wbf-*` defect phases | Narrow diffs in `src/`, `ts/`, plus `test/` | Same as B3 when phased; **undefined when not** |
| B5 Capability | "make this a skill"; `demo-skill-make-it-a-skill` | `.claude/skills/`, `.claude/commands/`, `.claude/agents/`, `.agents/skills/` | Full protocol; but `GOV-015` shows the surface is partly generated, so verification is structurally weak |
| B6 Governance | "add a rule", "from now on" | `docs/08-governance/GOV-*`, `AGENTS.md`, `CLAUDE.md` | **Owner-reserved.** `AGENTS.md` and `CLAUDE.md` edits need explicit per-change approval; `GOV-014` reserves this permanently |
| C1a Execution orch. | Owner-approved batch; `PROMPT-036`, `/resume-lit-review` | Queue state, integration commits | May complete phases under `GOV-003` 2026-09-16, given three conditions; integration still owner-gated |
| C1b Generative orch. | `/idea-triage`, partition sweeps | Idea annotations, proposed partitions | Proposes only; `GOV-014` reserves partition acceptance and `next_up` to the owner |
| C1c Pipeline orch. | `GOV-008` prompt packs, `GOV-009` research packs | Per-stage artifacts | Gated at each stage boundary |
| C2 Investigation | `/orient`; audit phases; `phase-lit-*`, `phase-expl-*` | `docs/08-governance/GOV-015`-style findings; `docs/00-working/` | Claim and record where phased; no mutation of the audited surface |
| C3 Retrospective | `log-anti-patterns` skill | `brain/procedures/`, `GOV-003` collisions ledger, ideas | None defined as a session; the skill defines the write, not the session |
| C4 Rehearsal | `docs/00-working/demo-runbook.md`; `phase-demo-05`, `phase-wb-07` | Defect notes; runbook corrections | None defined |

**Three gaps this table exposes.** They are predictions about the *governance surface*, testable by
reading it rather than the transcripts, and so are registered here as claims Part 2 may confirm
cheaply:

1. **Four of thirteen types have no defined obligation profile** — B4 unphased, C3, C4, and A1.
   `REQ-023`'s three types cover none of them.
2. **B6 is the only type whose primary artifact an agent may not write**, yet it shares an entry
   signal ("from now on") with A2 Capture, which any agent may write. The two are one word apart in
   the first prompt and a permission boundary apart in consequence. That is the highest-risk
   misidentification in the model.
3. **C1's obligations are defined by a decisions ledger entry rather than by the requirement**, which
   is why `REQ-023` can assert that a coordinator "is not a fourth type" while `GOV-003` grants
   coordinators an authority no other session has.

---

## 6. Reconciliation with REQ-023 and ADR-020

`REQ-023` defines **three** types — planning, brainstorming, implementation — and states explicitly:
"No fourth type is introduced. A coordinator session running several backlog phases in a batch is not
a fourth type." `ADR-020` Decision 3 infers the type from the claimed phase's deliverables.

This model proposes thirteen. The departures, each with its reason:

### Departure 1 — The three types are a partition of *committing* work only

Mapping is clean where it exists:

| `REQ-023` type | Absorbs |
|---|---|
| brainstorming | A3 Exploration, and by `ADR-020` Decision 1's routing, A2 Capture |
| planning | B1 Specification, B2 Adjudication |
| implementation | B3 Construction, B4 Repair, B5 Capability |

Unmapped entirely: **A1 Inquiry, C1 Orchestration, C2 Investigation, C3 Retrospective, C4
Rehearsal, and B6 Governance.** Six of thirteen. `REQ-023` R5 says the type "is determined by the
claimed phase's own nature" — which means a session with no phase and no governed output is outside
the requirement's reach by construction, not by oversight. The reason for the departure is therefore
not that `REQ-023` is wrong; it is that `REQ-023` answers a narrower question (what obligations
attach to a claimed phase) than the taxonomy needs to answer (what kinds of session exist).

### Departure 2 — Orchestration is a type, against REQ-023's explicit denial

`REQ-023` argues a coordinator is not a fourth type because "each phase it works is still planning or
implementation by the rules below". That is true of the *phases* and false of the *session*. A type is
a set of obligations plus a done-condition, and the coordinator's differ from both:

- **Obligations:** a coordinator claims phases serially rather than holding one, and under `GOV-003`'s
  2026-09-16 ruling it may mark a phase `complete` — an authority `REQ-023` R1 denies to every session
  it governs. A rule that says "no session decides its own completion" and a rule that says "a
  coordinator may complete a phase given three conditions" cannot both be about the same type.
- **Done-condition:** a coordinator finishes when its *batch* is exhausted or a gate stops it, not
  when any unit's acceptance holds.
- **Failure mode:** a coordinator fails by holding too much context, which is not a failure mode any
  of the three types has.

`REQ-023`'s own sentence concedes the point in passing — "the coordinator's own batching behavior is
governed by `PROMPT-036`, not by session type" — which is the observation that coordinator behaviour
needed its own governing document because the type system had no room for it.

### Departure 3 — ADR-020's inference rule misclassifies by construction

Decision 3 infers planning from "deliverables exclusively under `docs/0*` paths with no code or config
path", and implementation from code or config deliverables.

**A live counter-example, available without reading any transcript: this phase.** `phase-tax-01`
declares exactly one deliverable, `docs/00-working/session-types-theory.md`. It infers **planning**.
It is not planning: it writes no requirement, no plan, and no work item, and it enumerates no future
work with done-conditions. It is C2 Investigation (theory subtype). Under `REQ-023` R3 it inherits
planning's "must produce" — a requirement or plan document with an allocated code — which this
session cannot satisfy and should not.

The rule's defect is that it keys on **write path**, and write path is a proxy for D1 (object of
work) only. It cannot see D5 (convergence criterion), which is the dimension that separates
Specification from Investigation, and Construction from Repair. Any inference keyed on paths will
merge those pairs.

**The proposed correction, for the owner to consider and not adopted here:** infer from the
**first prompt's intent** — which is available at session start, before any path is known — and use
the phase's deliverables only to *confirm or contradict* that inference. Where they contradict, ask.
That ordering also fixes Appendix A's stated late-loading problem (§7).

### What this model does not touch

`ADR-020` Decision 1 (brainstorming produces no governed artifact) and Decision 2 (a mid-flight type
change binds from that point forward, without restarting the session) both survive unchanged and are
adopted into this model as stated. Decision 2 in particular is load-bearing here: with thirteen types,
mid-session type changes are more frequent, not less, and §7 depends on the rule being exactly what
`ADR-020` already says it is.

---

## 7. Appendix A evaluated against the model

Appendix A is the owner's CLAUDE.md design notes. Evaluated as design input, not policy.

### The behavioural spine (four rules) — sound, but **not type-neutral**

Rules 1 (think before coding; ask rather than guess) and 4 (explicit verification; define success
upfront, loop until verified) already exist in this repository's instruction files in substantially
this form, and the model supports both across every type.

Rules 2 and 3 do not generalise, and the taxonomy is what makes that visible:

- **"Simplicity first — the minimum code required for the immediate problem"** is correct for B4
  Repair, whose entire discipline is a narrow diff. It is **wrong for B1 Specification**, whose job is
  to widen the frame before the work starts, and **actively harmful for C2 Investigation**, whose
  convergence criterion is coverage of a declared scope — "the minimum required for the immediate
  problem" is a direct instruction to under-cover.
- **"Surgical changes — touch only the lines the request needs"** is correct for B3 and B4, and wrong
  for B5 Capability and B6 Governance, where the whole point of the change is that it applies
  system-wide. A governance rule written surgically is a governance rule that contradicts three others
  nobody checked.

**Recommendation.** Rules 1 and 4 belong in the unconditional spine. Rules 2 and 3 belong in the
Family B execution profile, and should be stated as scoped rather than universal. A universal rule
that four of thirteen types must violate teaches agents that the spine is negotiable, which is worse
than not stating it.

### "Core values over rigid rules" — the weakest claim, and this repository is the counter-example

The argument is that rigid rules break when context shifts, while values let the model make correct
trade-offs. Against first principles and this repository's own visible surface, that inverts where
each mechanism works:

A value is precisely what an agent can reinterpret under pressure. `AGENTS.md`'s own account of the
2026-09-09 incident is the argument in miniature: an agent holding a reasonable value — record what
you learned, keep the documents accurate — rewrote the file governing every future agent, inside a
diff about something else, generalising from a single one-time instruction. No plausible *value*
would have prevented that. A rule did, once it existed, and the rule had to be stated twice, in both
files, with the incident attached, precisely because a value-shaped version would have been
reinterpreted again.

**The distinction the model proposes instead of values-versus-rules:**

| Use a **rule** | Use a **value** |
|---|---|
| Boundaries *between* types — what a type may not do | Trade-offs *inside* a type |
| Irreversible acts — integration, deletion, publishing, rule changes | Reversible acts |
| Anything whose violation is only detectable after it has propagated | Anything a later session can correct cheaply |

By that test, Appendix A's own example is well chosen — "clarity matters more than brevity when
something is genuinely complex" is a within-type trade-off and should be a value. And the rules this
repository actually enforces (never edit the two instruction files; never write a confidential
identifier into a tracked file; ask before integrating) are all irreversible-act rules, which is why
they are rules. The notes' framing would have predicted the opposite.

### "Lean, under 50 lines, a behavioural router not a mini-wiki" — right shape, unverified budget

The router framing is exactly what this taxonomy is for: a router needs *routes*, and "a session that
looks like X follows protocol Y" is the route table. The taxonomy supplies thirteen candidate routes
and, more usefully, three family-level ones.

Two observations before the line budget is adopted:

- `CLAUDE.md` is currently **210 lines** and `AGENTS.md` **330**. A 50-line target is a 76% cut to the
  primary file, and `CLAUDE.md` contains a section explaining which facts are worth duplicating
  *despite* drift risk — with the bar set at "being unaware of it for one turn causes irreversible
  harm". That section is a considered argument for a floor above zero. The target and the argument
  should be reconciled deliberately rather than by one overriding the other silently.
- A router's length is set by its number of routes, not by a style preference. Thirteen types will not
  route in 50 lines; three families might. **If the owner wants a 50-line router, the family layer is
  the one to encode** — and the type layer belongs in whatever the routes point *at*.

### Path-scoped rules and the phase split — the vulnerability is real, and worse than stated

The notes identify a vulnerability: glob-based rule loading is deterministic but **late**, so a plan
drawn up before any file is opened is blind to path-specific constraints. The proposed fix splits
context by execution phase — unconditional root file for planning, glob-loaded rules for execution.

First, a factual note: **`.claude/rules/` does not exist in this repository today**, so this is a
proposal, not a description of something in place.

The taxonomy sharpens the vulnerability considerably. Glob-triggered loading is keyed on *a file being
touched*. Therefore:

- **Family A types touch nothing** — Inquiry, Capture and Exploration write no source file, so no glob
  ever fires, and they receive only the unconditional root context.
- **C1 Orchestration touches almost nothing by design** — its defining property is that it does not
  hold the work. Path globs will never fire for the session type that most needs a distinct protocol.
- The types the mechanism *does* serve — B3 Construction, B4 Repair — are the two that already have the
  strongest existing guardrails (a phase with a verification list, tests, a review gate).

So the mechanism loads context in inverse proportion to need. The phase split the notes propose
(planning versus execution) is a **two-type taxonomy in disguise**, and it is the wrong two: it splits
on *when in a session* rather than on *what kind of session*, which is why a whole family falls
through it.

**Recommendation.** Key the routing on **session type inferred from the first prompt**, with path
globs retained as a *second*, confirming trigger for Family B execution work only. The first prompt is
available at turn one — earlier than any glob can fire — which answers the notes' own late-loading
objection directly. Where the first-prompt inference and the later path evidence disagree, that
disagreement is a signal worth stopping on: it is exactly `ADR-020` Decision 2's mid-flight type
change, and this repository already has a decided rule for it.

---

## 8. Open questions for the owner, before the empirical phase

Ordered by how much the answer would change the model.

1. **Is the unit of analysis the session or the segment?** Several types above are predicted to be
   common as *segments* and uncommon as *sessions* — A2 Capture most obviously, and by `ADR-020`
   Decision 2 a session may legitimately change type mid-flight. If the empirical phase classifies one
   session to exactly one type, every one of those predictions is untestable as written. This is the
   single largest threat to the model's testability and it is a decision only the owner can make.

2. **Should Family A be exempt from records entirely, or recorded cheaply?** The model claims Family A
   needs no durable record. The cost is that the majority of sessions then leave no trace, and the
   repository's own history becomes unrepresentative of its own work. A cheap alternative exists — a
   one-line append rather than a governed document — but it is a new obligation on the type explicitly
   designed to have none.

3. **Does B6 Governance deserve a distinct entry ritual, given it is owner-reserved anyway?** If every
   governance change goes through the owner regardless, the type's value is not in its obligations but
   in *recognising the entry signal and refusing* — an agent that hears "from now on" should know it
   has been handed something it may not write. That is an identification rule, not a protocol, and it
   may belong in the router rather than in the requirement.

4. **Is C4 Rehearsal worth defining before it is observed?** The model proposes it knowing its most
   likely fate is disconfirmation by absence. Defining a type that does not occur costs little;
   *discovering* that end-to-end verification is only ever performed by the person who built the thing
   would be a finding worth having. The owner may prefer not to spend a scorecard row on it.

5. **Should the frequency bands be per-transcript or per-record?** §4 defines them over transcripts.
   Records only exist for claimed phases, so the two populations differ systematically — and one of
   the model's structural predictions (§9 below) depends on that difference being large. If the
   empirical phase scores against records, the Family A predictions are guaranteed to fail for a
   reason that has nothing to do with whether the types are real.

---

## 9. Structural predictions — registered separately from the type predictions

Four claims about the corpus as a whole, independent of any individual type. They are listed
separately so that a scorecard can record the model being wrong at the structural level while the
type-level predictions survive, or the reverse.

- **S1 — The transcript population is substantially larger than the record population, and the
  difference is Family A.** Records exist for claimed phases; Family A types claim nothing. Predicted:
  a large majority of record-less sessions classify into Family A or into C3/C4.
- **S2 — Type frequency is not stationary over time.** C1 Orchestration and B5 Capability should be
  near-absent early and concentrated late; B3 Construction should be more evenly spread. If frequency
  is flat across the corpus, the tooling surface has not changed how sessions are run, which would be
  a significant negative finding about the whole tooling programme.
- **S3 — Mid-flight type change is common, not exceptional.** `ADR-020` Decision 2 already asserts this
  ("`PLAN-008` names this the common case, not the exception"). The model adopts it as a prediction:
  a substantial fraction of sessions should show a first-prompt type different from their dominant
  activity type. If mid-flight change turns out to be rare, the thirteen types are cleaner than
  claimed — and `ADR-020` Decision 2 was solving a problem that does not occur.
- **S4 — The most common single session shape is Construction opened by Inquiry.** If A1's
  disconfirming observation fires — inquiry sessions routinely ending in writes — S4 is the reason, and
  A1 should be demoted from a type to an opening move.

---

## 10. What would make this model wrong as a whole

Registered so the empirical phase has a way to reject the framework rather than only its parts:

- **Over-splitting.** If more than four of the thirteen types fail their disconfirming observation in
  the direction of "this is a segment of another type", the model has mistaken phases for types and
  should be rebuilt on fewer, coarser types with named segments inside them.
- **Wrong dimension.** If D5 (convergence criterion) does not separate Specification from
  Investigation or Construction from Repair in the evidence, then the model's central methodological
  claim is false and a path-and-object model — which is what `ADR-020` already implements — is the
  better one.
- **Unusable entry signals.** If first-prompt intent does not predict dominant activity better than
  chance, the router proposal in §7 fails regardless of whether the types themselves are real, and
  path-scoped loading is vindicated.
