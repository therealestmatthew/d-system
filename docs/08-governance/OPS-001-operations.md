---
schema_version: 1
id: doc-governance-operations
code: OPS-001
title: Governance operations
kind: operation
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-06'
systems: [sys-governance, sys-delivery]
depends_on: [doc-governance-protocol]
---

# Governance operations

## Check or list the repository

From the repository root:

```bash
uv sync --extra dev
uv run python -m src.governance
uv run python -m src.governance --inventory
uv run python -m src.governance --catalog
uv run pytest test/test_governance.py test/test_codes.py
```

The first command installs the validator dependency. A successful check exits 0 and prints component/document/memory counts. Invalid input exits 1 with actionable file/field diagnostics. Review warnings do not fail CI. Inventory output is derived Markdown on stdout and is suppressed when validation fails. No database is required.

## Add or change documentation

1. Copy [the template](../../templates/governance/document.md) to the appropriate governed directory.
2. Run `uv run python -m src.governance --next-code <kind>` and name the file `<code>-<slug>.md`.
   Add `--parent <doc-id>` for a child plan. Never choose a code by reading the directory.
3. Assign a unique permanent `doc-*` ID, owner, real dates, kind and systems; remove unused optional fields.
4. Write the outcome and evidence. For a plan, start at `draft`; specify acceptance criteria before implementation.
5. Add a registry entry only for a new independent capability. Planned systems may reference their design document; implemented systems need actual implementation paths.
6. Regenerate the catalog: `uv run python -m src.governance --catalog > docs/08-governance/catalog.md`.
7. Run the validator and relevant code tests. Review the diff using the lifecycle rules in the protocol.

For memories, use the existing [memory procedure](../../brain/procedures/add-brain-memory.md) and schema, run governance validation, then rebuild only when deliberately synchronizing source data. This governance task itself requires no repository database rebuild.

## Respond to failures

| Diagnostic | Action |
|---|---|
| Missing/invalid front matter | Use the template; correct unknown fields, dates or misplaced kind |
| Unknown owner/system/tag/reference | Correct a typo or define the referenced item before using its ID |
| Duplicate ID or dependency cycle | Preserve the original ID; rename the new item or remove the incorrect prerequisite edge |
| Missing evidence/path | Restore/update the reference; do not mark a plan complete before evidence exists |
| Supersession mismatch | Change old status and replacement references together |
| Review overdue | Read the actual source, refresh content and `updated`, then set the next review date |
| `missing code` | Allocate one with `--next-code <kind>`; do not invent a number |
| `duplicate code` | A peer took the same number; renumber the later document and rename its file |
| `filename must start with` | Rename the file to its code, or correct the code if the file is right |
| `is reserved` | Remove the reservation in the same change that adds the document |
| `is retired and can never be reused` | Choose a fresh code; retired numbers are never reissued |
| `requires a parent` / `does not match parent` | Align the sub-code stem with the parent's code |
| `code date ... must equal created` | A dated code must carry its own document's created date |
| Catalog diff in CI | Regenerate with `--catalog` and commit the result; never hand-edit it |
| Symlink/protected path | Reference public repository files directly; the checker does not follow protected sources |
| `at most N phases may be active` | Wait for a claim to complete or release one; do not raise `max_active` to fit one more agent |
| `concurrent phases share system` / `share deliverable path` | Claim different work; the overlap is the collision the check exists to prevent |
| `concurrent phases are dependency-linked` | Finish and merge the prerequisite first; a dependent phase cannot be built on unmerged work |
| `requires an agent claim` / `holds N active phases` | Name the claiming agent, or release the other phase before claiming this one |
| `must release its agent claim` | Remove `agent` when returning a phase to queued/deferred/cancelled, and remove the worktree |

A stale date is a review cue, not permission to discard history. If a policy change itself is wrong, revert its focused commit or amend the schema, semantic rules, protocol and tests together. Never silence a new document by adding a blanket directory exemption. No recovery operation requires dropping DuckDB tables.

## Routine review

During weekly review, run the inventory, scan overdue warnings, and compare active plans with actual work. At plan completion, review acceptance evidence and component maturity together. Before a non-obvious architecture change, create an ADR. Branch protection and external approvals are outside this command; no external configuration is changed automatically.

## Plan and run a session

Use `uv run python -m src.governance --ready` to list eligible phases and `--backlog`
for all phases, details and plan coverage. Both reports open with the active-claims table and
carry a **Conflicts** column naming any active phase a candidate would collide with. Follow the
[backlog workflow](GOV-002-backlog-protocol.md) to capture new plans, claim a phase and record completion
evidence. The default check also validates the required backlog, rejects uncovered open plans, and
rejects unsafe concurrent claims.

## Close a session

**Interim.** This records the procedure actually followed, so that closing is not done from memory
each time. `phase-ses-03` replaces it with the governed protocol, and `phase-ses-01` decides the
session-type taxonomy this deliberately does not pre-empt. Where this section and a later governed
protocol disagree, the protocol wins.

Perform these in order. Do not mark a phase complete before the checks pass.

```bash
# 1. run every command in the phase's verification list; keep the real output
# 2. allocate the session code -- its date must equal the record's created date
uv run python -m src.governance --next-code session
# 7. regenerate the catalog and verify
uv run python -m src.governance --catalog > docs/08-governance/catalog.md
uv run python -m src.governance && uv run pytest
```

3. Write `docs/03-sessions/SESS-YYYY-MM-DD-NN-topic.md` with governed front matter (`kind: session`),
   covering outcomes, evidence, any deviation from `AGENTS.md`, and what is unresolved. Record
   verification output as observed — a failing check is a result, not a step to retry until quiet.
4. Confirm each `acceptance` condition is genuinely met.
5. Update the phase: `status: complete`, `session:`, `completion_evidence:` naming files that exist
   now, and `result:` summarising the actual output. Keep the `agent` field as the record of who did
   the work.
6. Remove the phase from `next_up` in the same change.
8. Commit in narrow batches, one concern each.

**When the session ends incomplete** — the more common case. Write the session record anyway, naming
what was done and what was not. Return the phase to `queued` with an exact `next_action`, and release
the `agent` claim when you do; leave it `active` only if you are continuing immediately. Never mark a
phase complete with an unmet acceptance condition.

**When the owner directs work outside any claimed phase**, that work still needs a session record.
Governed work is normally phase-shaped; the record is what keeps unphased work from being invisible.

A remote exists, so `git fetch`, `git pull` and `git push` all work — but ask the owner before
pushing (see `AGENTS.md`, *Confidentiality and publishing*). A worktree is required only under the
conditions in [GOV-003](GOV-003-backlog-decisions.md); a solo agent on a documentation-only phase
closes in the primary checkout on `main`.

## Claim and run a phase as an agent

Claim on `main` first — the catalog is the lock table and this command is the lock check — then work
in an isolated worktree. [AGENTS.md](../../AGENTS.md) has the full step list; the mechanics are:

```bash
git switch main                                   # git pull too, once a remote exists
uv run python -m src.governance --ready          # pick a phase whose Conflicts column is —
# edit docs/09-backlog/backlog.yaml: status: active, agent: agent-<name>, bump updated
uv run python -m src.governance                  # the lock check; must pass before committing
git commit -am "Claim phase-html-03"

git worktree add -b agent/phase-html-03 ../d-system-worktrees/phase-html-03 main
cd ../d-system-worktrees/phase-html-03
uv venv && uv sync --extra dev
```

The worktree is a sibling of the repository, never inside it, so `pytest`, `ruff`, `mypy` and the
governance Markdown scanner never walk a second copy of the tree. `.venv/` and `data/` are gitignored
and therefore per-worktree; install and rebuild them locally rather than sharing a peer's. Choose an
explicit free port for any dev server (`--port 8010`); `:8000` and `:5173` are not reserved for you.

To finish: run the phase's `verification` commands, write the dated session record, update the phase
with `session`, `completion_evidence` and `result`, then

```bash
git rebase main
uv run python -m src.governance && uv run pytest   # after the rebase; this run gates integration
git switch main && git merge --ff-only agent/phase-html-03
git worktree remove ../d-system-worktrees/phase-html-03 && git branch -d agent/phase-html-03
```

A rejected push means a peer integrated first: `git pull --rebase`, re-run both checks, and confirm
your claim is still safe before retrying. A `backlog.yaml` conflict is resolved by keeping both
sides — never `--ours` or `--theirs`, which silently discards a peer's phase. A conflict under
`src/`, `ts/`, `schemas/` or `sql/` means two phases declared disjoint boundaries they did not
respect: stop, fix the declarations, and record any resolution that required a real choice in
[the decision record](GOV-003-backlog-decisions.md). A worktree left behind by an abandoned claim is removed
with `git worktree prune` after `git worktree remove`.
