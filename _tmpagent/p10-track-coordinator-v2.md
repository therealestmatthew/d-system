# Track B — P10 programme execution (`phase-arch-*`) — v2

**Replaces `p10-track-coordinator.md`, which is superseded and must not be used.** That version
stated the wave-1 concurrency ceiling as 2. It is 3. The measurement behind it silently omitted
`phase-arch-00`, and an independent review of `phase-prog-03` caught it at session close on
2026-09-14. Everything else is unchanged.

Coordinator prompt for the workbench architecture and quality programme. Runs **after** Track A, on
whatever time remains, and continues past the 2026-09-15 demo.

`AGENTS.md` governs everything below. Where this prompt and `AGENTS.md` differ, `AGENTS.md` wins.

## Read the measured concurrency before planning any fan-out

`PLAN-028`'s *Execution order and real concurrency* section carries the numbers. They were measured
by running `src.governance.backlog.collisions()` over the whole `phase-arch-*` set on 2026-09-14, not
read off the dependency graph. The summary:

| Wave | Ready together | Actually concurrent |
|---|---|---|
| 1 | `00`, `01`, `11`, `14`, `16` | **3** — `00`+`01`+`11` |
| 2 | `02`, `03`, `05`, `12`, `15` | **2** — `02`+`12` only |
| 3 | `04`, `06` | **1** |
| 4 | `07` | 1 |
| 5 | `08`, `09`, `10` | **1** |
| 6 | `13`, `17` | **1** |

**Wave 1 admits 3 — `max_active` — and only wave 1 does.** `phase-arch-00` declares
`sys-governance` and `docs/08-governance/systems.yaml`, so it collides with nothing and runs
alongside the best wave-1 pair. Among the seventeen idea-derived phases the ceiling is **2**, and it
is **1 from wave 3 onward**: `sys-ui` is declared by 14 of them and the validator treats a shared
system as a collision. Past those numbers, more agents buy nothing except rejected claims.

**Do not queue claims the validator will reject.** A rejection is the answer, not an obstacle — but
a coordinator that discovers this by trial has spent real tokens learning what this table already
says.

Re-derive the table rather than trusting it if the backlog has changed since 2026-09-14:

```bash
uv run python -c "
import yaml
from src.governance.backlog import collisions
d=yaml.safe_load(open('docs/09-backlog/backlog.yaml'))
items={i['id']:i for i in d['items']}
arch=[i for i in items if i.startswith('phase-arch-')]
done=set(); remaining=set(arch); wave=1
while remaining:
    ready={p for p in remaining if all(x in done or not x.startswith('phase-arch') for x in items[p]['depends_on'])}
    r=sorted(ready); print(f'Wave {wave}: {r}')
    for a in range(len(r)):
        for b in range(a+1,len(r)):
            c=collisions(items[r[a]],items[r[b]])
            if c: print(f'  CONFLICT {r[a]} x {r[b]}: {c}')
    done|=ready; remaining-=ready; wave+=1
"
```

## Start `phase-arch-00` and `phase-arch-01` together

`phase-arch-00` decomposes `sys-ui` so the rest of the track stops serializing on one lock. The owner
directed on 2026-09-14 that it runs at the start, and the reason is concrete: every other
`phase-arch-*` phase would otherwise have to redeclare its `systems` afterwards.

**It does not gate anything and it does not run alone.** `phase-arch-00` and `phase-arch-01` both
declare `depends_on: []` and do not collide, and `phase-arch-11` joins them — three at once, which is
`max_active` and the only point in the programme where that is reachable. Start all three.

`phase-arch-00` edits `systems.yaml`, which every peer's claim reads, so **re-measure with the
snippet above once it lands** before planning wave 2. Do not let a second agent touch `systems.yaml`
while it is active.

Its own `next_action` says to measure the current ceiling first so the split is argued against a
number rather than an impression. Hold it to that. `REQ-011` `R29` makes the ceiling rising the
observable, and a split that does not raise it has not done its job.

The counter-consideration is recorded on idea `000234` and must survive into the change: a finer lock
table admits more genuine conflicts that the coarse lock was accidentally preventing. Argue the seams
from what is actually in the tree — the layout and slot engine, the panel implementations under
`ts/src/stage`, the notes strip and rotator, the explorer panels — not from a wish for more
parallelism.

## Per-phase protocol

Every phase runs `/session-start` in full: claim on `dev`, branch `agent/<phase-id>`, worktree
`../d-system-worktrees/<phase-id>`, isolated environment. No exceptions for documentation-only
phases — that exception was withdrawn on 2026-09-12 and the incidents are in `GOV-003`.

- **The claim commit and the catalog regeneration it forces** happen in the primary checkout on
  `dev`. Everything else happens in the worktree.
- **Never switch the primary checkout's branch.**
- Take each phase's `scope`, `acceptance` and `verification` as the work boundary. They were written
  to be sufficient; if one is not, that is a finding to report, not a licence to widen.
- **No phase in this track is complete until the owner runs `/session-close`.** The coordinator never
  writes `status: complete`.

## Phase order

`phase-arch-00`, then the waves above. Within a wave, prefer the phases that unblock the most:

- **`phase-arch-01` is the gate.** Six ideas cite its vocabulary as a prerequisite by their own text.
  It delivers the settled names *and* the migration ruling; `phase-arch-02` executes the migration
  and gates nothing, which is why they are separate phases.
- **`phase-arch-06` is the pivot.** Everything in waves 4–6 descends from it. It writes the ADR that
  supersedes `ADR-016`, and it must mark `ADR-016` `superseded` in the same change or governance
  fails.
- **`phase-arch-07` is the single point the whole back half passes through.** Nothing in waves 5 or 6
  can start until it lands. Size the session accordingly and do not fold anything else into it.
- **`phase-arch-11`, `14` and `16` are free-standing** and can fill any gap where a `sys-ui` phase
  holds the lock.

## Agent hygiene and spend — binding

The repository's standing conventions, from `GOV-008`'s *Cost protocols* and
[PROMPT-016](../docs/02-prompts/PROMPT-016-demo-guardrails.md). Binding on the coordinator and every
agent it dispatches.

**Models.** Haiku for mechanical gates — governance check, staged private-content check, front-matter
and checklist audits. **Sonnet is the standard for judgment work**: every creator and validator
dispatch. **Opus is never pre-assigned**, and is available as at most **one documented escalation per
build**, only after two failed sonnet attempts with validator findings attached. Report it. The
second failure of that kind goes to the owner rather than to a second escalation.

**Loop caps.** At most **two** creator→validator fix cycles per work item, then the coordinator
judges and reports up. **A third quiet retry is forbidden.** Two phases exhausting their caps is a
stop-and-report signal for the whole track.

**Truncation: resume, never re-run.** Cut-off output is resumed with `SendMessage` against the same
agent (idea `000077`). Re-running pays for the entire context a second time and is the most
expensive avoidable mistake on this track.

**Validator blindness.** Validators receive the diff, the requirement and the commands — **never the
creator's rationale.**

**Dispatch discipline.** One work item per dispatch. Do not spawn an agent for what a `grep` or a
single `Read` settles, and do not spawn a second agent to audit the first one's reading. Each spawn
starts cold and re-derives context the coordinator already holds. On a track whose real concurrency
is 1–2, most of the value of subagents is isolation of long tool output, not parallelism — dispatch
for that reason or not at all.

**Audit phases are cheap to over-run.** `phase-arch-03`, `04`, `14` and `16` all sweep the tree.
Bound them: name the directories, take the measurement with one command, and write the findings.
An audit that reads every file individually will burn a session's budget before it forms a view.

**Ports.** Explicit and free — `--port 8010`, Vite on 5180. **Never assume 8000 or 5173.**
`VITE_API_TARGET` defaults to `http://127.0.0.1:8000` as of commit `e1ab509`.

**Worktree hygiene.** Per-worktree `.venv`, `data/`, `ts/node_modules/`; `uv sync --extra dev` or the
governance check fails on a missing `jsonschema`. **Gitignored content never travels** — copy
anything that must survive out before `git worktree remove`. Rebase onto `dev` whenever a peer
integrates, never merge `dev` in.

**Git.** No `--force` push, no rewriting pushed history. `agent/*` pushes are free; integration into
`dev` is owner-approved. `tools/check_no_private_content.py` runs **with changes staged**.

**Codes.** Allocate every document code with `uv run python -m src.governance --next-code <kind>`.
**Never pick a number by reading a directory** — it cannot show reserved or retired codes. Codes are
free before merge and permanent after; on a duplicate, whoever integrates second renumbers.

**Collisions.** A conflict in `src/`, `ts/`, `schemas/` or `sql/` means the disjointness rule was
bypassed — **stop, do not force the merge, and report it**, because the phases' declared `systems` or
`deliverables` were wrong. `backlog.yaml` conflicts are normal: keep both sides, never `--ours` or
`--theirs`. When resolving requires an actual choice, record it in `GOV-003` in the same diff.

**When to ask.** `AskUserQuestion`, only when the answer changes what gets built and this prompt and
the phase do not already answer it: merge approvals, a phase that cannot meet an acceptance condition
as written, an undeclared dependency found mid-work. Otherwise state the assumption, keep working,
surface it at close-out.

## Close-out report

Per `GOV-006`. Per phase: the phase id and **title**, the real output of every command in its
`verification` list, and anything found wrong in the source material.

Then the **spend posture** for the track:

- dispatches run, and how many were resumed after truncation
- any escalation above sonnet — expected to be zero, at most one, justified if present
- fix cycles consumed per phase against the cap of two
- wall-clock against estimate, and the concurrency actually achieved against the ceiling of 2

Paste the output that carries information — a failing check, a row count, a diagnostic the owner
would otherwise reproduce. Summarise the walls of passing checks. **A summary of a failure is not a
result.**

Leave every branch green and unmerged, and name what shows each one:
`git diff dev..agent/<phase-id>`.
