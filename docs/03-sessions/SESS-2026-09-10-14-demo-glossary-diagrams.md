---
schema_version: 1
id: doc-session-demo-glossary-diagrams
code: SESS-2026-09-10-14
title: Skills-and-agents glossary and diagram library — audit and build (phase-demo-07)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-14'
systems: [sys-brain, sys-portfolio]
depends_on: [doc-live-demo, doc-live-demo-requirements, doc-prompt-demo-glossary-diagram-audit]
---

# Skills-and-agents glossary and diagram library — audit and build (phase-demo-07)

## Phase

`phase-demo-07` — Skills-and-agents glossary and diagram library, covering R13 in
`REQ-006`. Claimed by `agent-demo-glossary`, worked on `agent/phase-demo-07`.

Run under [PROMPT-019](../02-prompts/PROMPT-019-demo-glossary-diagram-audit.md), which asks a fresh
agent to audit the phase as drafted, revise what the audit finds wrong, then build it. The audit
found six problems; all six were fixed on `dev` before the claim.

## What the audit found

### 1. `sys-demo-overview` was the wrong lock, and would have blocked `phase-demo-05`

The phase touches `brain/`, `docs/00-working/` and `docs/07-architecture/`. None of that is the
deterministic overview generation `sys-demo-overview` describes — that system is the scripts, the
skill and the templates that emit the overview page, and its only declared path is `PLAN-021`.
Meanwhile `phase-demo-05` genuinely declares `sys-demo-overview` and sits second in `next_up`.
`collisions()` in `src/governance/backlog.py` compares declared systems, so an active
`phase-demo-07` would have shown as a conflict against the readiness phase the owner is about to
claim, for no work either phase shares.

Fixed: systems are now `sys-brain` and `sys-portfolio`.

### 2. The phase would have failed its own first verification command

`demo-glossary` is not a tag in `_data/tags.json`, and `src/governance/__main__.py` errors on any
tag in a memory's front matter that is absent from that taxonomy. `uv run python -m src.governance`
is the first line of the phase's `verification` list, so the phase as drafted could not pass it.

Fixed: registering the tag is now in scope, `_data/tags.json` is a deliverable, and `sys-portfolio`
— the system that owns it — is the second lock. The tag is `category: context`, because it selects a
view for one training session rather than naming a subject area.

The alternative considered and rejected was filtering by `--system` instead of `--tag`, which needs
no taxonomy change but would have made the memory declare `systems: [sys-demo-overview]` — claiming
a glossary of AI vocabulary belongs to overview generation, which is false, and re-introducing
finding 1.

### 3. The committed `GLOSSARY.md` goes stale and its test fails

`generate_glossary.load_concepts()` collects every `type: concept` memory regardless of tag. Adding
one therefore changes the committed `docs/08-governance/GLOSSARY.md`, and
`test/test_glossary.py::test_the_committed_glossary_matches_regenerated_output` asserts the file
equals regenerated output.
Neither the scope, the deliverables nor the verification list mentioned it.

Fixed: regenerating the unfiltered glossary is in scope, `docs/08-governance/GLOSSARY.md` is a
deliverable, and `uv run pytest test/test_glossary.py` is in the verification list.

### 4. `docs/07-architecture/diagrams/demo/README.md` would have failed the governance scan

`markdown_paths()` walks `docs/` recursively and exempts a fixed set of paths. That set contains
`docs/07-architecture/README.md` itself, not its subdirectories, so a new README under
`diagrams/demo/` would have needed governed front matter and an allocated code — a governed document
whose filename does not follow `<code>-<slug>.md`.

Fixed: the index is `index.html`, a contact sheet linking each SVG with a one-line caption. It is
also the better deliverable: R13 requires the library be viewable in a browser with no dev server
running, and an HTML page opened from the filesystem is what the presenter actually wants. A pointer
line was added to `docs/07-architecture/README.md`, which is exempt.

### 5. The diagram set had no diagram for `Sub-agent`

The five diagrams covered LLM, Agent, Skill, Tool, MCP, Context and Command. Nothing depicted a
sub-agent, though the owner listed it as a core term and this repository holds eleven agent
definitions under `.claude/agents/` plus the `demo-orch-*`/`demo-creator-*`/`demo-validator-*` split
— the richest local material available for the session.

Fixed: a sixth diagram, sub-agents and context isolation, whose point is that the sub-agent's tool
output never crosses back and only its report does. `R13`'s enumeration in `REQ-006` was updated to
match. `PLAN-021` needed no edit — its `phase-demo-07` bullet says "a standalone SVG diagram
library" without enumerating, so it stayed accurate, which also avoided touching a file owned by
`sys-demo-stage` while a peer holds that lock.

### 6. The term list, finalized

The prompt gave this agent authority to settle it. All eight core terms and all seven candidate
additions were kept, and two terms were added:

- **Agentic loop.** The acceptance condition is that each diagram's labels match the corresponding
  glossary entry's terminology exactly. A diagram named "the agentic loop" needs an entry whose
  terminology it can match.
- **Progressive disclosure.** The front-matter-always, body-on-demand mechanism is what makes many
  skills affordable, and it is the single most useful thing to know about skills. Nothing else in
  the candidate list stated it.

Nothing was trimmed. `Token` was the closest call and was kept because it is what makes the context
limit and the cost legible; it is written to pair with `Context` rather than to stand alone.

Seventeen terms in total, plus one-line entries for the four advanced topics named out of scope for
depth (Hooks, Agent permissions, Observability, Agent SDK).

## What was built

- `brain/concepts/terms-skills-and-agents-demo.md` — one grouped concept memory in the
  `terms-systems-vocabulary.md` style, tagged `demo-glossary`. Every term is defined against what
  the repository actually contains — the three skills under `.claude/skills/`, the eleven agent
  definitions and `demo-adversary`'s tool list, the four commands, the `permissions.deny` list in
  `.claude/settings.json`, and the single `playwright` server in `.mcp.json` — so a claim made in
  the session can be checked against a file on screen.
- `_data/tags.json` — the `demo-glossary` tag.
- `docs/08-governance/GLOSSARY.md` and `docs/00-working/demo-glossary.md` — both regenerated.
- `docs/07-architecture/diagrams/demo/` — six SVGs and `index.html`.
- `docs/07-architecture/README.md` — a pointer to the library, recording why these are SVG rather
  than Mermaid: the README states a Mermaid preference because Mermaid renders natively on GitHub,
  which is exactly what a diagram opened from the filesystem at a projector size cannot rely on.

## Verification

Every command in the phase's `verification` list, re-run in the worktree on 2026-09-14 after
rebasing onto `dev`. These figures supersede the 2026-09-10 run: `dev` moved 484 commits in between,
so the governance totals and the tracked-file count both changed.

```
$ uv run python -m src.governance
Governance OK: 20 systems, 212 documents, 24 memories, 148 backlog phases

$ uv run python tools/generate_glossary.py            # twice
wrote .../docs/08-governance/GLOSSARY.md — 9 term(s)
wrote .../docs/08-governance/GLOSSARY.md — 9 term(s)
diff empty: byte-identical; git diff against the committed file also empty

$ uv run python tools/generate_glossary.py --tag demo-glossary \
    --out docs/00-working/demo-glossary.md            # twice
wrote docs/00-working/demo-glossary.md — 9 term(s)
wrote docs/00-working/demo-glossary.md — 9 term(s)
diff empty: byte-identical; git diff against the committed file also empty

$ uv run pytest test/test_glossary.py
6 passed, 2 warnings

$ uv run pytest                                        # full suite, post-rebase
580 passed, 2 warnings
```

The filtered glossary renders seventeen `###` term headings plus an eighteenth heading for the
advanced-topics group — eighteen `###` in total. Recorded precisely because "seventeen headings" and
"eighteen headings" are both true of different things and the earlier phrasing invited the wrong count.

**The tool's "9 term(s)" is a mislabel, not a term count.** `tools/generate_glossary.py:119` prints
`len(entries)`, the number of concept-memory files loaded, and the tag filter is applied afterwards
inside `render()`. So the line reads `9 term(s)` identically for the unfiltered glossary (61 `###`)
and the filtered one (18 `###`). Cosmetic, in a tool this phase did not author, but it makes the
tool's own output useless as evidence for the term-count acceptance condition — the headings were
counted directly instead.

**The private-content check.** Run plainly inside a worktree it reports `0 identifiers checked`,
because `_private/portfolio/` is gitignored and so does not exist there — the content half of the
gate silently does not run, exactly the "passes by not looking" failure `AGENTS.md` warns about. It
is visible in this session's own commit hook output: `OK (583 tracked files, 0 identifiers checked)`.
That is not a pass.

A real run was taken instead, deriving the identifier list from the primary checkout's
`_private/portfolio/` and scanning the branch's tracked files by path, with the identifiers held in
memory and never written anywhere:

```
identifiers derived: 31
branch tracked files: 591
files content-scanned: 577
VIOLATIONS: 0
```

The scan refuses to report a pass if the derived identifier list is empty, so a vacuous run fails
rather than looking green. The number to trust is the identifier count, never the `OK`.

### Visual review — independently repeated

The phase requires a browser review of each SVG at 1024×768. The 2026-09-10 review was the original
author's own, and its five fixes were self-reported. This session repeated it independently.

A `demo-validator-web` sub-agent was dispatched first and returned **blocked, not verified**: the
Playwright MCP server binds one shared Chrome profile
(`~/.cache/ms-playwright-mcp/mcp-chrome-27f151d`), held by a live peer process, and every browser
call failed with "Browser is already in use … use `--isolated`". It took no screenshot and reached no
verdict. Killing a peer's browser was not an acceptable way to obtain one.

The review was then done directly with headless Chrome against `file://` URLs, using a throwaway
`--user-data-dir` in a scratch directory so the peer's profile was untouched. All six SVGs and
`index.html` were rendered at `--window-size=1024,768` and each image was inspected:

- `llm-vs-agent` — clean. No overlap, nothing clipped, the rotated "result appended" label clears
  the loop border.
- `skill-architecture` — clean. The directory tree keeps its indentation and the "front matter" and
  "body" callouts sit clear of their arrows.
- `agentic-loop` — clean. All four edge labels sit clear of their arrow lines.
- `sub-agents-context-isolation` — clean. The blocked-output marker meets the loop edge at the
  accumulated-results level, not the model call.
- `mcp-architecture` — clean. The `.mcp.json` snippet is left-aligned and keeps its indentation.
- `command-skill-tool` — clean. Three columns, no text clipped at the column edges.

No text overlap, no clipping at the viewBox boundary, and adequate contrast in all six. `index.html`
was additionally rendered at full page height: all six diagrams render as live frames with their
captions, none blank or broken, and the page is readable at 1024 wide.

This corroborates the earlier self-report on the outcome. It does not independently confirm the five
defects listed above ever existed — that history is still the original author's account, and only
the fixed state was observable here.

## Acceptance

- **Every listed term has an entry and the filtered glossary lists them.** Met. Seventeen `###` term
  headings covering the owner's eight and all nine audit additions, plus the advanced-topics group;
  counted directly from the file, not from the tool's mislabelled output.
- **Each SVG opens standalone at 1024×768 with labels matching the glossary.** Met, and now
  independently corroborated rather than self-reported — see the repeated visual review above. The
  substitution stands: headless Chrome from `file://` rather than the Playwright MCP server, which a
  peer holds. Diagram labels were checked against the glossary's heading list and match.
- **Both generations are byte-identical on a second run and `test_glossary.py` passes.** Met; output
  above, and both files also show no drift from their committed state.

**All three conditions are Met, and the phase still does not close.** The independent review raised
an unresolved discrepancy against the phase's *scope* — the entries misstate the counts they claim
to take from `.claude/` — and `/session-close` requires both a clean acceptance pass *and* a review
that corroborates it with nothing unresolved. The second half does not hold. That the acceptance
list can pass over a glossary which misstates the repository is itself the finding: condition 2
tests the SVGs against the glossary, and nothing tests the glossary against reality.

## Review

Independent completion-gate review by a fresh `demo-adversary` sub-agent on 2026-09-14, given the
scope, acceptance and verification lists, the range `fa60fc4..7786daa`, and eight named claims from
this record to attack. It shared none of the closing session's context. Its findings, recorded as
delivered:

**Acceptance condition 1 — Met.** "Counted directly (not via the tool's mislabeled output):
`docs/00-working/demo-glossary.md` has 18 `### ` headings — the 17 scope terms verified present by
exact string match … plus the 'Advanced topics' group, which itself names all four out-of-scope
topics. Confirmed with a script diff against the scope list — zero missing."

**Acceptance condition 2 — Met, narrowly.** "All six declare `width="1024" height="768"
viewBox="0 0 1024 768"`, no `http(s)://`, no `xlink:href`, no `@import`, no external `url()` (only
internal `url(#arrow)` marker refs), and only generic/websafe font stacks … Labels in the SVGs do
match the glossary's terminology word-for-word — **but only because both are wrong in the same way**
… The condition as literally worded (SVG-to-glossary consistency) passes; it does not test
SVG/glossary-to-reality accuracy, which is where this phase actually fails."

**Acceptance condition 3 — Met.** Both generations byte-identical on reruns, `test_glossary.py`
6 passed, full suite 580 passed.

**BLOCKER, as the reviewer stated it.** "The glossary's and diagrams' core claim ('defined against
this repository's actual .claude/ and .mcp.json conventions') is false in three places":

- `brain/concepts/terms-skills-and-agents-demo.md:103` says "This repository has three under
  `.claude/skills/` — `orient`, `checkpoint` and `d-system-overview`." Actual: **four**, missing
  `log-anti-patterns`.
- `:86` says "`.claude/agents/` holds eleven definitions." Actual: **twelve**, missing
  `partition-adversary.md`.
- `:119` says "`/backlog`, `/idea`, `/idea-triage` and `/session-close` are the four here." Actual:
  **six**, missing `/session-start` and `/resume-lit-review`. The reviewer's note on why this one
  matters most: "`/session-start` is arguably the single most load-bearing command in the repository
  … and it is entirely absent from a glossary whose stated purpose is to teach exactly this
  vocabulary to a live audience by pointing at real files."
- `skill-architecture.svg` and `command-skill-tool.svg` bake the same wrong counts into their
  rendered text.
- "A presenter who opens `.claude/commands/` on stage during this demo (the exact scenario the
  design is built around) will count six files against a slide/glossary claiming four."

**Minor.** `aria-label` differs from visible title text in two diagrams: `llm-vs-agent.svg`
("LLM versus agent" vs "LLM vs agent") and `command-skill-tool.svg` ("Command, skill and tool" vs
"Command, skill, tool"). Screen-reader only; invisible in the rendered image.

**No discrepancy found** on claims (a), (d), (f), (g) and (h), on the `_data/tags.json` addition, or
on scope containment — the diff touches only declared deliverables plus `backlog.yaml` and
`catalog.md`, and `b5b91b1` disturbs no deliverable.

### One correction to the review

The reviewer wrote that the counts were "false from the moment this phase started, not from later
drift." That is wrong, and the distinction matters for where the process failed. At `86a4f68`, the
branch's original base on 2026-09-10, the tree genuinely held **3 skills, 11 agents and 4 commands** —
exactly what the entries claim. The four additions landed on `dev` afterwards:
`/session-start` (`82b1abd`, 09-12), `/resume-lit-review` (`33a2972`, 09-12),
`partition-adversary.md` (`3b548a6`, 09-12), `log-anti-patterns` (`93802e7`, 09-13).

The entries were accurate when written and were falsified by the 484 commits that landed while the
branch sat unmerged. Everything else the reviewer found is confirmed.

## Decisions

- **The phase does not take `GOV-003`'s demo-track completion exception.** Owner decision,
  2026-09-14. That exception names `phase-demo-01` through `phase-demo-06`; this phase is not on the
  list, so the full `/session-close` review applies. This was the open question that left the phase
  active on 2026-09-10.
- **The session-code collision was resolved by renumbering this record, not dev's.** `AGENTS.md`
  gives the rule: whoever integrates second renumbers. `--next-code session` is the wrong tool for
  it — it returns today's date, and `src/governance/codes.py` requires the code's date to equal
  `created`.
- **`_public/skills-and-agents-lexicon.html` was left untouched.** Owner decision, 2026-09-14. It
  carries a frozen base64 copy of these diagrams and will go stale silently, but editing it would
  widen this phase's declared deliverables.
- **The `backlog.yaml` rebase conflict was resolved by keeping dev verbatim and proving it.** The
  ~2,200-line conflict block was edit-distance noise. Resolution was verified by diffing the result
  against `dev`: all 148 phase ids present, the only content change this phase's own two fields.
  A peer session had independently warned that a prior commit silently reverted four phases through
  this file; its regression check was run and came back clean.
- **The private-content gate was run for real rather than deferred.** A worktree run reports
  `0 identifiers checked` and is not a pass. The identifier list was derived from the primary
  checkout and held in memory only.
- **The phase was not marked complete.** See below.

## Corrections

- **The brief this session started from asserted that the glossary entries "were fact-checked
  against the real `.claude/` and `.mcp.json` counts and match."** That was true on 2026-09-10 and
  false by the time of the rebase. It was carried forward without re-checking, and the rebase — the
  one step whose whole purpose is reconciling the branch with four days of `dev` — did not re-verify
  the facts the entries assert about `dev`. The independent review caught it. This is the substantive
  failure of the session.
- **"Seventeen `###` headings" was an imprecise count** repeated from the brief. There are eighteen:
  seventeen terms plus the advanced-topics group. Corrected in `## Verification`.
- **The `demo-validator-web` dispatch was reported as producing a verdict it did not produce.** It
  returned blocked — the shared Playwright profile was held by a peer — and took no screenshot. The
  visual review was redone with headless Chrome on a private profile instead.

## Left undone

The phase stays `active`. Three things remain, and none is large:

1. **Fix the three stale counts** in `brain/concepts/terms-skills-and-agents-demo.md` — four skills,
   twelve agents, six commands — naming `log-anti-patterns`, `partition-adversary`, `/session-start`
   and `/resume-lit-review`. Then regenerate both glossaries.
2. **Update the two diagrams that bake the counts in**, `skill-architecture.svg` and
   `command-skill-tool.svg`, and re-render both at 1024×768 to confirm the added text does not break
   the layout.
3. **Optionally align the two `aria-label` strings** with their visible titles.

A fourth item is governance, not this phase: **the acceptance conditions do not test what the scope
requires.** All three conditions pass on a glossary that misstates the repository, because condition
2 tests SVG-against-glossary consistency and nothing tests glossary-against-reality. A phase whose
stated purpose is "defined against what this repository actually contains" needs an acceptance
condition that reruns those counts. Worth an idea or a check in `test_glossary.py`; recording it here
so it is not lost with this session.

## Not done, and why

`status: complete` was not set, and this session did not set it either. `GOV-003`'s "demo track
completes through its testing gate" section names five `phase-demo-*` phases plus `phase-demo-06` by
explicit owner decision; `phase-demo-07` is not on that list. **The owner resolved this on
2026-09-14: `phase-demo-07` does not take the demo-track exception and requires the full
`/session-close` review.** That is owner-only, so the phase stays `active`.

The branch is not integrated. Per `AGENTS.md` that is the owner's call, and it has not been asked
for yet as of this checkpoint.

## Backlog

- `status: active` — **not** advanced to `complete`. The owner invoked `/session-close`, its step 6
  was reached, and completion was withheld because the independent review raised an unresolved
  discrepancy. This is the outcome that step is written to allow, not a failure to finish.
- `session: doc-session-demo-glossary-diagrams` — unchanged; the id is permanent and survived the
  renumber.
- `completion_evidence` / `result` — not written. The work is merged into `dev` but is not correct
  yet, and evidence fields asserting otherwise would be false.
- `next_action` — rewritten at close to name the three stale counts, the two diagrams that bake them
  in, and the acceptance-vs-scope gap.
- `next_up` — not pruned. `phase-demo-07` is not on it, and nothing became `complete` this run.

## Unresolved

- **A session-code collision was resolved by renumbering this record.** `SESS-2026-09-10-09` was
  taken on `dev` by `SESS-2026-09-10-09-workbench-planning.md` while this branch sat unmerged for
  four days. Per `AGENTS.md`, the agent integrating second renumbers, so this record moved to
  `SESS-2026-09-10-14` — `-01` through `-13` are all held for that date. `created` stays
  `2026-09-10` because `src/governance/codes.py` requires the code's date to equal `created`, and
  the date is honest. The `id` is unchanged. `--next-code session` is the wrong tool here: it
  returns today's date, which that same rule would then reject.
- **`_public/skills-and-agents-lexicon.html` embeds a frozen copy of these diagrams.** It landed on
  `dev` in `b9433d3`, built from this phase's content but never named in this phase's scope, and it
  carries the diagrams as base64. If the SVGs change it goes stale silently and no test catches it.
  The owner's decision on 2026-09-14 was to leave it alone and record the risk: editing it would
  widen this phase's declared deliverables. Flagged, not fixed.
- **`AGENTS.md` contradicts itself about pushing, and both halves are load-bearing.** The
  *Confidentiality and publishing* section says "Pushing your own branch to `origin` needs no
  approval"; *Concurrent agents: claim a phase* cites that same section as authority for asking
  first. `CLAUDE.md` agrees with the first. No agent may edit `AGENTS.md`, so this is reported
  rather than fixed. Proposed replacement for the second passage: "A remote now exists, so
  `git fetch`, `git pull` and `git push` all work. Pushing your own branch needs no approval;
  integrating onto `dev` does (see *Confidentiality and publishing*)."
- **The Playwright MCP server cannot be shared between concurrent agents.** It fails with "Browser
  is already in use … use `--isolated`", and it blocked a validator dispatch again this session.
  Any phase whose verification depends on it is serialised behind whichever agent claimed the
  browser first. The workaround that worked both times is headless Chrome with a private
  `--user-data-dir`.
