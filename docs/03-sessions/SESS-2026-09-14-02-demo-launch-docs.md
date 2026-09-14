---
schema_version: 1
id: doc-session-demo-launch-docs
code: SESS-2026-09-14-02
title: Diagnose the demo launch failure and document it in the README and the runbook
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-demo-stage
depends_on:
- doc-live-demo
- doc-workbench
---

# Diagnose the demo launch failure and document it in the README and the runbook

## Phase

None. This session claimed no backlog phase. It was owner-directed work of the kind
`/session-start` provides for explicitly ("Owner-directed work sometimes has no phase ... then there
is nothing to claim"): the owner could not start the demo app, the cause was diagnosed live, and the
fix was written into the README and the demo runbook. Peers therefore held no lock against it. The
phases `active` elsewhere were not touched.

The work itself ran on 2026-09-13 and was integrated that night; the close ran after midnight, so
this record's code carries 2026-09-14.

## Verification

No phase means no declared `verification` list. Two sets of checks apply: the mechanical gates run
at close, and the live checks that establish the documented claims are true.

Close gates, re-run in this worktree after the review's corrections and the catalog regeneration:

```
uv run python -m src.governance --catalog -> (catalog regenerated; this record added to catalog.md)
uv run python -m src.governance -> Governance OK: 20 systems, 210 documents, 22 memories, 148 backlog phases
uv run pytest -> 580 passed, 2 warnings
```

These are the numbers after the branch was rebased twice onto a moving `dev`: peers landed a
literature-review close and twelve programme placeholder plans while this session was open, which
is why the document and phase counts are higher than anything quoted in the review below. An
earlier run, taken before this record existed, reported `196 documents` and `580 passed`. The review reproduced neither and correctly identified why: governance discovers
documents by walking the tree, so this record is itself the 197th, and its absence from
`docs/08-governance/catalog.md` failed `test_committed_catalog_matches_regenerated_output` until
the regeneration above. The numbers here are the post-regeneration ones.

Live checks behind the documented diagnosis (run against the owner's running stack):

```
# Before the fix — frontend proxying to :8000, where an unrelated app listens
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5180/api/v1/workbench/injection-sources -> 404
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8010/api/v1/workbench/injection-sources -> 200

# The frontend process's actual environment, both attempts
tr '\0' '\n' < /proc/<vite pid>/environ | grep -E 'D_SYSTEM|VITE_API' -> (no output)

# After relaunching with the env form
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5180/api/v1/workbench/injection-sources -> 200
tr '\0' '\n' < /proc/<vite pid>/environ | grep -E 'D_SYSTEM_DEMO_TERMINAL|VITE_API_TARGET'
  -> D_SYSTEM_DEMO_TERMINAL=1
  -> VITE_API_TARGET=http://localhost:8010
```

The `200` and the two environment lines are the state the owner's stack is in now; they are the
same two checks the README and the runbook now instruct a presenter to run, so the documented
procedure has been executed against a real failure and a real recovery rather than reasoned about.

The full test suite is green here, including the three `test/test_demo_terminal.py` PTY tests that
are intermittently environmental (ideas `000097`/`000099`, owned by `000129`). A green run is not
evidence that issue is resolved.

## Acceptance

Not applicable — no phase, no acceptance list. Against the owner's own ask: the proxy now reaches
the intended backend (the `200` above) and the owner reported the app working, and the cause is
written where the next person will hit it — the README's top and the runbook's `/orient` steps,
step markers and Launch Command Reference.

The `200` is evidence about the proxy, not about the UI. No agent-driven check of the rendered
terminal or the injection dropdowns was run this session, and the review below found the session's
model of the dropdowns' failure state wrong in detail, so the UI half rests on the owner's own
observation.

## Backlog

`docs/09-backlog/backlog.yaml` was not edited this session. No phase was claimed, none was
completed, and `next_up` was not touched.

## Unresolved

- An unrelated local service listening on `:8000` on the owner's machine is what turned a missing
  `VITE_API_TARGET` into 404s rather than connection-refused. Nothing in the repository can fix
  that; the documented `curl` check is the countermeasure, and whether an equivalent process runs
  on the Windows presentation machine is unverified.
- The runbook's two Dry-Run tables still carry unfilled placeholders (`__DATE_TIME_1__`,
  `__ACTUAL_N__`, `__RECORDING_PATH__`). The owner's timed passes, which `REQ-006` R09 closes on,
  have not been run. This session changed the commands those passes execute, not their status.

## Review

Independent review by a fresh (non-fork) sub-agent, given the commit range `e0638c8..d067bc8`, this
record, and the owner's ask as the standard to judge against — no phase meant no acceptance list.
Its findings, verbatim. One detail in them is now stale by design: the review read this record as
`SESS-2026-09-14-01`, the code allocated at the time. A peer integrated a session under that same
code while this one was open, so — per the rule that whoever integrates second renumbers — this
record became `SESS-2026-09-14-02` before merging. The quoted text is left as written rather than
edited to match.


> ## A. Technical correctness of the diagnosis
>
> **Proxy default — holds.** `ts/vite.config.ts:270-271`:
> ```
> const env = loadEnv(mode, process.cwd(), '')
> const apiTarget = env.VITE_API_TARGET || 'http://localhost:8000'
> ```
> `loadEnv(..., '')` with an empty prefix pulls in every `process.env` key, so the frontend process's own environment does reach it. There is no `ts/.env` file in the repo, so the process environment is the only source in practice.
>
> **`/workbench-file/*` gate — holds.** `ts/vite.config.ts:285`: `...(env.D_SYSTEM_DEMO_TERMINAL === '1' ? [serveRepositoryFiles()] : [])`. Same `env` object, so it is the frontend process's own environment (or a `.env` in `ts/`, which doesn't exist here).
>
> **"Terminal availability is unknown" on a 404 — holds.** `ts/src/stage/TerminalRegion.tsx:405-415`:
> ```js
> fetch('/api/v1/demo/stage/terminal-enabled')
>   .then((response) => { if (!response.ok) throw new Error(`status ${response.status}`) ... })
>   .catch(() => { if (!cancelled) setEnabledState('unknown') })
> ```
> A 404 is explicitly converted to a throw, so it lands in the same `unknown` branch as a network error, rendering the message at line 590. Not network-error-only.
>
> I also confirmed the squatter concretely. Both probe paths 404 on `:8000` right now:
> ```
> curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/api/v1/demo/stage/terminal-enabled  -> 404
> curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/api/v1/workbench/injection-sources   -> 404
> ```
>
> **Finding A1 — the documented symptom "empty Commands/Skills/Prompts/Agents dropdowns" is wrong, in two ways.** This claim appears in both new documents (README lines 32 and ~40, runbook line ~276, and inside both Dry-Run table cells as "empty injection dropdowns").
>
> 1. `TerminalRegion.tsx:481-489` passes `disabled={enabledState !== 'enabled'}` to both `CommandPanel` and `InjectionDropdowns`. In the 404 case `enabledState` is `'unknown'`, so `InjectionCategoryDropdown` takes its `if (disabled)` branch (`InjectionDropdowns.tsx:146-156`) and renders a **disabled button labelled "Skills (terminal absent)"** — it cannot be opened at all. The presenter does not see empty dropdowns; they see four greyed-out buttons reading "(terminal absent)".
> 2. **Commands is not proxy-fed.** `CommandPanel.tsx:4` fetches `/demo-commands.json`, a Vite static asset — it never touches the proxy. Naming it alongside the three API-fed dropdowns implies a shared cause that doesn't exist; it goes dark only via the shared `disabled` prop, not via the wrong backend.
>
> There is also a detail worth documenting that the new text misses: if the dropdown *were* openable, the 404 path sets `loadState='missing'` (`InjectionDropdowns.tsx:77-80`), whose message tells the reader to *"Start the backend with `D_SYSTEM_DEMO_TERMINAL=1`"* — actively wrong advice in this scenario, since the backend already has it. That is the strongest argument for the README section existing, and it is not mentioned.
>
> Fix: replace "and the dropdowns are empty" with "and all four injection dropdowns are greyed out, labelled '(terminal absent)'", and drop Commands from the list of proxy-caused symptoms.
>
> **Finding A2 — README overstates the `/workbench-file/*` failure mode.** README says the route "does not exist and the HTML Viewer cannot load pages." The config's own comment (`vite.config.ts`, `serveRepositoryFiles` docstring) and the runbook's pre-existing CRITICAL note (line 260) both say the opposite in the detail that matters: the dev server's history fallback answers those requests with the app shell at **HTTP 200**, and the viewer goes *silently blank* with no error anywhere. A presenter reading the README will look for a 404 they will never see. Fix: align the README wording with the runbook's.
>
> ## B. Accuracy of the new documentation
>
> **`env ...` launch commands — correct.** `ts/package.json:7` is `"dev": "vite"`, so `npm run dev -- --port 5180 --strictPort` passes through correctly; the running process confirms it (`node .../vite --port 5180 --strictPort`). `env VAR=x cmd` is valid POSIX and does keep the assignment attached to a recalled history line, as claimed.
>
> **`curl` check — correct and runnable.** Against the live stack:
> ```
> curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:5180/api/v1/workbench/injection-sources  -> 200
> ```
>
> **`pgrep`/`/proc` check — works interactively, but is fragile.** Run with a clean parent command line it produces exactly what the record claims:
> ```
> D_SYSTEM_DEMO_TERMINAL=1
> VITE_API_TARGET=http://localhost:8010
> ```
> The pattern correctly matches only pid 2000154 (the `node` process) and not its `sh -c vite --port 5180 --strictPort` parent, because of the `node.*` anchor.
>
> **Finding B1 — `pgrep -f` matches the invoking shell whenever the pattern appears in its own command line.** Run through any `bash -c '...'` wrapper (an agent shell, a CI step, `ssh host '...'`), pgrep returns two pids and the redirect dies:
> ```
> $ tr '\0' '\n' < /proc/$(pgrep -f 'node.*vite --port 5180')/environ | grep -E 'D_SYSTEM|VITE_API'
> /bin/bash: line 1: /proc/$(pgrep -f 'node.*vite --port 5180')/environ: ambiguous redirect
> ```
> Reproduced twice here. Adding `| head -1` after the pgrep, or quoting as `"/proc/$(pgrep -f ... | head -1)/environ"`, removes the failure mode.
>
> **Finding B2 — "Empty output means the environment prefix was dropped" is not the only reading.** If no vite process matches (server not running, or started on a different port), the substitution is empty and the shell errors on `/proc//environ` rather than printing nothing; and `grep -E 'D_SYSTEM|VITE_API'` would also match an unrelated `D_SYSTEM_DATA_ROOT`. Neither is serious — the doc does say "both lines must appear" — but "empty output" is imprecise about a case the reader will hit.
>
> ## C. Placement and consistency
>
> **Placement — fair reading of "at the top".** The section is the first `##` in `README.md` (line 9), directly under the title and intro, above "Working Agreement". That is as top as it gets without displacing the project description.
>
> **Finding C1 — the pre-existing "Running the App" block was left unreconciled.** `README.md:108-112` still reads:
> ```
> uv run uvicorn src.main:app --reload   # Backend API on :8000
> cd ts && npm run dev                   # Frontend UI on :5173 (proxies /api → :8000)
> ```
> Not a contradiction (different app, different ports), but two "how to run it" blocks now sit in one README with no cross-reference. A one-line pointer in the later block ("for the demo stage/workbench, see 'Running the demo app' above") would close it.
>
> **Both Dry-Run `/orient` steps updated consistently — holds.** Lines 35 and 51 received the same three insertions (the two `env ` prefixes, the history-recall parenthetical, the curl check with its `404` explanation), worded identically.
>
> **Tables well-formed — holds.** Every row in both tables carries exactly 6 unescaped pipes (5 columns), including the two edited rows. The inserted `curl` command contains no `|`; the pre-existing escaped `\|` in the `ss -tlnp` precondition is untouched.
>
> **Historical records untouched — holds.** `git diff --stat` shows 3 hunks only: the two Dry-Run rows and the Launch Command Reference. The Agent-Driven Pass 1/2 sections (lines 67, 84), the Rehearsal Findings (105) and the Ideas Recorded section (203) are byte-identical.
>
> **Runbook CRITICAL note — no contradiction.** The new text extends it (it covers `D_SYSTEM_DEMO_TERMINAL`; the addition covers `VITE_API_TARGET`) rather than restating or overriding it. See Finding A2 for the one wording mismatch, which is in the README rather than here.
>
> **Finding C2 — a third launch description was missed.** `docs/00-working/demo-runbook.md:179` (Step Markers → /orient step) still says "start backend with `D_SYSTEM_DEMO_TERMINAL=1`, start frontend with `D_SYSTEM_DEMO_TERMINAL=1` and `VITE_API_TARGET=...`" — no `env` prefix, no curl check. It is the owner-performed checklist for the same step the two Dry-Run rows describe. The session claims the fix was carried into the runbook's "`/orient` steps"; two of the three were updated.
>
> ## D. Integration hygiene
>
> **Fast-forward of exactly two commits — holds.** `git rev-list --count e0638c8..d067bc8` is 2; both commits have a single parent (`5525ce5` → `e0638c8`, `d067bc8` → `5525ce5`), so no merge commit and nothing rode along.
>
> **Only the two intended files — holds.**
> ```
>  README.md                       | 47 +++++++++++++++++++++++++++++++++++++++++
>  docs/00-working/demo-runbook.md | 23 +++++++++++++++-----
>  2 files changed, 65 insertions(+), 5 deletions(-)
> ```
>
> **No confidential identifier in tracked content — holds, verified in the primary checkout** (where `_private/portfolio/` actually exists):
> ```
> check_no_private_content: OK (558 tracked files, 31 identifiers checked)
> ```
>
> **Finding D1 — the same gate run in the worktree checks nothing.** In `/code/d-system-worktrees/session-demo-launch-docs`:
> ```
> note: _private/portfolio/ not found — content check skipped (path check still ran; ...)
> check_no_private_content: OK (555 tracked files, 0 identifiers checked)
> ```
> Zero identifiers. This is exactly the "gate passes by not looking" that `AGENTS.md:60-64` warns about, compounded by the session record being untracked (`git ls-files` cannot see it either). The confidentiality claim for this session rests on my primary-checkout run, not on anything run in the worktree. I checked the one candidate string by hand — the process named in the record — and it matches nothing under `_private/portfolio/` (count-only grep, 0 files), so it is not a portfolio identifier. Whether naming a process on the owner's machine in a tracked record is acceptable is the owner's call, not a gate failure. The record must get a staged run of the checker in the primary checkout before close.
>
> ## E. The record itself
>
> **Front matter — conforms.** Against `.claude/skills/checkpoint/SKILL.md:38-49`: `schema_version: 1`, `id: doc-session-demo-launch-docs`, `code: SESS-2026-09-14-01`, `title`, `kind: session`, `status: active`, `owner: repository-owner`, `created`/`updated` both `'2026-09-14'`, `systems`, `depends_on` — all present. The code's date equals `created`. The 09-13 work / 09-14 code gap is explained in the body and does not violate the contract, which constrains code against `created`, not against the work date.
>
> **Section order — conforms.** `# <title>` → `## Phase` → `## Verification` → `## Acceptance` → `## Backlog` → `## Unresolved`, exactly the fixed order in SKILL.md:59-73.
>
> **Finding E1 — neither close gate reproduces as stated.**
>
> Record claims:
> ```
> uv run python -m src.governance -> Governance OK: 20 systems, 196 documents, 22 memories, 136 backlog phases
> uv run pytest -> 580 passed, 2 warnings
> ```
>
> My reruns in the same worktree:
> ```
> Governance OK: 20 systems, 197 documents, 22 memories, 136 backlog phases
> ...
> FAILED test/test_codes.py::test_committed_catalog_matches_regenerated_output
> FAILED test/test_codes.py::test_catalog_flag_writes_committed_file
> 2 failed, 578 passed, 2 warnings in 35.35s
> ```
>
> Both differences have one innocent cause, which I confirmed rather than assumed. Governance discovers documents by `os.walk` (`src/governance/__main__.py:120`), so the untracked session record is itself the 197th document; the run reporting 196 therefore happened *before* the record file existed. The two test failures are that same record missing from `docs/08-governance/catalog.md` — the assertion diff names it directly:
> ```
> - | SESS-2026-09-14-01 | session | active | repository-owner | docs/03-sessions/SESS-2026-09-14-01-demo-launch-docs.md |
> ```
> This is the expected pre-close state, cleared by the catalog regeneration `/session-close` performs in the primary checkout. But as written the record presents two gate outputs that no longer reproduce and does not mention the catalog regeneration still owed. The `## Unresolved` section should say so, and the gate lines should be re-run and re-recorded at close.
>
> **Finding E2 — the record's Acceptance overstates one half.** It claims "the demo app starts and its terminal and injection dropdowns work (verified above at `200`)". The `200` verifies the proxy reaches the right backend; it is not a check that the dropdowns render entries or that the terminal attaches. Given Finding A1 — that the session's model of what the dropdowns do in the failure case is wrong in detail — a `curl` status code is thin evidence for a UI claim. The live checks section is otherwise accurate and I reproduced both of its post-fix lines exactly.
>
> **Everything else in the record holds.** `docs/09-backlog/backlog.yaml` is genuinely untouched (diff stat above). The no-phase framing is consistent with the diff. The `:8000` squatter is real and listening. The caveat that a green run is not evidence the intermittent PTY tests are fixed is properly stated.
>
> ## Summary
>
> The core diagnosis is correct and I reproduced it: the proxy default, the plugin gate, and the 404-to-"unknown" path all hold in the code, and both probe paths 404 on the squatted `:8000` right now. The integration is clean — two commits, two files, fast-forward, no private content in tracked files.
>
> Six things need attention before this is done, in rough priority:
>
> 1. **A1** — the documented symptom is wrong: the dropdowns are greyed out and labelled "(terminal absent)", not empty, and Commands is fed by a static asset, not the proxy. Affects four places across both documents.
> 2. **E1** — both close gates need re-running and re-recording; the catalog regeneration is still owed.
> 3. **D1** — the confidentiality gate checked 0 identifiers in the worktree; needs a staged run in the primary checkout.
> 4. **B1** — `pgrep -f` breaks under any `bash -c` wrapper; add `| head -1`.
> 5. **A2** — README says the route "does not exist"; it actually answers 200 with the app shell.
> 6. **C2** — runbook line 179 is a third `/orient` launch description left un-updated.

### What was done about it

All six were acted on in this session, before close, on the branch `agent/session-demo-launch-docs`:

- **A1** — corrected in four places: the README's symptom heading and bullet, the runbook's Launch
  Command Reference, and both Dry-Run `/orient` rows. The text now says all four dropdowns render as
  disabled buttons labelled "(terminal absent)", and states that Commands is fed by the static
  `/demo-commands.json` and so is not diagnostic of the proxy. The reviewer's point about the
  misleading in-app message was added to the README as a "do not trust the in-app message" note,
  since it is the strongest reason the section exists. I verified all three claims in the source
  myself rather than accepting them: `InjectionDropdowns.tsx:144-153` (the disabled branch and its
  label), `CommandPanel.tsx:4` (`/demo-commands.json`), `TerminalRegion.tsx:482,487` (the shared
  `disabled` prop), `InjectionDropdowns.tsx:166-169` (the `missing`-state advice).
- **A2** — README now says the request does not 404: the history fallback answers with the app shell
  at HTTP 200 and the viewer goes silently blank, matching the runbook's pre-existing CRITICAL note.
- **B1** — both `/proc` checks now use `"/proc/$(pgrep ... | head -1)/environ"`, with the reason
  named in the surrounding prose.
- **C1** — the README's ordinary "Running the App" block now points to the demo section above it.
- **C2** — the Step Markers `/orient` entry (the third launch description) now carries the `env`
  form and the curl check.
- **E1/E2** — the gate lines in `## Verification` were re-run after the catalog regeneration and
  re-recorded, with the earlier numbers and the reason they moved kept in the record; the
  `## Acceptance` claim was narrowed to what the `200` actually proves.
- **Code collision** — `SESS-2026-09-14-01` was taken by a peer's literature-review session that
  landed on `dev` during this close. This record was renumbered to `SESS-2026-09-14-02`, the file
  renamed, and the catalog regenerated against the new code. No choice was involved — the protocol
  names the second integrator as the one who renumbers — so nothing was recorded in `GOV-003`.
- **D1** — the record no longer names the unrelated `:8000` process, so the one candidate identifier
  is gone from tracked content. The meaningful confidentiality run is the primary checkout's, which
  the reviewer performed (`31 identifiers checked`) and which runs again at integration.

## Decisions

**The session ran unclaimed, and no phase was invented for it.** The owner asked a support question
that turned into a defect hunt and then a documentation fix. `/session-start` provides for exactly
this ("Owner-directed work sometimes has no phase"), and `AGENTS.md` forbids manufacturing a phase
to have something to claim. The cost is that this record has no `acceptance` list to be judged
against, which is why the review was briefed with the owner's ask instead.

**Documentation went to the README's top, as asked, rather than only to the runbook.** My own
inclination was the runbook alone — it is the demo-day document, and the README's top is prime
space. The owner directed the README, explicitly and by position, so the README got the fuller
treatment and the runbook got the same fix carried into its three launch descriptions. On the
evidence the owner was right: the failure is a first-run failure, and a first-run failure belongs
where someone starts, not in a document they only open on demo day.

**The work was done in worktrees even though it was documentation only.** `AGENTS.md` states that
documentation-only work is not an exception, and this session used two worktrees in sequence — one
for the two content commits, one for this record — rather than editing `dev` directly.

**The record does not name the `:8000` process.** The reviewer flagged it as the owner's call rather
than a gate failure. I removed it because the name identifies unrelated work on the owner's machine
and carries no information the sentence needs — "an unrelated local service" is the operative fact.
This is a judgement I made without asking; reverse it if you would rather the record be specific.

## Corrections

**The first diagnosis was incomplete, not wrong.** I identified the missing variables and gave a
restart command; the owner came back with "same issue still". The second look found the restart had
gone out as a bare `npm run dev --port 5180 --strictPort` — a history recall that dropped the
environment prefix. The fix was the `env ...` form, and that near-miss is the reason the `env` form
and the "verify before trusting the UI" check are now in both documents rather than just the bare
commands.

**The documented symptom was wrong in detail and the independent review caught it.** I wrote "empty
dropdowns" from the owner's own words plus the API 404, without opening `InjectionDropdowns.tsx`.
The dropdowns are disabled and labelled, not empty, and one of the four is not proxy-fed at all. A
presenter matching my text against the screen would have seen something that did not match. This is
the failure mode the review step exists to catch, and it was the review, not the session, that
caught it.

## Left undone

- **The owner's timed dry-run passes.** Both Dry-Run tables still carry `__DATE_TIME_N__`,
  `__ACTUAL_N__` and `__RECORDING_PATH__` placeholders. `REQ-006` R09 closes only on the owner's own
  recorded passes; this session changed the commands those passes execute and nothing about their
  status.
- **Whether the `:8000` collision exists on the Windows presentation machine.** Unverifiable from
  here. The `curl` check now in the runbook is the countermeasure, but nobody has run it there.
- **The intermittent PTY tests** (`test/test_demo_terminal.py`, ideas `000097`/`000099`, owned by
  `000129`) remain unfixed and unaddressed by this session. They passed in every run here, which is
  not evidence of a fix.
- **Finding B2 was judged not worth a change.** The reviewer noted that "empty output" is imprecise:
  with no matching process the shell errors rather than printing nothing, and the grep would also
  match an unrelated `D_SYSTEM_DATA_ROOT`. The corrected text now names the two exact lines that must
  appear, which covers the reader's decision; spelling out every failure mode of a diagnostic
  one-liner costs more than it returns.
