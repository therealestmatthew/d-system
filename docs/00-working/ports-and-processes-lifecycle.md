# Ports and system processes: lifecycle exploration

Staging document for `phase-arch-11` (the ports and system processes lifecycle exploration),
governed by the idea-staging decision (`ADR-010`): ungoverned, no front matter, nothing here is
scheduled. It answers the workbench architecture requirement `REQ-011` R17 and is the input to
`phase-arch-12` (building the port and process management application). It proposes no application.
Where a decision belongs to `phase-arch-12`, this document states the question and the evidence, not
the answer.

Source ideas: `000142` (explore ports and system processes and their management: lifecycle, when and
how to kill them), `000143` (small application for managing and visualizing port usage and system
processes), with `000099` (three demo-terminal PTY tests fail on dev and on origin), `000129` (fix
the three pre-existing environmental PTY test failures) and `000138` (system for tracking and
managing agent anti-patterns) supplying incidents.

## How to read the evidence

Every claim carries one of two labels.

- **Recorded** cites a repository document by code and date. The incident sections rely on these.
- **Observed here** is a fresh reproduction made on 2026-10-08 in a Linux sandbox (kernel 6.18,
  bash 5.2.21, the worktree's own `.venv` for Python and uvicorn). Nothing was changed in the
  repository to make it. Section 10 lists the commands, so `phase-arch-12` can re-run them.

Windows and macOS were not run. Cells and claims that depend on them are marked **owner-machine, not
run**, and are collected in section 8.

## 1. Terms used here

| Term | Meaning in this document |
|---|---|
| Listener | A process that has a socket in the LISTEN state on a port. |
| Squatter | A listener on a port that a different program expected to own. Used for any holder that is not the intended server. |
| Process group, session | The kernel groupings a signal can address at once. `kill -- -<pgid>` signals the whole group. A child that calls `setsid` leaves both. |
| Orphan | A process whose parent has exited. On Linux it is reparented to PID 1 and keeps running. |
| Zombie | A process that has exited but whose parent has not yet collected its exit status. It holds no port and runs no code. |
| Stale server | A running server whose code or configuration predates the files on disk. It still answers requests. |

## 2. What this repository starts

| Process | Started by | Port | Shape | Ends normally by | Source |
|---|---|---|---|---|---|
| Backend API (uvicorn) | The person or agent, `uv run uvicorn src.main:app [--reload] --port N` | 8000 default; 8010 demo; any explicit free port in a worktree | With `--reload`: `uv run` wrapper, reloader, worker (observed, section 4.3) | Ctrl-C in its terminal | `README.md`, `AGENTS.md`, `docs/00-working/demo-runbook.md` |
| Frontend dev server (Vite) | The person or agent, `cd ts && npm run dev -- --port N --strictPort` | 5173 default; 5180 demo | `sh -c vite ...` parent and a `node` child (recorded) | Ctrl-C in its terminal | `SESS-2026-09-14-02` (review finding B1), `README.md` |
| Terminal shell (PTY) | The backend, one per websocket, through `src/demo/posix.py` or `src/demo/windows.py` | none | Shell is its own session leader (`start_new_session=True`); up to 6 at once | Websocket close, 300 s idle timeout, or confirmed drop in the UI; teardown is `close()` (4.4) | `src/api/routes/demo_terminal.py`, `ADR-014` |
| Reveal opener | The backend, `POST /reveal`, `subprocess.Popen` of `xdg-open` or `explorer.exe`, never waited on | none | Single fire-and-forget child | The opener itself | `src/api/routes/workbench.py`, `ADR-015` rule 5 |
| Review-check command | `tools/run_review_checks.py`, `bash -c` in its own session | none | Process group, killed whole on timeout | Exit, or `os.killpg(..., SIGKILL)` after the timeout | `tools/run_review_checks.py`, `SESS-2026-10-01-04` |
| Orchestrator daemon | `python -m src.orchestrator start` | none | One per primary checkout, guarded by `flock` | `stop` sends SIGTERM to the lock holder | `src/orchestrator/daemon.py`, `SESS-2026-09-23-06` |
| Test-suite shells | `uv run pytest`, which opens real PTY shells in `test/test_demo_terminal.py` | none (test client) | Short-lived | The test finishing | `SESS-2026-09-10-11` |

Three facts about this inventory matter later.

1. Nothing in the repository records who launched a dev server or in which worktree. The dev servers
   are started by hand. There is no launcher, no pid file and no end-of-session cleanup for them.
   The two processes with a recorded lifecycle (the daemon and the review runner) are the only ones
   a script starts.
2. The default ports 8000 and 5173 are the ones the code assumes (`ts/vite.config.ts` proxy default,
   `src/main.py` CORS origin). Every other port is chosen by hand.
3. Observed here: a process's command line names its worktree when it was started from a worktree
   virtual environment. A peer's server on 8011 appeared in `ps` with
   `.../d-system-worktrees/phase-arch-02/.venv/bin/python3 ... uvicorn src.main:app --port 8011`.
   It was only read, not signalled. This is the one ownership signal available without a launcher.

## 3. The three recorded incident families

### 3.1 The port-8000 conflict

The owner's idea `000142` (recorded 2026-09-11) refers to "the port-8000 conflict noted mid-session
during the workbench builds". Which recorded event that is has not been established. The triage
annotation on `000142` points to `SESS-2026-09-11-08` (layout assignment model, `phase-wb-09`), but
that record states only that orphaned dev servers were killed and names no port. The table lists the
recorded port-8000 collisions found. The first two rows are collisions and are the same mechanism on
different days. The next two give context (where the 8000 default comes from, and the check working
when both ends are right) and the last is the standing rule.

| Date | Document | What happened |
|---|---|---|
| 2026-09-10 | `SESS-2026-09-10-07` (demo content, runbook, reset tool and rehearsals) | Rehearsal validator `D05-W` reproduced it: with `VITE_API_TARGET` unset, the Vite dev proxy targets `http://localhost:8000` instead of the demo backend on 8010, "and every stage route 404s if anything else holds port 8000". The same record says the coordinator "cleared the stray dev-server port collision" on the branch. Fix: the runbook's `/orient` step gained a port-free precondition, `ss -tlnp \| grep -E "8010\|5180"`, and both launch commands gained `VITE_API_TARGET`. |
| 2026-09-13 to 2026-09-14 | `SESS-2026-09-14-02` (diagnose the demo launch failure and document it in the README and the runbook) | The owner could not start the demo. Live checks showed the frontend on 5180 answering `404` for `/api/v1/workbench/injection-sources` while the backend on 8010 answered `200`. An unrelated local program was listening on 8000 and answering `404` for every API path. The frontend process's `/proc/<pid>/environ` held neither `D_SYSTEM_DEMO_TERMINAL` nor `VITE_API_TARGET`, because the variable prefix was lost when the launch command was recalled from shell history. After relaunching with `env ...` the same request returned `200`. |
| 2026-09-10 | `SESS-2026-09-10-04` (demo stage frontend, `phase-demo-02`) | Origin of the dependency. `ts/vite.config.ts` made the proxy target configurable through `VITE_API_TARGET` with the default "unchanged at `:8000`", and its validator confirmed the default was untouched and no `:8010` was hardcoded. Every launch that omits the variable therefore targets 8000. |
| 2026-09-11 | `SESS-2026-09-11-05` (rehearsal refresh, `phase-wb-07`) | The check working when both ends are right: the validator "ran the `curl` check live against running dev servers and got the documented `200`" and ran the `/proc/<pid>/environ` diagnostic with the documented output. It shows the check is executable; it records no collision. |
| Standing rule, undated here | `AGENTS.md` (concurrent agents: worktrees) and `OPS-001` (governance operations) | The standing rule: "Do not assume `:8000` or `:5173` is yours", and pick an explicit free port. The coordinator briefs (`_tmpagent/demo-track-coordinator.md`, `_tmpagent/p10-track-coordinator-v2.md`) repeat it because "peers are running". Later records show it applied: ports 8011/8012/5181/5182 in `SESS-2026-10-03-01`. |

Mechanism, as the records establish it:

- The conflict is not a bind failure. The squatter owned 8000 first, nobody tried to bind it, and the
  frontend connected to it as a client. The result was a successful TCP connection and a `404`, which
  the UI rendered as "Terminal availability is unknown" with four greyed-out injection dropdowns
  (review finding A1 in `SESS-2026-09-14-02`). Neither symptom names a port.
- The in-app 404 message for the dropdowns says to start the backend with `D_SYSTEM_DEMO_TERMINAL=1`,
  which is wrong advice in exactly this case (same review). A user following it would restart the
  backend and see no change.
- `SESS-2026-09-14-02` recorded the program holding 8000 only as "an unrelated local service". The
  review flagged naming it as the owner's call, and the author removed the name because it identifies
  unrelated work on the owner's machine. That is a standing constraint for any tool that displays
  listeners (section 7).
- Detection that worked was manual and had its own faults: `ss -tlnp`, `curl` for a status code, and
  `tr '\0' '\n' < /proc/<pid>/environ`. The review found that `pgrep -f` also matches the invoking
  shell when the pattern is in that shell's own command line (finding B1), so the documented command
  needed `| head -1`.
- Not established: whether the 8000 collision exists on the Windows presentation machine.
  `SESS-2026-09-14-02` lists it as unverifiable from the Linux side. **Owner-machine, not run.**

### 3.2 Orphaned and stale dev servers left by cut-off agents

`000138` (the agent anti-pattern system idea, 2026-09-11) lists "orphaned dev servers left by
cut-off agents" in its starter catalog. `000246` (terminal panel drops its connection, 2026-09-15)
names the same material as a hypothesis for an unprovoked terminal drop: "an agent's cut-off session
leaving an orphaned process". The records below are every instance found.

| Date | Document | What happened |
|---|---|---|
| 2026-09-10 | `SESS-2026-09-10-12` (layout engine and notes strip, `phase-wb-02`) | Stale dev servers from an earlier test run "were masking the layouts middleware". The validator diagnosed staleness by comparing the process start time with `vite.config.ts`'s modification time, killed the processes and restarted them. |
| 2026-09-10 to 2026-09-11 | `SESS-2026-09-10-13` (terminal panel rework, `phase-wb-03`) | The orchestrator and a gate dispatch "died mid-run when the API session limit hit". Recovery was by resuming the agents, "never re-running from scratch". This record does not mention a server left behind; it is the cut-off event that produces one. |
| 2026-09-11 | `SESS-2026-09-11-08` (layout assignment model, `phase-wb-09`) | "Orphaned dev servers from a truncated gate dispatch were killed", listed under operational notes as resolved. Seven dispatch truncations over two phases are tallied in `000138`; the post-mortems are `brain/procedures/scope-dispatches-to-the-turn-budget.md` and `brain/procedures/runtime-behavior-needs-runtime-evidence.md`. |
| 2026-09-14 | `SESS-2026-09-14-09` (widen the HTML Viewer to images and markdown) | A dev server started at 20:45 served stale code after Vite restarted it "onto an intermediate tree state during one of the rebases". `README.md` answered `application/octet-stream`. The reviewer reported this; the author first disbelieved it because earlier `curl` results had shown the new behavior. Re-running confirmed the reviewer. The record states the lesson: the earlier results were genuine when taken and the server drifted afterwards. |
| 2026-10-04 | `SESS-2026-10-04-09` (fix the terminal route's cap race, cap refusal reason and shell override) | "A stale server held the port and a `pkill` pattern matched its own shell, leaving dev's route file in the worktree uncommitted." Restored with `git checkout`. |

Mechanism:

- A server outlives the session that started it because nothing ties the two together. The server is
  a background process of a shell, and when the agent is cut off the shell and the server are not
  necessarily stopped together.
- Orphaned servers are harmful in two ways, both recorded: they hold a port (the next launch on the
  same port fails, or the next client connects to the old server), and they serve code that no longer
  matches the working tree (`SESS-2026-09-10-12`, `SESS-2026-09-14-09`). The second is the more
  expensive, because the old server answers normally.
- Observed here, section 4.3: killing only the parent of a `--reload` server leaves the worker alive,
  reparented to PID 1, still holding the listening socket and still answering requests. This is the
  concrete orphaned-server state, and it is reached by a plain SIGKILL of the process that was
  visible to the person.
- Kill by pattern is the recurring hazard (`SESS-2026-09-14-02` finding B1, `SESS-2026-10-04-09`).
  The pattern matched the killer's own shell. This was reproduced by accident during this
  exploration: a probe script that called `pgrep -f` with a pattern also present in its launching
  `bash -c` command line matched that shell's pid and signalled it, and the tool call exited 1.

### 3.3 PTY child reaping and the `alive` investigations

The terminal backend starts a shell per websocket and must end it. `000099` (2026-09-11) recorded
three failing tests in `test/test_demo_terminal.py`; `000129` (same day) recorded the owner's request
to fix them. Both were discarded on 2026-09-13 and revisited on 2026-09-24. The investigation showed a shell
that failed to exit within the test's deadline for an environmental reason (below). It was not an
investigation of child reaping; reaping proper is examined in section 4.4.

What the records establish:

- The failing assertion was `adapter.alive is False` five seconds after writing `exit\n` to the
  shell (`000099` body). It was not flaky: two consecutive runs failed identically.
- The first suspect was the session registry commit `f0801af` (phase-wb-01). The coordinator's
  finding on `000099` cleared it with a timeline: the failures were already present before that
  commit merged, and with the stale lock removed the file passed 46 of 46 with the commit in place.
- The cause was environmental. A lock file `~/.pyenv/shims/.pyenv-shim` made every spawned bash run
  pyenv's rehash hook, which stalls (60 seconds in `SESS-2026-09-12-02`) and writes
  `pyenv: cannot rehash: couldn't acquire lock` into the PTY output. The lock was recreated by
  concurrent agent activity, so removing it once was not a fix (`SESS-2026-09-10-11`: "recurrent
  contention, not a one-time stale file"). The first stale-lock removal was treated as the fix and
  the recurrence corrected that.
- The consequence was a standing evidence gap: every gate from `phase-wb-01` to `phase-wb-09` carried
  "3 failed, known environmental" (`000129`). `000099`'s resolution note of 2026-09-13 records the
  suite as green on dev afterward, with no status event on `000129` recording what changed.

What was ruled out and what was never examined:

- `PosixPtyAdapter.close()` was not shown to be at fault. `000099` found no change was needed in
  `src/demo/posix.py`.
- Whether the shell's own children are reaped was never part of that investigation. Other records
  cover it. `SESS-2026-09-10-06` (stage terminal interaction, `phase-demo-06`) found and fixed an
  orphan: a hard-killed client left `sleep 6666` running because `websocket.receive()` never returned,
  so `finally: adapter.close()` never ran. The fix was the idle timeout
  (`D_SYSTEM_DEMO_TERMINAL_IDLE_TIMEOUT_SECONDS`, 300 s). `SESS-2026-09-10-06` also records `REQ-006` R11
  (termination only after confirmation) confirmed with `/proc`-level proof of no orphaned shells,
  and `SESS-2026-09-10-08` records R11 as holding.
  `SESS-2026-10-04-11` (close the adapter and websocket when terminal startup fails) fixed a pty master
  fd leak when `Popen` failed after `pty.openpty()`, with the Windows ConPTY path left on code reading.
- `000246` (open, triaged 2026-09-22) names "the PTY child reaping that `000099` and `000129` turned
  on" as a place to start for unprovoked terminal drops. It was not investigated
  (`SESS-2026-09-15-12`: "the highest-consequence item this session touched and the one it did least
  about").

Observed here, section 4.4: what `close()` does to a shell and its children on Linux. This is new
evidence for the part of the lifecycle the earlier investigations did not examine.

## 4. Lifecycle, with traces

### 4.1 Ports

A port moves through these states for a TCP server, and the third and fifth matter to the incidents.

1. Free: nothing bound.
2. Listening: one process, or processes sharing an inherited socket, in LISTEN.
3. Held by a process the owner does not know about (a squatter or an orphan). Same kernel state as 2.
4. Connections open: established sockets.
5. After the listener is gone: sockets in TIME_WAIT on the port, for about a minute.

**Observed here, a bind conflict produces an error on the server side.** With a squatter on 8012,
`uvicorn src.main:app --port 8012` printed `Application startup complete.`, then
`ERROR: [Errno 98] error while attempting to bind on address ('127.0.0.1', 8012): address already in
use`, and exited with status 3.

**Observed here, a client connecting to a squatter gets no connection error.** The same squatter answered
`curl .../api/v1/workbench/injection-sources` with `404`. This is the same failure as 2026-09-14 at small scale. A bind conflict reports an error; a
connection to the wrong target succeeds and reports none.

**Observed here, naming the listener.** `lsof -nP -iTCP:8012 -sTCP:LISTEN` printed the command, pid,
user and `127.0.0.1:8012 (LISTEN)`. `fuser -n tcp 8012` printed the pid. `/proc/net/tcp` carried the
row (`0100007F:1F4C`, state `0A`, socket inode 7978) and no pid, so a pid needs a second lookup
through `/proc/<pid>/fd`. `ss`, which the runbook uses, is not installed in this sandbox.

**Observed here, "the port is free" depends on how you test it.** After the server was killed no
listener remained, and a plain `socket.bind(("127.0.0.1", 8012))` still failed with
`[Errno 98] Address already in use` because three TIME_WAIT sockets (state `06` in `/proc/net/tcp`)
remained. With `SO_REUSEADDR` set, which uvicorn sets, the same bind succeeded. The TIME_WAIT rows
were gone after 60 seconds. `REQ-011` R18's verification ("confirm the port is then bindable") is
therefore ambiguous until it says which bind.

### 4.2 Processes

A process moves through: spawned, ready (listening or reading), serving, signalled, exited, reaped.
The records and traces show where each goes wrong.

| Stage | How it goes wrong | Evidence |
|---|---|---|
| Spawned | The wrong environment is attached, so the process runs but points at the wrong peer. | `SESS-2026-09-14-02` |
| Ready | Starts on a port a squatter holds; or, for the PTY, the child cannot spawn and the master fd leaks. | 4.1; `SESS-2026-10-04-11` |
| Serving | The code on disk moves on; the process does not. | `SESS-2026-09-10-12`, `SESS-2026-09-14-09` |
| Signalled | The signal reaches a parent that does not forward it, or a pattern selects the wrong process. | 4.3; `SESS-2026-10-04-09` |
| Exited | A child outlives its parent and is reparented. | 4.3, 4.4 |
| Reaped | The parent never collects the status, leaving a zombie. | 4.4 |

### 4.3 A `--reload` server: what a kill reaches

**Observed here.** `uv run uvicorn src.main:app --reload --port 8012` produced this tree, in one
process group and session (the shell was launched with `setsid` so the group was isolated):

```
4160  uv run uvicorn src.main:app --reload --port 8012        (wrapper)
 4181  .../.venv/bin/uvicorn src.main:app --reload --port 8012  (reloader; holds the listening socket)
  4241  python -c "from multiprocessing.resource_tracker import main;main(4)"
  4242  python -c "from multiprocessing.spawn import spawn_main; ..."   (worker; also holds the listening socket)
```

`lsof` listed both pid 4181 and pid 4242 as LISTEN on the same socket inode.

Kills, in order, each followed by a re-check:

| Signal sent | Result |
|---|---|
| `SIGKILL` to the `uv run` wrapper (4160) | Reloader and worker survived; reloader reparented to PID 1; port still held; HTTP request still answered. |
| `SIGKILL` to the reloader (4181) | Worker (4242) and resource tracker survived, reparented to PID 1; port still held by 4242; HTTP request still answered. This is an orphaned dev server. |
| `SIGTERM` to the whole process group (`kill -TERM -- -4160`) | All gone; no listener on 8012. |

Two consequences for the kill-conditions section: the pid a person sees is often not the pid that
holds the port, and signalling the group reached every holder where signalling a pid did not. The
group was isolated because the launch used `setsid`. Whether a server launched another way (from an
interactive shell, or by an agent harness) has a group of its own, and whether a group signal there
could also reach unrelated processes, was not examined.

### 4.4 A PTY shell: what `close()` does

`PosixPtyAdapter.close()` calls `terminate()` (SIGTERM) on the shell if it is running, then closes the
master fd. It does not wait, escalate to SIGKILL, or signal a group.

**Observed here**, with the shell running a foreground `sleep` and, separately, a background
`sleep &`:

- The shell's Popen return code after `close()` was `-1`, which Python reports for death by signal 1
  (SIGHUP), not SIGTERM. The shell and its job were both gone within 0.2 seconds.
- Separating the two steps: SIGTERM alone left the shell running one second later (`poll()` still
  `None`, state `S`), and closing only the master fd ended it (`poll()` returned `-1`). So the
  `terminate()` call in `close()` did not stop an interactive bash in this observation, and the
  master fd close is what ended the session. This is consistent with the bash manual: an interactive
  shell ignores SIGTERM and, on SIGHUP, resends it to its jobs before exiting. Whether the same holds
  for a non-interactive shell or another shell was not examined.
- A child that ignores SIGHUP (`nohup sleep ... &`) survived `close()`, with parent pid 1. So did a
  child that left the session (`setsid sleep ... &`).
- With the adapter object still referenced and never polled, the exited shell stayed a zombie (state
  `Z`) for the three seconds observed. After the adapter was dropped and garbage-collected, the entry
  was gone. In `terminal_websocket` the adapter is dropped when the session function returns, so the
  zombie is short-lived there. A holder that keeps adapters in a long-lived structure would keep the
  zombies too.

The accurate summary is that session teardown is a hangup from closing the master fd, and it reaches
everything that honors a hangup. It does not reach what was deliberately detached. `SESS-2026-09-10-06`'s `sleep 6666` case was
the websocket never closing, not this.

The Windows adapter calls `terminate(force=True)` and swallows `OSError`, with a comment recording a
race that raises `ERROR_ACCESS_DENIED` (WinError 5) when the shell exits between `isalive()` and
`terminate()`. What a ConPTY child's own children do on `terminate` was not examined.
**Owner-machine, not run.**

## 5. When and how a process should be killed

This section states what the repository's records support. It does not choose a policy.

### 5.1 Conditions that have justified a kill, as recorded

| Condition | Recorded instance | Who decided |
|---|---|---|
| The owner of the process is gone (parent session cut off) | `SESS-2026-09-11-08` | The coordinator. |
| It serves stale code | `SESS-2026-09-10-12` (process older than `vite.config.ts`), `SESS-2026-09-14-09` | The validator, the reviewer. |
| It holds a port another process needs | `SESS-2026-09-10-07`, `SESS-2026-10-04-09` | The coordinator, the author. |
| The person asked to end the session | `REQ-006` R11, `ADR-014`: drop and tab close require an explicit confirmation | The user, by a confirm step. |
| A time bound passed | Idle timeout 300 s (`demo_terminal.py`); review command timeout, SIGKILL to the group (`run_review_checks.py`) | The code. |
| Orderly stop of a service | `stop_daemon`: SIGTERM, the daemon finishes its current tick | The operator. |

### 5.2 Practices the records support

- **Signal the group when the process has children.** Supported by 4.3. The review runner already
  does (`start_new_session=True`, then `os.killpg`). The PTY adapter signals only the shell, and in the
  observation its SIGTERM had no effect; the hangup from closing the master fd did the work (4.4).
- **Ask before forcing.** `stop_daemon` sends SIGTERM and lets the loop finish its tick. The review
  runner goes straight to SIGKILL because its job is disposable. The records contain both, with the
  reason for each.
- **Confirm the target before signalling it.** `stop_daemon` does not trust the pid in its lock file.
  It first tries the non-blocking `flock`; only a lock that is actually held leads to a signal. A
  pid left behind by a killed daemon "can already belong to an unrelated live process", and the
  docstring records the window that remains between the failed probe and `os.kill()`. Pid reuse is a
  property of any pid-based kill.
- **Never select by pattern against the caller's own command line.** `pgrep -f` and `pkill -f`
  matched the invoking shell in `SESS-2026-09-14-02`, `SESS-2026-10-04-09` and this exploration. Only exact argv comparison
  (used in section 4.4 here) selects the right process reliably. The documented `| head -1` and the
  pattern `node.*vite --port 5180` (`README.md`, the runbook) suit reading a process's environment,
  not choosing a kill target: the pattern is not anchored and matched the invoking shell's own pid
  when tested in a `bash -c` wrapper, and `head -1` takes the lowest pid, not the right one.
- **Verify the result, not the signal.** The checks that held evidential weight in the records were
  the post-condition: `curl` returns `200` (`SESS-2026-09-14-02`), no orphaned shell under `/proc`
  (`SESS-2026-09-10-08`), the port is bindable. A signal sent is not an exit observed.
- **Do not trust an earlier observation of a long-running server.** `SESS-2026-09-14-09`: results
  taken earlier were true when taken and the server then drifted. Re-run the check against the
  process now.

### 5.3 What the records do not settle

- Whether to escalate from SIGTERM to SIGKILL and after how long. No record sets a grace period for
  dev servers. The daemon tests cover SIGTERM-graceful and SIGKILL-recovery separately.
- What should happen to the children of a process that ignores SIGHUP (4.4).
- Kill authority on a shared host: peers' servers appear in the same process list (section 2). No
  record says who may stop whose.

## 6. How ports and processes should be managed

What exists, and where it falls short, all from the records.

| Practice | Where it is stated | Status |
|---|---|---|
| Choose an explicit free port per worktree; never assume 8000 or 5173 | `AGENTS.md`, `OPS-001`, coordinator briefs | Written; enforced by nothing. |
| Pass `--strictPort` so Vite refuses a taken port instead of moving | `README.md`, runbook, Windows checklist | Used in every documented launch. The records do not state the reason, and behavior without it was not reproduced here (`ts/node_modules` is absent in this worktree). |
| Check the port is free before launching | Runbook `/orient` precondition, `ss -tlnp \| grep -E "8010\|5180"` | Manual. `ss` is Linux only; absent in this sandbox. |
| Set `VITE_API_TARGET` and `D_SYSTEM_DEMO_TERMINAL` in the same invocation (`env ...`) | `README.md`, runbook | Manual; the 2026-09-14 failure was the prefix being lost. |
| After launching, `curl` must print `200` and `/proc/<pid>/environ` must show both variables | `README.md`, runbook | Manual. |
| Bind the terminal only to loopback | `ADR-013`, `enforce_loopback_bind()` | Enforced at import. |
| Cap concurrent PTY sessions at six, server-side, registered by session id | `ADR-014`, `demo_terminal.py` | Enforced. |
| Reap a PTY whose client vanished | Idle timeout | Enforced; tested. |
| Single instance of the daemon, stale lock recovery after SIGKILL | `daemon.py`, `flock` | Enforced; tested with real subprocesses. |

Gaps visible from this table:

1. No start-time record. Nothing writes which worktree or session started a dev server. Section 2's
   fact 3 (argv names the venv path) is the only ownership signal, and it exists only when the server
   was started from a worktree venv.
2. No end-of-session cleanup. The records show cleanup as an after-the-fact coordinator act.
3. No single check that distinguishes "my server on this port" from "a server on this port". The
   2026-09-14 failure passed every check that tested only for an answer.
4. The checks are shell one-liners that work on Linux. `ss` is not guaranteed present, `psutil` is not
   a project dependency (`pyproject.toml`), and the Windows equivalents were not run.
   **Owner-machine, not run.**

## 7. The read-only posture of `ADR-015`, and the tension a kill action creates

Described only. `phase-arch-12` records its own decision in its own ADR, and its scope says
"do not widen `ADR-015` in passing".

What `ADR-015` (the workbench read/action API decision, accepted 2026-09-10) says:

- Decision 4: "Read-only, except one named action." Enumeration, listing, search, idea and backlog
  routes respond to GET only and write nothing.
- Decision 5: reveal-in-explorer is "the sole action route", POST only, spawning "exactly one fixed
  opener" built as an argument list from a validated path. "No other OS command is reachable; new
  actions extend this record first."
- Rejected alternatives: "A generic 'run command' action. Rejected outright; the reveal action is a
  fixed opener with a validated argument, not a command surface."
- Consequences: "If the workbench ever needs a write route ... that starts from a new decision
  record; nothing here authorizes one."
- Decision 1: every workbench route mounts only with `D_SYSTEM_DEMO_TERMINAL=1`, loopback only.
- Decision 3: listings exclude private and derived content.

The tension, as it appears when each requirement is set against these decisions:

1. **A kill is a write.** `REQ-011` R18 asks for "killing a process, freeing a port". That is a second
   OS action, which decision 5 reserves to a record that extends it. It is also an action on a
   target the caller names (a pid or port), where reveal's target is a validated repository path and
   its command is fixed.
2. **The target space is not repository-bounded.** `ADR-015`'s boundary is the repository root.
   Processes and ports are host-wide. The path check that bounds reveal has no counterpart; a
   replacement boundary is needed or the need is argued away. Candidates, unranked and none chosen
   here: processes whose cwd or argv lies inside this repository or its worktree directory; processes
   this application started itself; processes holding ports on a configured list; no boundary, with
   confirmation as the only control.
3. **A read can already cross the line.** A process listing includes command lines and can include
   environment variables. Decision 3 keeps private content out of listings; a host-wide process list
   may carry other people's and other projects' identifiers. `SESS-2026-09-14-02` removed the name of
   the unrelated program on 8000 from a tracked record for this reason. A workbench shown to an
   audience (`SESS-2026-09-15-12` records a demo the workbench was not used for) would display it.
   The runbook already reads `/proc/<pid>/environ` by hand; a route that serves it would be a new
   disclosure.
4. **Some targets are the application's own.** The server hosting the route, its parent, the PTY
   shells in the session registry (which `REQ-006` R11 requires a confirmation step to end), and
   peers' servers on a shared host are all in the list the tool would show. Whether they are
   killable is undecided.
5. **A permitted generic kill approaches the rejected command surface.** The line between "kill a
   process the tool listed" and "run a command" is the validation, as it was for reveal. The
   rejection of a generic command action is recorded; what counts as validated here is not.
6. **The gate has precedent either way.** The existing action is behind the same flag as the
   terminal, which already starts arbitrary shells on the host. The terminal is a larger capability
   than a kill action and is accepted (`ADR-013`, `ADR-014`).

## 8. Not established

- Windows and macOS behavior of every item in sections 4 and 6: listener lookup (`netstat -ano`
  equivalent), process-tree kill, ConPTY child fate, TIME_WAIT behavior. **Owner-machine, not run.**
- Whether the port-8000 collision exists on the Windows presentation machine (`SESS-2026-09-14-02`).
- Vite's behavior without `--strictPort`, and its process tree (`npm` to `sh` to `node`) beyond what
  review finding B1 records. `ts/node_modules` is absent in this worktree, so Vite was not run.
- What stopped `000246`'s unprovoked terminal drops, and whether PTY reaping is involved. Open.
- Why the three PTY tests turned green on dev (`000129`'s note). The pyenv stall was not reproduced
  here; it is a host shell-init condition.
- The behavior of a `--reload` server's group when launched without `setsid` (4.3).

## 9. Questions `phase-arch-12` must answer

Each item names the evidence in this document that bears on it. None is answered here. `000144`
(package the port/process app for the modular panel pages) is the follow-on idea that
`phase-arch-13` carries out, so the app `phase-arch-12` builds is later packaged as a workbench
sub-app; nothing below depends on that packaging.

| # | Question | Evidence |
|---|---|---|
| 1 | What is listed: all host listeners, or those attributable to this repository? What attribution signal is accepted (cwd inside the repository or worktree root, venv path in argv, start time against file mtimes)? | 2 fact 3; `SESS-2026-09-10-12` (age against mtime) |
| 2 | What fields may be displayed, given that command lines and environments can carry identifiers of unrelated work? | 3.1 last bullets; section 7 point 3 |
| 3 | What is the unit of a kill: a pid, a group, or a tree? A pid kill left the port held and served. | 4.3 |
| 4 | Signal order and grace period, and whether the tool escalates or leaves that to the person. | 5.2, 5.3 |
| 5 | Is the target re-identified immediately before the signal, and how? Pid reuse is a property of pid-based kills. | 5.2, `stop_daemon` |
| 6 | Which processes are never killable through the tool (itself and its parent, the PTY sessions in the registry, processes of other users, peers' worktrees)? | Section 7 points 4, 5; 2 fact 3 |
| 7 | What does "free a port" mean: kill the listener, wait for release, or both? Is TIME_WAIT a failure? Which bind test counts? | 4.1 |
| 8 | What counts as the target port answering for the wrong program (a squatter) versus the right one? The 2026-09-14 failure passed every check that tested only for an answer. | 3.1, 6 gap 3 |
| 9 | Which lookup primitive: `lsof`, `fuser`, `/proc`, `ss`, or a library? `ss` is absent here and `psutil` is not a dependency. | 4.1, 6 gap 4 |
| 10 | What is the Windows column, and who runs it? | Section 8 |
| 11 | How does the decision sit against `ADR-015` decisions 1, 3, 4 and 5 and the rejected "run command" alternative? Its own ADR must say. | Section 7 |
| 12 | What is the test for `REQ-011` R18? The requirement says "a deliberately occupied port". A recipe that has worked here is in section 10 and uses a real listener, not a mock. | Section 10 |

Facts the build can rely on, from this exploration: a listener can be named by `lsof`/`fuser`/`/proc`
on Linux; a pid kill of a reloading server leaves it serving; a group kill clears it; a plain-bind test
of freedom can fail for about a minute after the listener is gone; and the repository already contains
an identity-first kill (`stop_daemon`) and a group-kill with timeout (`run_review_checks.py`) to read
before designing another.

## 10. Reproduction recipe

Run from a worktree with `.venv`. Use a free port; this used 8012. Do not signal processes you did
not start: peers' servers are in the same process list.

1. Squatter: `python -m http.server 8012 --bind 127.0.0.1` in its own session (`setsid`).
2. Name it: `lsof -nP -iTCP:8012 -sTCP:LISTEN`, `fuser -n tcp 8012`.
3. Wrong target: `curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8012/api/v1/workbench/injection-sources` printed `404`.
4. Bind failure: `uv run uvicorn src.main:app --port 8012`, exit status 3, `Errno 98`.
5. Orphan: stop the squatter, start `uv run uvicorn src.main:app --reload --port 8012` under `setsid`,
   list its tree, `kill -9` the wrapper, then the reloader, and check `lsof` and a `curl` after each.
6. Release: `kill -TERM -- -<pgid>`; confirm no listener; bind once without and once with `SO_REUSEADDR`.
7. PTY: construct `src.demo.posix.PosixPtyAdapter`, `start()`, `write()` a `sleep N &` (plain, `nohup`,
   `setsid`), `close()`, and compare process state from `/proc/<pid>/stat` at 0.3 s and 3 s. Find
   processes by exact `/proc/<pid>/cmdline` argv, not `pgrep -f`. To separate the two teardown steps,
   call `adapter._process.terminate()` on one adapter and `os.close(adapter._master_fd)` on another,
   and read `poll()` after one second.

## 11. Sources

| Document | Date | Used for |
|---|---|---|
| `REQ-011` (workbench architecture and quality requirements) R17, R18 | 2026-09-14 | The requirement this document answers. |
| `PLAN-028` (workbench architecture and quality), group `G45` | 2026-09-14 | Why exploration precedes the build. |
| `ADR-013`, `ADR-014`, `ADR-015` | 2026-09-10 | Terminal and API posture. |
| `REQ-006` (live demo) R11 | 2026-09-10 | Confirmation before termination. |
| `OPS-001` (governance operations), `AGENTS.md` | standing | Explicit-port rule. |
| `SESS-2026-09-10-04`, `-06`, `-07`, `-08`, `-11`, `-12`, `-13` | 2026-09-10 | Port-8000 default, orphan fix, stale servers, pyenv stall. |
| `SESS-2026-09-11-05`, `-08` | 2026-09-11 | Live `curl` checks, orphaned servers killed. |
| `SESS-2026-09-12-02` | 2026-09-12 | pyenv 60-second stall. |
| `SESS-2026-09-14-02`, `-09` | 2026-09-14 | 8000 squatter, stale dev server. |
| `SESS-2026-09-15-12` | 2026-09-15 | `000246` left uninvestigated. |
| `SESS-2026-09-23-06` | 2026-09-23 | Daemon lock and signals. |
| `SESS-2026-10-01-04`, `-03-01`, `-04-09`, `-04-11` | 2026-10 | Review runner, explicit ports, self-matching `pkill`, fd leak. |
| Ideas `000099`, `000129`, `000138`, `000142`, `000143`, `000144`, `000246` | 2026-09-11 to 2026-09-15 | Incident narrative and the owner's asks. |
| `src/demo/posix.py`, `src/demo/windows.py`, `src/api/routes/demo_terminal.py`, `src/api/routes/workbench.py`, `src/orchestrator/daemon.py`, `tools/run_review_checks.py`, `ts/vite.config.ts` | 2026-10-08 | Read for the inventory and the kill paths. |
