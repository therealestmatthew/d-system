# Prompt packs

How a multi-agent build is planned and run. A prompt pack is the complete governed artifact set a
build runs from: a requirement, decision records, a plan, backlog phases, agent-roster changes, a
delegation pack, a coordinator prompt and a kick-off record. The artifact set is always called a
prompt pack.

A planning session manufactures the pack and a separate build session spends it. The build session
sends nothing the planning session did not write.

## 1. The pipeline

The pipeline has eight stages, and each ends at a gate. The owner's sign-off freezes the stage's
artifact; a later change passes the same gate again.

1. **Prompt A, the pre-plan package.** A governed prompt document, planned with the owner through
   questions asked one batch at a time, at the point each matters. It carries the ratified
   decisions marked do-not-re-ask, the feature inventory, the open questions, the standing
   constraints and the deadline context.
2. **Prompt B, the pack-factory prompt.** A separate governed prompt document, drafted by executing
   Prompt A. It investigates the repository and writes the pack. Prompt A and Prompt B are never
   one document.
3. **Prompt B review.** An adversarial agent audits Prompt B against Prompt A and the repository,
   assuming it is broken. Findings become fixes, and the owner signs off the revised Prompt B
   before it runs.
4. **Prompt B runs**, in plan mode first. Automatic execution starts only after the owner confirms
   the plan.
5. **The pack.** It carries:
   - requirement rows with observable verification methods, including browser verification where
     the deliverable has a user interface, and a decision record for every boundary the build needs
     settled;
   - phases sized one session each, their order encoded in `depends_on` (`backlog-protocol.md`,
     sections 2 and 14);
   - agent-roster changes that extend existing agents' charters where possible; a new agent needs
     a stated cause;
   - the delegation pack, with one section per phase: kickoff `K`, creator and validator pairs
     `C*`/`V*`, the phase gate `G`, adversarial review `A`, and browser verification `W` where the
     phase has a user interface. Each section is idempotent and is dispatched verbatim;
   - the descope ladder, ordered for the actual runway.
6. **Pack audit.** A second adversarial agent audits the finished pack files. Fixes are committed,
   and the check exits 0 before the pack is done.
7. **The coordinator prompt.** A governed prompt document covering preflight, the phase graph, the
   completion gate, integration and close-out. It is generic and idempotent, so every re-run is a
   resume. Per-build rulings go in the kick-off record, not in the coordinator prompt. The owner
   signs it off; adversarial review at this gate runs only when the owner asks for it.
8. **The kick-off record.** A governed prompt document carrying the per-build ratified changes
   (integration cadence, descope authority, any special lane), gathered through questions with
   recommendations before it is written, and the pinned starting state (queue state, peer claims,
   deadline). Where the kick-off record and the coordinator prompt differ, the kick-off record
   wins. Its final section is the kick-off paragraph: one paragraph that references everything,
   also delivered in chat so the owner can paste it into a fresh terminal. The chat copy is never
   governed or tracked; its durable copy is the one inside the record.

## 2. Dispatched blocks

Every dispatched block of the delegation pack, and the gate block because a gate may re-run, opens
with this sentence:

> Assess the current state of the repository against the deliverables below; do only what is
> missing; report what already existed.

A block the coordinating session performs itself is headed "Not a dispatch." and carries no
idempotency sentence.

## 3. Standing rules for every pack

**Context is loaded when needed.** Context is loaded when the step that needs it begins. Parent
documents defer to their children, the coordinator prompt defers the phase protocol, and the
delegation pack is dispatched one section at a time. No agent's opening context holds the whole
pack.

**Agent hygiene.**

- In a prompt-pack build the coordinator claims nothing, writes no code, authors no prompts and
  never does a worker's job; the `K` dispatch claims. A missing prompt is a blocking finding for
  the owner.
- Before every claim, the active-claim limit and the path locks are checked numerically. The
  Conflicts column says nothing about the limit.
- One worktree per phase, with an explicitly chosen free port (`protocol.md`, section 11). Peers'
  claims are never touched and the agent instruction files are never edited (`backlog-protocol.md`
  section 6, `protocol.md` section 3).
- Validators receive the diff, the requirement text and the verification commands, and never the
  creator's rationale or report.
- Work is committed before it is validated. A truncated agent is resumed, never re-run. An
  orchestrator's assertion is checked against real output before anyone acts on it.

**Cost.**

- The cheapest capable model runs mechanical gates and the standard model does judgement work. The
  most capable model is never pre-assigned and is used at most once per build, as a documented
  escalation.
- Each work item gets at most two fix cycles. Whatever survives them is reported, not looped on.
- The close-out reports spend: loop counts, any escalation, and wall-clock time against the
  runway.

**Gates and descoping.**

- Prompt A's open questions always include whether the build stops at gates or runs through to
  close-out. The answer is recorded in the kick-off record.
- A critical issue (a design or functional impact too costly to defer) first gets a dual review,
  in which an adversarial agent challenges it and attempts a fix. The build pauses for the owner
  only if the issue survives unresolved.
- No descope rung is taken without the owner's explicit direction, unless the kick-off record
  grants a stated exception.

## 4. Templates

| Artifact | Sections |
|---|---|
| Prompt A | Ratified decisions (do-not-re-ask), feature inventory, what the planning session produces in order, open questions, standing constraints, deadline context, and the block that drafts Prompt B |
| Prompt B | Role and hard scope limits (documents only); preflight (check green, peer claims); the pack artifacts in order, with codes from the `next-code` skill; the open-questions protocol; the stop condition (the pack exists, the check exits 0, the owner has the review summary) |
| Phase section | `K` (claim, worktree, ports, item order); `C*`/`V*` in pairs; `G` (verification commands with real output); `A`; and `W` where there is a user interface |
| Coordinator prompt | Coordinator-only role; preflight (check, claim limit, clean checkout, tooling smoke test); phase graph with dispatch order and the locks that force it; completion gate and integration terms; close-out (checkpoint, spend, resume state) |
| Kick-off record | Starting state; owner-ratified changes with the precedence rule; the kick-off paragraph |
