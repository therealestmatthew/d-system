# Windows Machine Setup Checklist

Verification checklist for the presentation machine (Windows). This document is ungoverned (ADR-010)
and completed before the live demo session. Every item is checked by the owner; the coordinator
guides as needed.

The goal is to verify base setup is in place (repo clone, `uv`, Node, authentication), that
demo-specific dependencies are current, and that the terminal capability works end to end on Windows
before the rehearsal gate begins.

## Base Setup (Pre-Session, Usually Already Done)

- [ ] Repository cloned to: `__CLONE_PATH__` (owner to fill in)
- [ ] `uv` version: `uv --version` shows `uv 0.X.X` or later. Run `uv sync --extra dev` if `uv` is
      older.
- [ ] Node version: `node --version` shows `v18.X.X` or later. (Fill in actual version:
      `__NODE_VERSION__`)
- [ ] Claude Code authenticated and able to write to the repository.

## Demo-Specific Verification (Updated for Phase Demo-05)

### Python and Backend Dependencies

- [ ] Run `uv sync --extra dev` in the repository root. (This installs `pywinpty`, which was added
      for this build and postdates the base setup.)
- [ ] Run `uv run python -c "import pywinpty; print(pywinpty.__version__)"` to confirm `pywinpty`
      is installed. Expected output: a version string (fill in: `__PYWINPTY_VERSION__`).

### Frontend Dependencies

- [ ] Run `npm install` in the repository root to ensure frontend dependencies are current.
- [ ] Confirm no errors in the npm output.

### Environment Variable for Terminal Route

- [ ] Set `D_SYSTEM_DEMO_TERMINAL=1` in the shell environment **before** starting the backend.
      On Windows PowerShell: `$env:D_SYSTEM_DEMO_TERMINAL=1`. On cmd: `set D_SYSTEM_DEMO_TERMINAL=1`.

### Port Availability

- [ ] Port 8010 is not in use by another process. (The backend will listen on `127.0.0.1:8010`.)
- [ ] Port 5180 is not in use by another process. (The frontend dev server will serve on
      `http://localhost:5180`.)

## Terminal Capability Smoke Check (REQ-006 R06)

**Run this check on the presentation machine before the demo.** The result verifies end-to-end
terminal functionality on Windows.

### Steps

1. Start the backend:
   ```
   $env:D_SYSTEM_DEMO_TERMINAL=1
   uv run uvicorn src.main:app --port 8010
   ```
   Expected: backend starts and listens on `127.0.0.1:8010`.

2. In a new shell, start the frontend:
   ```
   cd ts
   npm run dev -- --port 5180
   ```
   Expected: Vite dev server starts on `http://localhost:5180`.

3. Open a browser and navigate to `http://localhost:5180`.
   Expected: the stage page loads; the layout is visible with the terminal region present.

4. Type a command in the embedded terminal (e.g., `echo Hello from Windows`).
   Expected: the command executes and real shell output appears in the terminal.

5. Stop the servers with Ctrl+C.

### Result

Record the result of the smoke check below. A passing result means the terminal capability works
on Windows and the stage is ready for rehearsal.

**Smoke check result (owner to fill in):**

```
Date and time:
Shell type observed (cmd or PowerShell):
Command typed:
Output received:
Status: [PASS / FAIL]
Notes:
```

## Full Fresh-Eyes Rehearsal Checklist (PROMPT-017)

**Run this once, in full, on the presentation machine before the demo.** This is the same
checklist `docs/02-prompts/PROMPT-017-demo-rehearsal-gate.md`'s fresh-eyes rehearsal runs on the
development machine; running it again here catches anything specific to the Windows machine
before the Windows-machine gate is called green.

1. [ ] Backend starts on 8010 with `D_SYSTEM_DEMO_TERMINAL=1`; frontend builds and serves on
       5180.
2. [ ] The stage page loads; at 1280×720, 1920×1080, **and a half-width window** there is zero
       page scrolling, no overlapping elements, and every reveal control (tabs, expanders,
       popups) opens and collapses as required.
3. [ ] The embedded terminal connects, runs a real shell, and echoes interactive input.
4. [ ] The talking-points panel cycles the owner's content from its data file.
5. [ ] `tools/demo_reset.py` parks the pre-built overview skill and seeds the fallback audience
       idea; the live-rebuild path runs end to end (idea recorded, triaged, skill rebuilt from
       the deterministic tools, skill invoked, overview page generated and rendered in the
       embedded panel); then `restore` returns the pre-built state.
6. [ ] **Determinism check**: run `tools/overview_metrics.py` and `tools/overview_inventory.py`
       (or `tools/generate_overview.py`, which wraps both) twice and confirm identical output.
7. [ ] **Side-by-side fallback**: exercise the stage without the embedded terminal (descope rung
       4) alongside an external terminal window, once.

**Result (owner to fill in):**

```
Date and time:
Items 1-7 status: [PASS / FAIL, per item]
Notes:
```

## Pre-Demo Git Tag

- [ ] Create a pre-demo git tag to capture the baseline state before live-segment ideas are
      recorded. Example:
      ```
      git tag demo-day-2026-09-10
      git push origin demo-day-2026-09-10
      ```
- [ ] Verify the tag exists: `git tag -l demo-day-*` lists the tag.
- [ ] Verify `tools/demo_reset.py prepare` once against the tagged state: run
      `uv run python tools/demo_reset.py prepare`, confirm it reports the skill parked and the
      fallback idea seeded (or already present), and record the result below.
- [ ] Verify `tools/demo_reset.py restore` once against the same tagged state: run
      `uv run python tools/demo_reset.py restore`, confirm it reports the skill restored, and
      record the result below.

**`prepare`/`restore` verification result (owner to fill in):**

```
Date and time:
prepare output:
prepare status: [PASS / FAIL]
restore output:
restore status: [PASS / FAIL]
Notes:
```

## Screen Hygiene (Live Session)

Before the live demo begins:

- [ ] Notifications and alerts are disabled (so no unexpected popups appear during the recording).
- [ ] The terminal window is opened in the repository root with a clean scrollback (no previous
      commands visible).
- [ ] The browser profile is clean: no personal tabs, bookmarks or history showing.
- [ ] Nothing from `_private/` is visible on screen at any point during the demo.

## Permission Allowlist

A pre-approved allowlist for the live-demo session is built from rehearsal transcripts before
the live session starts. The live segment runs with this allowlist loaded, so no permission
pauses interrupt the demo while the write fences still protect forbidden paths.

- [ ] Allowlist is generated and loaded before the live session starts. (The `fewer-permission-prompts`
      skill does this automatically based on rehearsal transcripts.)

## Verification Complete

- [ ] All items above are checked.
- [ ] Coordinator has reviewed and confirmed readiness.
- [ ] Owner confirms the stage is ready for the live demo.
