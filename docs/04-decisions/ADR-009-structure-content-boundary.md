---
schema_version: 1
id: doc-structure-content-boundary
code: ADR-009
title: The structure/content boundary and where the portfolio lives
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-portfolio, sys-projection, sys-retrieval]
depends_on: [doc-governance-protocol, doc-confidentiality-sweep]
---

# The structure/content boundary and where the portfolio lives

## Context

This repository has never been pushed. `git remote -v` is empty and every commit is local, so nothing
has leaked and history is still free to rewrite at no cost. That window closes at the first push.

The intended end state is that a remote carries the **system** — schemas, governance, tooling, the
agent workflow — and not the owner's portfolio content. The audit in
[PLAN-006](../01-plans/PLAN-006-confidentiality-sweep.md) found no credentials anywhere, but real
content in six locations: 33 project files including three named client engagements plus personal
finances and health, a client identifier as a first-class tag, eleven real project IDs in `README.md`,
the client identifier used as a worked example in `ARCH-001`, the same identifier in two brain
memories, and a real client project ID in a `tools/load_context.py` docstring.

The last four matter most: a sweep that only gitignored `_data/` would leave the client name in
documentation, a memory and a source file, while feeling complete.

There is a live contradiction to settle. This protocol names `_data/` the git-tracked source of
truth, `sys-portfolio` lists `_data/projects` and `_data/tags.json` as existence-checked paths, and
the governance validator reads them to resolve tag and project references. So `_data/` cannot simply
be gitignored: a fresh clone would fail its own governance check with a missing path, and CI would be
red on arrival.

The capture work makes this urgent rather than theoretical. `phase-cap-08` seeds the portfolio through
the capture pipeline, generating exactly the personal material this decision exists to keep out of the
tracked tree.

## Decision

### 1. The boundary

**Structure is tracked. Content is not.**

| Side | What it is | Examples |
|---|---|---|
| Structure | Anything that describes how the system works, and stays true if every record were replaced | Schemas, DDL, tooling, governance documents, ADRs, plans, the tag *taxonomy shape*, the agent workflow |
| Content | Anything that describes the owner's actual life or clients, and would be false or meaningless for another user | Project records, people, commitments, tasks, interactions, decisions, raw captures, client identifiers |

The test when a case is unclear: **would this file still be correct if a different person adopted the
system?** If yes it is structure; if no it is content. A worked example naming a real client is
content wearing a structure costume, which is how the identifier reached `ARCH-001` and two memories.

### 2. The portfolio relocates rather than hides

Real records move to `_private/portfolio/`, which is already gitignored. `_data/` stays tracked, keeps
its role in the protocol, and holds a small fictional portfolio that exercises every schema field in
use. A `D_SYSTEM_DATA_ROOT` environment variable, defaulting to `_data/`, points the loader, the
validator and the retrieval CLI at the real records on the owner's machine.

Gitignoring `_data/` in place was considered and rejected. It leaves real files sitting at the exact
path the tooling expects, protected only by an ignore rule: one `git add -f`, one careless `.gitignore`
edit, or one tool that writes there re-exposes everything. Moving the content removes the failure mode
instead of guarding it.

Stated plainly, the cost: the owner runs with an environment variable set, and two data roots exist.
That is the price of the tracked tree never containing real content **at any commit**.

### 3. A fresh clone stays green

This is a constraint on every later phase, not an aspiration. A clone into a clean directory, with no
environment variables set and no bootstrap step, must satisfy:

```bash
uv run python -m src.governance          # exits 0
uv run pytest                            # passes
uv run python tools/rebuild_db.py        # builds from the fictional set
```

Any design that requires the owner's machine to pass its own checks is rejected by this constraint.
It is also what forces the fictional portfolio to be real data rather than a stub: the validator
resolves document `tags` against `_data/tags.json` and memory projects against `_data/projects/`, so
an empty tracked `_data/` would fail.

### 4. Captured content is content

Raw captures, staging and everything promoted from them are content by the definition above.
[ADR-007](ADR-007-capture-routing.md) already makes capture private by default; this decision is what
that rule derives from. The owner's own test — that what gets committed should benefit the
application rather than encode personal prioritisation — is the same boundary stated from the other
direction.

### 5. The protocol yields to the code

`GOV-001` says `_data/` is where the original business data lives. After relocation that is true of
the *configured data root*, not of the tracked path. The protocol is amended to say so, in the same
change as this decision, so no reader is left with a document that contradicts the tooling.

## Alternatives considered

**Gitignore `_data/` and track `_data.example/`.** Rejected: real files stay at the expected path
behind an ignore rule, and a fresh clone needs a bootstrap step to become usable.

**Keep everything tracked in a private remote.** Rejected as the primary defence. It makes the sweep
unnecessary only for as long as the visibility setting never changes, and it protects nothing against
a fork, a clone, or a later decision to open the repository. A private remote is worth having *in
addition*, which is why PLAN-006 keeps it as an open question rather than a substitute.

**Scrub identifiers but keep the real portfolio tracked.** Rejected: the project names, descriptions
and notes are themselves the content, so scrubbing identifiers alone would leave three named client
engagements and the owner's finances and health in git.

## Consequences

- Two data roots exist, and the owner runs with `D_SYSTEM_DATA_ROOT` set. Every tool that reads source
  data must honour it, or it will silently read the fictional set.
- The fictional portfolio must exercise every schema field in use, which makes it maintenance work
  whenever a schema grows — and also gives the `phase-sig-*` and `phase-syn-*` tracks something to
  develop against that they have never had.
- `.gitignore` alone is not the enforcement mechanism. `phase-priv-04` adds a leak check because a
  rule that only lives in an ignore file protects against accident, not against `git add -f`.
- History still contains everything. This decision governs the working tree; `phase-priv-05` deals
  with history and remains the gate on any push.

## Revisit trigger

Revisit if the environment-variable indirection proves error-prone in practice — specifically if the
owner ever rebuilds the projection against the fictional set by accident, which would mean the default
is pointed the wrong way and the real root should become explicit instead.
