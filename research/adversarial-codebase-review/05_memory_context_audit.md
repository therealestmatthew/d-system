# Memory and context audit

Stored records, retrievable memory and active context are different in the current implementation, but the distinction is narrower than the research hypothesis. `brain/` is an explicit memory record family. `load_context.py` selects those records into Markdown; it does not derive memory from idea transitions or inject anything into an LLM API. [E22](../evidence/code-evidence.md#e22) (`schemas/memory.schema.json:17-69`) [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`) [E64](../evidence/code-evidence.md#e64) (`research/architecture/architecture.md:221-294`)

## Persistence to prompt path

| Stage | Actual behavior | Excluded / not demonstrated | Evidence |
|---|---|---|---|
| Persist | Markdown body with type, confidence, scope, source_model, project, related and systems | No memory version/supersession/stance record in closed schema | [E22](../evidence/code-evidence.md#e22) (`schemas/memory.schema.json:17-69`) |
| Project | Rebuild copies current body/frontmatter into DuckDB | No automatic refresh after source edits | [E25](../evidence/code-evidence.md#e25) (`tools/rebuild_db.py:331-353`) |
| Select | Case-insensitive title/content substring LIKE; AND across type/project/tags/system filters | No embeddings, semantic similarity, graph expansion, learned relevance or temporal validity | [E23](../evidence/code-evidence.md#e23) (`tools/load_context.py:29-70`) |
| Rank | High → medium → low → other, then created descending | Updated date, task relevance and provenance do not rank results; ties lack an ID tiebreaker | [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`) |
| Format | Full selected body, ID/type/title, confidence, project-derived scope, source file path | source_model, related edges, updated and stored scope omitted from SQL selection | [E23](../evidence/code-evidence.md#e23) (`tools/load_context.py:29-70`) [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`) |
| Consume | Plain Markdown printed for reuse; caller/agent must supply it as context | No observed model request or persistent context-package identity | [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`) |
| Triage separately | Prompt instructs fold of effective ideas and repository term searches | No fixed replayable record of exact search results/context read | [E39](../evidence/code-evidence.md#e39) (`.claude/agents/idea-triage.md:15-41`) |
| Consolidate | Human/agent writes memory or session record under instructions | No autonomous reflection/compression/feedback pipeline in source | [E25](../evidence/code-evidence.md#e25) (`tools/rebuild_db.py:331-353`) [E42](../evidence/code-evidence.md#e42) (`.claude/skills/checkpoint/SKILL.md:51-65`) [E51](../evidence/code-evidence.md#e51) (`docs/09-backlog/backlog.yaml:2649-2719`) |

Interpretation confidence HIGH, bounded by repository inventory. An external model/session may consume these materials; that runtime was not observed.

## Explicit retrieval counterexamples

Synthetic database of twelve valid memories:

```text
all_count_of_12: 10
global_scope_other_project_included: false
session_scope_null_project_included_as_global: true
```

`--all` clears filters but not `LIMIT 10`. A memory carrying `scope: global` plus another project is excluded for the requested project; a temporary `scope: session` memory with null project is included and labeled “global.” The latter can spread session-specific guidance beyond its intended context. These are semantic selection errors, not just formatting defects. [E23](../evidence/code-evidence.md#e23) (`tools/load_context.py:29-70`) [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`); [probe source](../evidence/review_probes.py), [actual results](../evidence/review-probe-results.json).

An actual structural example also exists: `brain/concepts/terms-memory-and-retrieval.md:8-13` has `project: d-system`, `confidence: high`, `scope: global`; its definitions say scope and lifecycle differ. This combination is legal but is not treated globally by the loader for another project. [E57](../evidence/code-evidence.md#e57) (`brain/concepts/terms-memory-and-retrieval.md:55-72`)

## Stale/superseded-context risks

1. **Stale projection:** source edits do not reach the loader until rebuild. No source hash or freshness timestamp is compared before retrieval. [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`) [E25](../evidence/code-evidence.md#e25) (`tools/rebuild_db.py:331-353`)
2. **Stale high-confidence narrative:** author confidence outranks other memories regardless of `updated`. `brain/concepts/terms-plans-and-work.md` says completion evidence is recorded only at close, while backlog validation allows it during active/blocked checkpoints. This demonstrates a real drift risk in the content family the loader uses. [E56](../evidence/code-evidence.md#e56) (`brain/concepts/terms-plans-and-work.md:31-87`) [E36](../evidence/code-evidence.md#e36) (`src/governance/backlog.py:116-190`) [E42](../evidence/code-evidence.md#e42) (`.claude/skills/checkpoint/SKILL.md:51-65`)
3. **No supersession filter:** memory schema has no such field, and loader never joins decision/idea supersession. Old advice must be manually corrected, removed or recast. [E22](../evidence/code-evidence.md#e22) (`schemas/memory.schema.json:17-69`) [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`)
4. **Lost lineage in context:** source_model and related survive storage but do not appear as structured context metadata. The file path allows manual inspection; it does not reconstruct who approved or which evidence supports the entry. [E22](../evidence/code-evidence.md#e22) (`schemas/memory.schema.json:17-69`) [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`)
5. **Historical ideas bypassed:** raw idea history, dissenting annotations and promotion lineage are not queried by this loader. The triage workflow reads them separately; do not confuse its instructions with a unified retrieval algorithm. [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`) [E39](../evidence/code-evidence.md#e39) (`.claude/agents/idea-triage.md:15-41`)
6. **Unbounded body size:** limit bounds records, not tokens. Full bodies are included without summarization, truncation or compression; fewer records do not necessarily mean a smaller prompt. [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`)

Selection is partly explainable: the output prints supplied filters, IDs and file paths. It omits score explanations and suppressed candidates, and all-mode can print supplied filters that were ignored. A future evaluated context package could preserve selection inputs/results without requiring the entire proposed ontology. [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`) [E65](../evidence/code-evidence.md#e65) (`research/architecture/phase_context_contract.md:1-94`) Confidence MEDIUM for that design inference; alternative: direct human browsing may remain enough.

**Special-check verdicts:** Memory distinct from stored records: **PARTIALLY_SUPPORTED** (separate stored memory family, not demonstrated lineage-based influence). Context distinct from persisted knowledge: **SUPPORTED** (derived output). Topology/provenance-aware selection: **NOT_IMPLEMENTED** in the reviewed loader. [E22](../evidence/code-evidence.md#e22) (`schemas/memory.schema.json:17-69`) [E24](../evidence/code-evidence.md#e24) (`tools/load_context.py:73-116`) [E64](../evidence/code-evidence.md#e64) (`research/architecture/architecture.md:221-294`)
