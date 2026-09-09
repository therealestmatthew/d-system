I’ll collect the outstanding decisions into one questionnaire, including the choices that
  affect the later feature plans.

• What should I implement next from the unfinished plans?
  - All remaining plans, delivered in phased changes

  Which file should authoritatively define project–person membership? The current loader
  reads person.projects, while project.stakeholders also exists in the schema.
  - Make project.stakeholders authoritative and derive person projects

  When retrieving context for a project, should memories marked scope: global—including
  those labeled project: d-system—always be included?
  - Yes; include global memories alongside that project's memories (Recommended)

  For dynamic HTML generation, how should authored YAML and generated JSON be stored?
  - Commit YAML; generate ignored JSON during builds (Recommended)

  How strictly should the future page-generation backend validate block content?

  - Validate every block type at runtime against a shared contract (Recommended)

  Who should be allowed to update brain/ as the memory-agent plan is implemented?

  - Keep direct human and authorized-agent edits, with validation (Recommended)

  How should Chronicle, the proposed session-to-memory extraction agent, be triggered?

  - Run manually for an explicitly selected session (Recommended)

  If semantic memory search is implemented, what is your preference for sending memory
  content to an embedding provider?

  - Defer embeddings until keyword/tag retrieval proves insufficient (Recommended)

  How should proposed retrieval hints such as how-to, why, and reference be represented?

  - Infer them from existing memory types where possible (Recommended)
  - Add explicit hints to the existing tag registry
  - Introduce a separate metadata field for retrieval hints

  How should conflicting memories and promotion of session memories into durable global/
  project knowledge be handled?

  - Agents propose changes; the repository owner resolves conflicts and approves promotion
    (Recommended)

• Submitted 10 questions covering implementation scope, data ownership, page generation,
  and memory behavior. Later-feature decisions can be deferred.
