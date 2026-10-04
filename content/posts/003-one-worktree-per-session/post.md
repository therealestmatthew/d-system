# 003 — One worktree per agent session, even for a docs edit

- **Status:** draft
- **Arc stage:** 5 Backlog, claims and multi-session coordination (posted early as a lesson)
- **Pillar:** Incident
- **Image:** none. The story is a sequence of events; text carries it, and a later animation
  (see "Later-stage formats" in `../../arc.md`) can show it.
- **Drafted against:** dev `518642d` (2026-10-04)
- **Posted:** —

## Single post

> Rule I learned running several AI coding sessions on one repo: every session gets its own git
> worktree, even for a docs-only edit. One session switched branches in the shared checkout, and
> another session's next two commits landed on the wrong branch.

## Thread

1. When I started running several AI coding sessions on one repository, I let documentation-only
   sessions work in the main checkout. The reasoning: a Markdown edit can't corrupt a test run that
   isn't happening.

2. That is true of runs and false of branches. On 2026-09-12 a session in the main checkout switched
   its branch, and another session's next two commits landed on that branch instead of the
   integration branch.

3. One was repaired by a ratified fast-forward. The second was caught only because `git branch -d`
   refused to delete a branch that was not fully merged.

4. The same day, two sessions drew wrong conclusions from accurate reads of a checkout that was
   mid-switch. One briefly believed a commit was lost. The other nearly recorded a real ordering
   failure as a flaky test.

5. The shared resource was never the virtualenv. It was the branch pointer and the index, and a
   docs-only session moves both as much as a code session does. I had drawn the exception around
   the wrong thing.

6. The rule since then: every session works in its own git worktree. The only writes to the main
   checkout are the backlog claim and the generated file it changes, because the claim on the
   integration branch is the lock the other sessions read.

## Sources

| Claim | Source |
|---|---|
| Documentation-only sessions worked in the primary checkout with the owner's approval; the reasoning about runs | `docs/08-governance/GOV-003-backlog-decisions.md` line 100-106 ("A solo agent on a documentation-only phase works in the primary checkout") |
| "True of runs and false of branches"; the three incidents on 2026-09-12; the branch pointer and the index | `GOV-003`, "Every session works in a worktree; the documentation-only exception is withdrawn", lines 328-362 |
| The rule and its two exceptions (claim commit, catalog regeneration) | `GOV-003` lines 336-341; `AGENTS.md`, "Concurrent agents: work in a worktree" |

## Notes for the owner

- The third incident that day (a session relaying an instruction to move work that was already
  isolated) is left out to keep the thread at six posts.
- "the generated file it changes" is the governance catalog (`docs/08-governance/catalog.md`); named
  generically because the catalog needs its own explanation.
