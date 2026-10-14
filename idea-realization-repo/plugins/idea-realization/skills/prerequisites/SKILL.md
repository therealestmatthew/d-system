---
name: prerequisites
description: Check that this machine has what the idea-realization scripts need (Python 3.12+, uv, git, and the claude CLI for triage and partition), report each missing item with its install command, and install only after the person says yes. Use before the first scaffold, or when a plugin script fails because a tool is missing.
---

# Check prerequisites

This skill never runs on its own at session start. Run it when asked, before the first scaffold, or
when a plugin script fails for want of a tool.

## 1. Check — changes nothing

Run the check with the machine's Python, not through `uv`, because `uv` may be the missing item:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prerequisites.py" --feature all
```

Use `--feature ideas`, `--feature backlog` or `--feature documents` instead of `all` when the
person uses only those; the `claude` CLI is then reported as optional. Exit 0 means everything
required is present: report that and stop.

## 2. Ask before installing

Exit 1 means something required is missing. Show the person every `missing` line exactly as
printed, including its install command, and ask with the AskUserQuestion tool whether to install
them. Recommend installing only when every command shown is one they would run themselves.

An unanswered question is not a yes. Without a yes, stop here and leave the machine unchanged.

## 3. Install on a yes

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prerequisites.py" --feature all --yes
```

Report the output as printed. A `still missing` line after an install usually means a new shell is
needed for `PATH` to update; say so, and re-run step 1 in a new shell rather than installing again.
