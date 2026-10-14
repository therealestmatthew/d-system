# Batches

A batch is an owner-approved, ordered set of queued phases, grouped into stages, that a coordinator
builds (`coordinator.md`). The plugin ships no batch schema, no batch directory and no batch check:
a batch table is a record the repository keeps where it chooses, and the rules below govern what it
says and how it is used.

## 1. What a batch table records

- A batch table records grouping, sequencing and parallelism only. Scope, acceptance, verification,
  systems, deliverables and `depends_on` stay in the backlog and are never restated.
- A phase title may be copied in for readability. The backlog wins wherever the two disagree.

## 2. Who composes a batch

- Composing and superseding a batch is the owner's decision. A coordinator never composes, adds to
  or edits a composition, whether to fix a defect or to absorb a newly ranked phase. A wrong
  composition is a question for the owner.
- A coordinator that finds nothing runnable computes a dependency-closed candidate from `next_up`,
  with its stages, puts it to the owner as a question, and stops.
- The coordinator proposes and the owner decides. A composition exists only after the owner's yes,
  and an unanswered proposal is not a yes.

## 3. Checking a composition

A batch runs only after its composition has been checked against the backlog by script, and the
check is recorded with the batch. The check confirms that:

- every phase id resolves in the backlog;
- every phase is queued and unclaimed;
- every `depends_on` edge points to an earlier phase in the batch or to a complete phase outside
  it, which is what dependency-closed means;
- every external dependency is listed with the batch;
- every stage boundary follows from a real dependency edge or a real collision, computed with the
  collision function.

A recorded check is evidence of its moment, not a licence. The coordinator re-verifies before every
run.

## 4. Stages

- Stages run in order. A stage opens only when every phase of the one before is complete and
  integrated.
- Phases within one stage share no dependency edge, no system and no overlapping deliverable path.
- A parallel stage means the check will admit its phases together, not that they run together. The
  numeric checks run before every claim (`backlog-protocol.md`, section 6), and a stage runs
  serially when peers leave room for only one.
- Collision, not dependency, usually serializes a batch. A recorded collision is a lock, not slack
  to reclaim.
- Deliverable paths collide by path component: two paths collide when they are equal or one
  contains the other. The rule is computed with the real function, never by exact matching.

## 5. Changing a composition

- Once a run opens against a composition it is frozen. Changed membership is a new composition
  that supersedes the old one; the old one is kept and names its successor.
- No check validates a batch table. The composing session runs the checks in section 3 and records
  them.
