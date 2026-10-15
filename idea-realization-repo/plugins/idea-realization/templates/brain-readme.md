# Brain

The team's shared memory: what we decided and why, what we found out, the words we use, who and
what we work with, and what each session learned. It is plain markdown in git, so every developer,
agent and model reads the same thing, and every entry says who wrote it.

## What goes where

| Folder | Kind | Holds |
|---|---|---|
| `decisions/` | `decision` | Why a choice was made: the options, what was chosen, what it costs |
| `research/` | `research` | Research notes, sources, comparisons, measurements |
| `concepts/` | `concept` | Domain terms, cloud and model concepts, product vocabulary: the glossary |
| `entities/` | `entity` | Teammates, stakeholders, sponsors, external services, cloud resources |
| `learnings/` | `lesson` | What a session learned that the next one should know |
| `learnings/` | `procedure` | How to do something. Only a developer marked `approves: [procedures]` in `docs/systems.yaml` records one; it carries `approved_by` and `approved_on` |
| `learnings/` | `note` | Meeting and demo notes |

`index.md` lists every entry and is generated; never edit it by hand.

## Recording an entry

```bash
uv run plugins/idea-realization/scripts/brain.py new decision \
  --title "Use one sandbox profile per role" \
  --body "We chose ... because ... The alternative was ..." \
  --tags cloud,security --sources "https://example.com/doc"
```

The author is your handle, from your git email (see `plugins/idea-realization/docs/workstreams.md`).
The command writes the entry in the right folder and regenerates the index. Commit both. `--links`
names related entries by id; every link must exist.

## Loading context

```bash
uv run plugins/idea-realization/scripts/brain.py load --kind decision
uv run plugins/idea-realization/scripts/brain.py load --tag cloud
uv run plugins/idea-realization/scripts/brain.py load --link use-one-sandbox-profile-per-role
uv run plugins/idea-realization/scripts/brain.py load --query bedrock
```

It prints the matching entries as one block to read before starting work. Superseded entries are
left out unless `--include-superseded` is given.

## Rules

- One idea per entry. Correct an entry by editing it and its `updated` date; replace one by writing
  a new entry that links to it and setting the old one's `status` to `superseded`.
- No confidential content: no customer names, credentials, account ids or keys. The
  confidentiality check runs on every commit.
- Until a developer is marked `approves: [procedures]` in `docs/systems.yaml`, no procedure can be
  recorded at all. Anyone else with a procedure in mind records it as a `lesson` and proposes it.
- `brain.py check` (also part of `check.py`) fails on bad front matter, an entry in the wrong
  folder, an author who is not a developer, a procedure without an approver's approval, a broken
  link or a stale index.
