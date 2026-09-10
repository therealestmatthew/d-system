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

## Pre-Demo Git Tag

- [ ] Create a pre-demo git tag to capture the baseline state before live-segment ideas are
      recorded. Example:
      ```
      git tag demo-day-2026-09-10
      git push origin demo-day-2026-09-10
      ```
- [ ] Verify the tag exists: `git tag -l demo-day-*` lists the tag.

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
