# Plan review

How a plan and its requirement are judged before the owner approves them. A plan is checked in two
ways: mechanically, by its headings, and then by review, against the content judgements below. The
review is run by an adversary at three altitudes. This review is separate from the completion
review of a phase's diff (`backlog-protocol.md`, section 10); its record goes to the owner in full
at the plan-approval gate.

## 1. The mechanical check

- The required plan sections and the two conditions that add sections are those in `protocol.md`
  section 4. The headings accepted for each section are listed in `scripts/plan_check.py`
  (`REQUIRED`), which the `plan-check` skill runs. Neither is restated here.
- A plan starts from `templates/plan.md`, which passes the check as shipped. A requirement starts
  from `templates/requirement.md`.
- The two investigation headings in the design section are for a plan whose outcome is the thing
  being investigated. Such a plan says why its later work is not yet specified.
- An open-questions section with nothing open still appears and says so, and records any question
  already settled as confirmed.
- A requirement's rows form one table with three columns: an id of the form `R01`, the observable
  behaviour, and the verification method. Every row has a non-empty verification cell. No script
  checks the table; the reviewer does.
- A requirement carries an accepted-decisions section when the owner has already ruled on choices
  the requirements depend on.

## 2. Content judgements

The reviewer applies the judgements after the mechanical check passes. Each stands on its own: a
document can meet one and fail another. They cover plans and requirements only. Front matter and
lifecycle are covered by `protocol.md` sections 5 to 7. Phase sizing is not covered here, and
neither is whether a document still describes the system.

### Plans

| Id | The plan meets it when | It fails when |
|---|---|---|
| P1 | The context names the observed problem (what went wrong or what is missing) and points to the record of it. | The context describes only the proposed solution, or cites a prior finding without saying which part each step answers. |
| P2 | Each decision names the alternative it rejected and what that alternative would cost in this setting. | The reason is only a merit of the chosen option, the alternative is only implied, its cost is not stated, or no alternative appears. |
| P3 | A settled decision is stated flatly, saying who ruled and when; an unsettled one is marked as a recommendation once, where it is made; the owner's words are quoted when they are the reason. | The document's status and its body disagree about whether something is settled, or the reader cannot tell who decided. |
| P4 | Every claim about the current state of the repository comes with the command, file line or record that confirms it. | A fact about the repository or a capability is asserted with no source. |
| P5 | Scope states what is excluded and why. | There is no boundary, or scope lists only what is included. |
| P6 | Acceptance names the command or observation, the expected result, and at least one input that must be rejected. A plan paired with a requirement maps every row to a step and every step to a row, and explains any deliberate gap. | Nothing states when the work is finished. |
| P7 | A plan that registers several phases states which can run at the same time, worked out from each phase's declared `systems` and `deliverables`, treating a shared system or deliverable as a collision (`backlog-protocol.md`, section 7). | The plan asserts the phases are independent without checking the declarations, or its own text contradicts that. |
| P8 | Each open question says who decides it, when, and which way the author leans. | A question is bare, or has a deadline but no decider or leaning. |
| P9 | A superseded passage in the plan is marked, dated and explained, and its old text stays readable. | The change carries no date; an edit makes a before-and-after record identical; or an amendment sits between a sentence and the content it introduces. |
| P10 | Every label is defined before it is used, so a reader who was not in the session can follow the document from the repository alone. Document codes, phase ids and idea ids count as defined, because each resolves to a record. | Labels are defined only outside the repository, or some are defined and others are not. |
| P11 | The work section states each step's prerequisites where the work is ordered, so the order can be checked. | A dependency is shown only in a separate section, or not at all. |

### Requirements

| Id | The requirement meets it when | It fails when |
|---|---|---|
| Q1 | The problem section names the observed failures and where each is recorded. | There is no problem section, or it describes what the work will do instead of the problem it answers. |
| Q2 | Each row states one observable behaviour. | One row bundles several independent deliverables or rules. |
| Q3 | Verification is a procedure someone else can run: it names the input and the expected result and, where possible, a control case that must not trigger. A row no command can verify says so. | Verification says "inspect" without saying what result passes, or gives a command that cannot run as written. |
| Q4 | Rows state behaviour, not implementation, unless the owner ruled on the implementation. | A row names specific libraries or mechanisms without saying they were ruled on. |
| Q5 | A boundary section says what each requirement does not require, ruling out readings a builder would otherwise guess at, and gives each exclusion its reason. | There is no boundary section, or scope is stated only as a whole. |

### Wording

| Id | Rule | It fails when |
|---|---|---|
| T1 | Write the direct statement, not a metaphor: a metaphor carries connotations the author did not choose, and the reader has to translate it back into the claim. | A figurative line stands where a shorter literal statement is available. |
| T2 | Do not repeat front matter (status, dates) in the body; the copy can disagree with the front matter the check reads. | Status or date lines appear under the title. |

### Length

- Length is not the measure of quality. A short plan passes when it is complete; a thin plan passes
  when it says why it is thin.
- A plan is too thin when it is short and also fails content judgements.
- A plan is too long when it specifies contracts and structure for components that do not yet
  exist, ahead of demonstrated need.
- A plan is too dense when its cells or sentences compress reasoning that cannot be evaluated
  without the conversation that produced it (a P10 failure).

### Optional sections

Each is included only when its condition holds. A copy written by habit, without its condition
holding, is a failure.

- **Known facts not to rediscover:** only facts the body does not already state; omitted when
  nothing new remains.
- **Key references:** only links the reader needs that the body does not already give, each with a
  note saying what it is needed for.
- **Sizing against a partition:** only in a plan derived from an idea partition, and only to
  explain a difference between the partition's estimate and the phases registered.
- **Deliverables:** what the work produces, each with what it is for; never the plan itself, never
  anything removed.

## 3. The three-altitude review

A plan review runs the entry check, then an adversary attacks the plan at three altitudes: the
plan against its requirement; each phase in isolation; and each phase added after the plan,
against the plan as it stands. The review produces one review record. The adversary's contract is
in `role-contracts.md`.

### Who does what

- The dispatcher runs the entry check and writes the record when the draft is returned.
- The adversary writes nothing and reports its findings in its reply.
- The dispatcher records the findings from the reply without changing any of them.
- The planner writes dispositions during revision. The owner writes them, at the plan-approval
  gate, for escalated findings only.

### The review record

The record lives in the session record of the session that runs the review, in a `## Review`
section: the entry check's result, the altitudes dispatched and their targets, every finding, and
every disposition. Its status is `returned`, `open` or `dispositioned`.

### Step 1: the entry check

- The plan's section check (the `plan-check` skill) runs before any adversarial time is spent. It
  reads headings only. It does not check the requirement's sections; the adversary reads the
  requirement at the plan altitude.
- **Pass** (exit 0): the entry check is recorded as `pass` and the review continues.
- **Returned** (exit 1): the plan goes back to the planner with the check's output, and no
  adversary is dispatched. The record is `returned`, with the missing sections, no altitudes run
  and no findings.
- A plan returned twice is escalated to the owner at the plan-approval gate.

### Step 2: what each altitude covers

- Each altitude's target list is written into the record before dispatch. The adversary reviews
  what the record names.
- **Plan altitude:** the plan and the requirement it depends on. A child plan is its own target
  and gets its own review.
- **Phase altitude:** every phase whose `plan` is this plan, that was in the original phase set,
  with status `queued` or `blocked`. Active and complete phases are not reviewed, because a finding
  could no longer change them.
- **Later-added altitude:** phases with the same `plan` and status filter, first registered in a
  later commit than the original set. The original set is the phases first registered in the same
  commit as the plan's earliest phases. A phase's first commit is found with
  `git log --format='%h %ad %s' --date=short -S "id: <phase-id>" --reverse -- <backlog> | head -1`.
- Once any later-added phase exists, the third altitude runs, even when the first two came back
  clean.
- The record lists the altitudes dispatched, so a skipped altitude shows as skipped rather than as
  clean.

### Step 3: dispatch

- The adversary is dispatched with the prompt in `adversary-prompt.md`, once per altitude, in a
  fresh agent that shares none of the planner's context. A read-only agent type is used when the
  repository defines one; otherwise the prompt alone keeps the adversary read-only.
- Every placeholder is filled with an absolute path.
- If the phase altitude's phases do not fit one dispatch, they are split across dispatches, each
  covering only the phase altitude.

### Step 4: recording

- Each finding in the reply becomes one record entry, numbered `F01` onwards in the order read. The
  record's status is `open`.
- The dispatcher copies the adversary's fields without editing them, adding only the id and an
  author naming the agent type and the prompt.
- No finding is dropped at recording. A finding the dispatcher believes is wrong is recorded as
  reported, and the planner dispositions it `rejected`.
- `slug` and `aliases` are optional; the adversary proposes them when a finding looks like an
  instance of a recurring kind of defect.

### Step 5: dispositions

| Disposition | What its reason says |
|---|---|
| `fixed` | Where the change was made: document and section, or backlog line |
| `accepted-no-change` | Why no change is made |
| `rejected` | Why, with evidence |
| `escalated` | What the owner must decide |

- Every finding carries a disposition. Each disposition is appended to the finding's list, and the
  last one is current.
- The planner may write any of the four values. The owner writes a disposition only on a finding
  the planner escalated, and never writes `escalated`. The adversary writes none.
- There is one revision cycle. A blocker still unresolved after it is escalated. The revised plan
  does not get a second review.
- When every finding has a disposition, the record is `dispositioned`. It goes with the plan to
  phase-fit, and its escalated findings go to the owner at the plan-approval gate.

### Boundaries

- Splitting an oversized phase belongs to phase-fit (`role-contracts.md`), not to this procedure.
- The procedure is run by hand, by a person or a session. The entry check is the `plan-check`
  skill.

## 4. Reviewing queued phases under a review pack

A review session working under a prompt pack the owner approved (`prompt-packs.md`) may edit the
in-scope phases' backlog lines, the backlog `updated` date and the catalog regeneration that edit
forces. Before each edit it re-checks readiness and skips any phase a peer has claimed. It never
touches `next_up`, `status` or `agent`, or other documents, and it integrates only on the owner's
yes. This does not widen what the `checkpoint` skill writes.
