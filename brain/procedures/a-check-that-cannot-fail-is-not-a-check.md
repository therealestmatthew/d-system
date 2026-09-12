---
id: mem-proc-check-that-cannot-fail
title: A Check That Cannot Fail Is Not A Check
type: procedure
tags: [agentic-systems, ai-tools, automation]
source_model: anthropic/claude-fable-5
project: d-system
created: 2026-09-12
updated: 2026-09-12
confidence: high
related: [mem-proc-runtime-behavior-needs-runtime-evidence, mem-proc-verify-before-claiming-ignorance]
scope: global
---

## The rule

Before running a verification, ask what output would mean **failure**. If no realistic outcome
produces one, the check is theatre: it will report success regardless of the state of the world, and
reporting that success is a false claim about having verified something.

Two questions catch nearly every instance:

1. **What would a failure look like here?** If the answer is "I'm not sure it can fail," stop and
   rebuild the check.
2. **Am I comparing two things that could actually differ?** A file against itself, a variable
   against a copy of itself, an expectation derived from the same source as the result — all of these
   compare a thing to itself and always pass.

## The tooling half of the trap

This failure usually starts earlier, as an **assumption about what a command does**. A flag named
`--catalog` sounds like it regenerates the catalog file; it may only print the catalog to stdout. A
check built on the assumed behaviour inherits the assumption and cannot detect that it was wrong.

Verify the mechanism before building a check on it: read the `--help`, or run it and look at what
changed on disk. One command settles it.

## Worked example (2026-09-12)

During the literature-review research pack work, a peer session correctly pointed out that
`docs/08-governance/catalog.md` renders from the backlog as well as the document set, so a
`backlog.yaml` edit can move it even when no document is added. The peer suggested the right check:

```bash
diff <(uv run python -m src.governance --catalog) docs/08-governance/catalog.md
```

What got run instead was: copy `catalog.md` aside, run `--catalog >/dev/null`, then diff the copy
against `catalog.md`. This was believed to be a drift check. It was a file compared to a copy of
itself — guaranteed to pass — and it was built on the unverified assumption that `--catalog` writes
the file. It does not; it prints, which is exactly why the peer's version pipes it into `diff`.

"CATALOG UNCHANGED" was duly reported. It meant nothing. The catalog genuinely was fine, confirmed
later by the full suite's `test_committed_catalog_matches_regenerated_output` — so the real
verification came from a test that was always going to run anyway, and the hand-rolled check
contributed nothing but false confidence.

**The generalisable lesson:** a check's value is entirely in its ability to fail. One that cannot
fail is worse than no check, because it converts an open question into a confident wrong answer, and
the next person inherits the confidence without the question.

## The near-miss variant

Reporting a check's result in terms that hide what was actually compared — "verified unchanged",
"confirmed in sync" — makes the defect invisible to a reader who might otherwise have caught it.
State what was compared against what, so the claim can be audited: not "catalog verified" but
"regenerated output diffed against the committed file."

## Why this is model-agnostic

Filed in `brain/` deliberately. Any agent under time pressure can reach for a plausible-looking
verification without asking what its failure mode is, and the repository's standing rule that a
failing check is a result to record presumes the check could produce one.
