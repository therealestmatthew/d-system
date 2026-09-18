---
schema_version: 1
id: doc-schema-architecture-review
code: ARCH-009
title: Adversarial schema, source and projection review
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-17'
updated: '2026-09-17'
systems: [sys-contracts, sys-portfolio, sys-capture, sys-projection, sys-governance]
depends_on: [doc-schema-catalog, doc-organizational-and-wbs-data-model, doc-architecture-overview]
---

# Adversarial schema, source and projection review

This review checks the repository's declared schema contracts against the source files, validators,
writers, DuckDB DDL, rebuild loader and current architecture documents. It is a review artifact,
not an implementation plan and not a replacement for the decisions in [ARCH-007](ARCH-007-organizational-and-wbs-data-model.md)
or [ARCH-008](ARCH-008-schema-catalog.md). No existing architecture decision is changed here.

The review intentionally excludes `_private/`. The source snapshot below is therefore the tracked
fictional example set plus the public repository structure. Counts are observations at review time,
not durable domain facts.

## Executive findings

1. **The schema directory is larger than the live projection.** There are 20 schema files. Eleven
   participate in `tools/rebuild_db.py`'s source preflight (the eight entity directories, tags,
   ideas and memories); four are validated by the governance audit (`document`, `backlog`, `codes`
   and `systems`); `capture`, `staged-record`, `evidence`, `idea-priority` and `workbench-layout`
   have writer, governance or isolated-test coverage but are not part of the DuckDB rebuild. The
   catalog needs this maturity distinction instead of treating every schema as an implemented
   domain contract.

2. **Relationship authority is currently split.** `person.projects` feeds `project_people`, while
   `project.stakeholders` is accepted by the project schema and ignored by the loader. `project.tags`
   is both an embedded source list and a projected junction. `promised_to`, `owed_by`, participant
   arrays and decision authors are person-shaped strings, not a shared party reference. This is the
   concrete migration pressure behind ARCH-007, not merely future ontology work.

3. **The planned graph is missing several mapping objects.** ARCH-008 names `opportunity` and
   `engagement`, but not the role-bearing `opportunity-party` and `engagement-party` records needed
   by ARCH-007's many-party language. It also names WBS elements and changes but leaves baseline
   metadata placement open. These omissions make the intended cardinalities impossible to represent
   without embedding arrays again.

4. **Cross-record integrity is weaker than the architecture prose implies.** The source preflight
   validates each file in isolation. The loader inserts optional `project_id`, tag IDs, person IDs,
   and task parents without resolving them, and the DDL has no foreign keys. ARCH-007 assigns this
   responsibility to source validation and loader checks, but those checks are not yet present.

5. **Several snapshots are stale or internally inconsistent.** ARCH-004 still describes six JSON
   schemas; the repository currently has 20. ARCH-001 and ARCH-002 describe 27 and 28 tags in their
   dated snapshots, while `_data/tags.json` currently contains 29. ARCH-002's zero-person and
   zero-commitment observation is also historical: the tracked example set currently has one of
   each. These are documentation refresh candidates, not changes made by this review.

## Current contract inventory

Status meanings in this table are deliberately operational:

- **projected** — a source path, validation path, loader and DuckDB table or view are all present.
- **governed** — a source and validator are live, but the object is intentionally outside DuckDB.
- **intake** — a writer and schema are live, but the object is not part of the rebuild projection.
- **contract-only** — schema/tests exist without a complete production source-to-consumer path.
- **partial** — a path exists, but it contradicts or drops part of the declared contract.
- **embedded** — a reusable schema fragment is carried inside another record rather than stored as
  its own durable object.

| Schema | Authoritative source | Validation / writer | Loader or consumer | Projection | Review status |
|---|---|---|---|---|---|
| `backlog` | `docs/09-backlog/backlog.yaml` | `src/governance/__main__.py`, `src/governance/backlog.py` | governance and workbench backlog routes | none | governed |
| `capture` | `_capture/raw/<id>.json` (ignored; absent in this checkout) | `src/capture/raw.py`; `test/test_capture_intake.py` | raw capture CLI/inbox writer | none | intake |
| `codes` | `docs/08-governance/codes.yaml` | governance audit and `src/governance/codes.py` | document-code allocation | none | governed |
| `commitment` | `_data/commitments/*.json` | `src/db/source_validation.py` | `tools/rebuild_db.py` | `commitments` | projected |
| `decision` | `_data/decisions/*.json` (directory not currently present) | source preflight when present | `tools/rebuild_db.py` | `decisions` | projected, no current sample |
| `development-event` | `_data/development-events/*.json` (directory not currently present) | source preflight when present | `tools/rebuild_db.py` | `development_events` | projected, no current sample |
| `document` | governed Markdown under `docs/` | governance audit and `schemas/document.schema.json` | catalog and governance tools | none | governed |
| `evidence` | embedded evidence maps on staged/domain records | `$ref` consumers and contract tests | staging/structuring contract | none | embedded |
| `idea` | `_data/ideas.jsonl` | `tools/append_idea.py`, `src/db/source_validation.py` | `tools/rebuild_db.py`, `src/db/ideas.py` | `idea_events`, `ideas`, `idea_annotations`, `idea_links` | projected |
| `idea-priority` | `docs/00-working/ideas-priority.yaml` | `src/governance/__main__.py`, `src/governance/idea_priority.py` | `tools/generate_ideas_md.py`, workbench queue | none | governed |
| `interaction` | `_data/interactions/*.json` (directory not currently present) | source preflight when present | `tools/rebuild_db.py` | `interactions` | projected, no current sample |
| `memory` | `brain/**/*.md` with YAML front matter | source preflight and governance audit | `tools/rebuild_db.py`, retrieval tools | `memories` | projected |
| `person` | `_data/people/*.json` | `src/db/source_validation.py` | `tools/rebuild_db.py` | `people`, `project_people` | partial: legacy relationship fields |
| `project` | `_data/projects/*.json` | `src/db/source_validation.py` | `tools/rebuild_db.py` | `projects`, `project_tags` | partial: embedded relations and dropped stakeholders |
| `staged-record` | `_capture/staging/*.json` (ignored; absent in this checkout) | isolated contract tests; no production staging writer | no rebuild consumer | none | contract-only |
| `systems` | `docs/08-governance/systems.yaml` | governance audit | governance inventory and document references | none | governed |
| `tag` | `_data/tags.json` | `src/db/source_validation.py` | `tools/rebuild_db.py` | `tags`, `project_tags` | projected |
| `task` | `_data/tasks/*.json` | `src/db/source_validation.py` | `tools/rebuild_db.py` | `tasks` | projected, unresolved parents allowed by current loader |
| `waiting-on` | `_data/waiting-on/*.json` (directory not currently present) | source preflight when present | `tools/rebuild_db.py` | `waiting_on` | projected, no current sample |
| `workbench-layout` | `_data/workbench/layouts/*.json` | `test/test_workbench_layout_schema.py` | workbench fixture/test surface; no rebuild loader | none | contract-only / UI configuration |

The current tracked example set has five projects, one person, one commitment, three tasks, 29
tags, and 26 brain memories. Several valid source directories are intentionally empty or absent;
that is different from having no schema or loader support.

## Contradictions and omissions

### Source and projection boundary

- `src/db/source_validation.py` has an explicit `ENTITY_DIRECTORIES` map for eight entity schemas,
  but no equivalent map for capture, staged records, workbench layouts, or governance registries.
  That is coherent only if the architecture labels those as separate pipelines. ARCH-008 currently
  presents one flat list and does not show the boundary.
- `tools/rebuild_db.py` drops and recreates 15 tables/views, but does not enforce references before
  inserts. Optional `project_id`, `commitment_id`, `interaction_id`, person IDs, and tag IDs can
  point to absent records. `sql/001_schema.sql` also has no foreign keys. This makes the documented
  “cross-record resolution in source validation and loader checks” a target state, not current
  behavior.
- The loader uses `person.projects` to create `project_people`; `project.stakeholders` is a valid
  schema property but is ignored. There are therefore two declared inputs for one relationship and
  one silently loses data. Choose one migration authority before adding project-party records.
- `project.tags` is a source array and `project_tags` is a relational projection, but there is no
  source contract for the relationship itself and no tag-existence check. The same pattern appears
  in document tags, memory tags, and several participant arrays.
- `workbench-layout` is structurally tested, including relational invariants inside the layout, but
  no general source preflight or runtime consumer is visible in the inspected backend. It should be
  labeled configuration-contract-only until a loader/consumer is named.

### Domain and identity boundary

- ARCH-007 says unresolved names remain text until identity is confirmed. ARCH-008 says unresolved
  parties are first-class provisional records. Those are different lifecycle choices: one preserves
  text in a relationship, the other creates a durable party object. Resolve this before defining a
  polymorphic `PartyRef`.
- `person.organization` and `person.email` are scalar fields, while ARCH-007 proposes separate
  `Company`, `Affiliation`, and `PersonAlias` records. Migration must define precedence and history;
  otherwise the old scalar and new normalized sources can disagree.
- `commitment.promised_to`, `waiting-on.owed_by`, `interaction.participants`, and
  `decision.decided_by` use person IDs or unresolved names independently. ARCH-007's party
  generalization cannot be implemented by renaming those fields; it needs a shared reference shape
  plus explicit unresolved/provisional semantics.
- Existing IDs such as `d-system`, `c-1`, and `t-1` do not follow the future global opaque identity
  rule. ARCH-008 acknowledges aliases, but the mapping owner, cutover order, and collision behavior
  are not yet represented by a schema or migration contract.
- `evidence` is a reusable per-field map, while promoted records retain only a compact `capture`
  source reference. That is a deliberate staging boundary in the capture design, but it means the
  long-term provenance needed by identity merges, contracts, and WBS history is not yet a common
  durable relationship.

### Catalog and architecture boundary

- ARCH-008's planned list contains object schemas but not all relationship schemas implied by its
  cardinalities. In particular, opportunity participants and engagement participants need their
  own records if they carry role, dates, confidence, or provisional identity.
- ARCH-007 names baseline metadata as undecided, while ARCH-008's relationship rules already state
  that baselines pin replay position and integrity evidence. That is a useful invariant but not yet
  an implementable `wbs-baseline` contract.
- ARCH-007 says temporal or technical dependencies remain separate from WBS, but neither document
  names a dependency schema. Without one, “separate” is only a boundary statement and has no
  durable home.
- `project_people` and `project_tags` are durable analytical relationships in the projection, yet
  they have no corresponding source schemas. This conflicts with ARCH-008's rule that mappings
  among governed objects create structured data and that every durable object has an authoritative
  schema. Either classify them as derived projections explicitly or add mapping contracts.

## Proposed missing contracts beyond ARCH-008

These are recommendations for the next governed requirements/plan work; they are not silently
added to the catalog in this review.

| Proposed contract | Why it is missing | Minimum responsibility |
|---|---|---|
| `party-reference` | ARCH-007 depends on `PartyRef`, but no shared contract defines person/company/affiliation versus unresolved representation | Discriminated target, optional affiliation, unresolved/provisional state, provenance and resolution lifecycle |
| `opportunity-party` | ARCH-008 lists opportunity but not its role-bearing people/company links | Opportunity-to-party role, relationship dates, source/confidence, and cardinality |
| `engagement-party` | ARCH-007 says an engagement may connect companies and people, but no mapping object carries those links | Engagement-to-party role, representation, dates and primary/secondary semantics |
| `project-tag` | `project.tags` currently feeds a junction table without an authoritative relationship schema | Project/tag link, source ordering if meaningful, effective dates and deprecation behavior |
| `wbs-baseline` | Baselines are promised by both architecture documents but placement is explicitly undecided | Baseline identity, project/WBS scope, replay position or immutable snapshot hash, approval and supersession |
| `work-dependency` | ARCH-007 says technical/temporal dependencies are outside the WBS but names no durable object | Directed predecessor/successor links across tasks, commitments, WBS elements or projects, with dependency type |
| `document-link` | Business contracts, engagements, projects and glossary lineage need typed links to governed documents | Source/target identity, link type, effective dates and provenance; should not overload `depends_on` |
| `external-reference` | Repository URLs, credentials, contract/SOW references and provider identifiers are currently ad hoc scalar fields | System/provider namespace, external key, target identity, validity and secrecy classification |

`party-reference` may remain a shared JSON definition rather than a top-level stored object if the
owner chooses text-preserving unresolved links. If unresolved parties are durable records, add a
separate `provisional-party` contract instead of hiding that lifecycle inside a generic reference.
That choice is the first dependency for the proposed participant junctions.

## Shared-dimensionality link map

The following machine-readable map is the review's proposed relationship inventory. It distinguishes
direct foreign-key-like links from junction/mapping links and from derived projection links. It does
not assert that any link is implemented. `cardinality` is written from `from` to `to`; `direction`
names the navigable semantic direction, not a SQL constraint.

```json
{
  "schema_map_version": 1,
  "source_documents": ["ARCH-007", "ARCH-008", "ARCH-009"],
  "links": [
    {"dimension":"portfolio scope","from":"project","to":"commitment","cardinality":"1:N","direction":"project contains commitment","link_type":"direct","status":"implemented"},
    {"dimension":"portfolio scope","from":"project","to":"task","cardinality":"1:N","direction":"project contains task","link_type":"direct","status":"implemented"},
    {"dimension":"execution decomposition","from":"commitment","to":"task","cardinality":"1:N","direction":"commitment decomposes to task","link_type":"direct","status":"implemented"},
    {"dimension":"portfolio context","from":"project","to":"interaction","cardinality":"1:N","direction":"project contextualizes interaction","link_type":"direct","status":"implemented"},
    {"dimension":"portfolio context","from":"project","to":"decision","cardinality":"1:N","direction":"project contextualizes decision","link_type":"direct","status":"implemented"},
    {"dimension":"decision provenance","from":"interaction","to":"decision","cardinality":"1:N","direction":"interaction records decision context","link_type":"direct","status":"implemented"},
    {"dimension":"portfolio context","from":"project","to":"waiting-on","cardinality":"1:N","direction":"project contextualizes waiting-on","link_type":"direct","status":"implemented"},
    {"dimension":"portfolio context","from":"project","to":"development-event","cardinality":"1:N","direction":"project contextualizes development event","link_type":"direct","status":"implemented"},
    {"dimension":"memory scope","from":"project","to":"memory","cardinality":"1:N","direction":"project scopes memory","link_type":"direct","status":"implemented"},
    {"dimension":"taxonomy","from":"project","to":"tag","cardinality":"N:M","direction":"project is classified by tag","link_type":"junction","mapping_schema":"project-tag","status":"partial"},
    {"dimension":"legacy participation","from":"person","to":"project","cardinality":"N:M","direction":"person participates in project","link_type":"junction","mapping_schema":"project-party","status":"partial"},
    {"dimension":"organizational identity","from":"person","to":"company","cardinality":"N:M over time","direction":"person is affiliated with company","link_type":"junction","mapping_schema":"affiliation","status":"planned"},
    {"dimension":"identity aliases","from":"person","to":"person-alias","cardinality":"1:N","direction":"person owns alias","link_type":"direct","status":"planned"},
    {"dimension":"company hierarchy","from":"company","to":"company","cardinality":"N:M over time","direction":"company relates to company","link_type":"junction","mapping_schema":"company-relationship","status":"planned"},
    {"dimension":"project participation","from":"project","to":"project-party","cardinality":"1:N","direction":"project records party relationship","link_type":"direct","status":"planned"},
    {"dimension":"party target","from":"project-party","to":"party-reference","cardinality":"N:1","direction":"project-party identifies person/company/affiliation","link_type":"direct","status":"planned"},
    {"dimension":"project roles","from":"project","to":"role-definition","cardinality":"1:N","direction":"project defines role","link_type":"direct","status":"planned"},
    {"dimension":"role assignment","from":"role-definition","to":"project-party","cardinality":"1:N","direction":"role is assigned to project party","link_type":"direct","status":"planned"},
    {"dimension":"opportunity participation","from":"opportunity","to":"opportunity-party","cardinality":"1:N","direction":"opportunity records party link","link_type":"direct","status":"proposed"},
    {"dimension":"opportunity target","from":"opportunity-party","to":"party-reference","cardinality":"N:1","direction":"opportunity-party identifies party","link_type":"direct","status":"proposed"},
    {"dimension":"commercial participation","from":"engagement","to":"engagement-party","cardinality":"1:N","direction":"engagement records party link","link_type":"direct","status":"proposed"},
    {"dimension":"engagement target","from":"engagement-party","to":"party-reference","cardinality":"N:1","direction":"engagement-party identifies party","link_type":"direct","status":"proposed"},
    {"dimension":"commercial delivery","from":"engagement","to":"project","cardinality":"N:M","direction":"engagement covers project","link_type":"junction","mapping_schema":"engagement-project","status":"planned"},
    {"dimension":"commercial paperwork","from":"engagement","to":"business-contract","cardinality":"N:M","direction":"engagement is evidenced by contract","link_type":"junction","mapping_schema":"engagement-contract","status":"proposed"},
    {"dimension":"document lineage","from":"document","to":"document-link","cardinality":"1:N","direction":"document participates in typed lineage","link_type":"direct","status":"proposed"},
    {"dimension":"scope hierarchy","from":"project","to":"wbs-element","cardinality":"1:N","direction":"project owns WBS element","link_type":"direct","status":"planned"},
    {"dimension":"WBS hierarchy","from":"wbs-element","to":"wbs-element","cardinality":"1:N","direction":"parent contains child","link_type":"direct","status":"planned"},
    {"dimension":"responsibility","from":"wbs-element","to":"project-party","cardinality":"N:1 optional","direction":"WBS element is owned by responsible party","link_type":"direct","status":"planned"},
    {"dimension":"scope attachment","from":"task","to":"wbs-element","cardinality":"N:1 optional","direction":"task is scoped to work package","link_type":"direct","status":"planned"},
    {"dimension":"scope attachment","from":"commitment","to":"wbs-element","cardinality":"N:1 optional","direction":"commitment is scoped to work package","link_type":"direct","status":"planned"},
    {"dimension":"WBS history","from":"wbs-change","to":"wbs-element","cardinality":"N:1 or event payload","direction":"change affects element","link_type":"direct","status":"planned"},
    {"dimension":"WBS approval","from":"wbs-baseline","to":"wbs-change","cardinality":"N:1 replay anchor","direction":"baseline pins WBS history","link_type":"direct","status":"proposed"},
    {"dimension":"execution dependency","from":"work-dependency","to":"task","cardinality":"N:1 or typed endpoint","direction":"dependency endpoint is task","link_type":"mapping","status":"proposed"},
    {"dimension":"identity resolution","from":"identity-registry","to":"* durable object","cardinality":"1:N","direction":"global identity aliases domain object","link_type":"mapping","status":"planned"},
    {"dimension":"schema governance","from":"schema-registry","to":"schema-mapping","cardinality":"1:N","direction":"registry governs mapping","link_type":"direct","status":"planned"},
    {"dimension":"schema transformation","from":"schema-mapping","to":"schema","cardinality":"N:2","direction":"mapping connects source and target schema versions","link_type":"mapping","status":"planned"},
    {"dimension":"capture provenance","from":"capture","to":"staged-record","cardinality":"1:N","direction":"capture produces staged candidates","link_type":"direct","status":"intake / contract-only"},
    {"dimension":"field provenance","from":"evidence","to":"capture","cardinality":"N:1","direction":"evidence cites raw capture","link_type":"direct","status":"embedded"},
    {"dimension":"vocabulary lineage","from":"glossary-term","to":"schema/document/decision","cardinality":"N:M","direction":"term is defined or evidenced by governed artifact","link_type":"mapping","status":"planned"},
    {"dimension":"idea realization","from":"idea","to":"document","cardinality":"N:M","direction":"idea promotes or links to document","link_type":"mapping","status":"implemented in idea projection"}
  ]
}
```

The map deliberately includes `* durable object` and the polymorphic `schema` endpoint as
architecture notation, not as a proposed SQL table. The implementation plan must replace those
wildcards with explicit registry/mapping rows and validation rules.

## Recommended follow-up updates

These recommendations should be handled in their own owner-reviewed changes:

1. Add maturity columns to ARCH-008 for authoritative source, validation path, writer, loader,
   projection and current status. Keep planned contracts visibly separate from implemented ones.
2. Add the missing participant and baseline decisions to the next requirements document. Resolve
   the unresolved-party contradiction before finalizing `party-reference`.
3. Add glossary entries for authoritative source, projection, junction/mapping link, PartyRef,
   provisional party, opportunity-party, engagement-party, WBS baseline and work dependency.
4. Refresh stale counts and live-system descriptions in ARCH-001, ARCH-002 and ARCH-004 only after
   confirming that the snapshots are meant to be living documents. Do not rewrite their historical
   observations merely to make this review's count agree.
5. Add a source/projection consistency check that reports ignored schema properties and unresolved
   references before the rebuild mutates DuckDB. The first targeted checks should cover
   `project.stakeholders`, project/tag/person references and the optional parent IDs on tasks.
6. Decide whether `project_people` and `project_tags` are derived-only projections or durable mapping
   sources. If source-authoritative, give them contracts; if derived-only, record their derivation
   and stop treating them as independent objects in the catalog.

## Review boundary

This artifact is evidence for planning. It does not create schemas, alter DDL, change loaders,
modify glossary/catalog content, or revise ARCH-007/ARCH-008. The next implementation work should
start with a governed requirement and plan for the identity/party boundary, followed by explicit
mapping contracts and cross-record validation.
