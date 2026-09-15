---
schema_version: 1
id: doc-concurrency-git-safety-requirements
code: REQ-013
title: Concurrency, git safety and enforcement requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-governance, sys-backlog, sys-delivery]
depends_on: [doc-adr-multi-agent-concurrency, doc-backlog-decisions, doc-confidentiality-sweep]
---

# Concurrency, git safety and enforcement requirements

## Observed problem and scope

`ADR-003` gave this repository a claim-and-lock model: `docs/09-backlog/backlog.yaml` on `dev` is the
lock table, `uv run python -m src.governance` is the lock check, and every agent works in its own
worktree on `agent/<phase-id>`. The model is sound and in daily use. What it does not have is a way
to fail safely — every rule that protects a peer's work is a sentence an agent has to remember, and
the rules that were forgotten are the reason this programme exists.

Four failures are recorded in the repository rather than hypothesised.

1. **A claim can be abandoned with no recovery path.** An agent marks a phase `status: active`, cuts
   a worktree, and then stops — a crash, a context exhaustion, an API session limit. The phase stays
   `active` indefinitely, the branch and worktree sit orphaned, and every peer whose systems overlap
   reads a dead claim as a live one. `000025` names this, and its own body records the case that
   produced it: one of the two agents in that research batch hit a session limit mid-run.

2. **A peer's uncommitted work has been destroyed.** A concurrent agent ran `git stash` against the
   primary checkout to merge its own work, popping another session's in-progress changes without
   asking. The collision left three scratch scripts in the repository root, a duplicate `next_action`
   key in `backlog.yaml`, and a session-code collision — `SESS-2026-09-08-07` allocated independently
   by both sessions, surfacing only after it was already committed to shared history. `000041` is the
   incident report.

3. **Nothing prevents a direct commit to `main`.** The owner's direction of 2026-09-09 is that work
   reaches `main` only through a pull request from `dev`. Today that is prose in `AGENTS.md`, not a
   setting on the remote. `000066` also carries the protocol question the gate forces: what a claim
   means once merges become asynchronous and a pull request can sit open across sessions.

4. **Enforcement lives in prose that agents skip.** `dev` was left red for three commits because
   `--catalog` prints rather than writes and the regeneration was redirected away; a check at the
   moment of action would have caught it, and the written step did not. `000014` and `000012` are two
   instances; `000051` was created to parent them and ask the general question — where enforcement
   belongs, in hooks, in tests, or in prose.

Two further facts bound the scope rather than motivate it. The repository's history and all of
`_private/portfolio/` exist on one machine's disk, and `_private/` is permanently gitignored, so no
remote will ever cover it (`000021`, umbrella'd by `000058` with its git slice in `000059`). And the
private-content check reports `0 identifiers checked` from a worktree against `31` from the primary
checkout, because `_private/portfolio/` is absent there — a gate that passes by not looking, observed
on 2026-09-14.

This requirement covers the concurrency, git safety and enforcement programme (`P3`): claim recovery,
protection of uncommitted work, collision-proof code allocation, the branch topology and pull-request
gate, the backup posture for non-git state, and the rule that decides where any future enforcement
belongs. It does **not** cover agent design or orchestration — that is `P4`
([PLAN-031](../01-plans/PLAN-031-agent-engineering-delegation.md)). The boundary is that `P4` designs
the agents and `P3` constrains the ground they run on; the one real bridge, `000082`, stays in `P4`.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | The governance report identifies every claim that meets a stated staleness signal, and prints it as a distinct state rather than leaving it indistinguishable from a live claim. | Set a phase `active` with an `agent` and no branch activity past the threshold; run `uv run python -m src.governance --ready` and confirm the phase is reported as stale, naming the signal that fired. Confirm a genuinely live claim in the same run is not flagged. |
| R02 | The staleness signal is defined in terms a check can evaluate without judgement, and the definition names what it does **not** prove. | Read the definition for evaluable inputs only — no "seems abandoned". Confirm it states explicitly that staleness is evidence for the owner, not proof the agent is dead. |
| R03 | Releasing another agent's claim is an authorised procedure with a written sequence, and no check performs it automatically. | Read the procedure for who may release, what must be confirmed first, and what happens to the orphaned branch and worktree. Confirm no code path in `src/governance/` writes `status: queued` over a peer's claim; a grep finding one is a defect. |
| R04 | An integration into `dev` is refused while the primary checkout holds uncommitted changes, by a mechanism rather than by a rule an agent may skip. | With an unrelated modified file in the primary checkout, attempt the integration and confirm it is refused and names the dirty paths. Confirm the refusal cannot be satisfied by `git stash`. |
| R05 | Document codes cannot be allocated twice across concurrent sessions. Two allocations of the same `kind` in flight at once yield two different codes. | Allocate the same `kind` from two worktrees before either commits, and confirm the codes differ. Confirm the reservation is visible to the second caller before the first has merged — an allocator that only reads committed state is the defect `SESS-2026-09-08-07` demonstrates. |
| R06 | `main` rejects a direct push, and a pull request from `dev` with a failing required check cannot be merged. | Attempt a direct push to `main` and record the rejection. Open a pull request from a branch with a deliberately failing check and confirm merge is blocked. Both are observations against the remote, not readings of a document. |
| R07 | The branch-protection settings record states, per setting enabled, whether it is load-bearing today or ceremony kept for later, and why. | Read the record for a judgement on each setting — required review, required status checks, linear history, owner exemption, force-push protection. A setting enabled with no stated reason is a defect. |
| R08 | `tools/check_no_private_content.py` is a required status check on the pull-request gate, and it reports a non-zero identifier count when it runs. | Confirm the check is required on the remote. Run it in an environment without `_private/portfolio/` and confirm it fails or warns rather than reporting `OK (… 0 identifiers checked)`. A gate that passes by finding nothing to check is the 2026-09-14 observation asserted as a standing check. |
| R09 | The multi-agent protocol states what a claim means under the pull-request gate: when a claim is released relative to merge, and how an agent determines whether its work has landed. | Read the protocol for all three. Confirm it answers whether agents integrate onto `dev` directly with only `dev`-to-`main` gated, or open a pull request per `agent/<phase-id>`, and states the reason for the choice rather than asserting it. |
| R10 | Every governed document's description of the branch model matches the model actually in force. | Grep the document corpus for branch-model claims and check each against the remote's settings. This is the failure class that produced `0c82996`, where 31 references were rewritten to a model that then changed; a stale reference is a defect. |
| R11 | The backup posture for non-git state is recorded as a decision, naming what is covered, what is not, and at what cadence. `_private/portfolio/` is addressed explicitly. | Read the decision for a named mechanism and a named cadence, or an explicit acceptance of the risk with the loss it accepts stated. "To be decided" is not a posture. |
| R12 | The backup mechanism, if one is chosen, is verified by restoring from it rather than by confirming it ran. | Restore into a scratch location and diff against the source. A backup verified only by its own exit code does not satisfy this row. |
| R13 | An enforcement-placement rule exists that decides, for a given standing rule, whether it belongs in a hook, a test, or prose — and it is applied to the rules already in force rather than stated abstractly. | Read the rule for a decision procedure with stated inputs. Confirm it is applied to at least the governance check, catalog staleness, the private-content gate and `_private/` reads, each landing somewhere with a reason. |
| R14 | `.claude/settings.json` and `.claude/settings.local.json` are audited, with every permission recorded as belonging in tracked project settings or local personal settings, and any permission broader than the work requires named. | Read the audit for one row per permission present. Confirm it names which file each belongs in, and that at least the `Edit(AGENTS.md)` deny rule is reconciled against `000091`'s blocked change. |
| R15 | Any enforcement placed in `.claude/` is recorded as tool-specific, with the equivalent stated for an agent not running under that harness. | Read each hook's record for its non-Claude-Code equivalent. `AGENTS.md` is written for any agent; a rule enforceable only in one harness is a rule the others do not have, and the gap is to be stated rather than discovered. |
| R16 | `AGENTS.md`'s push rule reads as one general rule plus one named exception, and neither passage states an absolute that the other contradicts. | Read both passages. Confirm each names the structure — general rule, standing exception — and that the cross-reference points at a passage that agrees with it. The approved replacement text is recorded verbatim on `000091`. |

## What each requirement is not

**R04 is not a rule against `git stash`.** An agent may stash its own work freely. The observable is
that an integration cannot proceed over someone else's uncommitted changes, whatever the agent does
to get there.

**R06 is not satisfied by a document.** Both halves are observations against the remote. A governance
document asserting that `main` is protected is `R10`'s subject, not `R06`'s evidence.

**R11 permits accepting the risk.** A recorded decision to run without off-machine backup, naming
what is lost if the disk fails, satisfies the row. What does not satisfy it is leaving the question
open, which is the state `000021` reports.

**R16 is owner-executed.** `.claude/settings.json` hard-denies `Edit(AGENTS.md)` and `Write(AGENTS.md)`,
and `AGENTS.md`'s own standing rule forbids any agent editing it regardless. The row is verifiable by
an agent and satisfiable only by the owner.
