---
id: mem-proc-audit-your-own-corrections
title: Auditing a Document for Accuracy Introduces New False Claims
type: procedure
tags: [knowledge-base, agentic-systems, ai-tools]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-10
updated: 2026-09-10
confidence: high
related: [mem-proc-verify-before-claiming-ignorance, mem-proc-session-close-no-active-phase]
scope: project
---

## The situation

Someone asks for a document to be audited and cleaned up — a README, an orientation document, a
protocol page. The work is to find claims that have drifted from reality and replace them with
accurate ones. It feels like a low-risk task: you are removing errors, not adding features.

The characteristic failure is that **the replacement claims are themselves wrong**, and nothing
catches them. The old claims were at least written when they were true and drifted slowly. The new
ones can be false from the moment they are committed, and they arrive wearing the authority of a
freshly-audited document — which is worse than the staleness they replaced, because a reader has no
reason to doubt them.

The governance check does not catch this. `uv run python -m src.governance` validates front matter,
document codes, references and backlog structure. It has no opinion on whether a document's prose
matches the repository it describes. A table list can name relations that do not exist and the
check stays green.

## Why it happens even when you verify

Verification during an audit is naturally *sampled*, not exhaustive. You check the claims you
doubted enough to look up. The claims that go wrong are the ones you did not doubt:

- **A claim you inherited from a stale source.** Citing a registry, systems file or index as
  authoritative without checking that the registry is itself current. The document you are fixing
  and the document you cite may have drifted together.
- **A claim you compressed.** Replacing a long hand-maintained list with a pointer is usually right,
  but the pointer's own accuracy is a new claim you just made. "X lists the current entries" is a
  factual assertion about X.
- **A claim that is true of the example data but not of the contract.** Every tracked record having
  a field does not mean the schema requires it. Read the schema, not the fixtures.
- **A precision drift.** "References its owning commitment" reads as mandatory when the schema types
  the field as nullable and a view exists specifically for the parentless case.

## What to do

1. **Treat every claim you write as a new assertion requiring its own evidence**, at the same
   standard as the stale claim you are removing. Removing a wrong number and writing a different
   wrong number is not progress.
2. **When you replace a list with a pointer, verify the pointer's target.** The pointer is now the
   claim. If it points at a curated index or a registry, check that the index or registry is
   current — and if it is not, say so in the document rather than silently inheriting its error.
3. **Prefer code over registries as the authority for behaviour.** A `systems.yaml` entry describing
   what a preflight enforces is documentation that can drift; the module that runs the preflight
   cannot. Cite the module.
4. **Get an independent check of your own diff before it closes.** This is the only step that
   reliably works, because the failure is by construction invisible to the person who made it — you
   do not re-examine the claims you were not suspicious of. `/session-close`'s sub-agent review is
   the mechanism already available; give it the diff and instruct it to verify claims against the
   repository, not to check whether the session record is internally consistent.
5. **Do not fix an adjacent registry you hold no claim on.** If the correct fix reaches into another
   system's declared paths — and a peer may be active on that system — name the discrepancy in the
   document you are already editing and leave the registry to a phase that owns it.

## Worked example (2026-09-10)

`SESS-2026-09-10-10` audited `README.md` and `GOV-007-repo-orientation.md`, correctly removing
project counts describing gitignored records, wrong DuckDB row counts, a memory count that said 7
when the real number was 15, and a stale "Planned But Not Yet Built" section. Every removal was
right, and most replacements were verified against the repository.

Two replacements were false anyway:

- `GOV-007` asserted that `sys-contracts` in `systems.yaml` "lists the set the preflight enforces."
  `sys-contracts` lists six schemas and omits `task`; the sentence's own preceding clause named
  seven; and `ENTITY_DIRECTORIES` in `src/db/source_validation.py` plus the separate tag, memory and
  idea checks make the real number eleven. The error came from citing a registry without checking
  the registry.
- `README.md` asserted that `brain/index.md` "lists the current entries." It lists 10 of 15. The
  error came from replacing a wrong count with a pointer and not verifying the pointer's target.

Both were caught by the `/session-close` sub-agent review, not by the governance check, the test
suite, or the author's own verification pass — which had checked the DuckDB inventory, the
`load_context.py` flags, the Python version, every markdown link and every directory entry, all of
which were correct.

## Why this is worth a durable entry

The lesson is not "be more careful." Care was applied and the errors still landed, because the
mechanism of the failure is that you cannot audit the claims you had no reason to doubt. The
durable countermeasure is structural — an independent read of the diff by something that did not
write it — and it is worth knowing before starting an accuracy audit rather than discovering it at
close.
