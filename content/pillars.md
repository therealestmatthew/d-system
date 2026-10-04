# Content pillars

Five recurring post types. A five-post week normally has one of each, so every arc stage is covered
from five angles. Each pillar names the repository records it draws from; a post cites the specific
file in its `Sources` section.

| # | Pillar | What the post does | Image |
|---|---|---|---|
| 1 | Mechanism | Explains one part of the system and why it is built that way | Usually a diagram |
| 2 | Incident | Tells one failure, what it cost, and the rule or check it produced | Sometimes; often text only |
| 3 | Numbers | Reports a measured fact about the system and what it shows | A chart or a stat card |
| 4 | Artifact | Shows a real file: a prompt, an agent definition, a procedure, a page | A screenshot or the file itself |
| 5 | Reflection | A short first-person take on what working this way is like | Text only |

## 1. Mechanism

How a part of the pipeline works. One mechanism per post.

| Topic | Source evidence |
|---|---|
| Append-only idea log and its fold | `tools/append_idea.py`, `src/db/ideas.py`, `ADR-007` |
| Ungoverned staging for parked ideas | `ADR-010`, `docs/00-working/` |
| Triage, one agent per idea | `.claude/agents/idea-triage.md`, `ARCH-006` stage 2 |
| Partition with an adversary and a control run | `PLAN-025`, `REQ-009`, `.claude/agents/partition-adversary.md` |
| Five gates, nine stages, a failure path for each stage | `ARCH-006` |
| Three-altitude plan review | `GOV-018`, `docs/08-governance/reviews/` |
| Claims, declared systems and `max_active` | `docs/09-backlog/backlog.yaml`, `ADR-003`, `AGENTS.md` |
| One worktree per session | `AGENTS.md` "Concurrent agents: work in a worktree", `GOV-003` 2026-09-12 ruling |
| Session roles and the message protocol | `GOV-017` |
| Pre-commit guards | `tools/git-hooks/pre-commit`, `tools/check_no_private_content.py`, `src/governance/` |
| Structure and content separated | `ADR-009`, `_data/` (fictional set) vs `_private/portfolio/` |
| Deterministic engine pages | `tools/generate_engine_pages.py`, `REQ-036`, `OPS-028` |
| The portable plugin | `plugins/idea-realization/README.md` |

## 2. Incident

A failure told in order: what happened, how it was caught, what changed. Each source records the
incident in the repository's own words.

| Incident | Source evidence |
|---|---|
| The same document code issued to two decisions | `GOV-003` "Concurrency collisions", 2026-09-06 |
| Two sessions allocated the same idea id; then a 36-idea collision with no git conflict | `GOV-003` "Concurrency collisions", 2026-09-12 and 2026-09-13; `brain/procedures/yield-and-renumber-a-collided-identifier.md` |
| A branch switch in the shared checkout sent another session's commits to the wrong branch | `GOV-003`, "Every session works in a worktree" (2026-09-12) |
| A piped command hid a failed merge and the worktree was deleted | `brain/procedures/a-pipe-discards-the-exit-code-you-were-guarding-on.md` |
| A heredoc ended early and bash ran prose as commands | `brain/procedures/never-pass-file-content-through-a-heredoc.md` |
| An infinite render loop passed build, lint, tests and governance | `brain/procedures/runtime-behavior-needs-runtime-evidence.md` |
| A check built on a command that only printed | `brain/procedures/a-check-that-cannot-fail-is-not-a-check.md` |
| Four phases silently reverted while governance exited 0 | `src/governance/regression.py` |
| Delegated measurements reported false results three times | `brain/procedures/recompute-a-delegated-measurement.md` |
| Heavy schemas produced documents that existed only to satisfy the schema | `ADR-010` |

## 3. Numbers

Each number is computed at a named commit and the command is recorded in the post's sources, so the
post can be re-checked. Examples at dev `518642d` (2026-10-04):

| Fact | Value | How it is computed |
|---|---|---|
| Ideas captured | 564 | `fold(load_events())` in `src/db/ideas.py` |
| Events in the idea log | 2,717 | `load_events()` |
| Ideas by status | 494 triaged, 39 open, 13 promoted, 10 reviewing, 7 discarded, 1 delivered | `fold()` |
| Plan review findings | 100 across 12 dispositioned reviews: 18 blocker, 53 major, 29 minor | `docs/08-governance/reviews/*.json` |
| Partition | 371 of 383 ideas in 87 groups under 12 tracks | `docs/00-working/idea-partition-2026-09-23.md` |
| Phases blocked by one claim's system | 46 of 74 ready phases, 2026-09-22 | `GOV-017` |
| Commits on the integration branch | 1,648 | `git rev-list --count dev` |

Recompute every number at the commit the post is drafted against; the values above go stale.

## 4. Artifact

A real file, shown and explained. The file is the content; the post says what to look at.

| Artifact | Source |
|---|---|
| The adversarial reviewer prompt | `.claude/agents/partition-adversary.md` |
| A brain procedure | `brain/procedures/` |
| How agents report to the owner | `docs/08-governance/GOV-006-conversation-guidelines.md` |
| The portable working agreement | `plugins/idea-realization/templates/CLAUDE.md`, `AGENTS.md` |
| An engine page | `_public/engine/index.html`, `ideas.html`, `backlog.html` |
| A plan review record | one file in `docs/08-governance/reviews/` |

Shared files follow the rules for shared reference files in [arc.md](arc.md) and the
confidentiality rules in [README.md](README.md).

## 5. Reflection

Short, first person, no image. What it is like to direct several agent sessions, what the owner
would do differently, a question to readers. A reflection still cites the record it reflects on
when it states a fact.
