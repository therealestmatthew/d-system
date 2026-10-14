---
name: scaffold
description: Create the idea log, rendered view, priority file, backlog, document root, registers and schemas that the idea-realization features need in this repository, without overwriting anything, and record every file written in an install-state record. Use when setting the plugin up in a repository or adding a feature to one that has it.
---

# Scaffold the repository

The scaffold never overwrites a file that exists; it reports every path as created or skipped and
records each file it writes, with its SHA-256, in `.idea-realization/install-state.json`. It never
writes `.claude/settings.json` or a hook. It changes `.gitignore` only with the person's separate
consent, and records that consent.

Both commands below start with the same option assignments, so the person's saved plugin options
reach the script. Run them from the repository root, assignments included. An option the person
never saved appears in them as its `${user_config.…}` text; the script treats that as unset and
uses the documented default. The values are single-quoted so the shell leaves that text alone; a
saved path that itself contains a single quote is not supported.

## 1. Choose the features

Ask with the AskUserQuestion tool which features to set up, as a multi-select: `ideas` (the idea
log, rendered view and priority file), `partition` (the staging directory), `backlog` (the phase
catalog) and `documents` (the document root, code register and systems registry). Recommend `all`
for a repository adopting the whole pipeline.

## 2. Dry run

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py" --feature <feature> --dry-run
```

Repeat `--feature` for each choice. Show the person the plan as printed. `skipped … (exists)`
means their file stays exactly as it is; `not shipped by this plugin version` means this version of
the plugin has no file to copy there yet.

## 3. Ask for consent to change `.gitignore`

If the plan contains a `needs consent  .gitignore` line, ask separately, with the AskUserQuestion
tool, whether the scaffold may add the lines it names. This consent is independent of the scaffold
itself: a no still scaffolds everything else.

## 4. Scaffold

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_STAGING_DIR='${user_config.staging_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py" --feature <feature> [--consent gitignore]
```

Pass `--consent gitignore` only on a yes in step 3. Report every line as printed, then run the
`doctor` skill once to confirm the record matches the disk.
