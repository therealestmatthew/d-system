# Session types — the evidence-tested taxonomy

Working document. Ungoverned staging under [ADR-010](../04-decisions/ADR-010-idea-staging.md); no
policy, no front matter, no code allocation. Produced by `phase-tax-02` under the session-taxonomy
investigation plan (`PLAN-042`), against `REQ-026` R03–R06.

**Nothing in this document edits, or instructs an edit to, `CLAUDE.md` or `AGENTS.md`.** Section 6
proposes; the owner disposes.

## What was tested, against what, and how

The registered theory is [session-types-theory.md](session-types-theory.md), written by
`phase-tax-01` before any evidence was examined. It proposes thirteen types in three families, each
carrying five prediction elements, plus four structural predictions (S1–S4), three claims about the
governance surface, and three framework-level rejection criteria. Every one of them is scored below.

| Population | Size | What it is |
|---|---|---|
| Raw transcripts | **113** top-level `.jsonl` files | every owner session the corpus holds, 2026-09-05 to 2026-09-21 |
| Session records | **123** `SESS-*.md` files | the project's own account of its sessions, 2026-09-05 to 2026-09-20 |
| Tooling and governance surface | 13 skills, 12 commands, 15 agent definitions, 12 GOV + 16 OPS documents | what the repository provides and requires |

Of the 113 transcripts, **15 carry no owner prompt at all** — 13 harness-only shells (`/clear`,
`/model`, `/effort`, nothing else) and 2 crash stubs with no user records whatsoever. **98**
transcripts carry at least one real owner prompt, and that is the denominator every transcript
percentage below uses. Saying so matters: using 113 would deflate every band by 13%.

Per the owner's rulings (theory §11) every session carries **two** labels — an entry type from its
first prompt and a dominant type from its activity — and every frequency band is scored **twice**,
once over transcripts and once over records. A prediction can confirm in one column and fail in the
other, and where it does, both are reported rather than resolved.

### How the labels were produced

1. **Deterministic reduction, once.** One script parsed all 113 transcripts (0 parse errors) and
   emitted a manifest, an owner-prompts-only file per session, and an activity signature per
   session. No agent — including the orchestrator — read a raw transcript at any point.
2. **A mechanical rule pass** assigned candidate entry and dominant labels from marker *presence*
   only. Its rules are stated in §7 so they can be criticised.
3. **Agent judgment over derived files only.** Two adjudication agents took the 66 low-confidence
   or rule-defying sessions; a blind agent classified a 24-session sample from the *confident*
   classes with no labels and no rules in front of it; a second blind agent took the remaining 13
   confident sessions. Two more agents labelled all 123 session records; one mapped the tooling and
   governance surface; one attacked the portable definitions with no repository access at all.
4. **The 10 sessions no agent labelled** are the empty shells, settled deterministically.

**The blind check produced the single most important methodological result, and it is a negative
one.** On the sessions the mechanical rules were *most confident* about, the blind judge agreed with
the rules on **11 of 24 entry labels (46%)** and **12 of 24 dominant labels (50%)**. Two systematic
rule defects explain most of it, and both are findings about inference-by-path rather than about the
agent:

- The dominant-label rule reads write paths, so it labelled orchestrators **B1 Specification**
  because an orchestrator writes queue state into `docs/09-backlog/`. The blind judge, seeing 57
  sub-agent dispatches, said C1. **A path-keyed inference cannot see orchestration at all** — which
  is `ADR-020`'s inference rule, and the theory's Departure 3 predicted exactly this.
- The entry rule keys on lexical markers, so a bare "Proceed with `phase-xyz`" or an opening
  `/backlog` carried no signal it could use.

Because of that result the rules' confident labels were not trusted as a counting basis; a second
wave re-labelled the remaining confident set blind, and the frequencies below rest on agent labels
for 103 of 113 transcripts and all 123 records.

---

## 1. Prediction scorecard

Disconfirmations lead, as the method requires.

### 1.1 The framework-level criteria (theory §10) — what would make the whole model wrong

| Criterion | Outcome | Evidence |
|---|---|---|
| **Over-splitting** — "if more than four of thirteen types fail their disconfirming observation in the direction of *this is a segment of another type*, the model has mistaken phases for types" | **Met on the inclusive reading; exactly at the boundary on the strict one** | Four types fail unambiguously in that direction: **A1** (9 of 17 question-opened sessions, 53%, end in a tracked write), **B2** (7 of 7 decision-record sessions, 100%, also wrote a plan or requirement), **B6** (27 of 28 governance-path writes, 96%, landed inside a session whose stated purpose was something else), **C4** (never a primary purpose anywhere in 113 transcripts or 123 records). Two more fail partially: **A2** (2 of 4 capture-dominant sessions also touched what the captured thought concerned) and **C2** (2 of ~6 investigation-entry sessions mutated what they had investigated). Strictly four is not "more than four"; counting the partials it is six. **The model sits on its own rejection threshold and cannot be said to have cleared it.** |
| **Wrong dimension** — "if D5 (convergence criterion) does not separate Specification from Investigation or Construction from Repair, the central methodological claim is false" | **Not demonstrated; and not refutable from this corpus** | B4 Repair's "clearest quantitative fingerprint" — a markedly higher ratio of reads before the first write — **is flatly disconfirmed**: median reads-before-first-write is 20 for product-source writers and 21 for everything else. The pairs D5 was supposed to separate are also too thin to test: 2 Repair and 3 Investigation sessions in 98 transcripts. Whether D5 is wrong or merely unexercised here cannot be settled on this evidence. |
| **Unusable entry signals** — "if first-prompt intent does not predict dominant activity better than chance, the router proposal fails" | **Not met — the router proposal survives** | Entry label equals dominant label in **54 of 82 transcripts (66%)** where both are known, and **93 of 123 records (76%)**. Against thirteen classes, chance is far below that. **But the qualification is load-bearing:** a *lexical* rule pass over first prompts agreed with blind judgment only 46% of the time. First-prompt intent predicts activity; a regex over first prompts does not. |

### 1.2 Structural predictions (theory §9)

| Prediction | Outcome | Evidence |
|---|---|---|
| **S1** — the transcript population is substantially larger than the record population, and the difference is Family A | **Disconfirmed on the count; confirmed on the composition** | There are **123 records and 98 prompt-bearing transcripts**. The record population is the *larger* one, by 25. The composition claim holds strongly: Family A is **15% of live transcripts and 1% of records** (one A3 record in 123). The inversion has a mechanism: one orchestration session emits many records. 2026-09-16 has **1 transcript and 12 records**; 2026-09-15 has 8 and 14. A second check refutes the obvious alternative explanation — that worktree sessions are filed elsewhere and missing. They are not: only 3 of 113 transcripts live in a worktree project directory, but **60 transcripts touch a worktree path and 35 write directly into one** (800 of 2,236 Edit/Write calls). Worktree work is in this corpus, filed under the primary checkout. |
| **S2** — type frequency is not stationary; C1 and B5 near-absent early, concentrated late | **Confirmed for C1, disconfirmed for B5** | C1-dominant share by corpus third: transcripts **6% → 41% → 32%**; records **2% → 61% → 12%**. Orchestration rose sharply and then receded as the work moved back to specification. B5 Capability ran the *opposite* way: 6 capability-dominant records in the first third, 1 in the second, 2 in the last. Capability work was front-loaded, not late. |
| **S3** — mid-flight type change is common, not exceptional | **Confirmed, as "common but minority"** | Entry differs from dominant in **28 of 82 transcripts (34%)** and **30 of 123 records (24%)**. `ADR-020` Decision 2 is vindicated as describing a real and frequent case; it is not the majority case. |
| **S4** — the most common single session shape is Construction opened by Inquiry | **Disconfirmed** | The most common shapes are sessions that stayed what they opened as: transcripts C1→C1 (18), B1→B1 (12), B3→B3 (12); records B1→B1 (28), B3→B3 (25), C1→C1 (20). A1→B3 occurs **twice** in transcripts. The most common *mixed* shape is **B3→C1** (9 records): a session that opened on a specified phase and was executed by dispatch. |

### 1.3 Governance-surface claims (theory §5)

| Claim | Outcome | Evidence |
|---|---|---|
| Four of thirteen types have no defined obligation profile — B4 unphased, C3, C4, A1 | **Confirmed for B4-unphased and B6; partially for C3 and C4; confirmed-by-design for A1** | No GOV or OPS document gives unphased Repair a profile distinct from Construction's. C3 has tooling (`log-anti-patterns`) and no obligations — pure convention. C4 has `OPS-013` and an embedded rehearsal dispatch, but both sit *inside* a construction or orchestration phase rather than defining a session. A1's zero obligations are deliberate and correct. |
| B6 is the only type whose primary artifact an agent may not write, and it shares an entry signal with A2 | **Mixed, and the evidence sharpens it into something worse** | `GOV-014` also reserves phase completion and `next_up` ranking, so B6 is not uniquely unwritable — but `AGENTS.md`/`CLAUDE.md` are the one case with no agent-write path at all. The shared-entry-signal claim is not the real risk. **B6 never appears as an entry label at all** — 0 of 98 transcripts opened as governance — yet it is the dominant label of 5 transcripts and 6 records. Governance does not arrive announced and get misread; it arrives *unannounced, mid-session*. A first-prompt router cannot catch it, because there is no first prompt to catch. |
| C1's obligations are defined by a decisions-ledger entry rather than by the requirement | **Confirmed** | The coordinator's worktree, verification and completion-authority obligations live in `GOV-003` and `GOV-013`, with no cross-reference to `REQ-023` in either direction. |

### 1.4 Per-type predictions

Frequency is scored over both populations. Bands: rare <3%, occasional 3–12%, common 12–30%,
dominant >30%. Transcript denominator 98 (live sessions); record denominator 123.

#### Family A

| Type | Element | Outcome | Evidence |
|---|---|---|---|
| **A1 Inquiry** | first-prompt signature | Confirmed | 17 transcripts opened on an interrogative with no deliverable named; blind and adjudicating agents agreed on these independently. |
| | activity signature (read-only, low tool count) | **Disconfirmed** | 9 of 17 (53%) made tracked writes. The 5 that stayed pure A1 average 3–17 tool calls; the rest ran to 121, 193, 258. |
| | artifact (nothing) | **Disconfirmed for the majority** | 9 of 17 left artefacts on disk. |
| | **disconfirmer** — "an Inquiry session that ends with a tracked-file write" | **Fires** | 53% is a large share. A1's own registered consequence applies: inquiry is at least partly a *prelude*, not only a type. Its dominant labels run A1(5), B1(3), C1(3), A3(2), B3(2), A2(1), B4(1). |
| | frequency (common, 12–30%) | **Transcripts: disconfirmed low (7.1%, occasional). Records: disconfirmed (0.0%, rare)** | As an *entry* type it is 17.3% of transcripts — inside the band. As a *dominant* type it is 7.1%. The record column is 0 by construction, which is Q2's accepted cost, not a fact about the type. |
| **A2 Capture** | first-prompt signature | Confirmed | Capture openings are plural and unrelated, exactly as predicted. |
| | activity signature (append-only, shortest sessions) | Confirmed for the pure cases | `bcbf1028` completed in 4 tool calls, `220e216d` in 7. |
| | artifact (appended records with ids) | Confirmed | |
| | **disconfirmer** — "a capture session that also reads or writes what the thought concerns" | **Partially fires** | 2 of 4 capture-dominant sessions did: one made 10 writes including backlog edits, one ran 45 tool calls of orientation. |
| | frequency (occasional standalone, near-dominant as a segment) | **Confirmed in the split, disconfirmed in the band** | **56 of 98 transcripts (57%) invoke `tools/append_idea.py`; only 4 are capture-dominant and only 1 is pure.** Capture as a session is 4.1% of transcripts and **0.0% of records**. The prediction's shape — common behaviour, uncommon session — is confirmed more strongly than it was stated. |
| **A3 Exploration** | first-prompt signature | Confirmed | |
| | activity signature (read-heavy, many turns per tool call) | Confirmed | Two 9-hour sessions with zero writes and heavy `AskUserQuestion` use. |
| | artifact (nothing governed) | Confirmed with one exception | 3 of 4 wrote nothing governed. |
| | **disconfirmer** — "an exploration session that writes a requirement, plan or decision record" | **Does not fire** (1 of 4 borderline) | `REQ-023` R2's "must never" survives contact with the evidence. |
| | frequency (occasional, 3–12%) | **Transcripts: confirmed (4.1%). Records: disconfirmed low (0.8%, rare)** | One A3 record exists in 123. |

#### Family B

| Type | Element | Outcome | Evidence |
|---|---|---|---|
| **B1 Specification** | first-prompt signature | Confirmed | |
| | activity signature (docs and work-item paths, no product source) | Confirmed | |
| | artifact (specification plus enumerated work items) | Confirmed | The 11 consecutive programme-plan records of 2026-09-15 are the clearest instance. |
| | **disconfirmer** (writes product source; or produces documents with no work items) | **Does not fire** | |
| | frequency (common, 12–30%) | **Transcripts: confirmed (18.4%). Records: disconfirmed high (30.1%, dominant)** | A textbook case for scoring both columns: B1 is common in the corpus and dominant in the repository's own account of itself. |
| **B2 Adjudication** | first-prompt signature | Confirmed | |
| | activity signature (small concentrated write) | Confirmed | |
| | artifact (a decision record) | Confirmed | |
| | **disconfirmer** — "every session that produces a decision record also produces a plan or requirement in the same session" | **Fires, unanimously** | **7 of 7 transcripts that wrote to `docs/04-decisions/` also wrote a plan, requirement or backlog item.** On the theory's own terms, adjudication is a *section* of specification and its separate obligation profile is unjustified. |
| | frequency (occasional, 3–12%) | **Transcripts: disconfirmed low (2.0%, rare). Records: confirmed (5.7%)** | |
| **B3 Construction** | first-prompt signature | Confirmed | |
| | activity signature (product paths; verification runs more than once) | **Confirmed, strongly** | **All 23 product-writing transcripts ran verification more than once. Median 37 runs, maximum 91, minimum 2. Zero ran it exactly once.** |
| | artifact (code, tests, a record) | Confirmed | |
| | **disconfirmer** — "verification commands run exactly once and pass" | **Does not fire anywhere** | The build-verify loop is real and is the type's strongest confirmed signature. |
| | frequency (dominant among recorded sessions >30%; common across all 12–30%) | **Transcripts: confirmed (20.4%, common). Records: disconfirmed (22.0%, common not dominant)** | The record column is where the prediction expected >30% and got 22%. It lost the top slot to B1. |
| **B4 Repair** | first-prompt signature (a symptom, no identifier) | Confirmed in the few instances | |
| | activity signature — "the ratio of reads before first write is markedly higher than in Construction; that ratio is the type's clearest quantitative fingerprint" | **Disconfirmed** | Median reads-before-first-write: **20** among product writers, **21** among everything else. The fingerprint does not exist in this corpus. |
| | artifact (narrow diff plus regression test) | Not testable | n = 2 transcripts. |
| | **disconfirmer** (repair opens with an identifier and a pre-written verification list) | **Partially fires** | Both record-side Repair sessions that were phased entered on a phase identifier — `SESS-2026-09-08-15` and `SESS-2026-09-14-09` — which is the disconfirming pattern. |
| | frequency (common, 12–30%) | **Disconfirmed in both columns: 2.0% transcripts, 1.6% records (rare)** | Repair is the model's largest frequency miss. Defects in this repository are overwhelmingly specified into phases and executed as Construction. |
| **B5 Capability** | first-prompt signature (a backward reference, "the thing we just did") | Confirmed | |
| | activity signature (agent-config paths; weak verification) | **Verification half disconfirmed** | The largest capability session ran an adversarial validator agent over its output; verification was not weak. |
| | artifact (a new or amended agent-facing definition) | Confirmed | |
| | **disconfirmer** — either the full specify-build arc with verification, or never a primary purpose | **Does not fire** | 9 records are capability-dominant, so it clearly *is* a primary purpose. Only 1 of 10 transcripts that write agent-config paths has them as the majority of its writes — capability is usually a segment — but the primary-purpose cases exist and are numerous enough. |
| | frequency (occasional, 3–12%) | **Transcripts: disconfirmed low (2.0%, rare). Records: confirmed (7.3%)** | |
| **B6 Governance** | first-prompt signature ("from now on", proposes a standing rule) | **Disconfirmed by absence** | **No transcript in the corpus opens as governance.** 0 of 98. |
| | activity signature (small mutations, heavy prior reading) | Not testable as a ratio | The reads-per-line-written measure needs a line count the reduction does not produce. |
| | artifact (an amended governing document plus a record of why) | Confirmed where it occurs | |
| | **disconfirmer** — "a governance change that lands inside a diff whose stated purpose was something else" | **Fires, overwhelmingly** | **28 transcripts wrote to a governance or instruction path; 27 of them (96%) also did other substantive work.** Exactly 1 session had governance as its only substantive output. The record sweeps found the same thing by hand: `GOV-003`'s completion-authority clause was amended inside a session whose stated purpose was commissioning a build coordinator; `GOV-007` was created inside a session whose brief was a README fix. **The theory's own consequence applies: the identification logic cannot key on the first prompt for this type.** |
| | frequency (rare, <3%) | **Disconfirmed high in both columns as a dominant type: 5.1% transcripts, 4.9% records (occasional)** | And disconfirmed far harder as a *behaviour*: 29% of live transcripts touch a governance path. |

#### Family C

| Type | Element | Outcome | Evidence |
|---|---|---|---|
| **C1 Orchestration** | first-prompt signature (a plural target, an instruction to run) | Confirmed | 18 of 26 orchestration-dominant transcripts opened on that signature. |
| | activity signature (dispatch-dominant, sparse structural own-writes) | **Confirmed for two thirds** | See the disconfirmer row. |
| | artifact (units' artifacts plus queue transitions) | Confirmed | |
| | **disconfirmer** — "own direct edits to work-product files exceed its dispatches" | **Fires for 10 of 30 (33%)** | Counting only work-product writes and excluding the structural writes the type's own definition permits (session records, backlog queue state, `_tmpagent/`, memories), 20 of 30 heavy dispatchers hold the context-offloading posture and 10 do not. The claim is true of most orchestration sessions and false of a third of them. |
| | frequency (rare rising to occasional, <3% → 3–12%) | **Disconfirmed, by a wide margin, in both columns** | **26.5% of transcripts and 25.2% of records are orchestration-dominant** — common, not rare. The *rising* half of the prediction is confirmed (S2 above): 6% → 41% → 32% across corpus thirds. |
| | variant boundary — "C1b never closes anything" | **Confirmed** | All 5 transcript-side and 3 record-side C1b sessions staged proposals for owner sign-off and closed nothing. The discriminator drawn on closing authority rather than domain holds. |
| **C2 Investigation** | first-prompt signature (a population word) | Confirmed | |
| | activity signature (read-dominant, read-only fan-out, one late large write) | Confirmed | |
| | artifact (a findings document, often one row per population member) | Confirmed | |
| | **disconfirmer** — "an investigation that changes what it investigates in the same session" | **Partially fires** | 2 of ~6 investigation-entry sessions turned their findings into plans or rulings in the same session. |
| | frequency (occasional, 3–12%) | **Transcripts: confirmed (3.1%). Records: disconfirmed low (1.6%, rare)** | |
| **C3 Retrospective** | all five elements | **Disconfirmed by absence** | **Zero sessions in either population, on either label.** The `log-anti-patterns` skill exists and is invoked from inside other sessions; retrospection is a section, never a session. The type's registered consequence applies: the tooling is correctly a skill, and the type should not be an entry point. |
| **C4 Rehearsal** | all five elements | **Disconfirmed by absence — as the theory predicted it would be** | **Zero sessions in either population, on either label.** Only 2 transcripts drive a browser at all, both on 2026-09-10, and both also made 10+ edits — rehearsal inside construction. Every genuine end-to-end rehearsal in the records (`W07-R`, `D05-R`) is a dispatch inside a C1a orchestrator's phase. **The absence is the finding the owner's Q4 ruling asked for: in this repository, end-to-end behaviour is only ever checked by whoever just built the thing, or by an agent that orchestrator dispatched. There is no independent verification session.** |

---

## 2. The portable taxonomy

Each type below is stated without naming a d-system artefact. **External validity, stated plainly:
this is one user in one repository over sixteen days. The portable claim is the *existence* of a
type and the shape of its entry signal. Frequency is a local fact and lives in §3, not here.** A
second caveat the evidence forces: the corpus is a single person's working habit, so a type's
absence here (C3, C4) is evidence about this repository's practice, not about the type's existence
anywhere.

A dedicated agent was given only the portable definitions, no repository access, and asked to flag
every term presupposing an artefact a generic repository lacks. Its verdicts are in the last column.

| Type | Definition (no local artefact named) | Generic entry signals | Status | Portability verdict |
|---|---|---|---|---|
| **A1 Inquiry** | The human wants to know something; the repository is a subject to read, not an object to change. | Interrogative opening; no imperative verb of change; no deliverable named. | **Observed** (7.1% dominant, 17.3% entry) | Portable as written |
| **A2 Capture** | A thought is stored so it survives, and deliberately not acted on. | A declarative want with no request to execute it; often several unrelated wants at once. | **Observed** (4.1%) | Portable as written |
| **A3 Exploration** | An undecided question is shaped without being closed; it finishes when the human says it has gone far enough. | Request for options, objections or a second view; absence of a named deliverable. | **Observed** (4.1%) | Portable as written |
| **B1 Specification** | The work ahead is made explicit: what will be built, in what order, and how anyone will know it is done. | A named future capability plus an explicit or implicit "not yet". | **Observed** (18.4% / 30.1%) | Portable after rewording — "binding on acceptance" presumes an approval step; use "binding once approved". |
| **B2 Adjudication** | An open choice is closed and the reason made durable; the output removes options. | Two or more named alternatives already on the table. | **Observed but not independent** — see §5 | Portable as written |
| **B3 Construction** | A specified unit of work is built and verified; the done-condition existed before the session opened. | A reference to something already written down, plus an imperative to build it. | **Observed** (20.4% / 22.0%) | Portable after rewording — "work-item identifier" presumes a tracker; use "an issue reference, or a link to a written spec". |
| **B4 Repair** | Something that was supposed to work does not, and the session must derive its own done-condition from the symptom. | A symptom, not a desired behaviour; no identifier, often no reproduction steps. | **Observed, rare** (2.0% / 1.6%) | Portable as written |
| **B5 Capability** | The object of work is what the assistant itself can do; the artefact is consumed by the assistant, not by a user of the product. | A backward reference to a manual sequence just performed, plus "make this reusable". | **Observed** (2.0% / 7.3%) | Portable after rewording — the skills/commands/agents vocabulary is local. The auditor warns that **B3 and B5 collapse into one type in a repository with no agent framework**, because the second consumer does not exist there. |
| **B6 Governance** | The rules binding all future work change; the output binds immediately. | "Add a rule", "this should be policy", "from now on". | **Observed as an outcome, never as an entry** (5.1% / 4.9%; 0% entry) | Portable after rewording — "the working agreement" and the assumption that the rules file is *automatically* read are both local. |
| **C1 Orchestration** | A session drives many units of work to completion through delegated workers while deliberately holding almost none of their content. The context posture is the definition. | A plural target plus an instruction to run rather than to decide. | **Observed, common** (26.5% / 25.2%) | **Not portable as such.** The auditor's verdict: without dispatchable workers the type does not shrink, it disappears. It has no smaller portable residue. In this taxonomy C1 is therefore a *capability-conditional* type: real wherever delegation exists, absent where it does not. |
| **C2 Investigation** | A question is answered by systematic evidence-gathering and finishes when a declared scope has been covered, not when the answer feels sufficient. | A population word — every, all, each — is close to definitional. | **Observed** (3.1% / 1.6%) | Portable as written |
| **C3 Retrospective** | The object is the project's own history: what happened, and what should change because of it. | Backward-looking reference plus a forward ask. | **Proposed, never observed as a session** | Portable as written |
| **C4 Rehearsal** | The system is executed as a user would execute it, to discover whether it works, not to change it. | "Walk through", "run it end to end", "does this actually work". | **Proposed, never observed as a session** | Portable as written |

Two structural observations from the portability attack are worth carrying forward: the three
*family* definitions leak nothing local, and the entry-signal sets mix genuinely generic lexical
cues with local jargon, so a router built from the jargon alone would fail on a plain repository's
first message.

---

## 3. The d-system binding, per type

Frequencies as measured. "Obligations that should attach" is a proposal, not a rule.

| Type | Local entry signals seen in evidence | Frequency (transcripts / records) | Obligations that should attach | Tooling that serves it | Gaps and failure modes seen |
|---|---|---|---|---|---|
| **A1 Inquiry** | A bare question; `/orient`, `/backlog` used as orientation; `/demo-cmd-explain-this` | 7.1% / 0.0% (17.3% as entry) | **None** (owner's Q2 ruling) | `orient`, `backlog`, `/demo-cmd-context-check` | **Its dominant failure mode is drift**: 53% of question-opened sessions ended up writing. Nothing marks the moment an inquiry became committing work. |
| **A2 Capture** | `/idea`; any owner want voiced mid-session | 4.1% / 0.0% | None beyond the sanctioned writer | `idea` skill/command, `tools/append_idea.py`, `OPS-005`, `OPS-008` | Capture is overwhelmingly a *segment*: 57% of live transcripts invoke the idea writer, 4% are capture sessions. The tooling is correctly shaped for this; the session type barely exists. |
| **A3 Exploration** | `/demo-cmd-rubber-duck`, `/demo-cmd-second-opinion`, `demo-skill-brainstorm` | 4.1% / 0.8% | None; `REQ-023` R2 holds | those three | Two multi-hour exploration sessions opened with explicit "begin implementation" language and produced nothing — an expensive, invisible failure with no record. |
| **B1 Specification** | `/backlog`, `/session-start` on a docs-deliverable phase | 18.4% / **30.1%** | Claim, worktree, record, `--next-code`, governance check | **No dedicated skill, command or agent** | The largest type in the repository's own account of itself, and the one with the least tooling. |
| **B2 Adjudication** | "rule on", an open question carried forward | 2.0% / 5.7% | Same as B1 — and the evidence says that is right, because it never occurs alone | `GOV-003` as the ledger; no authoring tool | 7 of 7 decision-writing sessions also wrote a plan. See §5. |
| **B3 Construction** | `/session-start <phase-id>`; "Proceed with `phase-…`" | 20.4% / 22.0% | Full protocol; verification list; `/session-close` | `checkpoint`, `session-start`, `session-close`, the creator and validator agents | Healthiest type in the corpus: verification ran a median of 37 times per session and never exactly once. |
| **B4 Repair** | A pasted error; defect phases | 2.0% / 1.6% | Undefined when unphased | **None** | Nearly extinct as a type because defects get specified into phases first. Where it does occur unphased, no obligation profile exists. |
| **B5 Capability** | "make this a skill"; `demo-skill-make-it-a-skill` | 2.0% / 7.3% | Full protocol | `demo-skill-make-it-a-skill`, `OPS-010`, `GOV-015` | Front-loaded, not late (S2). Usually a tail segment of another session; 9 records show it as a primary purpose. |
| **B6 Governance** | **None observed.** Governance arrived mid-session, every time but one | 5.1% / 4.9%, **0% as an entry** | Owner-reserved; identification-and-refusal rule (Q3) | **No agent-invocable tool, correctly** | **The highest-risk finding in this investigation.** 96% of governance writes rode along inside a session about something else. A router keyed on the first prompt cannot catch this type, because it has no first prompt. |
| **C1 Orchestration** | Owner-approved batch; `PROMPT-035`/`PROMPT-036`; `/idea-triage`; `/resume-lit-review` | 26.5% / 25.2% | `GOV-003` completion authority under three conditions; integration owner-gated; `GOV-013`/`GOV-014` | `demo-orch-*` agents, `/idea-triage`, `/resume-lit-review`, `GOV-008`, `GOV-009`, `GOV-013` | A third of heavy dispatchers wrote more work product than they dispatched — the context-offloading claim fails for them. |
| **C2 Investigation** | `/orient`; audit phases; `phase-lit-*` | 3.1% / 1.6% | Claim and record where phased; no mutation of the audited surface | `demo-adversary`, `partition-adversary`, the validator agents, `GOV-009`, `GOV-015` | The no-mutation obligation is breached about a third of the time, always by turning findings into plans. |
| **C3 Retrospective** | `log-anti-patterns` invoked from inside other sessions | **0% / 0%** | None — correctly, it is a skill not a session | `log-anti-patterns` | Confirms the theory's own fallback: keep it as a skill, do not make it an entry point. |
| **C4 Rehearsal** | Rehearsal dispatches inside orchestrator phases | **0% / 0%** | None defined | `OPS-013`, the rehearsal dispatch inside `demo-orch-content` | **No independent verification session exists in this repository.** |

**Governance obligations, as the surface actually states them** (from the tooling sweep): durable
session record (`GOV-002`, `/session-close`); backlog phase claim (`GOV-002`, `AGENTS.md`); isolated
worktree (`GOV-003`, `GOV-013`); verification list run to green (`GOV-002`, `GOV-013`); human gate
before integration (`AGENTS.md`, `GOV-003`); governance check (`OPS-001`); private-content check
(`OPS-009`); `--next-code` allocation (`GOV-005`); owner-reserved decisions and the per-dispatch
token ceiling (`GOV-014`). Measured compliance on the record side: **87 of 123 records claim a
phase, 78 use a worktree, 97 dispatch sub-agents.**

---

## 4. Orchestrator variants

The theory proposed that the correct discriminator is **what the orchestrator is allowed to close**,
not which domain it works in. The evidence supports it, and the variants separate cleanly enough
that two independent agents assigned them without disagreement on any session.

| Variant | Transcripts | Records | Boundary test, as applied | Held? |
|---|---|---|---|---|
| **C1a Execution** | 11 | 19 | Every unit existed before the session opened; the orchestrator may close units under a gate | Yes |
| **C1b Generative** | 5 | 3 | The set of units is not known at session start; it closes nothing | **Yes, unanimously** — all 8 staged proposals for owner sign-off |
| **C1c Pipeline** | 10 | 9 | Units are sequentially dependent stages of one campaign | Yes |

Two boundary observations the evidence adds:

- **C1a and B3 are genuinely adjacent, not confusable.** The build-batch records of 2026-09-16 each
  claim a single specified unit — which makes them B3 — but build it entirely through a recon →
  creator → validator → adversary dispatch chain, which makes them C1a. The discriminator that
  works is **whether the session holds the work's content**, not how many units it names. The
  record sweep classified them B3-entry / C1-dominant, which is the honest answer.
- **C1c has a distinct and repeated entry defect.** Nine of the literature-review records enter as
  B3 ("execute `phase-lit-NN`") and are dominated by C1c. The entry signal names a phase; the
  session is a pipeline stage. This is the single most reproducible entry/dominant divergence in
  the corpus.

---

## 5. Undocumented and proposed types

**What the evidence showed that the theory missed.**

1. **NO-PROMPT sessions — 13 of 113 transcripts (12%).** Opened, given a harness command or two
   (`/clear`, `/model`, `/effort`), and abandoned. Two further transcripts are crash stubs with no
   user records at all. The theory has no category for a session that never becomes one. They are
   not a type — they are noise that any future measurement must exclude explicitly, or every band
   is deflated by 13%.
2. **Relay sessions.** Several transcripts open not with owner prose but with a returning agent's
   task-notification, or with a handoff string meant to be pasted into a *different* session. Entry
   classification is undefined for these: there is no first owner prompt. Three adjudicated
   sessions hit this; one consists of nothing but a handoff string. **A two-label scheme keyed on
   "the first prompt" has an unhandled case, and it is not rare.**
3. **Maintenance.** One record (`SESS-2026-09-19-02`) is a pure git rebase — no decision, no
   specification, no construction, no investigation, nothing broken. The record sweep could not
   place it in any of the thirteen. It is a real and recurring shape: repository housekeeping that
   changes no content.
4. **Harness and meta sessions.** Two transcripts are a connectivity test and a model-identity
   question. Trivial, but they are sessions and they are not in the model.

**Types that should be merged rather than kept.**

- **B2 Adjudication into B1 Specification.** Its disconfirmer fired 7 times out of 7. The evidence
  says adjudication is the closing section of a specification session, not a session. It should
  keep its *artefact* (a decision record) and lose its *obligation profile*.

**Proposed but unobserved, and why to keep them anyway.**

- **C3 Retrospective — keep as a skill, drop as a type.** Zero sessions. Its own registered fallback
  is exactly this.
- **C4 Rehearsal — keep the type, act on the absence.** Zero sessions in either population. That is
  the finding: nothing in this repository independently exercises the system end to end. Every
  rehearsal is performed by the orchestrator that built the thing. If independent verification is
  wanted, it has to be created, not identified.

---

## 6. Inputs to the CLAUDE.md / AGENTS.md revamp

**Proposals only. Nothing here is an instruction to edit either file.**

### 6.1 A candidate session-identification section

The evidence supports routing on session type, with three corrections the theory could not have
anticipated:

| If the first message looks like… | Route to | Why the evidence supports it |
|---|---|---|
| a question, with no imperative of change | **Family A — no claim, no worktree, no record** | 17 transcripts opened this way; 5 stayed pure |
| "record this / for later / park it" | **A2 — sanctioned writer only** | the dominant capture path is already a segment, not a session |
| "what are our options / push back / second opinion" | **A3 — no governed document** | `REQ-023` R2 survived the evidence |
| a named future capability plus "not yet" | **B1 — claim, worktree, record, code allocation** | 30% of records |
| a reference to something already written, plus "build it" | **B3 — full protocol, verification list, close gate** | the healthiest type; verification median 37 runs |
| a symptom with no identifier | **B4 — currently undefined; needs a profile** | rare but real, and unphased repair has no rules |
| "make this reusable / make it a skill" | **B5 — full protocol** | 9 records |
| **"from now on" / "add a rule" / "this should be policy"** | **B6 — stop and hand it to the owner** | Q3's identification-and-refusal rule |
| a plural target plus an instruction to run | **C1 — coordinator protocol, `GOV-013`** | 26% of transcripts |
| a population word: every / all / each | **C2 — claim and record; no mutation of the audited surface** | |

**Correction 1 — the router cannot be keyed only on the first prompt.** B6 never appeared as an
entry signal in 98 sessions, yet governance changed in 28 of them. A first-prompt router catches
governance zero percent of the time. What would catch it is a **write-path trigger**: any edit under
`docs/08-governance/`, `AGENTS.md` or `CLAUDE.md`, mid-session, regardless of how the session
opened. That is the inverse of the theory's §7 recommendation, and the evidence forces it: for
twelve types the first prompt is the better trigger and the path glob is confirmation; **for B6 the
path glob is the only trigger there is.**

**Correction 2 — the router needs a mid-flight re-check, not just an entry rule.** Entry and
dominant labels diverge in 34% of transcripts and 24% of records. `ADR-020` Decision 2 already
rules that a mid-flight change binds from that point forward; what is missing is anything that
*notices* the change. The cheapest candidate the evidence suggests: when a session labelled Family A
makes its first tracked write, say so and re-route. That single check would have caught 9 of the 17
inquiry sessions that drifted.

**Correction 3 — lexical matching is not enough.** A regex over first prompts agreed with
independent judgment 46% of the time. The router rules should be stated as *intent* descriptions for
a model to apply, not as phrase lists to match.

### 6.2 Appendix A evaluated against the evidence

The theory's §7 assessed Appendix A before seeing any evidence. What the evidence adds:

**The behavioural spine (four rules).** Rules 1 (ask rather than guess) and 4 (explicit
verification, loop until verified) are **confirmed as universally correct** — and rule 4 is the
single best-supported claim in the whole investigation: 23 of 23 product-writing sessions ran
verification more than once, median 37. Rules 2 and 3 are **confirmed as type-scoped, as §7
predicted**: "the minimum code required for the immediate problem" is right for the 2 Repair
sessions and wrong for the 37 record-side Specification sessions whose job was to widen the frame;
"touch only the lines the request needs" is wrong for the 5 Governance sessions and the 9 Capability
sessions, whose changes are system-wide by design. The evidence supports §7's recommendation to
split the spine: 1 and 4 unconditional, 2 and 3 in a Family B execution profile.

**"Core values over rigid rules."** The evidence is against the notes and stronger than §7's
argument. Governance changes landed inside somebody else's diff **27 times out of 28**. No value
prevented that; a value is exactly what a reasonable agent reinterprets under pressure. The rules
this repository actually enforces are all irreversible-act rules, and the one place where a value
was doing the work — "record what you learned, keep the documents accurate" — is the mechanism that
produced the 96% figure.

**"Lean, under 50 lines, a behavioural router not a mini-wiki."** The router framing is right and
the line budget is now measurable rather than aspirational. Thirteen types will not route in 50
lines. **Three families might, and the evidence supports the family layer as the routing layer**:
Family A carries no obligations at all (15% of live transcripts), Family B carries all of them, and
Family C's obligations are inherited from what it acts on. That is three routes, not thirteen, and
it fits. The type layer belongs in whatever the routes point at.

**Path-scoped rules and the phase split.** `.claude/rules/` still does not exist in this repository.
The evidence sharpens §7's objection and then partly reverses it:

- §7 predicted that path globs would never fire for Family A or C1, and that is confirmed — Family A
  writes nothing, and orchestrators write queue state, which is exactly why the path-keyed rule pass
  in this investigation misclassified orchestrators as planners half the time.
- **But the evidence also found the one case where a path glob is the *only* working trigger**: B6.
  The correct design is not first-prompt-instead-of-globs; it is **first prompt as the primary
  trigger for twelve types, and a governance-path glob as an independent, always-on interrupt**.
- The planning-versus-execution phase split is confirmed as the wrong axis: it splits on *when in a
  session* rather than *what kind of session*, and 34% of sessions change type mid-flight, which a
  phase split has no way to represent.

**What the taxonomy adds that the notes lack** — the same point §7 made, now measured: this
repository's routing dimension is *session type*, and session type is not recoverable from file
paths. The 46% agreement between a path-and-phrase rule pass and independent judgment is the number
that says so.

---

## 7. The Stage 1 rules, stated so they can be criticised

Recorded because the method requires it, and because their failure rate is itself a finding.

**Entry rules** — regex over the first owner prompt plus the opening command, priority-ordered B6 →
C1 → C2 → C3 → C4 → B5 → B4 → B2 → B1 → B3 → A2 → A3 → A1, highest score wins, confidence from the
margin. `/idea` → A2, `/idea-triage` → C1, `/orient` → C2, `/resume-lit-review` → C1,
`/demo-cmd-rubber-duck` → A3, `/session-start` → family B with the type left to the text.

**Dominant rules** — ≥5 Agent calls and dispatches ≥ own writes → C1; zero writes with an
`append_idea` marker → A2; zero writes and ≤15 tool calls → A1; zero writes and more → needs
adjudication; otherwise the largest write bucket decides, with `docs/01-plans|06-requirements|
09-backlog|02-prompts` → B1, `docs/04-decisions` → B2, `docs/08-governance|AGENTS.md|CLAUDE.md` →
B6, `.claude|.agents|.codex` → B5, product paths → B3, `docs/00-working|07-architecture` → C2,
`brain/` → C3; session records and memories never decide a type on their own.

**Their three known defects**, all confirmed against blind judgment:

1. **Path inference cannot see orchestration.** Queue-state writes to `docs/09-backlog/` made
   orchestrators read as specification.
2. **Edit/Write counting misses real mutation.** Six adjudicated sessions did substantive work
   through Bash (`git mv`, `sed`) or through sub-agents, and the rule read them as read-only.
3. **A bare identifier carries no lexical signal.** "Proceed with `phase-priv-03`" and "Run
   `PROMPT-035`" are strong entry signals to a reader and invisible to a phrase list.

The vocabulary was enumerated from the repository's own surface and is **today's** surface; the
corpus spans weeks in which it changed. Only marker *presence* was ever used as evidence. A marker's
absence never was, and no conclusion above rests on one.

---

## 8. Where the derived data and the engine live

All derived transcript reductions are at **`_private/analysis/session-taxonomy/`** — inside the
gitignored `_private/` boundary (`ADR-009`), and nowhere trackable:

| File | What it holds |
|---|---|
| `manifest.tsv` | one row per transcript: titles, timestamps, prompt and tool counts, write buckets, dispatch counts, branches |
| `prompts/<session-id>.md` | the real owner prompts only, in order, with command invocations marked |
| `digests/<session-id>.md` | bounded per-session digests — first prompt verbatim, later prompts truncated, full activity signature — sized for a sub-agent's scope |
| `signatures/<session-id>.tsv` | tool histogram, sub-agent types, skills, write buckets, registered-name marker hits |
| `record-structure.tsv` | the structural census of all 123 session records |
| `stage1-labels.tsv`, `final-labels.tsv`, `record-labels.tsv`, `blind-labels.tsv` | candidate, adjudicated, record-side and blind labels |
| `evidence-counts.txt`, `evidence-counts-2.txt`, `run-log.txt`, `agent-reports-1.md` | the counts every number above is drawn from |

**The engine** is four scripts, kept alongside the outputs at the same path:
`reduce_sessions.py` (Stage 0), `record_structure.py` (Stage 0b), `make_digests.py` (Stage 0c) and
`stage1_classify.py` (Stage 1). An idea proposing the **scripts only** be promoted to `tools/` with
an OPS document is captured as **`000291`** (*promote the session-taxonomy reduction engine to
tools/ with an OPS doc*). The derived outputs are never promoted: they carry owner prompt text.

**`record-structure.tsv` is ready for Part 3** — the record-quality and template phase
(`PROMPT-session-taxonomy-part3-record-templates.md`, serving ideas `000276` and `000277`, and
consumed by `phase-fwa-03`). It covers all 125 records with sections-present-versus-contract, line
count, front-matter completeness and non-contract sections. Collected here; analysed there. Three
headline numbers it already carries: **88 of 125** records satisfy the checkpoint contract
(`Phase`/`Verification`/`Acceptance`/`Backlog`/`Unresolved`), **74 of 125** the session-close
contract (`Review`/`Decisions`/`Corrections`/`Left undone`), **98 of 125** have complete front
matter, and the corpus uses **159 distinct non-contract section headings**.

**Regenerated at close (2026-09-20).** The table first ran at 123 records and was regenerated to 125
during `/session-close`, after `phase-tax-02`'s independent review found that "covers every SESS
file" is the requirement body's unqualified demand and that the two absent records — a peer's
`SESS-2026-09-20-02` and this phase's own `SESS-2026-09-20-03` — could simply be added. Re-running
`record_structure.py` is deterministic, reads no transcript, changes none of the 123 existing rows,
and converges: 125 rows against 125 files. The four figures above are the regenerated ones; the
distinct-heading count moved most (151 → 159), which matters because heading drift is the dimension
`phase-fwa-03` exists to assess.

---

## 9. Open questions for the owner

Few, and only the ones that change the design.

1. **Where should the engine and the two prompts live permanently?** `tools/` plus an OPS document;
   a prompt pack under `GOV-008`; or staying in `docs/00-working/` and `_private/analysis/`. This is
   `000291`'s open question and the reason the idea was captured rather than acted on.
2. **Does B2 Adjudication survive as a type?** Its disconfirmer fired 7 times out of 7. The evidence
   says merge it into B1 and keep the decision record as an artefact. That is a change to the model,
   not a measurement, so it is yours.
3. **Is C4 Rehearsal worth creating, now that its absence is measured?** Nothing in this repository
   independently exercises the system end to end. Keeping the type costs a row; creating the
   *practice* costs a session per release.
4. **Should the governance interrupt be built?** The single clearest actionable finding is that 96%
   of governance changes arrive unannounced mid-session. A write-path trigger on
   `docs/08-governance/`, `AGENTS.md` and `CLAUDE.md` would catch every one of them. Whether that
   belongs in a router proposal, a hook, or neither, is a decision reserved to you.

---

## 10. What this investigation could not test

Stated so the scorecard is not read as more than it is.

- **B6's reads-per-line-written ratio** and **B4's artefact shape** are marked not testable: the
  reduction counts tool calls, not lines written, and there are only 2 Repair sessions.
- **D5 as a separating dimension** cannot be refuted or confirmed here; the corpus holds too few
  Repair and Investigation sessions to exercise it.
- **Sixteen days, one user, one repository.** Every frequency in this document is local. The type
  set is the portable claim; the numbers are not.
- **The corpus cannot see sub-agent work.** 744 sub-agent transcripts were deliberately excluded as
  not being owner sessions. Where a session's real work happened inside its dispatched agents, this
  measurement sees only the dispatch.

---

## 11. Owner rulings on §9's open questions

Settled by the owner on 2026-09-20, after reading this document's findings and before
`phase-tax-02` closed. Recorded here beside the questions they answer, on the same basis as the
theory document's §11: `PLAN-042` states that nothing under it creates governed policy, and these
rulings bind this investigation rather than the repository.

**The measurements above are unchanged by anything below.** No scorecard outcome, count or verdict
was revised after the rulings were made.

### Q1 — The engine goes to `tools/` with an OPS document; the prompts go to `docs/02-prompts/`

**Ruled:** split them by what they are. The four reduction scripts are a reusable deterministic
reducer and go to `tools/`, each shipping the `OPS-NNN` document `AGENTS.md` requires, paired by
filename so `tools/generate_tool_docs.py` can find it. The two taxonomy prompts are method documents
and go to `docs/02-prompts/` alongside the other thirty-six.

**Rejected:** packaging the whole set as a `GOV-008` prompt pack, which suits a repeatable campaign
rather than a tool plus two documents; and leaving them where they are, which is exactly what idea
`000291` was captured to prevent — a gitignored engine is lost or rewritten the next time anyone
wants it.

**One consequence to carry into that work.** Promoting the engine makes a raw-transcript reader a
first-class repository tool — the precise surface `REQ-026` R06 exists to constrain. Idea `000292`
holds the question of making R06 enforceable rather than attested, and the two should be planned
together rather than in either order alone.

The ruling is recorded as an assessment annotation on idea `000291`, which carried this as its open
question.

### Q2 — B2 Adjudication is merged into B1; the decision record survives as an artefact

**Ruled:** B2 does not survive as a type. Its disconfirming observation — "every session that
produces a decision record also produces a plan or requirement in the same session" — fired **7 times
out of 7**. The decision record remains a distinct artefact that B1 Specification sessions produce;
it is not a distinct session type.

**Why this ruling and not the available escapes.** Two were offered and declined. Reading 7-of-7 as
local rather than general is defensible on n=7, but the portable claim was about *existence* of the
type, and the evidence says the type does not separate here even once. Narrowing B2 to sessions whose
only governed output is a decision record would salvage the distinction — by redefining a type after
seeing the evidence, which is the curve-fitting the whole theory-first design was built to prevent.

The model is now **twelve types**. Keeping B2 after a complete disconfirmation would have made every
other disconfirmer in the model decorative, and the registration was worth having only if a clean
failure actually removes something.

### Q3 — C4 Rehearsal keeps its place in the model; the practice is not instituted

**Ruled:** the type stays and stays scored. The practice is **not** created now.

The finding stands and is worth preserving: nothing in this repository independently exercises the
system end to end, and where it is exercised at all it is by whoever just built the thing. But a
per-release ritual on a system with no release cadence is a rule that will not be followed, and an
unfollowed rule erodes the ones around it. What is needed first is a trigger that would actually fire
here. Idea `000293` holds that question.

### Q4 — The governance interrupt is captured, not built in this session

**Ruled:** the write-path interrupt is the investigation's clearest actionable finding and will be
specified properly rather than improvised. `AGENTS.md`'s plan-before-code rule applies: a hook on
`docs/08-governance/`, `AGENTS.md` and `CLAUDE.md` is a non-trivial change and needs a requirement
and a plan first. Idea `000294` carries the finding, its counts, and the proposed shape.

**Declined:** a router-proposal-only treatment. The evidence argues directly against it — first-prompt
routing catches this type 0% of the time, so an identification rule agents are expected to read is the
one option the data rules out.

### A ruling this document did not ask for

**The executing agent's two reaches into `_private/`.** It mirrored 363 derived files into the
primary checkout's `_private/analysis/session-taxonomy/`, and it temporarily symlinked
`_private/portfolio` into the worktree to make the identifier check run, removing the symlink
afterwards.

The owner **ratified the mirror** — `git worktree remove` destroys ignored content, and the
coordinating session's dispatch had authorised that path — and **ruled against the symlink**. The
correct move there was to report the check's limitation and let the primary-checkout run settle it,
which is what `phase-tax-01` did and what the coordinating session did here. `AGENTS.md` reserves
`_private/` access to the owner's direction, and an agent may not extend its own authorisation to
reach it. Logged as an anti-pattern so the ruling reaches the next agent rather than staying in one
session record.
