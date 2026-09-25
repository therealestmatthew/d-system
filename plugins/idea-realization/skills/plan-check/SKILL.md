---
name: plan-check
description: Check a plan draft for the sections a plan needs — context, design, work, verification, boundaries and open questions, plus requirement coverage and execution order when they apply — by reading its headings. Use before a plan goes to review, and on the plugin's plan template when writing a new plan.
---

# Check a plan's sections

The check reads headings only: a section is present when a `##` or `###` heading matches one of
its accepted names exactly, outside fenced code blocks. Whether a section says anything useful is
a reviewer's judgement, not this check's.

Run it from the repository root, assignments included. An option the person never saved appears
as its `${user_config.…}` text; the script treats that as unset and uses the documented default.

```bash
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py" <plan draft> [<plan draft> ...]
```

Report the output as printed. Exit 0: every draft has every section it needs. Exit 1: each
`<draft>: missing: <section>` line names one section the draft lacks. Exit 2: a draft could not
be read.

A new plan starts from the plugin's template, `${CLAUDE_PLUGIN_ROOT}/templates/plan.md`, which
passes this check as shipped.
