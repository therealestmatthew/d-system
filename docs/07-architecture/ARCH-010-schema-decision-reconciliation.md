---
schema_version: 1
id: doc-schema-decision-reconciliation
code: ARCH-010
title: Schema discussion reconciliation and remaining design work
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-18'
updated: '2026-09-18'
systems: [sys-contracts, sys-portfolio, sys-capture, sys-governance, sys-projection]
depends_on: [doc-schema-catalog, doc-organizational-and-wbs-data-model, doc-schema-architecture-review]
---

# Schema discussion reconciliation and remaining design work

This is the traceability index for the owner's September 17–18 interview. It records design
decisions, not delivered schemas. No implementation plan, requirement, or backlog phase is created
by this reconciliation. The owner authorized committing and merging the documentation into dev.

## Accepted decisions and lineage

| Topic | Accepted outcome | Canonical idea lineage |
|---|---|---|
| Organizations | Separate company records for legal/operational entities; typed directed dated company relationships; operational/legal names, domains, status and external identity | 000257 |
| People | One canonical person; separate dated affiliations; typed aliases with normalized values, organization context, provenance, primary/review state; controlled address sharing/reuse | 000258, 000259 |
| Project parties | People, companies and representation through affiliations; one role per dated participation; delivery and client sides may each contain multiple parties | 000260, 000265 |
| Roles | Reusable catalog and project-specific definitions; project type, scale and complexity influence role requirements, quantity, allowed party types and overlaps | 000261 |
| Temporal semantics | Half-open effective intervals; effective and recorded time for historical corrections; distinct recurring/concurrent assignments | 000258, 000261, 000267 |
| Opportunity | Potential engagement; prospect denotes the party and prospecting the activity; role-bearing participants and staged transition history; one opportunity can yield multiple engagements through explicit links | 000262, 000267; expanded scope, no separate idea yet |
| Engagement | Begins at qualified mutual intent to pursue or authorize work, before contract signature; projects and non-project work; dated many-to-many project participation | 000262 |
| Non-project execution | Existing tasks/commitments may reference engagements directly with projects optional | 000262 |
| Business paperwork | Business-contract separated from data/programming contracts; many-to-many engagement-contract links; document-asset for files/versions/locations; typed document-link and external-reference records | 000267; expanded scope, no separate idea yet |
| Templates | Reusable versioned patterns; instances pin the exact version; updates are explicitly applied with lineage preserved | 000267; expanded scope |
| WBS | Typed hierarchy with work packages, immutable element IDs, versioned dotted codes, responsibility via project party, task/commitment attachments; event-driven changes and separate approved baselines | 000263, 000264 |
| Dependencies | Separate typed work-dependency links; hierarchy is not schedule precedence | 000263, 000267 |
| Identity | Central append-only allocation/history registry, stable prefixed opaque IDs, never reuse; legacy IDs and document codes preserved; readable codes initially for documents, ideas, projects, engagements, WBS only | 000267; expanded scope |
| Registries | Separate identity/schema registries; schema registry foundational; separate schema-mapping with versions, transformations, cardinality, provenance and validation | 000267 |
| Schema evolution | Breaking changes versioned with migration and compatibility validation; domain steward prepares/validates, repository owner approves | 000267 |
| Unresolved identity | Separate provisional-party records; shared PartyRef discriminates resolved/provisional targets; manual identity stewardship now, automation later | 000255, 000259, 000265 |
| Classification and links | Shared tag-assignment; analytical shared dimensions distinguished from explicit record relationships; mappings require semantic compatibility | 000267, 000268 |
| Amendment semantics | Per-schema event folding or full-record replacement, separate retention declaration; multiplicity is independent; event payloads typed with shared metadata; incompatible amendments require explicit resolution | 000267 |
| Migration | Phased implementation; new relationships authoritative, temporary generated legacy compatibility, usage measurement then retirement | 000260, 000267 |
| Vocabulary | Conceptual/relational glossary, separate glossary-term schema, links to authoritative schemas and evidence; field manuals remain separate | 000266, 000267 |
| Future work | MDM system and dedicated stewardship agent parked; ontology/epistemic/temporal idea classification and tags/links/transitions captured for further design | 000255, 000256, 000268 |

ARCH-007 contains the architectural narrative; ARCH-008 records schema names and policies; the
canonical glossary source is brain/concepts/terms-organizational-schema-system.md. The generated
glossary is not hand-edited. This table identifies topic lineage, not formal idea promotion. The
expanded topics above do not yet each have a dedicated idea, plan, or implementation completion link.

## Corrections and superseded alternatives

- Full event sourcing for every object was superseded by the owner's per-schema replacement/fold
  clarification. Idea and WBS histories remain append-only. Global identity remains stable under
  replacement; replacement retention must be declared, not assumed.
- WBS dotted codes are versioned labels, not immutable object identities. Historical codes remain
  traceable after explicit moves; silently reusing a retired code is prohibited.
- Provisional identities are durable records, replacing the earlier text-only unresolved fallback.
- The planned business schema is business-contract, not the ambiguous contract name.
- Project membership moves to one relationship authority with derived transitional legacy fields.
- Effective intervals and engagement start are settled; they are no longer open interview questions.
- Role and alias rule capabilities are accepted, but exact vocabularies/algorithms are still open.
- An engagement's existence does not itself assert a signed agreement or authorize delivery.
- A shared property name is insufficient to infer a join between particular business records.

## Audit reconciliation

ARCH-009 and its 40 links remain an evidence snapshot. The adjacent ARCH-010-schema-links.json
records later accepted relationship additions and shared-dimension groups as design data. It is
not an executable runtime registry. Every link states direction, cardinality and relationship
mechanism; provisional cardinalities are marked for review. A shared-dimension group denotes pairwise
analytical association among its members, never a foreign-key assertion.

The originally delayed worker also completed: commit d39d007 on agent/schema-review-01 contains
a separate ARCH-009-schema-adversarial-review.md and link map. That branch is preserved, not merged:
its document code collides with the integrated review. Relevant additional findings carried forward
here are projection loss of repository/capture fields, overloaded project types, runtime-config
schema gaps, identity-event and contract-party modeling, and reproducible projection metadata.
Neither review's proposal of many-to-many WBS work attachment was approved; the current accepted
model allows tasks/commitments to reference an element, and additional allocation semantics remain open.

The second review identifies a TypeScript workbench-layout consumer, whereas the first labels it
contract-only based on backend inspection. Therefore lack of DuckDB projection is not evidence of
lack of a UI consumer; verify that consumer path when building the machine-readable maturity register.
Do not rewrite historical tag/schema counts as though those snapshots described today's checkout.

## Idea history reconciliation

The primary checkout contained canonical writer-produced creation events 000255–000268, including
MDM ideas 000255/000256 and triage for 000255–000266. The architecture worktree had ten independently
allocated, uncommitted duplicates using 000255–000264 for company-through-vocabulary ideas. They
were not merged as events: that would assign two meanings to the same IDs. The canonical log was
transferred byte-for-byte and its generated view rebuilt. No canonical event was edited or renumbered.

Duplicate-to-canonical correspondence: 000255→000257, 000256→000258, 000257→000259,
000258→000260, 000259→000261, 000260→000262, 000261→000263, 000262→000264,
000263→000265, 000264→000266. The discarded working-copy interpretation is not an alias allocation.
Both pre-reconciliation files are preserved in /tmp/schema-reconcile-00gxDw; the exact duplicate
events are also retained in the reconciliation evidence file under docs/00-working/.
Ideas 000267 and 000268 now have independently verified agent findings and are triaged, alongside
the earlier twelve. 000267 matches the planned registry architecture but is not implemented;
000268 matches ARCH-005, PLAN-029/REQ-014 and PLAN-039, with implementation phases still queued.
Proposed links, not executed: 000267 extends 000255 and relates_to 000268; 000268 extends 000061
and relates_to 000236. No promotion was proposed.
Earlier findings saying the organizational effort is deferred describe its earlier stage; design
has since advanced, but no implementation plan has been approved or ideas promoted.

## Remaining work and gates

| Area | What remains | Gate |
|---|---|---|
| Idea lineage | Review proposed links; decide whether expanded opportunity, contract, template, registry and history topics need distinct ideas; attach plan/phase/completion evidence later | Before plan promotion |
| Party contracts | Exact reusable PartyRef, affiliation validation, provisional merge/split/resolution events; contract-party representation | Before party schemas |
| Identity | UUID/ULID choice, prefix semantics, atomic allocation, namespace collisions, alias/supersession rules, domain-code formatting and scope | Before foundational registry implementation |
| Object policies | Assign fold/replacement and retention policies per schema, shared event envelope fields, amendment conflict detection and authority | Before writers/migrations |
| Roles and aliases | Versioning, primary scope, normalization, shared/recycled mailbox rules, overlap cardinalities, unknown dates, warning versus rejection | Before people/participation migrations |
| Commercial lifecycle | Exact opportunity states and transition guards; distinguish won/converted/mutual intent; partial conversion; engagement/contract state propagation and delivery authorization | Before lifecycle implementation |
| Contract/template assets | Parties and amendments, signatures versus file versions, version storage/access, template-use representation | Before business-contract implementation |
| WBS | Root/acyclic/same-project invariants, allowed parent types, tombstones, code allocation scope, atomic event publication, baseline hash/replay algorithm | Before WBS implementation |
| Relationships | Opportunity-engagement conversion storage; task/commitment engagement cardinality; WBS attachment allocation; dependency cycle rules | Before relation contracts |
| Registry coverage | Enumerate source/validator/writer/loader/consumer per schema; include JSONL/YAML and durable configuration; distinguish fragments from objects; prevent recursive governance/event regress | Before registry acceptance |
| Projection integrity | Source-reference validation, accepted-but-unprojected fields, idempotent migrations and before/after counts; classify portfolio activity/goal/system/certification versus bounded project | Before migration acceptance |
| Vocabulary | Concrete glossary-term fields/migration from concept memories; shared dimensions' units, grains and semantics | Before glossary registry implementation |
| Delivery | Governed requirements, plan, backlog phases and revised adversarial review; implementation fixtures, privacy/access/retention choices | Before implementation |

New schemas remain planned. Universal history, additional schemas, and complete machine-executable
relationship enforcement must not be inferred from a passing documentation-governance check.
