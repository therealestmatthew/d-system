# Superseded: session-taxonomy investigation prompt

This document was split in two on 2026-09-19, after an adversarial review, so that the theory
session never sees the measurement design:

- **Part 1 (theory)** — `PROMPT-session-taxonomy-part1-theory.md`. Run first, in a fresh
  session. Halts after delivering `session-types-theory.md`.
- **Part 2 (empirical test)** — `PROMPT-session-taxonomy-part2-evidence.md`. Run only on the
  owner's explicit go, in a later fresh session, with Part 1's deliverable as input. Its
  session-record sweep also collects per-record structural facts for Part 3.
- **Part 3 (record quality and templates)** — `PROMPT-session-taxonomy-part3-record-templates.md`.
  Serves 000276 (session-record quality analysis) and 000277 (session-documentation template and
  schema); proposes, never applies. Not a phase of the taxonomy plan: it is executed by
  `phase-fwa-03` (PLAN-041), and its schema output feeds `phase-fwt-04` (PLAN-040).

The review's other fixes are folded into Part 2: corrected corpus facts and record shapes, the
real-prompt extraction rule (command wrappers as signal, `/clear` openers skipped, meta records
excluded), the privacy guard routing all derived outputs to `_private/analysis/session-taxonomy/`,
worktree project dirs added to the corpus, blind anti-confirmation sampling, fuzzy
transcript↔SESS matching with confidence, the marker-absence-is-never-evidence rule, and the
portability attack step. Do not paste this file into a session.
