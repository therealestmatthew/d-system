---
id: mem-proc-earlier-steps-are-not-absorbed-by-a-later-one
title: A Later Step Does Not Absorb an Earlier One
type: procedure
tags: [agentic-systems, ai-tools]
source_model: anthropic/claude-opus-5-5
project: d-system
created: 2026-10-04
updated: 2026-10-04
confidence: high
related: []
scope: global
---

## The rule

When an instruction names a later step of a governed procedure, still do every earlier step as the
procedure states it. A summary of how a process ends does not stand in for its middle steps.

`AGENTS.md` hand-off step 5 records `session`, `completion_evidence` and `result` on the phase. You
do it on the branch, before the rebase and before asking to merge. The completion edit made on `dev`
after the merge only sets `status: complete` and adds the merge to `result`.

## What happened (2026-10-04)

The coordinator's contract described the end of a phase as a "completion edit on dev after the
merge". That phrase was read as covering every completion field. Step 5 was skipped on three phases
in a row: `phase-des-11`, `phase-des-01` and `phase-des-02`. On the first two, `session`,
`completion_evidence` and `result` first appeared in the post-merge completion commits, `8042375`
and `7d06a7c`. On the third, the adversarial review compared the branch with `AGENTS.md`'s numbered
steps and caught the gap before the merge. The rule had been in `AGENTS.md` the whole time.

## The procedure

- **Before sending READY,** read your own phase entry on the branch. Confirm that `session`,
  `completion_evidence` and `result` are present and agree with the session record. Leave `status`
  as it is.
- **In the post-merge completion commit,** change `status` and the end of `result` only. Any other
  field that changes there was missed earlier.
- **When a peer's message summarises a procedure,** follow the governing document's numbered steps.
  Treat the summary as a reminder of where the process ends, not as a replacement for it.

## Why this is model-agnostic

The rule names files, fields and steps that every agent here works with. It does not depend on how
any one model reads instructions. The failure it guards against happens whenever a shorter
description of a process is used in place of the full one.
