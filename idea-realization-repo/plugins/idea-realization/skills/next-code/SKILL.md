---
name: next-code
description: Allocate the next free document code for a kind (plan, requirement, adr, architecture, prompt, operation, governance, session or walkthrough), reserved against every other worktree of this repository, or release a reservation taken for a document that will not be written. Use before creating any governed document, and whenever someone is about to choose a code by hand.
---

# Allocate a document code

A code is never chosen by hand, and the code register (`codes.yaml`) is never edited by hand to
take one. This
command reads every governed document and the register, computes the next free code for the kind,
and holds it with a reservation under the git common directory before printing it, so another
worktree allocating the same kind before either merges receives a different code.

Run it from the repository root, assignments included. An option the person never saved appears
as its `${user_config.…}` text; the script treats that as unset and uses the documented default.

```bash
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" next-code <kind> [--parent <plan document id>]
```

`--parent` allocates a sub-code under that plan's code, for a child plan. A dated kind (session,
walkthrough) takes today's date and no parent.

Report the printed code, or the output as printed when the command fails. Exit 1 means the
document tree fails its check or no code could be allocated; nothing was reserved.

If the document will not be written after all, release the reservation with the same script:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" release-code <code>
```

With no code, `release-code` lists the reservations held. An unreleased reservation expires on its
own after fourteen days.
