---
name: catalog
description: Regenerate the document catalog, catalog.md under the document root, from the governed documents, the code register and the backlog when one exists. Use after adding, renaming or changing the status of a governed document, or when the check reports the catalog is missing or stale.
---

# Regenerate the catalog

The catalog is generated and committed; it is never edited by hand. The check renders it afresh
and fails when the committed file differs.

Run it from the repository root, assignments included. An option the person never saved appears
as its `${user_config.…}` text; the script treats that as unset and uses the documented default.

```bash
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" catalog
```

Report the output as printed. Exit 0 names the file written and how many documents it lists. Exit
1 lists every problem in the document tree and writes nothing; the catalog cannot be regenerated
until they are fixed.
