---
description: Scout every open idea for related plans, phases and documents, record a finding on each, and move it from open to triaged
argument-hint: "[idea id] (optional — defaults to every open idea)"
---

# Triage open ideas

Drives the `idea-triage` subagent over every idea currently `status: open` in
`_data/ideas.jsonl`, records what it finds as a `kind: finding` annotation, then moves the
idea to `triaged`. This is `phase-idea-02` — see `PLAN-016` (idea record system) and
`PLAN-017.04` (annotations) for why the boundaries below are drawn where they are.

**This command never moves an idea past `triaged`.** `reviewing`, `promoted` and
`discarded` are owner judgement calls (`ADR-010`, `PLAN-016`); automating them is the one
thing this phase's acceptance explicitly forbids.

## 1. Find the open ideas

```bash
uv run python -c "
from src.db.ideas import load_events, fold
state = fold(load_events())
for idea_id, s in sorted(state.items()):
    if s.get('status') == 'open':
        print(idea_id, '|', s.get('title'))
"
```

If `$ARGUMENTS` names a specific idea id, triage only that one (and only if its current
status is `open` — report and stop if it is not, rather than guessing what the owner meant).
Otherwise triage every open idea found above, one at a time.

## 2. Triage each one

For each open idea, in order:

1. Read its **effective** title and body from the fold output above — never from
   `_data/ideas.jsonl` directly. A raw `created` event can be stale if the idea was ever
   `amend`ed, since amendments correct title/body without rewriting the original line.
2. Dispatch the `idea-triage` subagent with that id, title and body. **Include this exact
   line in the dispatch prompt, with `<id>` already substituted by you, the driver — never
   left for the subagent to fill in itself:**

   ```
   When you write your finding, save the text to a file, then run this exact command with
   only the file path changed — do not retype or otherwise reconstruct the idea id yourself:
   uv run python tools/append_idea.py annotate <id> --author agent-idea-triage --kind finding --text "$(cat <your-file>)"
   ```

   This exists because a prior session had a subagent write one idea's finding text under a
   *different* idea's id — it held the right id in its prompt but retyped the wrong one when
   constructing the command from memory. Handing it the literal command with the id already
   filled in removes that retyping step at its actual source, rather than trusting the
   subagent to copy a number correctly across several tool calls.
3. Once the subagent reports the `annotate` call succeeded, **verify it independently before
   trusting the report** — a subagent's self-report is not proof of what it actually wrote
   (this is exactly how the misdirected write above went undetected until an unrelated
   audit caught it):

   ```bash
   uv run python -c "
   from src.db.ideas import load_events, fold
   state = fold(load_events())
   anns = state['<id>']['annotations']
   print(anns[-1]['text'][:200] if anns else 'NO ANNOTATION FOUND')
   "
   ```

   Read the printed text. If it opens by naming a *different* six-digit idea id as its own
   subject (e.g. idea `<id>`'s newest annotation starts "Idea 000012 proposes..." when `<id>`
   is not `000012`), the write landed on the wrong idea — stop, do not move status to
   `triaged`, and fix it with `amend-annotation` (see `.claude/agents/idea-triage.md`'s
   corrected-entry precedent) before continuing to the next idea.
4. Only once verified, move the idea to `triaged`:

   ```bash
   uv run python tools/append_idea.py status <id> triaged
   ```

5. If the subagent found nothing to report, it still writes a finding saying so — every
   triaged idea has at least one finding annotation, even an empty-handed one. Do not skip
   the annotation step because there was nothing notable to find.

**Do not batch multiple ideas into one subagent call.** Each idea gets its own dispatch, so
a finding never accidentally conflates two ideas' overlap.

## 3. Afterwards

Regenerate the markdown view and leave the tree green:

```bash
uv run python tools/generate_ideas_md.py
uv run python -m src.governance
```

Then report to the owner, per idea: its id, title (`000046 (idea planner agent)`, per
`GOV-006`), and the finding in one line — not just "triaged N ideas." A count with no content
makes them open the log to find out what was actually found.

**Collect every `PROPOSED LINK:` and `PROPOSED PROMOTION:` line across the batch into their own
lists at the end of your report**, separate from the per-idea summary and from each other.
These are candidate `tools/append_idea.py link` / `status ... promoted --promoted-to ...`
calls the subagent found but never executed — the owner reviews and runs (or discards) each
one by hand; nothing here writes a link or a promotion automatically. A `PROPOSED PROMOTION`
is the stricter of the two: the subagent only raises one when an idea's actual ask already
shipped, not merely when a document touches the same area.
