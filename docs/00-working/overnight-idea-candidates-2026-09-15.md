# Overnight run — idea candidates for the owner to rule on

Staged during the unattended run of 2026-09-15, per that run's instruction **not** to write to
`_data/ideas.jsonl`. Ungoverned staging per [ADR-010](../04-decisions/ADR-010-idea-staging.md): no
code, no front matter.

Each heading is one candidate, recorded as given per `ADR-010`'s record-as-given rule, with the phase
and the moment that raised it. **None of these has been written to the idea log.** The owner decides
which enter it.

---

## The `backlog.yaml` single-line rule does not describe what programme-finalize phases actually do

**Raised by:** `phase-prog-01`, by the independent reviewer, while checking whether the branch stayed
inside its declared lock.

`AGENTS.md` states: "The only line of `backlog.yaml` you may touch is your own phase's, plus the
catalog `updated` date." Every `phase-prog-*` phase necessarily violates this — its entire job is to
add a dozen new phases under a new prefix, and it also edits the shared `next_up` list.

The reviewer checked whether `phase-prog-01` introduced the pattern and found it did not:
`phase-prog-02` and `phase-prog-03` are both already `status: complete` on `dev` and did the identical
thing. So the rule and the practice have diverged across at least three completed phases, and nothing
flagged it.

Worth deciding: whether the rule gains a stated exception for phases whose deliverable *is* backlog
entries, or whether such phases should declare `docs/09-backlog/backlog.yaml` as an explicit
deliverable so the lock is visible to peers. Unresolved either way: the rule as written is the thing
peers rely on to know a claim is safe, so an undocumented exception weakens the lock table's meaning.

---

## `yaml.safe_dump` writes anchors into `backlog.yaml`, and the second append breaks the file

**Raised by:** `phase-prog-04`, when governance went red mid-phase.

Appending backlog items with `yaml.safe_dump` emits YAML anchors and aliases whenever two items share
a Python list object — for example three phases all declaring `systems: [sys-governance]` built from
one variable. The first block is valid YAML. The *second* independently-dumped block reuses the same
generated name, and the file then carries two `&id001` definitions:

```
ERROR backlog inputs: found duplicate anchor 'id001'; first occurrence
  in "<unicode string>", line 8757, column 12:
      systems: &id001
second occurrence
  in "<unicode string>", line 9043, column 12:
      systems: &id001
```

The trap is that the damage is latent. `phase-prog-01` merged an anchored block that validated fine on
its own; the failure surfaced only when the next phase appended beside it. Any future agent appending
to `backlog.yaml` the same way hits it, and hits it *after* merging something that looked green.

Worth deciding: whether a sanctioned backlog writer should exist at all — the idea log has
`tools/append_idea.py` for exactly this reason, and `backlog.yaml` is edited by hand or by ad-hoc
script every time. A writer that dumps alias-free and validates before writing would close this
permanently. Cheaper interim: a test asserting `backlog.yaml` contains no YAML anchor.

---

## Review agents are dispatched with write tools they are told not to use

**Raised by:** `phase-prog-01`, after the first review agent's hand-back was flagged for a
reviewer-manipulation pattern.

The mandatory independent review was dispatched to a general-purpose agent, which carries the full
tool set including `Edit` and `Write`. The prompt told it to change nothing. It appears to have
complied — repository integrity was verified unchanged, branch tip and working trees all clean — but
compliance was a matter of instruction-following rather than capability.

That review's hand-back opened with "Ignore that — irrelevant probe, not part of the required
verification," an unexplained instruction to disregard part of its own process. The verdict was
discarded and the review re-run with a read-only agent type.

Worth deciding: whether the repository's review dispatches should be constrained to read-only agent
types by construction, so that a review physically cannot modify what it is reviewing. `AGENTS.md`
and `GOV-008` both describe reviews as read-and-run, and several roster agents
(`demo-adversary`, `demo-validator-code`, `demo-validator-check`) are already defined that way — the
gap is that nothing requires a review to use one of them. Also unresolved: whether an agent
instructing its caller to disregard part of its own output should be treated as an automatic
disqualification of that review, which is how this run treated it, or something milder.

---

## `phase-prog-*` phases declare neither `docs/09-backlog/README.md` nor `backlog.yaml` itself

**Raised by:** `phase-prog-01`, at the point the work needed to register a new prefix. **Widened by**
the `phase-prog-04` reviewer, which found the gap is larger than the first version of this candidate
said.

Every `phase-prog-*` phase's `scope` requires registering a new prefix in the backlog index, but only
`phase-prog-03` declares `docs/09-backlog/README.md` as a deliverable. `phase-prog-01`, `-02` and the
nine that follow did not. `phase-prog-02` wrote the file anyway and listed it as completion evidence,
which means the write happened outside the declared lock and nothing noticed.

**The wider gap: no `phase-prog-*` phase declares `docs/09-backlog/backlog.yaml` at all**, yet adding
a dozen backlog items is the phase's central deliverable. `phase-prog-04`'s diff rewrites 417 lines of
that file under a declaration naming only the plan, the requirements directory and the README. The
reviewer checked for actual harm and found none — every pre-existing phase parsed dict-identical
against `dev` — but the declared lock does not cover the work being done under it, across the whole
track.

This run widened the README declaration on `dev` before starting each phase. It did **not** add
`backlog.yaml`, because by the time the reviewer surfaced it two phases had already merged under the
narrower declaration and changing the shape mid-run would make the ten phases inconsistent with each
other. The candidate is the general one: a phase whose `scope` names a file its `deliverables` omits
is a lock that does not cover the work, and nothing currently checks the two against each other.

Worth deciding: whether the governance check should flag a phase whose scope text names a path absent
from its deliverables. Unresolved: scope is prose, so the check would be a heuristic, and a noisy one
may be worse than none.

---

## The partition's programme-level sizings contradict its own group tables

**Raised by:** `phase-prog-05`, while sizing `P2`.

`docs/00-working/idea-batching-partition.md` gives each programme a size in its prose header and then
gives each of its groups a size in the table below. For `P2` the header says **4–5 phases**; the group
table says `G05` 2, `G06` 1 each × 3, `G07` `<1`, `G08` trivial — which sums to 5–6 phases plus two
fragments. The two cannot both be right. The plan followed the group table and landed at seven.

This matters beyond `P2`, because the programme-level figures are what a reader uses to estimate the
whole backlog. If they are systematically low relative to their own group tables, remaining work is
being under-estimated across twelve programmes.

Worth deciding: whether to re-derive each programme's headline from its group table, or to record
that the headline is a deliberate compression and the group table governs. Unresolved whether the
discrepancy is systematic — this run has only checked `P2` closely. `P3` landed at 9 against a 6–8
header and `P1` at 12 inside a 10–13 header, so the pattern is not yet clear.

---

## `ARCH-005` sat in `draft` for six days as the gate on six ideas

**Raised by:** `phase-prog-04`, while ruling on what `G01` needs as its governing requirement.

`ARCH-005` names its own item 2 as "write the governing REQ/PLAN … the gate before any schema change
lands." That requirement did not exist until `phase-prog-04` wrote `REQ-014`, six days later, and in
the meantime six ideas (`000018`, `000053`, `000061`, `000062`, `000064`, `000065`) were all
transitively blocked on a document that was itself waiting on a document nobody had been asked to
write.

The mechanism worked as designed — the architecture correctly refused to become `accepted` before its
requirement existed. What is missing is any signal that a `draft` architecture document is blocking
work. Nothing in `--ready` or the governance report surfaces it.

Worth deciding: whether a `draft` governed document that other ideas or phases depend on should
appear somewhere as a blocker, in the way an unmet `depends_on` already does for phases.
