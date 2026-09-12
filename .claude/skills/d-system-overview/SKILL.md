---
name: d-system-overview
description: Regenerate the D-System overview page by running tools/generate_overview.py, then report the page's location and the headline numbers the tool emitted. Run it when the live demo needs a fresh overview page, or whenever someone asks to "rebuild the overview".
---

# d-system-overview

Runs one script, reads what it printed, and stops. Nothing here computes a number. Metrics figures
(idea count, event count, backlog phase count) come from `tools/overview_metrics.py`, which reads
the idea log via `fold()`/`load_events()` in `src/db/ideas.py` (REQ-006 R08). Inventory figures
(concept count, term count, system count) come from `tools/overview_inventory.py`, which reads the
`brain/` concept memories and `docs/08-governance/systems.yaml`, not the idea log.
`tools/generate_overview.py` copies both sets of figures onto the page verbatim.

## What this skill must never do

- **Never recompute or adjust a number the tools produced.** Not by re-reading `_data/ideas.jsonl`,
  not by counting rows in the rendered HTML, not by rounding or restating a figure "for clarity". If
  a number looks wrong, report it exactly as generated and say it looks wrong — do not correct it.
- **Never edit the generated page by hand.** `_public/overview/index.html` is output, not a document
  to touch — if it is stale or wrong, the fix is to rerun the generator, never to open the file and
  change text or numbers in it.
- **Never read `_data/ideas.jsonl` directly.** The two tools this skill invokes already read the
  idea log the sanctioned way; this skill does not need to and must not read it a second time.

## Running it

### 1. Generate the page

```bash
uv run python tools/generate_overview.py
```

This runs `tools/overview_metrics.py` and `tools/overview_inventory.py` as subprocesses, parses
their JSON, and renders `templates/html/overview-*.html` + `templates/styles/overview.css` into a
single self-contained page. It writes to `_public/overview/index.html` by default (override with
`--out FILE`, if the calling context needs the page written elsewhere).

### 2. If generation fails

Report the failure output exactly as printed — stderr, exit code, the traceback if one appears — and
stop. A failed generation is the result to report, not a step to retry silently. Do not attempt to
hand-write or patch the page to make the failure go away.

### 3. If generation succeeds

Report:

- **The page location** — the path the tool printed (`wrote <path>`), normally
  `_public/overview/index.html`.
- **The headline numbers**, read off the page or the tools' own stdout, not recomputed: idea count,
  event count, backlog phase count, concept count, term count, system count, and the
  `GENERATED_AT` timestamp. All of these are `tools/overview_metrics.py`'s and
  `tools/overview_inventory.py`'s own `meta` fields, copied through unchanged — this skill only
  reads and reports them.

Then stop. This skill does not open a browser, does not commit anything, and does not touch
`docs/09-backlog/backlog.yaml` or any session record.
