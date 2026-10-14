# Workstreams: who owns which paths

A team of developers on separate machines works in two layers.

- The **inner layer** is the phase claim: one phase at a time per agent, claimed on the control
  integration branch, with the concurrency check refusing phases whose systems, deliverables or
  dependencies overlap. It works the same for one developer running one agent as for one running
  several.
- The **outer layer** is the workstream: a part of the product one developer owns, such as the user
  interface, the product's own agent orchestration or the backend. A workstream names the paths it
  covers. Other developers' phases stay out of them.

A workstream is ownership, not a lock. It is claimed once and held, so the git race that a
frequent claim would run into almost never happens. It feeds the phase claim rather than replacing
it: the check refuses a phase whose deliverables fall inside a workstream someone else owns.

## The registry

`docs/workstreams.yaml`, validated by `.idea-realization/schemas/workstreams.schema.json`:

```yaml
schema_version: 1
workstreams:
  - id: ui
    title: User interface
    owner: ""            # a developer handle once claimed
    status: open         # open | claimed
    paths:
      - product:web/
    interfaces: []       # documents stating what this workstream provides to others
```

The owner writes the list of workstreams. Developers claim them.

## Developers and handles

A developer is an entry in the `owners` map of `docs/systems.yaml` that lists their git author
emails:

```yaml
owners:
  repository-owner: The person accountable for this repository.
  ana:
    description: Ana, user interface.
    emails: [ana@example.com]
```

The key is the developer's **handle**: lower-case letters and digits, starting with a letter, at
most sixteen characters. `uv run plugins/idea-realization/scripts/identity.py` prints yours, from
`git config user.email`. The handle scopes every identifier a developer allocates, so two
developers working offline never allocate the same one:

- an idea id is `<handle>-NNNNNN`, counting that developer's own ideas;
- a phase claim's agent is `<handle>/agent-<name>`.

## Claiming and releasing

```bash
uv run plugins/idea-realization/scripts/workstreams.py show
uv run plugins/idea-realization/scripts/workstreams.py claim <id>
uv run plugins/idea-realization/scripts/workstreams.py release <id>
```

`claim` writes your handle into an open workstream and validates the result; it never commits.
Then, in the control repository's primary checkout on its integration branch:

1. commit only `docs/workstreams.yaml`;
2. push;
3. if the push is rejected, someone else pushed first: `git pull --rebase`, then
   `workstreams.py check`. If the workstream is still yours and the check is clean, push again;
   if someone else claimed it, choose another.

Only a workstream's owner releases it.

## What the check enforces

`workstreams.py check`, which also runs as part of the plugin's `check.py`, reports:

- two workstreams whose paths overlap;
- a claimed workstream whose owner is not a developer, or an open one that names an owner;
- once at least one workstream exists, an active or blocked phase whose `agent` carries no handle;
- an active or blocked phase whose deliverables fall inside a workstream claimed by another
  developer, unless the phase records that developer's approval:

```yaml
cross_workstream:
  - workstream: ui
    approved_by: ana
```

A path outside every workstream is shared ground: only the phase claim applies to it.
