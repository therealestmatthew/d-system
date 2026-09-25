---
name: idea-triage
description: Triage one open idea — dispatch the idea-triage agent to search the configured directories and files for related material, verify the finding it writes landed on the right idea, then move the idea from open to triaged. Use when someone asks to triage, scout or review an open idea.
---

# Triage one open idea

This skill triages **one idea per invocation**. It never moves an idea past `triaged`:
`reviewing`, `promoted`, `discarded` and every closing status are the owner's decisions.

Every command below starts with the same option assignments, so the person's saved plugin options
reach the script. Run them from the repository root, assignments included. An option the person
never saved appears as its `${user_config.…}` text; the script treats that as unset and uses the
documented default.

## 1. Choose the idea

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" list --status open
```

If the request names an idea id, triage that one, and only if the list shows it `open` — if it does
not, report its status and stop rather than guessing what was meant. If the request names none,
show the open ideas and ask the person which one to triage. Do not pick one yourself.

## 2. Read its effective state and the search list

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" show <id>

CLAUDE_PLUGIN_OPTION_TRIAGE_SEARCH='${user_config.triage_search}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/paths.py"
```

Take the title and body from `show`, never from the raw log: an amended idea's raw `created` line
still holds the text the amendment corrected. Take the search list from the `triage_search:` line
of the `paths.py` output; the paths there are absolute.

## 3. Dispatch the agent

Dispatch the `idea-realization:idea-triage` agent with the idea's id, title and body, the search
list, and these two commands written out in full — the id already substituted by you, never left
for the agent to fill in:

- the read command: the `idea.py list` command from step 1 without `--status open`, and the
  `idea.py show` command from step 2, for any idea id;
- the write command, with `<id>` replaced by the idea's id:

  ```
  CLAUDE_PLUGIN_OPTION_IDEAS_PATH='<the same value as above>' \
  uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" annotate <id> --author agent-idea-triage --kind finding --file <your finding file>
  ```

Tell the agent to run the write command verbatim, changing only the file path. Handing it the
literal command removes the step where an agent retypes an id from memory and writes one idea's
finding onto another idea.

## 4. Verify the write before trusting the report

A self-report is not proof of what was written. Run `idea.py show <id>` again and read the newest
annotation. If it is missing, or it opens by naming a different idea as its subject, the write went
wrong: stop, do not move the status, and tell the person. Correct a misdirected finding with
`amend-annotation` on the idea that received it, using the `idea` skill.

The agent always writes a finding, including one that says nothing related was found. Every
triaged idea has at least one finding.

## 5. Move it to triaged

Only once the finding is verified:

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/idea.py" status <id> triaged
```

## 6. Afterwards

Re-render the view and check the feature:

```bash
CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/render_ideas.py"

CLAUDE_PLUGIN_OPTION_IDEAS_PATH='${user_config.ideas_path}' \
CLAUDE_PLUGIN_OPTION_IDEAS_VIEW_PATH='${user_config.ideas_view_path}' \
CLAUDE_PLUGIN_OPTION_PRIORITY_PATH='${user_config.priority_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py" --feature ideas
```

Report the idea's id and title, and the finding in one or two lines. Then list, separately, every
`PROPOSED LINK:` and `PROPOSED PROMOTION:` line the finding carries. They are proposals for the
person to run or discard with the `idea` skill. This skill never writes a `linked` event and never
moves an idea to `promoted`, whatever the finding proposes.
