# Validated bibliography

Every source a synthesis claim (`07_anti_novelty_case.md` through `12_experiment_proposals.md`) rests on, plus every seed source from `research/sources/source_ledger.md` run through the evidence contract's five-step promotion (`docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md`, methodology `CLAUDE.md` §16): (1) bibliographic identity verified, (2) primary source inspected, (3) cited interpretation confirmed, (4) exact supporting location recorded, (5) status updated. The historical seed ledger (`research/sources/source_ledger.md`) is never edited; every outcome below is recorded here instead, including the seeds that failed a step.

**Coverage caveat, binding on this document.** This bibliography is built from the 49 rows this campaign deep-read into `04_evidence_matrix.csv`, not the full candidate pool: 340 of 387 collision candidates surfaced by search have never been deep-read. The sources below are not represented as the strongest candidates the campaign could have found, only as the strongest candidates it actually read and the ones synthesis claims actually cite. No saturation claim is made anywhere in this document. Two source_id values in `03_source_inventory.csv` are known duplicates of other rows (`memtx-transactional-belief-commit-2026`, `semantically-seeded-graph-propagated-impact-analysis-vision-2026`) — the inventory's row count is not a distinct-source count, and neither duplicate pair affects the count below, since the evidence matrix (the source of Part A) already carries each underlying source once.

---

## Part A — Sources synthesis claims rest on

45 of the evidence matrix's 49 deep-read rows are cited by at least one claim in `07_anti_novelty_case.md`, `08_surviving_distinctions.md`, `09_reuse_recommendations.md`, `10_architecture_implications.md`, `11_open_research_questions.md` or `12_experiment_proposals.md` (checked by direct text search for each `source_id` and, where a slug did not match verbatim, by author-name cross-check against the citing prose). The remaining 4 matrix rows -- `capilla-et-al-web-based-tool-architectural-design-decisions-2006`, `keim-kaplan-scattered-to-structured-akm-vision-2026`, `lineagerag-2026`, and `perry-wolf-foundations-software-architecture-1992` -- were deep-read but are not drawn on by any synthesis claim; they remain in `04_evidence_matrix.csv` as read-but-unused evidence and are not listed here, per this document's scope (sources a synthesis claim *rests on*).

Each entry: `source_id` -- citation. Identifier is in the canonical single form (bare DOI, `arxiv:NNNN.NNNNN`, `semanticscholar:<hash>`, `uspto:<number>`, or a plain URL where no identifier exists). `hypotheses` lists the H1-H11 challenged per the matrix's `hypotheses_challenged` field; `cc` is the matrix's `critical_collision` flag; `access` is the matrix's `access_limitation` value, carried forward so a paywalled or abstract-only assessment is never presented here as a full read it was not.

- `de-boer-architectural-knowledge-management-dissertation-2009` -- Farenhorst, R. and de Boer, R.C.: Architectural Knowledge Management: Supporting Architects and Auditors, PhD dissertation, Vrije Universiteit Amsterdam, defended 5 Oct 2009 (SIKS Dissertation Series No. 2009-32). A single shared thesis text defended jointly by both authors the same day; the VU Research Portal catalogs it under de Boer's name alone, which the inventory row's citation follows.
  Identifier: `research.vu.nl/ws/portalfiles/portal/42190776/complete%20dissertation.pdf` | type: tech report | hypotheses: H7;H9 | cc: no | access: full_text

- `decision-oriented-programming-aporia-2026` -- Kasibatla, S.R., Rothkopf, R., Peleg, H., Pierce, B.C., Lerner, S., Goldstein, H., Polikarpova, N.: Decision-Oriented Programming with Aporia, arXiv preprint, submitted 6 Apr 2026 (UC San Diego, Technion, U Penn, Cornell, U Buffalo).
  Identifier: `arxiv:2604.05203` | type: preprint | hypotheses: H7;H8;H9 | cc: yes | access: preprint_version

- `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` -- Dhar, R., Vaidhyanathan, K., Varma, V.: AgenticAKM: Enroute to Agentic Architecture Knowledge Management, arXiv preprint (also AGENT'26 workshop @ ICSE 2026, Rio de Janeiro, ACM DOI 10.1145/3786167.3788416), IIIT Hyderabad, submitted 4 Feb 2026.
  Identifier: `arxiv:2602.04445` | type: preprint | hypotheses: H6;H9 | cc: yes | access: preprint_version

- `em-llm-human-inspired-episodic-memory-infinite-context-2024` -- Fountas, Z., Benfeghoul, M.A., Oomerjee, A., Christopoulou, F., Lampouras, G., Bou-Ammar, H., Wang, J.: Human-inspired Episodic Memory for Infinite Context LLMs (EM-LLM). Huawei Noah's Ark Lab, London + UCL AI Centre. Published as a conference paper at ICLR 2025; originally posted as an arXiv preprint 12 Jul 2024, revised through v3 (10 Oct 2025).
  Identifier: `arxiv:2407.09450` | type: peer-reviewed | hypotheses: H5 | cc: yes | access: full_text

- `evidence-graphs-fair-computation-defeasible-reasoning-2021` -- Al Manir, S., Niestroy, J., Levinson, M.A., Clark, T.: Evidence Graphs: Supporting Transparent and FAIR Computation, with Defeasible Reasoning on Data, Methods, and Results. bioRxiv preprint, posted 2021; also published as a peer-reviewed chapter in Provenance and Annotation of Data and Processes: 8th/9th International Provenance and Annotation Workshop (IPAW 2020+2021), Springer LNCS vol.12839, 2021.
  Identifier: `biorxiv.org/content/10.1101/2021.03.29.437561` | type: peer-reviewed | hypotheses: H2;H3;H9 | cc: yes | access: full_text

- `graph-native-cognitive-memory-belief-revision-semantics-2026` -- Park, Y.B.: Graph-Native Cognitive Memory for AI Agents: Formal Belief Revision Semantics for Versioned Memory Architectures (Kumiho). Kumiho Inc. arXiv preprint, 18 Mar 2026 (in-body date 17 Mar 2026), CC BY-NC-ND 4.0.
  Identifier: `arxiv:2603.17244` | type: preprint | hypotheses: H2;H7;H9 | cc: yes | access: preprint_version

- `jansen-bosch-architecture-as-decisions-wicsa-2005` -- Jansen, A., Bosch, J.: Software Architecture as a Set of Architectural Design Decisions, Proceedings of the 5th IEEE/IFIP Working Conference on Software Architecture (WICSA 2005), pp.109-119, November 2005. (Read via the open-access republication as Chapter 4 of Jansen's 2008 PhD dissertation, University of Groningen; the WICSA proceedings version itself is paywalled on IEEE Xplore.)
  Identifier: `10.1109/wicsa.2005.61` | type: conference | hypotheses: H2;H7;H9 | cc: yes | access: full_text

- `log-is-the-agent-event-sourced-reactive-graphs-2026` -- Nakajima, Y.: The Log is the Agent: Event-Sourced Reactive Graphs for Auditable, Forkable Agentic Systems. arXiv preprint, submitted 21 May 2026 (v1). Untapped Capital / activegraph.ai. Open source (Apache-2.0): github.com/yoheinakajima/activegraph.
  Identifier: `arxiv:2605.21997` | type: preprint | hypotheses: H2;H3;H5;H7;H9 | cc: yes | access: full_text

- `procko-provtracer-erau-dissertation-2025` -- Procko, T.: On the Provenance of Software Systems: Automating Software Traceability with Knowledge Graph and Large Language Model Synergy. PhD dissertation, Electrical Engineering & Computer Science, Embry-Riddle Aeronautical University, defended Spring 2025. Chair/Advisor: Omar Ochoa; committee: Massood Towhidnejad, Nicholas Del Rio, Alex Vargas, Keith Garfield.
  Identifier: `commons.erau.edu/edt/898` | type: tech report | hypotheses: H7;H9 | cc: no | access: abstract_only

- `tgms-agent-native-bitemporal-graph-2026` -- Zhang, X.: TGMS: An Agent-Native Bi-Temporal Graph Management System -- Validated Temporal Operators and Trace-Grounded Answer Checking. arXiv preprint, v1 11 Jul 2026, v2 24 Jul 2026 (current). University of Memphis. System Description Preprint accompanying TGMS v0.3.0. Open source (Apache-2.0): https://github.com/zxf-work/tgms.
  Identifier: `arxiv:2607.10265` | type: preprint | hypotheses: H2;H3;H5;H9 | cc: yes | access: full_text

- `assumptions-management-software-development-mapping-study-2018` -- Yang, C., Liang, P., Avgeriou, P.: Assumptions and their management in software development: A systematic mapping study. Information and Software Technology 94 (2018) 82-110. State Key Laboratory of Software Engineering, Wuhan University / Department of Mathematics and Computing Science, University of Groningen.
  Identifier: `10.1016/j.infsof.2017.10.003` | type: peer-reviewed | hypotheses: H10 | cc: no | access: full_text

- `ibm-architectural-blueprint-autonomic-computing-whitepaper-2006` -- IBM Corporation: An Architectural Blueprint for Autonomic Computing, IBM technical white paper, 4th edition, June 2006. (No individual author credited; an IBM corporate/Autonomic Computing initiative publication.)
  Identifier: `semanticscholar:54bc974d3e9ebc3c0adbce99665cdcf2a94b27f1` | type: tech report | hypotheses: H11 | cc: no | access: secondary_coverage

- `langgraph-checkpoint-library-oss` -- LangChain AI: LangGraph checkpoint library (langgraph-checkpoint), part of the LangGraph framework, GitHub repository libs/checkpoint
  Identifier: `github.com/langchain-ai/langgraph/tree/main/libs/checkpoint` | type: OSS | hypotheses: H8;H9 | cc: yes | access: full_text

- `model-based-digital-threads-sociotechnical-systems-2022` -- Pessoa, M.V.P., Pires, L.F., Moreira, J.L.R., Wu, C.: Model-Based Digital Threads for Socio-Technical Systems. In: Machine Learning for Smart Environments/Cities, Intelligent Systems Reference Library vol.121, Springer, Cham, pp.27-52, 2022.
  Identifier: `10.1007/978-3-030-97516-6_2` | type: book-chapter | hypotheses: H7;H9 | cc: yes | access: full_text

- `omniscientist-coevolving-ecosystem-human-ai-scientists-2026` -- Shao, C., Huang, D., Li, Y., Zhao, K., Lin, W., Zhang, Y., Zeng, Q., Chen, Z., Li, T., Huang, Y., Wu, T., Liu, X., Zhao, R., Zhao, M., Li, J., Zhang, X., Wang, Y., Zhen, Y., Xu, F., Li, Y., Liu, T.-Y.: OmniScientist: Toward a Co-evolving Ecosystem of Human and AI Scientists. arXiv preprint, v1 21 Nov 2025, v2 14 Dec 2025. Tsinghua University / Zhongguancun Academy.
  Identifier: `arxiv:2511.16931` | type: preprint | hypotheses: H2;H3;H6;H9 | cc: yes | access: full_text

- `solozobov-verify-gated-completion-admission-control-2026` -- Nguyen, H.-D., Tran, X.-T.: Verify-Gated Completion as Admission Control in a Governed Multi-Agent Runtime: A Bounded Architecture Case Study. arXiv preprint, v2 21 May 2026. Vietnam Maritime University, Haiphong, Vietnam. NOTE: the inventory's source_id slug and lineage annotation name 'Solozobov' as author/lineage label, but the paper's own title page lists only Hai-Duong Nguyen and Xuan-The Tran, with no author named Solozobov appearing anywhere in the text -- a bibliographic identity mismatch between the inventory's naming convention and the source's own authorship, recorded here per this dispatch's verify-at-the-source instruction rather than silently accepted.
  Identifier: `arxiv:2605.17998` | type: preprint | hypotheses: H2;H5;H8;H9 | cc: yes | access: full_text

- `us20250165226a1-ai-digital-thread-patent` -- Roper, W. Jr., Benson, C.L., Krishnan, S., Galvin, P., Abunojaim, B.E.A., Doijode, P.S., Abu Rmaileh, N.A. (Istari Digital, Inc.): Software-Code-Defined Digital Threads in Digital Engineering Systems with Artificial Intelligence (AI) Assistance. US Patent Application US20250165226A1, published 2025-05-22 (filed 2024-03-10, priority 2023-03-10, application no. US18/730,782). NOTE: confirmed via the patent's own legal-status metadata to have since GRANTED as US12461717B2 (status='Granted', grant number confirmed directly in the page's raw HTML, not merely from a WebFetch summary).
  Identifier: `uspto:US20250165226A1` | type: tech report | hypotheses: H7;H9 | cc: yes | access: full_text

- `zep-graphiti-temporal-kg-agent-memory-2025` -- Rasmussen, P., Paliychuk, P., Beauvais, T., Ryan, J., Chalef, D. (Zep AI): Zep: A Temporal Knowledge Graph Architecture for Agent Memory. arXiv preprint, v1 20 Jan 2025.
  Identifier: `arxiv:2501.13956` | type: preprint | hypotheses: H2;H5;H9 | cc: yes | access: full_text

- `w3c-prov-o-2013` -- Lebo, T., Sahoo, S., McGuinness, D. (eds.): PROV-O: The PROV Ontology. W3C Recommendation, 30 April 2013.
  Identifier: `https://www.w3.org/TR/prov-o/` | type: standard | hypotheses: H2;H3;H7;H9 | cc: no | access: full_text

- `snodgrass-developing-time-oriented-database-applications-sql-1999` -- Snodgrass, R.T.: Developing Time-Oriented Database Applications in SQL. Morgan Kaufmann, San Francisco, 1999. ISBN 1-55860-436-7.
  Identifier: `https://www2.cs.arizona.edu/~rts/tdbbook.pdf` | type: book | hypotheses: H2 | cc: no | access: full_text

- `agm-partial-meet-contraction-revision-1985` -- Alchourron, C.E., Gardenfors, P., Makinson, D.: On the Logic of Theory Change: Partial Meet Contraction and Revision Functions. Journal of Symbolic Logic 50(2), 1985, pp. 510-530.
  Identifier: `10.2307/2274239` | type: peer-reviewed | hypotheses: H2;H3 | cc: no | access: secondary_coverage

- `nii-blackboard-model-problem-solving-1986` -- Nii, H.P.: The Blackboard Model of Problem Solving and the Evolution of Blackboard Architectures (Part One). AI Magazine 7(2), 1986, pp. 38-53.
  Identifier: `10.1609/aimag.v7i2.537` | type: peer-reviewed | hypotheses: H5 | cc: no | access: full_text

- `burckhardt-et-al-durable-functions-stateful-serverless-2021` -- Burckhardt, S., Gillum, C., Justo, D., Kallas, K., McMahon, C., Meiklejohn, C.S.: Durable Functions: Semantics for Stateful Serverless. Proc. ACM Program. Lang. 5, OOPSLA, Article 133 (October 2021), 27 pages.
  Identifier: `10.1145/3485510` | type: peer-reviewed | hypotheses: H8 | cc: no | access: full_text

- `zimmermann-et-al-managing-architectural-decision-models-2009` -- Zimmermann, O., Koehler, J., Leymann, F., Polley, R., Schuster, N.: Managing Architectural Decision Models with Dependency Relations, Integrity Constraints, and Production Rules. Journal of Systems and Software 82(8), 1249-1267 (Aug 2009).
  Identifier: `10.1016/j.jss.2009.01.039` | type: peer-reviewed | hypotheses: H2;H7 | cc: yes | access: full_text

- `burns-groth-agentic-ontological-notebook-memory-2026` -- Burns, G.A., Groth, P.: Complex Knowledge Curation using Agentic Ontological Notebook Memory. In: Proceedings of the 1st ACM Conference on AI and Agentic Systems (CAIS '26), May 26, 2026, San Jose, CA, USA. ACM, 5 pages.
  Identifier: `10.1145/3786335.3813226` | type: conference | hypotheses: H1;H3;H11 | cc: yes | access: preprint_version

- `levinson-et-al-fairscape-fair-reproducible-biomedical-analytics-2021` -- Levinson, M.A., Niestroy, J., Al Manir, S., Fairchild, K., Lake, D.E., Moorman, J.R., Clark, T.: FAIRSCAPE: A Framework for FAIR and Reproducible Biomedical Analytics. Neuroinformatics 20(1), 187-202 (Jul 2021).
  Identifier: `10.1007/s12021-021-09529-4` | type: peer-reviewed | hypotheses: H3 | cc: no | access: full_text

- `epistemic-sybil-resistance-bara-2026` -- Bara, M.: Epistemic Sybil Resistance: Multiplying AI Agents Without Multiplying Evidence, arXiv preprint, 1 Sep 2026
  Identifier: `arxiv:2609.01873` | type: preprint | hypotheses: H4 | cc: yes | access: full_text

- `eywa-provenance-grounded-memory-joshi-2026` -- Joshi, R.: Eywa: Provenance-Grounded Long-Term Memory for AI Agents, arXiv preprint, May 2026
  Identifier: `arxiv:2605.30771` | type: preprint | hypotheses: H1;H5 | cc: yes | access: full_text

- `dong-berti-equille-srivastava-truth-discovery-copying-detection-2009` -- Dong, X.L., Berti-Equille, L., Srivastava, D.: Truth Discovery and Copying Detection in a Dynamic World, Proceedings of the VLDB Endowment, Vol.2, Issue 1, pp.562-573, 2009
  Identifier: `10.14778/1687627.1687691` | type: conference | hypotheses: NOT_APPLICABLE | cc: no | access: full_text

- `memtx-transactional-belief-commit-2026` -- Li, X., Wang, Y., Lu, H., Chen, Z., Li, M., Song, P., Zheng, M., Cai, T.: MemTX: Transactional Belief Commit for Stateful Agent Memory, arXiv preprint, 27 Jul 2026 (v2 28 Jul 2026)
  Identifier: `arxiv:2607.23929` | type: preprint | hypotheses: H10 | cc: yes | access: full_text

- `toki-bitemporal-operator-algebra-contradiction-2026` -- Wang, Z.: TOKI: A Bitemporal Operator Algebra for Contradiction Resolution in LLM-Agent Persistent Memory, arXiv preprint, 4 Jun 2026
  Identifier: `arxiv:2606.06240` | type: preprint | hypotheses: H1 | cc: no | access: full_text

- `mythologiq-agent-memory-oss` -- MythologIQ-Labs-LLC: agent-memory -- governed reference architecture for agentic memory, GitHub repository (README, PAMA governance doctrine, 58 JSON Schemas, SHA256-chained Meta Ledger)
  Identifier: `https://github.com/MythologIQ-Labs-LLC/agent-memory` | type: OSS | hypotheses: H1 | cc: yes | access: full_text

- `subit-wiki-epistemic-hmm-oss` -- sciganec: subit-wiki -- SUBIT: Epistemic State Machine with Self-Evolving Ontology, GitHub repository
  Identifier: `https://github.com/sciganec/subit-wiki` | type: OSS | hypotheses: H1 | cc: yes | access: full_text

- `symbolic-memory-prolog-oss` -- lost-rob0t: symbolic-memory -- Prolog-first durable memory for LLM/agent clients, GitHub repository (README, prolog/symbolic_memory.pl, IMPLEMENTATION-STATUS.md, issues #4/#6/#7/#14)
  Identifier: `https://github.com/lost-rob0t/symbolic-memory` | type: OSS | hypotheses: H1 | cc: no | access: full_text

- `barakat-corroboration-provenance-patterns-tapp2017` -- Barakat, L., Taylor, P., Griffiths, N., Miles, S. "Corroboration via Provenance Patterns." Proceedings of the 9th USENIX Workshop on the Theory and Practice of Provenance (TaPP 2017), Seattle, WA, June 22-23, 2017.
  Identifier: `https://www.usenix.org/system/files/conference/tapp2017/tapp17_paper_barakat.pdf` | type: conference | hypotheses: H4 | cc: yes | access: full_text

- `extending-nanopublications-knowledge-provenance` -- Giachelle, F., Marchesin, S., Menotti, L., Silvello, G. "Extending Nanopublications with Knowledge Provenance for Multi-Source Scientific Assertions." Proc. IRCDL 2025 (21st Conference on Information and Research Science Connecting to Digital and Library Science), Udine, Italy, Feb 20-21, 2025. CEUR-WS Vol-3937, paper 10.
  Identifier: `https://ceur-ws.org/Vol-3937/paper10.pdf` | type: conference | hypotheses: H3;H4 | cc: no | access: full_text

- `provenance-based-interpretation-multi-agent-information-analysis-2020` -- Friedman, S., Rye, J., LaVergne, D., Thomsen, D. (SIFT, LLC), Allen, M., Tunis, K. (Raytheon BBN Technologies). "Provenance-Based Interpretation of Multi-Agent Information Analysis." Proceedings of TaPP 2020 (12th USENIX Workshop on the Theory and Practice of Provenance). arXiv:2011.04016.
  Identifier: `arxiv:2011.04016` | type: conference | hypotheses: H3;H4;H5 | cc: yes | access: full_text

- `reliability-testimonial-norms-scientific-communities-synthese` -- Mayo-Wilson, Conor. "Reliability of Testimonial Norms in Scientific Communities." Synthese 191 (2014): 55-78. (Author preprint dated July 19, 2013, used for this read; DOI 10.1007/s11229-013-0320-2.)
  Identifier: `10.1007/s11229-013-0320-2` | type: peer-reviewed | hypotheses: H4 | cc: no | access: preprint_version

- `goldman-experts-which-ones-should-you-trust-2001` -- Goldman, Alvin I. "Experts: Which Ones Should You Trust?" Philosophy and Phenomenological Research 63, no. 1 (2001): 85-110.
  Identifier: `10.1111/j.1933-1592.2001.tb00093.x` | type: peer-reviewed | hypotheses: H4 | cc: yes | access: full_text

- `runtime-verification-self-adaptive-changing-requirements-2023` -- Carwehl, M., Vogel, T., Rodrigues, G.N., Grunske, L.: Runtime Verification of Self-Adaptive Systems with Changing Requirements. 18th International Symposium on Software Engineering for Adaptive and Self-Managing Systems (SEAMS 2023).
  Identifier: `arxiv:2303.16530` | type: preprint | hypotheses: H11 | cc: no | access: full_text

- `souza-lapouchnian-robinson-mylopoulos-awareness-requirements-seams-2011` -- Souza, V.E.S., Lapouchnian, A., Robinson, W.N., Mylopoulos, J.: Awareness Requirements for Adaptive Systems. Proceedings of the 6th International Symposium on Software Engineering for Adaptive and Self-Managing Systems (SEAMS 2011), Waikiki, Honolulu, pp. 60-69.
  Identifier: `10.1145/1988008.1988018` | type: conference | hypotheses: H11 | cc: no | access: full_text

- `sawyer-bencomo-whittle-letier-requirements-reflection-icse-2010` -- Bencomo, N., Whittle, J., Sawyer, P., Finkelstein, A., Letier, E.: Requirements Reflection: Requirements as Runtime Entities. Proceedings of the 32nd ACM/IEEE International Conference on Software Engineering (ICSE 2010), Volume 2, NIER track, Cape Town, South Africa, pp. 199-202. (Author order on the published paper is Bencomo, Whittle, Sawyer, Finkelstein, Letier -- differs from the inventory row's listed order, corrected here.)
  Identifier: `10.1145/1810295.1810329` | type: conference | hypotheses: H11 | cc: no | access: full_text

- `requirement-evolution-requirements-adaptive-systems-seams-2012` -- Souza, V.E.S., Lapouchnian, A., Mylopoulos, J.: (Requirement) Evolution Requirements for Adaptive Systems. Proceedings of the 7th International Symposium on Software Engineering for Adaptive and Self-Managing Systems (SEAMS 2012), Zurich, pp. 155-164.
  Identifier: `10.1109/SEAMS.2012.6224402` | type: conference | hypotheses: H11 | cc: no | access: full_text

- `krentsel-agarwal-cemri-reality-final-verifier-two-gaps-agentic-se-2026` -- Krentsel, A., Agarwal, S., Cemri, M., Liu, S., Sankhe, S., Mao, Z., Zaharia, M., Stoica, I.: Reality Is the Final Verifier: On Two Key Gaps in Agentic Software Engineering. arXiv preprint, September 2026.
  Identifier: `arxiv:2609.12039` | type: preprint | hypotheses: H11 | cc: no | access: full_text

- `bajaj-ai-augmented-closed-loop-quality-engineering-2026` -- Bajaj, D.: AI-Augmented Closed-Loop Quality Engineering: A Reference Architecture for Continuous Software Quality Intelligence. arXiv preprint, June 2026.
  Identifier: `arxiv:2606.08793` | type: preprint | hypotheses: H11 | cc: no | access: full_text

---
## Part B — Seed sources from `research/sources/source_ledger.md`

All 9 seeds in the historical seed ledger, run through the five-step promotion process this dispatch
(`LIT-07-S001`-`LIT-07-S016`). The ledger itself is untouched; every outcome is recorded here only.

### Seed 1 — W3C PROV-O

- **1. Bibliographic identity verified:** PASS. Confirmed at the source's own page
  (`https://www.w3.org/TR/prov-o/`, `LIT-07-S001`): title "PROV-O: The PROV Ontology," W3C
  Recommendation, 30 April 2013.
- **2. Primary source inspected:** PASS. Read directly, `LIT-07-S001`; previously also deep-read in
  `phase-lit-01`/`phase-lit-04`.
- **3. Cited interpretation confirmed:** PASS. The seed's claimed content -- Entity/Activity/Agent,
  responsibility/delegation ("bears responsibility for another agent's activity"), role, and Plan as
  a distinct entity type -- is confirmed verbatim in the document's own Abstract and Introduction.
- **4. Exact supporting location recorded:** Abstract (top-level definition); Introduction
  (Entity/Activity/Agent definitions, delegation and Plan language).
- **5. Status updated:** PROMOTED. This is the same underlying document as the synthesis-cited
  `w3c-prov-o-2013` row in Part A -- cross-referenced there, not duplicated as a second bibliography
  entry.

### Seed 2 — Event Sourcing Pattern (Microsoft Azure Architecture Center)

- **1. Bibliographic identity verified:** PASS. Confirmed at the source's own page
  (`https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing`, `LIT-07-S002`):
  page metadata gives author `claytonsiemens77`, `ms.date` 2026-03-27, last updated 2026-08-15.
- **2. Primary source inspected:** PASS. Read in full directly, `LIT-07-S002`.
- **3. Cited interpretation confirmed:** PASS. The seed's claims -- append-only event storage,
  events representing logical state changes, current state reconstructable/projectable from event
  history, the event store as system of record -- are confirmed verbatim in the page's "Solution"
  and "Pattern advantages" sections.
- **4. Exact supporting location recorded:** "Solution" section (append-only store, system of
  record); "Pattern advantages" bullet list (rehydration/replay, audit trail, materialized-view
  projection).
- **5. Status updated:** PROMOTED. Identifier: `https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing`
  (plain URL, no DOI/identifier exists). Type: product/vendor documentation page (methodology's
  lowest source-priority tier; used here only to validate the seed's own claim about the pattern,
  not as research evidence for any hypothesis).

### Seed 3 — Provenance-Enhanced Statements in Knowledge Graphs (Vitali, Pasqual)

- **1. Bibliographic identity verified:** PASS. Confirmed at the arXiv abstract page
  (`arxiv:2606.15246`, `LIT-07-S003`): title "Provenance-Enhanced Statements in Knowledge Graphs,"
  authors Fabio Vitali and Valentina Pasqual, submitted 13 June 2026.
- **2. Primary source inspected:** PASS. Abstract read directly, `LIT-07-S003`. (Not deep-read
  beyond the abstract in this dispatch -- the source remains a source-inventory `candidate`, not a
  `04_evidence_matrix.csv` row; this promotion validates the seed at abstract-access depth only.)
- **3. Cited interpretation confirmed:** PARTIAL. Three of the seed's four claimed terms are
  verbatim in the abstract: "epistemic stance" (provenance predicates interpreted as indicators of
  epistemic stance), "cognitive worlds" (provenance-homogeneous statement sets grouped into cognitive
  worlds), and disagreement/"controlled factualisation." The fourth claimed term, "agent-relative
  claims," is not a verbatim abstract phrase -- the abstract's own framing (statements grouped by
  provenance into distinct cognitive worlds) is a defensible paraphrase of an agent-relative-claims
  idea, but this dispatch did not confirm the exact phrase and records the mismatch rather than
  silently treating paraphrase as verbatim confirmation.
- **4. Exact supporting location recorded:** Abstract text (all four checked terms located there or
  found absent there).
- **5. Status updated:** PROMOTED, with the step-3 partial-match caveat carried forward. Identifier:
  `arxiv:2606.15246`. Type: preprint. `access_limitation: abstract_only` (full text not read in this
  dispatch) -- per campaign discipline this caps any absence-type claim about this source at
  `interpretation_confidence: medium`, not `high`.

### Seed 4 — Context Objects (Madhu Chamarty, SSRN working paper)

- **1. Bibliographic identity verified:** FAILED. The source's own page
  (`https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6775102`, `LIT-07-S004`, retried via
  `https://ssrn.com/abstract=6775102`, `LIT-07-S013`) returns HTTP 403 Forbidden on both the
  long-form and short-form URL -- the block is source-side, not a one-off fetch error. Identity is
  corroborated only via the author's own secondary writing: a real person, Madhu Chamarty (Larridin),
  who states in his own Substack essay that he "submitted a formal paper to SSRN specifying the
  Context Object primitive, the six dimensions that make it categorically distinct from existing
  database primitives" (`LIT-07-S010`, `LIT-07-S014`, `LIT-07-S016`). This establishes the paper's
  real-world existence and authorship but does not constitute verifying bibliographic identity **at
  the source's own page**, which the operational instructions require.
- **2. Primary source inspected:** FAILED (blocked; consequence of step 1's failure). The essay
  read at `LIT-07-S016` explicitly states the six dimensions are not disclosed outside the SSRN paper
  itself, so no substitute reading was available.
- **3-5:** Not reached.
- **Outcome:** NOT PROMOTED. Listed here per the contract's instruction that a seed failing a step is
  named with the failing step, not silently dropped. Failing step: **1 (bibliographic identity
  verified)**. `access_limitation: secondary_coverage` if this were scored, since only the author's
  own adjacent blog writing was readable, never the primary paper.

### Seed 5 — ENGRAM

- **1. Bibliographic identity verified:** PASS. Confirmed at the project's own page
  (`https://engram-agents.org/`, `LIT-07-S005`): "ENGRAM -- Epistemic substrate for AI agents."
- **2. Primary source inspected:** PASS. Read directly, `LIT-07-S005`. This seed never appeared in
  `03_source_inventory.csv` under any prior phase -- this is the first time it has been searched at
  all, not a re-verification of an existing row.
- **3. Cited interpretation confirmed:** PASS. The seed's claimed content -- provenance-tracked
  knowledge graph, claims citing evidence, derivations citing premises, retraction propagating to
  dependent claims, arbitration via a `contradicts` edge type, and persistence across sessions -- is
  confirmed verbatim on the project's own page.
- **4. Exact supporting location recorded:** Homepage tagline and description paragraph ("Every claim
  cites its evidence. Every derivation cites its premises."); the `contradicts`-edge description.
- **5. Status updated:** PROMOTED. Identifier: `https://engram-agents.org/` (plain URL, no
  DOI/identifier exists). Type: product/project page, not peer-reviewed -- recorded as such, and the
  seed ledger's "Open-source" characterization was not independently confirmed on the fetched page
  (no repository link was returned in this read); this sub-claim is flagged as unconfirmed rather
  than assumed true, without blocking promotion of the page's own core claims.

### Seed 6 — The Loom (`jpwinans/the-loom`)

- **1. Bibliographic identity verified:** FAILED. The cited repository
  (`https://github.com/jpwinans/the-loom`, `LIT-07-S006`) returns HTTP 404 Not Found. A web search
  (`LIT-07-S011`) and a direct fetch of the account's profile page (`LIT-07-S012`) found no
  "the-loom" repository, renamed or otherwise, among the account's "popular repositories." A
  conclusive check via the GitHub public API (`LIT-07-S015`, `api.github.com/users/jpwinans/repos`)
  enumerated the account's complete list of 28 public repositories -- none named `the-loom` or any
  close variant. The cited source does not exist at the stated location and no relocation was found.
- **2-5:** Not reached.
- **Outcome:** NOT PROMOTED. Failing step: **1 (bibliographic identity verified)**.

### Seed 7 — Micropublications (Clark, Ciccarese, Goble, 2014)

- **1. Bibliographic identity verified:** PASS. Confirmed at the source's own page
  (`https://pmc.ncbi.nlm.nih.gov/articles/PMC4530550/`, `LIT-07-S007`): title "Micropublications: a
  semantic model for claims, evidence, arguments and annotations in biomedical communications,"
  authors Tim Clark, Paolo N. Ciccarese, Carole A. Goble, Journal of Biomedical Semantics, published
  4 July 2014.
- **2. Primary source inspected:** PASS. Read directly, `LIT-07-S007`.
- **3. Cited interpretation confirmed:** PASS. The seed's claimed content -- claims and evidence,
  methods and attribution, support/challenge relationships, and defeasible evolution of accepted
  claims over time -- is confirmed verbatim ("scientific reasoning is defeasible"; "assertions may be
  criticised and refuted"; claims "may evolve over time, based on re-examination of evidence").
- **4. Exact supporting location recorded:** Article body's model description (Attribution,
  support/attack relationships, defeasibility discussion).
- **5. Status updated:** PROMOTED. Identifier: `10.1186/2041-1480-5-28`. Type: peer-reviewed journal
  article.

### Seed 8 — Nanopublication Guidelines

- **1. Bibliographic identity verified:** PASS. Confirmed at the source's own stated page
  (`https://nanopub.net/guidelines/working_draft/`, `LIT-07-S008`): "Nanopublication Guidelines"
  working draft.
- **2. Primary source inspected:** PASS. Read directly, `LIT-07-S008`.
- **3. Cited interpretation confirmed:** PASS. The seed's claimed content -- assertion, assertion
  provenance, and publication information as three separated parts, with provenance covering
  derivation, actor, time, location, and generation method -- is confirmed verbatim: "A
  nanopublication consists of an assertion, the provenance of the assertion..., and the provenance of
  the whole nanopublication."
- **4. Exact supporting location recorded:** The guidelines' structural-definition section.
- **5. Status updated:** PROMOTED. Identifier: `https://nanopub.net/guidelines/working_draft/` (plain
  URL). Note: an earlier-phase inventory candidate (`nanopublication-guidelines-spec`, found by
  `LIT-01`) cites a related but distinct URL (`nanopub.org/guidelines`, a different domain); this
  promotion verifies the seed's own cited URL directly rather than assuming the two are identical.

### Seed 9 — Transparent, Traceable, Deterministic: Agentic Memory via Knowledge Graphs (Gentile, An, DeLuca; IBM Research)

- **1. Bibliographic identity verified:** PASS. Confirmed at the source's own page
  (`https://research.ibm.com/publications/transparent-traceable-deterministic-agentic-memory-via-knowledge-graphs`,
  `LIT-07-S009`): authors Anna Lisa Gentile, Sungeun An, Chad Deluca; venue ISWC 2026, dated 25
  October 2026.
- **2. Primary source inspected:** PASS. Abstract read directly, `LIT-07-S009`.
- **3. Cited interpretation confirmed:** PASS. The seed's claimed content -- knowledge graphs for
  agentic conversational memory, structured updating, provenance tracing, trustworthy/deterministic
  response generation -- is confirmed in the page's own abstract text.
- **4. Exact supporting location recorded:** IBM Research publication page's abstract.
- **5. Status updated:** PROMOTED, with a status caveat: the page's own date (25 October 2026) is
  after this dispatch's run (14 September 2026) -- the paper is accepted/forthcoming for ISWC 2026,
  not yet published as of this read, and is recorded as such rather than treated as already-published
  peer-reviewed literature. This seed never appeared in `03_source_inventory.csv` under any prior
  phase. Identifier: `https://research.ibm.com/publications/transparent-traceable-deterministic-agentic-memory-via-knowledge-graphs`
  (plain URL; no DOI assigned pre-publication).

---

## Summary

- **9** seeds in the historical ledger; **1** (PROV-O) is the same document as an existing
  synthesis-cited Part A entry; **6** newly promoted (Event Sourcing Pattern, the DEC paper, ENGRAM,
  Micropublications, Nanopublications, the IBM paper); **2** failed and are listed above rather than
  dropped (Context Objects -- failed step 1; The Loom -- failed step 1).
- Total distinct validated/promoted bibliography entries in this document: **45** (Part A) **+ 6**
  (newly promoted seeds) **= 51** distinct sources, plus the 2 failed seeds recorded with their
  failing step named.
