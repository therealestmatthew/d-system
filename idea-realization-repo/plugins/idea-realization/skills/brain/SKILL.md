---
name: brain
description: Load the team's shared memory before work, or record a decision, research note, concept, entity, lesson, procedure or meeting note in one step. Use at the start of a session to load context, when a session reaches a decision or learns something the next one should know, or when someone says "remember this", "write this down", "record that decision" or "what do we know about".
---

# The brain

The team's shared memory lives under `brain_root` (default `brain/`), one markdown entry per file.
`brain/README.md` says what goes where.

## Values

```bash
CLAUDE_PLUGIN_OPTION_BRAIN_ROOT='${user_config.brain_root}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/brain.py" check
```

If the check fails, report what it says before recording anything.

## Load context at the start of a session

Load what bears on the work: by the phase's tags or subject, and every decision touching it.

```bash
CLAUDE_PLUGIN_OPTION_BRAIN_ROOT='${user_config.brain_root}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/brain.py" load --query <subject>

CLAUDE_PLUGIN_OPTION_BRAIN_ROOT='${user_config.brain_root}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/brain.py" load --kind decision --tag <tag>
```

Read what it prints before planning. If an entry contradicts what you were about to do, say so
rather than working around it.

## Record in one step

Choose the kind:

| You have | Kind |
|---|---|
| A choice made, with its reason and the alternative | `decision` |
| Findings, sources, a comparison | `research` |
| A term or how something works | `concept` |
| A person, stakeholder, sponsor, service or cloud resource | `entity` |
| Something this session learned that the next should know | `lesson` |
| How to do something | `procedure` |
| Meeting or demo notes | `note` |

Then write it, with the body passed on standard input so no quoting gets in the way:

```bash
CLAUDE_PLUGIN_OPTION_BRAIN_ROOT='${user_config.brain_root}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/brain.py" new <kind> --title "<one line>" \
  --tags <a,b> --links <ids> --sources <urls or documents> --body - < <body file>
```

Write the body as a reader in a month would need it: what, why, and what it rules out. Commit the
entry and `index.md` together.

## What this skill never does

- It never records confidential content: customer names, credentials, account ids or keys.
- It never adds an anti-pattern `procedure` without the owner's approval of that procedure; it
  proposes one instead.
- It never edits another developer's entry to change its meaning; it writes a new entry that links
  to it.
