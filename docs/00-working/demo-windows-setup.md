# Windows Machine Setup Checklist

Verification checklist for the presentation machine (Windows). This document is ungoverned (ADR-010)
and completed before the live demo session. Every item is checked by the owner; the coordinator
guides as needed.

The goal is to verify base setup is in place (repo clone, `uv`, Node, authentication), that
demo-specific dependencies are current, the terminal capability works end to end on Windows,
the workbench launch works correctly, and that CMD and PowerShell panels function before
rehearsal begins.

## Base Setup (Pre-Session, Usually Already Done)

- [ ] Repository cloned to: `__CLONE_PATH__` (owner to fill in)
- [ ] `uv` version: `uv --version` shows `uv 0.X.X` or later. Run `uv sync --extra dev` if `uv` is
      older.
- [ ] Node version: `node --version` shows `v18.X.X` or later. (Fill in actual version:
      `__NODE_VERSION__`)
- [ ] Claude Code authenticated and able to write to the repository.

## Demo-Specific Verification (Updated for Workbench)

### Python and Backend Dependencies

- [ ] Run `uv sync --extra dev` in the repository root. (This installs `pywinpty`, which was added
      for this build and postdates the base setup.)
- [ ] Run `uv run python -c "import pywinpty; print(pywinpty.__version__)"` to confirm `pywinpty`
      is installed. Expected output: a version string (fill in: `__PYWINPTY_VERSION__`).

### Frontend Dependencies

- [ ] Run `npm install` in the repository root to ensure frontend dependencies are current.
- [ ] Confirm no errors in the npm output.

### Environment Variables for Terminal Route and Frontend API Target

- [ ] Set `D_SYSTEM_DEMO_TERMINAL=1` in the shell environment **before starting the backend, and
      again in the frontend's own shell before starting the dev server** — the flag must be set on
      **both** processes. On the backend it gates every workbench route. On the frontend it gates
      the dev server's repository file-serving route (`/workbench-file/*`), which the HTML Viewer
      loads every page through: with the flag missing from the frontend process, the route is
      absent, page requests answer HTTP 200 with the app shell, and the HTML Viewer goes silently
      blank with no error anywhere (owner-confirmed on Windows, 2026-09-11).
      On Windows PowerShell: `$env:D_SYSTEM_DEMO_TERMINAL=1`. On cmd: `set D_SYSTEM_DEMO_TERMINAL=1`.
- [ ] Set `VITE_API_TARGET=http://localhost:8010` **before** starting the frontend dev server.
      On PowerShell: `$env:VITE_API_TARGET="http://localhost:8010"`. On cmd: `set VITE_API_TARGET=http://localhost:8010`.

### Port Availability

- [ ] Port 8010 is not in use by another process. (The backend will listen on `127.0.0.1:8010`.)
- [ ] Port 5180 is not in use by another process. (The frontend dev server will serve on
      `http://localhost:5180`.)

## Terminal Capability Smoke Check (REQ-006 R06)

**Run this check on the presentation machine before the demo.** The result verifies end-to-end
terminal functionality on Windows.

### Steps

1. Start the backend (PowerShell):
   ```
   $env:D_SYSTEM_DEMO_TERMINAL=1
   uv run uvicorn src.main:app --port 8010
   ```
   Expected: backend starts and listens on `127.0.0.1:8010`.

2. In a new shell, start the frontend (Windows PowerShell):
   ```
   cd ts
   $env:D_SYSTEM_DEMO_TERMINAL=1
   $env:VITE_API_TARGET="http://localhost:8010"
   npm run dev -- --port 5180 --strictPort
   ```
   Without `VITE_API_TARGET`, the dev proxy silently targets `http://localhost:8000` instead of
   the demo backend on `8010`, and every stage route 404s if anything else holds port 8000.
   The `--strictPort` flag ensures the frontend fails rather than silently falling back to
   another port.
   Without `D_SYSTEM_DEMO_TERMINAL=1` on this frontend process, the HTML Viewer's file-serving
   route (`/workbench-file/*`) is never registered: the workbench still loads with no error —
   every viewer page request answers HTTP 200 with the app shell — and the HTML Viewer renders
   silently blank (owner-confirmed on Windows, 2026-09-11).
   Expected: Vite dev server starts on `http://localhost:5180`.

3. Open a browser and navigate to `http://localhost:5180`.
   Expected: the workbench page loads; the layout is visible with the terminal region present.

4. Check the terminal slot's header (top left): on a fresh store it should read "PowerShell ▾" —
   the platform-conditional Windows default (REQ-007 W17). Then type a command in the embedded
   terminal (e.g., `echo Hello from Windows`).
   Expected: the header shows PowerShell; the command executes and real shell output appears in
   the terminal.

5. Stop the servers with Ctrl+C.

### Result

Record the result of the smoke check below. A passing result means the terminal capability works
on Windows and the stage is ready for rehearsal.

**Smoke check result (owner to fill in):**

```
Date and time:
Shell type observed (PowerShell or cmd):
Command typed:
Output received:
Status: [PASS / FAIL]
Notes:
```

## Workbench Launch Check

**Run this check to verify the workbench launches correctly with the proper environment variables.**

### Steps

1. From the repository root, start the backend in PowerShell:
   ```
   $env:D_SYSTEM_DEMO_TERMINAL=1
   uv run uvicorn src.main:app --port 8010
   ```

2. In a new PowerShell window, navigate to the `ts` directory and start the frontend:
   ```
   cd ts
   $env:D_SYSTEM_DEMO_TERMINAL=1
   $env:VITE_API_TARGET="http://localhost:8010"
   npm run dev -- --port 5180 --strictPort
   ```

3. Open a browser and navigate to `http://localhost:5180`.

4. Verify the workbench interface loads with these elements:
   - Notes strip at top right with `?` tooltip at far left and dropdown menu
   - Terminal panel on left with ellipsis menu (`...`) in top right, its header reading
     "PowerShell ▾" on a fresh store (the Windows platform default) with a switcher dropdown
     over the slot's other assigned shells
   - Injection dropdowns (Commands, Skills, Prompts, Agents) below terminal header
   - "Configure layout" button at top right, opening the assignment-only dialog:
     active-layout radio buttons plus exactly one eligible-slot selector per panel
     (no per-slot visible-panel selects)
   - HTML Viewer panel on right with refresh button, file dropdown, and directory button
   - Explorer slot below HTML Viewer with File Browser visible (Idea Explorer and Backlog Explorer in header dropdown)

5. Stop the servers with Ctrl+C.

### Result

**Workbench launch result (owner to fill in):**

```
Date and time:
All interface elements present: [YES / NO]
Status: [PASS / FAIL]
Notes:
```

## CMD and PowerShell Panel Round-Trip Checks (REQ-007 W12)

**Run these checks to verify CMD and PowerShell panels work correctly.** Each check executes a
command in the respective shell and verifies output appears.

### CMD Panel Check

1. In the workbench, the terminal slot (left side) holds three assigned shell panels — Terminal
   (bash), CMD and PowerShell — so its header renders a dropdown (small downward triangle, top
   left) that switches which one is visible. The dropdown is a switcher only; it never moves a
   panel between slots (that is the "Configure layout" dialog's job). On Windows the fresh-store
   default visible shell is PowerShell, so expect the header to read "PowerShell ▾" before this
   check.
2. Click the terminal slot's header dropdown and select **CMD**.
3. Type a test command: `echo Hello from CMD`
4. Verify the command executes and output appears: `Hello from CMD`

**CMD panel result (owner to fill in):**

```
Date and time:
Command typed: echo Hello from CMD
Output received: [TEXT]
Status: [PASS / FAIL]
Notes:
```

### PowerShell Panel Check

1. In the workbench, click the terminal slot's header dropdown (top left) and select **PowerShell**.
2. Type a test command: `Write-Host "Hello from PowerShell"`
3. Verify the command executes and output appears: `Hello from PowerShell`

**PowerShell panel result (owner to fill in):**

```
Date and time:
Command typed: Write-Host "Hello from PowerShell"
Output received: [TEXT]
Status: [PASS / FAIL]
Notes:
```

## Full Fresh-Eyes Rehearsal Checklist (PROMPT-017 and REQ-007 W13)

**Run this once, in full, on the presentation machine before the demo.** This is the same
checklist the rehearsal gate runs; running it again here on the presentation machine catches
anything specific to Windows before the live demo begins.

1. [ ] Backend and frontend start with `D_SYSTEM_DEMO_TERMINAL=1` on ports 8010 and 5180 respectively.
2. [ ] The workbench page loads at 1280×720, 1920×1080, and intermediate sizes; there is zero page
       scrolling, no overlapping elements, and every reveal control (tabs, expanders, dropdowns)
       opens and collapses as required.
3. [ ] The embedded terminal connects, runs a real shell (PowerShell by default on a fresh store on
       Windows; bash on other hosts), and echoes interactive input. Session tabs function.
4. [ ] The notes strip displays the active entry with no title label; all controls live in the dropdown
       menu (cycling, file picker, timed advance); the `?` tooltip appears at the strip's far left.
5. [ ] The terminal panel's ellipsis menu (top right) contains Collapse and Drop/restore options and
       both function: collapse does not terminate sessions; drop displays an info page and grays out
       injection dropdowns; restore returns a working terminal.
6. [ ] Injection dropdowns (Commands, Skills, Prompts, Agents) inject their entries' text un-executed
       into the active terminal tab. Selections persist across the panel.
7. [ ] `tools/demo_reset.py prepare` parks the pre-built overview skill and seeds the fallback audience
       idea; the live-rebuild path runs end to end (idea recorded, triaged, skill rebuilt from the
       deterministic tools, skill invoked, overview page generated and rendered in the HTML Viewer);
       then `restore` returns the pre-built state.
8. [ ] The HTML Viewer displays the generated overview; the refresh button reloads it; the file dropdown
       lists files in the chosen directory; the directory button opens a dialog to change the search
       directory. The viewer has tabs with directory, search text, and displayed page scoped per tab.
9. [ ] The explorer slot displays File Browser by default (with Idea Explorer and Backlog Explorer behind
       the header dropdown); the File Browser shows a collapsible tree, is filterable by text and file type,
       and right-click context menus work (reveal-in-explorer, open-in-HTML-Viewer, copy paths, inject path).
10. [ ] The "Configure layout" dialog switches between layouts and re-assigns panels through its
        per-panel eligible-slot selectors (it offers no per-slot visible-panel selects); moving a
        panel into an occupied slot shows the in-place confirm notice naming the displaced panel,
        and applies only on Confirm. Zero scroll and no overlapping regions in both layouts at
        all sizes.
11. [ ] **Determinism check**: run `tools/overview_metrics.py` and `tools/overview_inventory.py`
        (or `tools/generate_overview.py`, which wraps both) twice and confirm identical output.
12. [ ] CMD and PowerShell panel options each execute a command and display output correctly (W12).
13. [ ] **Side-by-side fallback**: exercise the workbench without the embedded terminal (descope rung 8)
        alongside an external terminal window, once.

**Result (owner to fill in):**

```
Date and time:
Items 1-13 status: [PASS / FAIL, per item]
Notes:
```

## Pre-Demo Git Tag

- [ ] Create a pre-demo git tag to capture the baseline state before live-segment ideas are
      recorded. Example:
      ```
      git tag demo-day-2026-09-15
      git push origin demo-day-2026-09-15
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
- [ ] The PowerShell or cmd window is opened in the repository root with a clean scrollback (no previous
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
