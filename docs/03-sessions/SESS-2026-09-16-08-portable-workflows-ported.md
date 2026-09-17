---
schema_version: 1
id: doc-session-portable-workflows-ported
code: SESS-2026-09-16-08
title: Safe commands and the idea-triage agent ported to portable workflows
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-governance, sys-backlog, sys-delivery]
depends_on: [doc-portable-agent-workflows, doc-portable-agent-workflow-requirements, doc-idea-record-system, doc-build-coordinator]
---

# Safe commands and the idea-triage agent ported to portable workflows

Second phase of [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md) batch 1, built by
dispatched agents under the coordinator (`agent-build`), executing **phase-port-02** — port safe
commands and the idea-triage agent — from the portable agent workflows plan (`PLAN-020`) and its
requirements (`REQ-005`).

## Outcome

Four canonical workflow bodies were added under `agent-workflows/` (`idea`, `backlog`,
`idea-triage`, and the `idea-triage-agent` role). `tools/generate_agent_workflows.py` — added to
this phase's deliverables by the owner's ruling at the batch open — gained three target kinds:
Claude command files, Claude custom agents, and Codex custom-agent TOML (rendered by a hand-rolled
writer, round-trip-tested with `tomllib`). Eight adapters are generated with provenance: three
Claude commands, one Claude agent, three Open Agent Skills (the Codex-compatible surface PLAN-020
designates), and one Codex TOML. The previously hand-authored, drift-prone copies of these files
are replaced by generated ones. The Codex adapter maps the triage role to `gpt-5.6-luna` (medium
reasoning, `workspace-write` sandbox) and declares the execution limits Codex cannot enforce.
`session-close` is excluded from every agent-discoverable kind by a single generic gate, with
refusal tests. Ten new tests in `test/test_agent_workflows.py`.

## Evidence

- `generate_agent_workflows.py --check`: 14 adapters current. Drift detection verified by the
  adversary via a tampered copy.
- `pytest test/test_agent_workflows.py test/test_ideas.py`: 82 passed. Full suite: 599 passed.
  Governance OK. All re-run by the coordinator directly.
- Independent validator: pass on all four acceptance conditions. Adversarial review: one blocker
  (integration hazard, below), one major refuted, one minor accepted.
- The adversary's challenge to `gpt-5.6-luna` was refuted by the coordinator's independent web
  verification: OpenAI's model page lists GPT-5.6 Luna as the cost-sensitive tier with Codex CLI
  agent-TOML support.

## Unresolved / integration notes

- The primary checkout carried an untracked local `.codex/agents/idea-triage.toml` (hidden by
  `.git/info/exclude`, still containing the old broken `.Codex/` path) colliding with this
  branch's tracked file. Defused at integration: the local file was backed up to the coordinator's
  working directory and removed before the merge; the now-obsolete exclude line is flagged to the
  owner.
- Accepted minor: the three command workflows reach Codex through Open Agent Skills rather than a
  Codex-native agent surface, per PLAN-020's designation.
- OPS-010's prose is slightly stale about the generator's target kinds (not a declared
  deliverable; left untouched).

Full evidence trail in `_working/build-b1/phase-port-02.md` (gitignored).
