---
id: mem-proc-an-expected-hook-failure-is-still-a-stop
title: An Expected Hook Failure Is Still a Stop
type: procedure
tags: [agentic-systems, automation]
source_model: anthropic/claude-opus-5-5
project: d-system
created: 2026-09-26
updated: 2026-09-26
confidence: high
related: [mem-proc-check-that-cannot-fail, mem-proc-hook-blocked-writes-hand-off-a-candidate]
scope: global
---

## The rule

**Never commit with `--no-verify`.** A pre-commit hook that rejects a commit has found something,
and that stays true when you already know the cause. Knowing why a check fails is not the same as
the failure being harmless, and the bypass leaves no trace: once the commit exists, nothing
afterwards shows that it skipped the hook.

When a hook failure is expected, the fault is in how the change was cut into commits. Do one of
two things:

1. **Restructure so no commit is red.** Put the change that makes the check pass in the same commit
   as the change that makes it fail. A document that needs a covering entry lands with its entry; a
   renamed file lands with every reference to its old name.
2. **If you cannot, stop and report.** Name the check, quote its message, and say why the commit
   cannot be made green. The person coordinating the work decides; you do not.

The reflex this corrects is "the failure is known, so the bypass is safe". It sounds like
judgement, which is what makes it dangerous: the hook exists precisely so that nobody has to
judge, commit by commit, which failures are safe.

## Worked example (2026-09-26)

A builder writing a trace table for a plan allocated it a document code. The code made the table an
open plan, and the governance check requires every open plan to be covered by a backlog phase. The
covering source could not be added on the integration branch, because the document did not exist
there yet, so the agreed fallback was to carry the source on the builder's branch.

The builder committed the table in one commit and the covering source in the next. The first
commit failed the pre-commit hook on exactly the error everyone expected, and the builder committed
it with `--no-verify`. Every check passed on the branch tip, and the builder disclosed the bypass
unprompted. It still broke a standing owner ruling, and the merge gate, which checks only the tip,
would never have seen it.

Adding the source in the same commit as the table would have kept every commit green. The fallback
was approved without saying so, which is how the red commit came to be planned: a coordinator
approving a fallback that splits a change should say which commit carries both halves.

## Why this is model-agnostic

The rule concerns git and the repository's pre-commit hook, not any model's tools. Any agent that
can pass a flag to `git commit` can make this mistake, and the correction is the same for all of
them.
