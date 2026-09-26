# System Boundary Study — System and Interface Inventory

## Baseline and method

- **Baseline:** `2fd11e9ccabc15dbab227e78e05c08b68750396c` on `agent/phase-bnd-01`, recorded 2026-09-26.
- **Registry authority:** `docs/08-governance/systems.yaml` at that revision. This inventory covers its 43 registered entries exactly once; no `_private/` path was read.
- **Evidence rule:** `Registry` below means that entry's `paths`, `depends_on`, and description in `systems.yaml`; `ARCH-002` and `ARCH-006` are supporting evidence where cited. “Unknown” identifies an evidence gap rather than guessing an ownership fact.
- **Concern labels:** personal-productivity core (durable portfolio and memory work); idea-realization core (idea-to-delivery workflow); workbench core (interactive repository surface); cross-cutting framework (governance/rules); shared foundation (reused technical substrate); adjacent (related but independently bounded); incubating (planned work with no present runtime); legacy/retired (kept only as historical registry context).

## Whole-registry inventory

| System | Disposition | Source of truth | Writers | Readers / interfaces | Evidence / unknowns |
| --- | --- | --- | --- | --- | --- |
| `sys-contracts` | shared foundation | Schemas under `schemas/` | Schema authors | Source preflight; rebuild and validators | Registry; no runtime schema-to-API contract evidenced. |
| `sys-portfolio` | personal-productivity core | Tracked fictional `_data/`; real data is explicitly outside this study | File editors; `tools/append_idea.py` for ideas | Rebuild, idea projection, overview tools | Registry; current production data authority is intentionally not inspected. |
| `sys-capture` | personal-productivity core | Gitignored capture locations and capture contracts | `tools/capture.py` / inbox scanner | Future structuring and human operators | Registry; promotion into portfolio remains unimplemented. |
| `sys-brain` | personal-productivity core | `brain/` Markdown with YAML | Humans and models directly | Rebuild; glossary; retrieval | Registry; no dedicated writer or conflict resolver. |
| `sys-projection` | shared foundation | Rebuild inputs, DDL, generated DuckDB | `tools/rebuild_db.py` | Retrieval and any direct DB consumer | Registry, `ARCH-002`; DuckDB is a disposable projection, not authority. |
| `sys-retrieval` | personal-productivity core | DuckDB projection | No writer (read-only CLI) | Human/model callers via `tools/load_context.py` | Registry; no agent router or vector search. |
| `sys-api` | shared foundation | Python application source | Application developers | HTTP health/router surface; React proxy | Registry, `ARCH-002`; no domain API is evidenced. |
| `sys-ui` | workbench core | React scaffold and workbench plan | Frontend developers | Browser users; FastAPI interface | Registry; identity is transitional while detailed workbench ids operate. |
| `sys-wb-layout` | workbench core | Layout files and slot engine | Layout/configuration authors | All registered workbench panels | Registry; configuration storage is browser-side plus `_data/workbench/layouts`. |
| `sys-wb-styles` | workbench core | `StagePage.css` | Frontend developers | Stage/layout/panel rendering | Registry; shared presentation contract. |
| `sys-wb-shared` | workbench core | Shared stage primitives | Frontend developers | Terminal, explorers, viewer through imports/bridge | Registry; `panelBridge` is the stated cross-slot interface. |
| `sys-wb-terminal` | workbench core | Terminal panel source and injection override data | Frontend developers; override-data editors | Browser ↔ demo PTY websocket backend | Registry; backend ownership remains `sys-demo-stage`. |
| `sys-wb-notes` | workbench core | Notes-strip component | Frontend developers | Browser stage | Registry; no separate durable notes authority is stated. |
| `sys-wb-explorers` | workbench core | Explorer and file-browser components | Frontend developers | Repository-facing browser panels; viewer bridge | Registry; explicitly imports a viewer extension constant (known dependency leak). |
| `sys-wb-viewer` | workbench core | HTML/overview viewer components | Frontend developers | Browser panels; API / generated HTML inputs | Registry; caching/staleness policy is component-owned. |
| `sys-html` | incubating | Dynamic-HTML plan and templates placeholder | No implemented writer | Intended YAML→JSON→API→UI path | Registry; planned, so live ownership/interface unknown. |
| `sys-course` | retired | None in this repository | None | Historical registry entry only | Registry; explicitly extracted elsewhere and no tracked path remains. |
| `sys-signals` | incubating | Mini-systems plan | No implemented writer | Intended projection consumers | Registry; no SQL views exist. |
| `sys-synthesis` | incubating | Mini-systems plan | No implemented writer | Intended briefs/digests | Registry; depends on planned signals. |
| `sys-memory-agents` | incubating | Agent-memory plan | No implemented writer | Intended memory/retrieval roles | Registry; no agents/vectors/pruning tool. |
| `sys-delivery` | cross-cutting framework | CI/configuration/tests | Developers and CI configuration editors | CI and local contributors | Registry; no deploy or release interface. |
| `sys-governance` | cross-cutting framework | Governance engine, schemas, registry and code register | Governance implementation maintainers | All document/phase validation callers | Registry; validates structure, not semantic truth. |
| `sys-plugin` | adjacent | Plugin plan and requirements | Future plugin builders | Future private installation target | Registry; package is planned and has no dependency on this repository runtime. |
| `sys-plugin-core` | incubating | Plugin skeleton child plan | Future plugin builders | Plugin installation/check dispatch | Registry; planned plugin sub-area. |
| `sys-plugin-ideas` | incubating | Plugin idea-system child plan | Future plugin builders | Plugin idea workflow | Registry; planned plugin sub-area. |
| `sys-plugin-partition` | incubating | Plugin partition child plan | Future plugin builders | Plugin partition workflow | Registry; planned plugin sub-area. |
| `sys-plugin-backlog` | incubating | Plugin backlog/session child plan | Future plugin builders | Plugin backlog/session skills | Registry; planned plugin sub-area. |
| `sys-plugin-documents` | incubating | Plugin document-governance child plan | Future plugin builders | Plugin governance checks | Registry; planned plugin sub-area. |
| `sys-plugin-generators` | incubating | Plugin generator child plan | Future plugin builders | Plugin templates/generators | Registry; planned plugin sub-area. |
| `sys-plugin-absolutes` | incubating | Plugin absolute-documents child plan | Future plugin builders | Plugin governance documents | Registry; planned plugin sub-area. |
| `sys-demo-stage` | workbench core | Stage source and demo plans | Frontend/backend developers | Browser ↔ loopback-gated PTY websocket | Registry; `ADR-014` narrows its terminal posture. |
| `sys-demo-overview` | incubating | Demo plan | Intended deterministic scripts | Intended generated overview page / workbench | Registry; planned despite named source inputs. |
| `sys-demo-kit` | adjacent | No tracked source path | Unknown | Intended consultant teaching artifacts | Registry explicitly provides no path; ownership and interfaces unknown. |
| `sys-backlog` | cross-cutting framework | `backlog.yaml`, schema and governance code | Owner/agents under claim protocol | Governance readiness, contributors, generated catalog | Registry; lifecycle authority is the backlog. |
| `sys-research` | adjacent | `research/` corpus | Research authors/campaign phases | Literature-review agents and readers | Registry; baseline/seed ledgers are read-only to campaign agents. |
| `sys-gov-docs` | cross-cutting framework | `docs/08-governance/` prose | Governance-document authors | Contributors and governance procedures | Registry; validation engine is deliberately separate (`sys-governance`). |
| `sys-auto-gateway` | incubating | Autonomous-operations plan | No implemented writer | Intended event-normalisation interface | Registry; planned only. |
| `sys-auto-ledger` | incubating | Autonomous-operations plan | No implemented writer | Intended durable run-ledger interface | Registry; planned only. |
| `sys-realization` | idea-realization core | `ARCH-006`, REQ-022 and PLAN-039 family | Owner and future orchestration agents | Idea log, backlog, governance; planned LangGraph/agent runtime | Registry, `ARCH-006`; system is planned, not runtime evidence. |
| `sys-fw-templates` | adjacent | Un-governed framework staging files | Framework-template authors | Future repository governance engine | Registry; explicitly not an extension of this engine. |
| `sys-fw-analysis-patterns` | incubating | PLAN-041 | Future analysis phase | Portable-framework pattern output | Registry; planned analysis only. |
| `sys-fw-analysis-sessions` | incubating | PLAN-041 | Future analysis phase | Portable-framework session extraction output | Registry; planned analysis only. |
| `sys-fw-analysis-protocol` | incubating | PLAN-041 | Future analysis phase | Portable-framework form-critique output | Registry; planned analysis only. |

### Reconciliation

The table has 43 rows: one for each `id` in the 43-entry registry at the baseline. Each has one disposition. The labels do not amend registry ownership or maturity; they are study evidence for later owner review.

## Boundary observations

- **Personal-productivity core** owns durable portfolio records and shared Markdown memory. The projection is an explicitly disposable read model, so it must not become an independent data authority (`ARCH-002`).
- **Idea-realization core** consumes the idea log and backlog as durable repository records; it does not own their lifecycle rules. Its orchestration/runtime is still planned (`ARCH-006`).
- **Workbench core** owns browser composition and panel state, while `sys-demo-stage` owns the PTY API behind the terminal panel. The viewer/explorer dependency is an existing code-level seam, not evidence that either owns the other’s data.
- **Cross-cutting framework** owns validation/coordination rules and their documentation, not portfolio data, user-facing workbench state, or an autonomous run’s business outcome.
- **Adjacent/incubating entries** remain explicitly visible rather than being forced into one of the three product concerns. Their planned state is a limit on any claim about present interfaces.
