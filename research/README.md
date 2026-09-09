# Research materials and adversarial codebase review

The twelve codebase-review reports are in [adversarial-codebase-review/](adversarial-codebase-review/01_actual_architecture.md). Start with [ranked findings and the sixteen claim tests](adversarial-codebase-review/10_adversarial_findings.md), then inspect [contradictions](adversarial-codebase-review/08_contradictions.md) and the [real traceability attempts](adversarial-codebase-review/06_traceability_audit.md).

The organized architecture and hypothesis files are proposed research, not authoritative descriptions of the implementation. All source ZIPs and loose artifacts remain intact. Extracted archives retain their internal paths and README files under `sources/archive-extractions/`. Identical loose files were preferred for the organized copies. No requested named artifact was missing, and no content/path correction to either CLAUDE instruction file was needed.

`research/sources/cited_sources_chat_seed.md` contains sources encountered or cited during ideation before formal validation. It is historically intact and **not a validated bibliography**. Neither it nor `source_ledger.md` was bibliographically validated in this review.

The [literature-review instructions](literature-review/CLAUDE.md) are prepared only. No literature review or external search has begun. External review of the adversarial codebase audit must occur first.

Evidence and reproducibility:

- [Repository inventory and review exclusions](evidence/repository-inventory.md)
- [Exact excerpts, interpretations, confidence and alternatives](evidence/code-evidence.md)
- [Synthetic adversarial probe script](evidence/review_probes.py) and [results](evidence/review-probe-results.json)
- [Existing test-suite output](evidence/pytest-review.txt)
- [Verification and limitations](evidence/verification.md)
- [Original/copy hashes and provenance](evidence/organization_manifest.json)
- [Implementation snapshot](evidence/implementation-snapshot.json)
- [All created/copied files](CREATED_FILES.md)

The review is the deliverable. This review changed no production source, schema, migration, prompt, retrieval behavior or real data, no backlog phase was closed, and no recommendations were executed.
