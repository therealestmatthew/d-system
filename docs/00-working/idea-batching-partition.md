# Idea batching — the partition

Ungoverned staging document per [ADR-010](../04-decisions/ADR-010-idea-staging.md). No code, no
front matter. Produced by the idea-batching build on 2026-09-13 under
[PROMPT-033](../02-prompts/PROMPT-033-idea-batching-kickoff.md) and
[PROMPT-032](../02-prompts/PROMPT-032-idea-batching-delegation-pack.md), from four independent
analyst partitions and two adversarial audits.

This document proposes. The owner rules — on the partition, and on every decline candidate
individually.

---

## What was partitioned

The corpus built by `tools/build_idea_corpus.py` held **152** ideas: every `triaged` idea minus
the six the demo fast lane consumed.

**Twenty-three of those were removed at GATE 2 by owner ruling** — `000171`–`000193`, the
consultant demo kit. Audit 1 established, and this session verified, that the kit is already
governed work:

| Artifact | State |
|---|---|
| `docs/06-requirements/REQ-008-consultant-demo-kit.md` | exists, `status: draft`, `systems: [sys-demo-kit]` |
| `docs/01-plans/PLAN-024-consultant-demo-kit.md` | exists |
| `phase-kit-01` … `phase-kit-08` | 8 phases, all `queued` |

Every one of the 23 idea bodies asserts that "no requirement, plan or phase exists" for the kit.
That claim is false and was false before the corpus was built. `REQ-008` line 34 also records that
the roster was **already cut from 23 entries to 13** by a blind adversarial triage — so all four
analysts partitioned a superseded roster. Partitioning them again would duplicate governed work,
so they are out of scope here and carry no group below. The 23 ideas remain `triaged` in the log;
nothing was written to them.

**The corpus this document partitions is therefore 129 ideas.**

---

## Corrections applied

Audit 1 found that several groups were sized against facts the repository had already overtaken.
The owner ruled at GATE 2 that synthesis states the verified current fact wherever it changes a
group's scope. Each was verified in this session or by the audit, not taken from a report.

| Idea | The corpus says | Verified state |
|---|---|---|
| `000098` | Layout-schema test ADR-016 promised was never shipped | **Done.** `schemas/workbench-layout.schema.json` and `test/test_workbench_layout_schema.py` exist; 21 tests pass |
| `000099`, `000129` | Three demo-terminal PTY tests fail on `dev` | **Done.** `test/test_demo_terminal.py` passes 46 tests; the full suite is `578 passed` on this branch |
| `000066` | Branch protection blocked — `HTTP 403: Upgrade to GitHub Pro or make this repository public` | **Unblocked.** `gh repo view` reports `"isPrivate": false, "visibility": "PUBLIC"` — the 403's own named workaround is already in place |
| `000097` | Session-failure tracking is unbuilt | **Half delivered.** `.claude/skills/log-anti-patterns/SKILL.md` covers capture; derivation remains open |

The systemic gap behind the first three — a fix lands and the idea that reported it never gets a
status event, so later planning re-plans finished work — is captured as idea **`000201`**. Three
further observations outside the partition task are captured as **`000202`** (corpus presentation
order changed no substantive answer), **`000203`** (subagents cannot write report files in this
harness) and **`000204`** (`REQ-008`'s artifact count does not sum to the roster size it states).

---

## How disagreement was resolved

The synthesis protocol forbids counting analysts, splitting the difference, and deferring to an
analyst because it read more. Three of the four read identical evidence, so a majority among them
is not independent corroboration. Every contested boundary below was ruled by reading the
repository or the idea's own text.

| Contested | Ruling | What decided it |
|---|---|---|
| `000081` context pipelines — framework child, or retrieval? | **Retrieval** (`G30`) | Its own body names `tools/load_context.py`, the memory loader, the DuckDB projection and idea `000040` as its subject. Its deliverable shares implementation surface with the retrieval groups and shares only a parent label with `079`/`080`/`082`. Dependency beats taxonomy. R1 left it unbatched calling it "plausibly both"; R2/R3/R4 filed it under the umbrella. |
| `000013` "other useful commands" — own item, or subsumed? | **Subsumed into `G20`** with `000126` | `000126`'s scope explicitly includes "missing-and-needed" findings, which is `000013`'s entire question. Checkable from both bodies. Only R4 saw it. Several of `000013`'s candidates have since shipped as `/session-close`, `/orient`, `/backlog`. |
| `000054` observability — agent sensors, or retrieval, or standalone? | **Its own group** (`G57`) | No `sys-observability` exists in `systems.yaml`. Its scope (FastAPI latency, DB rebuild timing, generation-script telemetry) spans `sys-api`, `sys-projection` and `sys-html`. It is cross-cutting greenfield, not a child of `080`, whose target is agent-behaviour validation. All four placed it differently; none checked the registry. |
| `000106` overview drift test — testing, or workbench? | **Testing** (`G35`) | Its own recorded link is `relates_to -> 000057`, the testing-strategy umbrella. Link graph is the checkable fact; subject-matter proximity is not. |
| `000102` timestamp badge — rehearsal artifact, or viewer feature? | **Viewer feature** (`G48`) | Its content is a "last refreshed" badge on the HTML Viewer — implementable work. Three analysts filed it by provenance (it surfaced during a rehearsal); R4 filed it by content. Content decides whether something is buildable. |
| `000089` demo fallback seed | **Unbatched, already delivered** | Its own body: seeded by `tools/demo_reset.py prepare`, which checks folded state before appending; "not reverted after the demo" per PLAN-021's afterlife decision. Nothing to build. |
| `000125` holistic triage direction | **Unbatched, self-discharged** | It is the instruction this document carries out. R2, R3 and R4 — including the control — reached this independently; R1 alone placed it in a programme. |
| `000055` connection-builder — inside the ARCH-005 bundle? | **Outside it** (`G02`) | ARCH-005's own bundle names `000061`–`000065`, `000053` and `000018`, and does not include `000055`. It depends on that schema; it is not part of it. |

**Where unanimity across all four held**, it is recorded as the strongest signal available,
because the control read different evidence and could not have inherited the framing: the ARCH-005
schema bundle, the autonomous-operations five, the version-control trio, the HTML Viewer bundle,
the bookmarks pair, the rotator pair, the schema-drift trio, and the content-strategy trio.

---

## Level 2 — the programmes

Twelve, inside the 8–12 target. Each would become one governed plan. Six fields per programme;
the fine partition sits underneath.

### P1 — Idea graph and lifecycle · 19 ideas · `G01`–`G04`

**Why together:** every member changes, agentifies, or reports on the append-only idea log and the
schema it folds through. **Independence:** argued in detail against P2 — P2 governs *plan and
requirement documents and the backlog*, a different substrate with no shared file; `G04`'s
idea→plan drafting is the one bridge, and it consumes P2's rules rather than sharing its
deliverables. One line against every other programme. **Precedes:** nothing outside itself.
**Size:** 10–13 phases if built in full; `G03` is the most shovel-ready.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G01` ARCH-005 schema bundle | 018, 053, 061, 062, 063, 064, 065 | ARCH-005 names exactly these as one governed unit — tagging, doc-code link targets, the three-axis classification, its agent, the withdrawn forking link resolved into a lineage annotation, and the decomposition procedure | Not internally separable by design; the owner's own document already bundled them | A governing REQ/PLAN, not yet written | 1 spec session + 4–5 phases |
| `G02` Idea-system agents | 048, 127, 055 | `048` and `127` are the same ask six days apart (move `/idea`'s write into a subagent returning only the id); `055` maintains the link graph those writes create | Distinct from `G01` — these consume the schema, they do not define it | `G01` for `055` only | 2–3 phases |
| `G03` Idea and backlog reporting | 008, 010, 042, 050, 070, 071 | `050` is the umbrella parenting `010`; `008` supplies the metrics `010` renders; `042` is the same instinct over two logs; `071` is already prototyped; `070` walks a training audience through the same surface | Argued in detail against P9: `042` builds on the *existing* generation framework (`templates/html/`, `sys-html`), not on P9's *new* libraries. R2 and R3 never tested this overlap; R1 and R4 both did | None hard | 3–4 phases; `071` and `070` largely delivered |
| `G04` Idea-to-plan drafting | 046, 047, 049 | `046` names `047` its own prerequisite; `049` (where a promoted document stages before it earns a code) surfaced from triaging `046` and blocks its design | Unanimous across all four analysts | `G05`'s requirement-vs-plan rule informs it | 2–3 phases |

### P2 — Document and backlog governance · 7 ideas · `G05`–`G08`

**Why together:** the contract governing what a governed document is and how the backlog carries
it. **Independence:** one line against P1 (different substrate) and P3 (that is agent safety
mechanics, this is document contract). **Precedes:** `G05` informs P1's `G04`. **Size:** 4–5
phases; every member is small.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G05` Document contract | 038, 056 | `038` fixes the requirement-vs-plan boundary; `056` governs document staleness and retirement — both define what a correct governed document is | Kept out of `G04` deliberately: `056`'s own text admits unresolved overlap with `047`. An unresolved scope question is a reason for the owner to scope it, not to merge it | None | 2 phases |
| `G06` Backlog substrate | 006, 011, 037 | Three capacity/scaling questions against the same registry — index widths, a reprioritisation recipe, and splitting `backlog.yaml` before it clogs agent context | Each independently shippable; grouped for readability, not dependency | None | 1 phase each |
| `G07` Phase containment check | 027 | Nothing diffs a completed phase's actual change set against its declared paths | Independent. Nearest mechanism to hang `000201` on | None | <1 phase |
| `G08` `_tmpagent` registry | 023 | A load-bearing mechanism missing from `systems.yaml`'s maturity registry | Independent, near-mechanical | None | trivial |

### P3 — Concurrency, git safety and enforcement · 10 ideas · `G09`–`G13`

**Why together:** every member hardens how concurrent agents share one repository without
destroying each other's work. **Independence:** argued in detail against P4 — P4 designs agents,
P3 constrains the ground they run on; the one real bridge is `000082` (orchestration), which stays
in P4 because it is an open survey while `G09` is two already-diagnosed incidents with a known fix
shape. **Precedes:** `G10` touches the same `AGENTS.md` passages as `G09` and should land first.
**Size:** 6–8 phases.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G09` Claim and clobber hardening | 025, 041 | Two observed failures of one protocol — an abandoned claim with no recovery path, and a `git stash` that destroyed a peer's uncommitted work | Distinct from `G10`: these are mechanism bugs that exist under any branch topology | After `G10`'s document rewrite | 1–2 phases |
| `G10` Branch protection and PR gate | 066 | Branch topology, GitHub settings, CI-as-gate, and the multi-agent PR protocol that follows | **Correction:** no longer blocked. The repository is public, which was the 403's named workaround. R1 and R2 both carried the stale blocker | None — now actionable | 3–4 phases |
| `G11` Version control and backup | 021, 058, 059 | `058` is the umbrella; `059` its git slice; `021` the concrete gap for gitignored `_private/` | Unanimous across all four | None | 2–3 phases |
| `G12` Harness enforcement | 051, 012, 014 | `051` was created to parent `012` and `014`; all three ask where enforcement belongs — hooks, settings, tests or prose | `012`'s "blocked pending remote/CI" is stale; both now exist | None | 2 phases |
| `G13` `AGENTS.md` push-rule rewrite | 091 | Two hunks in one file, replacement text already approved and recorded twice | Blocked only by `.claude/settings.json`'s `Edit(AGENTS.md)` deny rule — needs the owner to apply by hand or lift it | Owner action | <1 phase |

### P4 — Agent engineering and delegation · 18 ideas · `G14`–`G23`

**Why together:** how agents in general are instructed, observed, coordinated and reviewed.
**Independence:** argued against P1 (those are idea-log agents, a specific application) and P5
(that is unattended execution infrastructure, which none of this assumes). **Precedes:** `G20`'s
audit informs `G02`, `G19`, `G21` and `G22` without blocking them. **Size:** the largest
programme, 12–15 phases; it also carries the most internal near-duplication and deserves a scoping
pass before any phase count is committed.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G14` Framework umbrella | 078, 079, 080, 082 | `078` and its three remaining named children — guides, sensors, orchestration | `081` was removed to P6 (see rulings). `082` stays here rather than joining `G09`: it is an open survey of orchestration, not the two diagnosed incidents | None | 3–4 phases, mostly writing |
| `G15` Truncation handling | 077 | Resume a truncated subagent rather than rerunning it | Split from `G14` on R4's checkable argument: `077` is a prose fix shippable today (`maxTurns` guidance), `080` needs monitoring infrastructure that does not exist | None | <1 phase |
| `G16` Lifecycle roster | 072, 069 | The planner/executor/verifier/auditor roster, and whether to build it in a Claude-specific format at all | **`072`'s planner bullet duplicates `000046`** (P1 `G04`) — only R4 caught this; recommend striking the bullet rather than building it twice | Gated on PLAN-020 | 2–3 phases |
| `G17` Deliberation trio | 073, 074, 075 | Expander, minimalist, arbiter — "none of the three is useful alone" | Kept out of `G16` **on `072`'s own instruction**: a different family, planned alongside but not merged | `G16` | 2–3 phases |
| `G18` Anti-pattern tracking | 097, 138 | The same ask a day apart at two scales; `138` is the fuller description | **Correction:** `097`'s capture half is delivered by the `log-anti-patterns` skill; derivation is what remains | None | 2 phases |
| `G19` Delegation methodology | 139 | Dispatch-cost estimation, per-role model assignment, escalation, and a retrospective that updates the rules | Separate from `G18`: that is a data store, this is a process built on top of it and two others | Benefits from `G18`, `G20` | 2–3 phases; scope down first |
| `G20` Commands/skills/agents audit | 126, 013 | `126`'s "missing-and-needed" output is exactly `013`'s question | Ruled above. `013`'s candidate list is partly shipped already | None | 1–2 phases |
| `G21` Shared state model | 128 | Extend `_tmpagent/` so cross-agent context stops being hand-carried by a coordinator | The light alternative to `000020` in P5 — R4 nominates declining `020` in its favour | None | 1–2 phases |
| `G22` Runtime-evidence pack convention | 136 | Browser smoke dispatch and runtime instruments as a pack-authoring convention | Its substance may already sit in `brain/procedures/runtime-behavior-needs-runtime-evidence.md` — verify before sizing | None | possibly <1 phase |
| `G23` Transcript review | 009 | Deterministic transcript extraction plus an independent adversarial reviewer | Carries no recorded links to anything. The weakest-evidenced placement in this partition; genuinely standalone, filed here by subject | None | 1–2 phases |

### P5 — Autonomous agent operations · 5 ideas · `G24`

**Why together:** all five assume the system operating with no chat session open. **Independence:**
unanimous across all four analysts, control included — the strongest signal in the set. **Precedes:**
internally `028` → `029` → `030`, with `031` required before anything runs unsupervised.
**Size:** 10+ phases if built in full; the most speculative programme here.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G24` Gateway, ledger, worker, broker, librarian | 020, 028, 029, 030, 031 | Deliberately decomposed from one proposal so each could be evaluated alone; `030` has "no purpose until" `028` and `029` exist; `031` gates unattended running; `020` links to both `028` and `031` | `020`'s librarian half overlaps P6's retrieval ground and `G21`'s lighter mechanism — see decline tiers | `028`, `029` before `030` | 4 phases + design |

### P6 — Retrieval and knowledge infrastructure · 10 ideas · `G25`–`G30`

**Why together:** how the system finds and judges its own accumulated knowledge. **Independence:**
one line against P1 (that is the idea graph's shape, not search over it). **Precedes:** nothing;
the whole programme is gated on a recorded retrieval failure that nothing currently collects —
`G25` is what would supply it. **Size:** 1 session per sub-question surveyed; mostly design, not
code.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G25` Ordering and deterministic search | 002, 040 | `002` is named by `040` as its conceptual parent; `040` is the deterministic layer, explicitly not the vector work | Independent of `G26`; would unblock it by producing the failure evidence `phase-mem-15/16/18/19` wait on | None | 3–4 phases |
| `G26` Vector retrieval | 004, 045 | Vector/RAG tooling for the same corpus | Complementary to `G27`/`G28`, not a substitute | Gated externally | 1–2 phases |
| `G27` Code-graph retrieval | 005 | GitNexus evaluated against this repository's code | Distinct from `G28`: different corpus (code vs. documents), and resolvable by installing a tool with no design work | None | 1 phase |
| `G28` Documentation graph and projection | 043, 044 | The structured/front-matter half and the graph half of the same documentation-retrieval question | `043` reverses ADR-001's decision and needs it revisited first | ADR-001 | 2 phases |
| `G29` Memory lifecycle and provenance | 060, 032 | Staleness, contradiction and confidence over memory content, with `032`'s lineage graph as its trust layer | Distinct from `G25`–`G28`: whether what is found is trustworthy, not how it is found | None | 2–3 phases |
| `G30` Context pipelines | 081 | What an agent is given before it starts | Moved here from the framework umbrella by ruling above — its deliverables are this programme's subject | `G25` | 1–2 phases |

### P7 — Blocked downstream projections · 4 ideas · `G31`–`G32`

**Why together:** each needs infrastructure that does not exist, and `022` is the root fact behind
most of it. **Independence:** total against everything else. **Precedes:** `G31` gates `G32`.
**Size:** not yet sizeable — see decline tiers, where R4 nominates all three of `G32`.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G31` Portfolio data gap | 022 | Two of four core entities hold zero records — tooling friction, or no current need? | Independent; a question for the owner more than a build | None | <1 phase to resolve |
| `G32` Temporal, scenario and calibration | 033, 034, 036 | Three views over projections that do not yet exist — history snapshots, what-if simulation, and whether advice helped | `033` needs `phase-idea-07`'s fold; `034` needs portfolio signals and `G31`; `036` needs recommendations to exist at all | `G31`; external plans | dormant |

### P8 — Schema consistency and testing · 8 ideas · `G33`–`G36`

**Why together:** making drift between schema, DDL, fixtures and CI mechanically impossible.
**Independence:** one line against P2 — that is document hygiene, this is code and contract
hygiene. **Precedes:** nothing. **Size:** 4–5 phases.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G33` Schema/DDL drift and contract compiler | 024, 035, 052 | `052` is the umbrella; `024` the concrete four-entity drift; `035` the general compiler proposed to fix it | Unanimous. Scope which of `024`/`035` is being committed to before sizing | None | 2–3 phases |
| `G34` Testing strategy | 001, 026, 057 | `057` names both members; `026` adds the missing `ts/` lint and test gate; `001` governs HTML-gen fixtures | `026` is actionable today; `001` is dormant until PLAN-003 builds | PLAN-003 for `001` | 2 phases |
| `G35` Overview drift test | 106 | One pytest mirroring `test_ideas.py`'s committed-output pattern for `_public/overview/index.html` | Placed here on its own `relates_to -> 000057` link | None | <1 phase |
| `G36` Layout-schema test **[RESOLVED]** | 098 | — | **Already shipped.** Schema and 21 passing tests exist. Carried for completeness; no work remains | — | 0 |

### P9 — HTML generation and design system · 6 ideas · `G37`–`G39`

**Why together:** the template/component/palette layer of the generation pipeline and its
relationship to plans written before the workbench existed. **Independence:** argued against P1's
`G03` above, and against P10–P11 (different consumer: generated report pages, not an interactive
panel app). **Precedes:** `G39` should precede detailed scoping of `G37`. **Size:** 5–6 phases,
mostly gated on PLAN-003.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G37` Libraries and designer agent | 083, 084, 085, 092 | Three cross-linked asset layers feeding one pipeline, plus the agent that would populate all three by scanning shipped pages | Blocked on PLAN-003; the atlas family is an existing manual precedent so evaluation can start | PLAN-003 | 3–4 phases |
| `G38` Governance atlas page | 093 | Content deliverable from the existing atlas family | Depends on the family that exists, not on `G37`'s automation. Owner already deferred it once | None | 1 phase |
| `G39` HTML-gen plan reconciliation | 123 | Dispositions each old `phase-html-*` requirement as accomplished, open, superseded or retired | Independent research; produces scope for `G37` | None | 1 phase |

### P10 — Workbench architecture and quality · 13 ideas · `G40`–`G47`

**Why together:** audits and architecture of the workbench itself, as against P11's discrete
features. **Independence:** one line against P11 — different kind of work on the same product,
though `G40` should land before P11 work renames anything. **Precedes:** `G40` gates `G43` and
`G44`. **Size:** 12–15 phases; `G43` alone approaches a full architecture revision.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G40` Vocabulary | 124 | Settles container-vs-content naming before more work names things wrong | Cited as prerequisite by `133`, `135`, `141`, `144`, `115`, `116`. A documentation deliverable completable alone | None | 1 phase |
| `G41` Duplication and structure audits | 115, 116 | Explicit two-way cross-reference: an abstraction extracted in one is often the refactor proposed in the other | Distinct from `G46`: code shape, not runtime behaviour | Benefits from `G40` | 2 phases |
| `G42` Content-fit methodology | 134 | Per-panel visibility contracts and mechanised checks | Distinct from `G43`: produces a contract, not a redesign | Feeds `G43` | 1–2 phases |
| `G43` Slot/panel architecture | 133, 135, 141 | `141` generalises `135` structurally and would prevent the double-header defect by construction; `133` revisits geometry on the same model | All three presuppose `G40`'s vocabulary by their own text | `G40` | 4–5 phases |
| `G44` Sub-app packaging | 144 | How a sub-app plugs into a slot | Dual-natured: its concrete half rides `G45`, its general half needs `G40` and `G43`. Kept whole because the idea is one entry | `G40`, `G43` | 2 phases |
| `G45` Ports/process app | 142, 143 | Explore the lifecycle, then build the tool — raised together against the same port-conflict incidents | Fully standalone; named as a *candidate* first sub-app for `G44`, not a requirement | None | 1–2 phases |
| `G46` Performance and cache invalidation | 114, 121 | `121` sharpens `114`'s invalidation requirement with a dated failure — a stale overview page during demo prep | `121` is a refinement of `114`, not separable | `114` measures first | 2 phases |
| `G47` Terminal persistence audit | 113 | Session survival and latency across all three shells | Distinct from `G46`'s general audit; some checks need the owner's Windows machine | None | 1–2 phases |

### P11 — Workbench features and defects · 16 ideas · `G48`–`G56`

**Why together:** discrete, mostly small, user-facing features and bugs in the shipped workbench.
**Independence:** each group below touches a different panel or route and is independently
shippable; the programme is an administrative rollup, which is what level 2 is for.
**Precedes:** should follow `G40` where naming is involved. **Size:** 8–10 phases, excluding
`G56`.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G48` HTML Viewer | 109, 110, 118, 119, 102 | `119` is the load-bearing render-location decision that `109` and `110` collide without; `118` extends the extension list the viewer's own preset needs; `102` adds a freshness badge on the same surface | Unanimous on the first four. `102` placed by content, not provenance — see rulings | `119` decided first | 2 phases |
| `G49` File bookmarks | 111, 120 | `120` exists because `111`'s "open a category as a set" has no mechanism without a batch panel-bridge contract | Unanimous. `111` is requirement-and-ADR-first by its own text | `111`'s storage model | 2–3 phases |
| `G50` Rotator | 131, 132 | Two variants of the same notes-strip component | Unanimous | None | 1 phase |
| `G51` Terminal interaction API | 087 | External HTTP inject/read, detach/reattach, output buffering — the part ADR-014 did not absorb | New capability, not a defect fix; needs its own ADR per ADR-013's precedent. R1 lost this idea entirely (see audit finding 4) | Own ADR | 1–2 phases |
| `G52` Session-cap race | 095 | TOCTOU between the session-count check and `accept()` | Independent; never reproduced despite connect storms | None | <1 phase |
| `G53` Shell override docs | 096 | `D_SYSTEM_DEMO_SHELL` silently overrides per-session selection | Independent | None | <1 phase |
| `G54` Flag-off 404 noise | 100 | Cosmetic console noise when the terminal flag is unset | Independent | None | <1 phase |
| `G55` Websocket close reason | 137 | A global-cap refusal reaches the browser as a bare 1006 instead of a structured close | Independent | None | <1 phase |
| `G56` PTY tests **[RESOLVED]** | 099, 129 | — | **Already fixed.** 46 tests pass; the full suite is green. Carried for completeness; no work remains | — | 0 |

### P12 — Standalone explorations and housekeeping · 11 ideas · `G57`–`G63`

**Why together:** nothing. This is an explicit readability bucket — every group is independent of
every other idea in the corpus, including its bucket-mates. Six singletons and two small chains
would otherwise inflate the programme count without adding a programme. **Independence:** total,
by construction. **Precedes:** nothing. **Size:** size each member alone; the bucket's total is
not a meaningful number.

| Group | Ids | Why together | Independence | Precede | Size |
|---|---|---|---|---|---|
| `G57` Observability and telemetry | 054 | System-wide logging, metrics and tracing | Ruled above: no `sys-observability` exists; spans `sys-api`, `sys-projection`, `sys-html`. Not a child of `080` | None | unscoped — needs a scoping pass |
| `G58` Content strategy | 015, 016, 017 | One expanding chain: one platform → multi-platform → automation | The cleanest mutual-exclusivity case in the corpus; shares no file, system or consumer with anything | `015`→`016`→`017` | 1 session to decide |
| `G59` Research scouting | 068 | Capture pass over the `research/` corpus | Produces ideas, not features; edits no research file | None | 1–2 sessions |
| `G60` Repo tracker | 086 | Tracked-repo list plus a cross-repo awareness agent | Standalone greenfield; may split into two ideas on contact | None | 2–3 phases |
| `G61` Platform evaluation | 122 | Non-web rebuild language/platform comparison | Deliberately standalone and future-only; a document, not code | None | 1 session |
| `G62` Websockets education | 140 | Owner-education deep dive using this repository's terminal stack | Produces no product code; uses `G55` as a worked example | None | 1 session |
| `G63` Demo rehearsal placeholders | 088, 090, 103 | Self-declared timing artifacts from dry runs, carrying no product content | Nominated for decline by **all four** analysts | None | 0 |

---

## Unbatched

Two ideas, reported as the quality signal this section is for. **Two of 129 is a low residual** —
the partition found a defensible home for 98.4% of the corpus, and neither exception is a failure
to place so much as a case where placing would misstate what the idea is.

- **`000125` — Holistic triage of the accumulated idea batch.** This is the instruction this
  document carries out, not a candidate for a future plan. It is discharged by this document's
  existence and should be annotated or promoted with a pointer to it. R2, R3 and R4 reached this
  independently, the control among them.
- **`000089` — Demo fallback seed.** Already implemented and deliberately kept per PLAN-021's
  afterlife decision; `tools/demo_reset.py prepare` checks folded state before appending, so it
  never duplicates. Not a decline — it is neither dead nor unwanted — and not a build candidate,
  because nothing is missing. It simply has no plan-shaped home.

---

## Decline candidates

Nominations only. **Nothing was written to `_data/ideas.jsonl` for any of these** — no status
event, no annotation, no link. The owner rules on each individually.

Nothing has been filtered. Nominations against the 23 demo-kit ideas are not listed, because those
ideas left the corpus at GATE 2 and are governed by `REQ-008`'s own already-completed triage; every
analyst's kit nominations survive in the four reports under `_working/idea-corpus/`.

**On the tiers.** `PROMPT-025` decision 11 specifies all-four / majority / single. With four
analysts, two nominations is neither a majority nor a single voice, so each row carries its exact
count rather than being rounded into a tier that would misstate its confidence.

### Tier 1 — nominated by all four (4/4)

The only tier where the control agrees with the finding-readers, and therefore the only one whose
agreement cannot be inherited framing.

| Idea | Reason given |
|---|---|
| `000088` | Rehearsal placeholder; its own body says "not a real audience suggestion", recorded only to time a step |
| `000090` | Duplicate-in-kind rehearsal placeholder from a second dry run |
| `000103` | Its own body: "should be discarded during a later triage pass rather than promoted" |

### Tier 2 — nominated by two of four (2/4)

| Idea | Nominated by | Reason given | Counter-argument on record |
|---|---|---|---|
| `000005` | R1, R3 | GitNexus's backend (KuzuDB) was acquired and archived in October 2025; the specific tool proposal is dead | Both note the underlying need may survive via a successor; R3 calls the decline **partial** |
| `000099` | R3, R4 | Superseded — its purpose completed when the coordinator's finding root-caused the failure | **Now stronger than either knew:** verified resolved. R4 additionally nominates `000129` |
| `000102` | R1, R2 | Rehearsal timing artifact | R1 concedes the underlying "last refreshed" badge "has mild merit"; R4 treats it as a real viewer feature, and this document places it in `G48` on that basis |

### Tier 3 — nominated by one of four (1/4)

R4, the control, is the sole nominator of six of these. That is the expected shape of the
findings ablation and is **not** evidence against them: R4 reasoned from idea bodies rather than
from triage verdicts, and in two verified cases it was right where all three finding-readers were
wrong.

| Idea | By | Reason given |
|---|---|---|
| `000098` | R4 | **Verified resolved** — schema and 21 passing tests already exist |
| `000129` | R4 | **Verified resolved** — 46 tests pass; the full suite is green |
| `000020` | R4 | Decline *in favour of* `000128` (`G21`), which solves the same coordinator-hand-carrying pain by extending `_tmpagent/` — no MCP server, no vector DB, no librarian role. Revisit only if the light version proves insufficient |
| `000030` | R4 | Decline-until-evidence: "least urgent" of its trio by its own text, and both prerequisites (`028`, `029`) are unbuilt |
| `000033` | R4 | Decline-until-evidence: only one idea in the real log has more than a `created` event, so there is nothing to query |
| `000034` | R4 | Decline-until-evidence: portfolio signals are unbuilt and `000022` records zero people/commitments records to simulate against |
| `000036` | R4 | Decline-until-evidence: the most downstream idea in the corpus; needs recommendations and outcomes to accumulate first |
| `000063` | R3 | **Partial** — the forking half is superseded by `000064`/`000065` plus `component_of`; only the abstraction question remains live |
| `000070` | R2 | Realized by the live-demo pack (REQ-006, PLAN-021, ADR-013, `phase-demo-01`–`06`); mark delivered rather than carry forward |
| `000097` | R2 | Capture half delivered by `log-anti-patterns`; scope otherwise subsumed by `000138` |
| `000015`, `000016`, `000017` | R1 | Captured together, never resumed across ~130 subsequent ideas, adjacent to but outside this system's purpose |

**Explicitly not nominated, on the record.** R1 declined to nominate `000033`, `000034` and
`000036` — "genuinely gated on prerequisites, not dead" — and `000122` ("deliberately deferred,
not stale"). R1 and R2 both refused to nominate `000089`. These refusals are carried because the
owner rules on each candidate individually and a refusal is evidence too.

---

## Completeness arithmetic

Verified mechanically by set comparison against the corpus id list, not by hand count.

```
corpus (post-ruling)        : 129
placed in fine groups       : 127 across 63 groups
unbatched                   : 2
total accounted             : 129
duplicates                  : none
in corpus, never placed     : none
placed but not in corpus    : none
balances                    : True
groups not in any programme : none
programmes                  : 12
```

| Programme | Groups | Ideas |
|---|---|---|
| P1 Idea graph and lifecycle | 4 | 19 |
| P2 Document and backlog governance | 4 | 7 |
| P3 Concurrency, git safety and enforcement | 5 | 10 |
| P4 Agent engineering and delegation | 10 | 18 |
| P5 Autonomous agent operations | 1 | 5 |
| P6 Retrieval and knowledge infrastructure | 6 | 10 |
| P7 Blocked downstream projections | 2 | 4 |
| P8 Schema consistency and testing | 4 | 8 |
| P9 HTML generation and design system | 3 | 6 |
| P10 Workbench architecture and quality | 8 | 13 |
| P11 Workbench features and defects | 9 | 16 |
| P12 Standalone explorations and housekeeping | 7 | 11 |
| **Total** | **63** | **127** |

Excluded by ruling and not counted above: `000171`–`000193` (23), governed by `REQ-008`,
`PLAN-024` and `phase-kit-01`–`08`.

### Residual — placements made with lower confidence

Flagged so a reader who disagrees knows where to look first.

- `000009` (`G23`) — carries no recorded links to anything; filed by subject alone.
- `000054` (`G57`) — an umbrella with no members; its own scope is unscoped.
- `000081` (`G30`) — moved against three analysts on a deliverable-surface argument; the taxonomy
  reading is defensible.
- `000102` (`G48`) — content and provenance point to different homes; content was chosen.
- `000144` (`G44`) — genuinely two halves in one idea; kept whole.
- `000013` (`G20`) — placed as subsumed, not as distinct content.
- `000069` (`G16`) — produces a decision record, not code; not really phase-shaped.
- `000087` (`G51`) — scope ambiguous between a demo bolt-on and a platform feature, by its own text.
- `000106` (`G35`) — its stated model sits in testing, its subject in the overview generator.

---

## What the owner is being asked to do

1. **Accept or correct the partition** — both levels.
2. **Rule on every decline candidate individually**, across all three tiers.
3. Note that `000125` is promoted only when this document is **approved**, not when it is written.
