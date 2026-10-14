---
name: tools
description: Answer which idea-realization script does what, which arguments and configured paths it takes, what its exit codes mean, and how to run it, from the plugin's generated tools reference. Use when someone asks what the plugin can do from the command line, which script to run for a task, or how to invoke one.
---

# Which script does what

Answer from one source only: the plugin's tools reference, generated from the scripts themselves.

Read `${CLAUDE_PLUGIN_ROOT}/docs/tools.md`.

It opens with the configuration rule every script shares: how a flag, an environment variable, a
saved plugin option and a default are ranked, and what relative paths are relative to. Then it has
one section per script: what the script does, the exact `uv run` invocation, its arguments, the
shared configuration flags it accepts, and the exit codes found in its source.

- To say which script fits a task, match the task against each section's opening paragraph and
  name the script, quoting its invocation.
- To say how to run one, give the invocation from its section and the arguments the task needs.
- When the reference does not cover the question, say so. Do not read the scripts' source to fill
  the gap, and do not guess a flag that is not listed.

This skill runs nothing. A task that needs a script run is the job of the skill that wraps it,
such as `next-code`, `catalog`, `plan-check`, `scaffold` or `doctor`.
