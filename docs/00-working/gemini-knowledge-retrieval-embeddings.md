# Deep Dive: Embeddings & Semantic Search

### 2.4 Embedding model

**Question:** Which locally-runnable embedding model fits this corpus?

**Finding:** **`nomic-embed-text-v2`** via Ollama is the clear recommendation.

| Criterion | nomic-embed-text-v2 | text-embedding-3-small (OpenAI) |
|---|---|---|
| **Local-only** | ✅ Runs fully local via Ollama | ❌ API call — violates constraint |
| **CPU performance** | ~580 chunks/sec on modern CPU | N/A (API) |
| **Model size** | ~274 MB download, ~0.3 GB RAM | N/A |
| **Dimensions** | 768 (truncatable to 256/512 via Matryoshka) | 1536 |
| **Python integration** | `ollama.embeddings()` — one function call | `openai.embeddings.create()` |
| **GPU required?** | No — MoE architecture optimized for CPU | N/A |
| **Cost** | Free | ~$0.02 per 1M tokens |

**Resource requirements for this corpus:**
-   ~13 brain memory files (averaging ~2 KB each)
-   ~20 governed documents (averaging ~5 KB each)
-   ~45 ideas (averaging ~2 KB each)
-   ~30 session records (averaging ~10 KB each)
-   Total: roughly 500 KB of text, or about 500 chunks at 1 KB per chunk.

At 580 chunks/sec on CPU, the full corpus embeds in under 1 second. Incremental re-embedding
(content-hash based invalidation, as PLAN-001's `memory_embeddings` table already specifies) would
touch only changed documents. This is not a performance-sensitive workload.

**Matryoshka dimension truncation** is worth using: 256 dimensions are likely sufficient for this
corpus size (hundreds, not millions, of documents) and reduce DuckDB VSS index size proportionally.
Start at 256; increase to 512 if retrieval quality measurement (phase-mem-10) shows it's needed.

**Runtime requirement:** Ollama must be installed and running as a local service. This is a separate
runtime from `uv`'s Python environment. The embedding adapter in Python calls Ollama's HTTP API
(`localhost:11434`). This is the same pattern used by any local LLM tool. No GPU is required.

**Conclusion:** Use `nomic-embed-text-v2` via Ollama. PLAN-001's recommendation of
`text-embedding-3-small` as primary with `nomic-embed-text` as fallback should be inverted and
simplified: Nomic is the only provider, run locally, no API dependency.

