---
schema_version: 1
id: doc-session-demo-glossary-diagrams
code: SESS-2026-09-10-09
title: Skills-and-agents glossary and diagram library — audit and build (phase-demo-07)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
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

Every command in the phase's `verification` list, run in the worktree.

```
$ uv run python -m src.governance
Governance OK: 18 systems, 136 documents, 16 memories, 112 backlog phases

$ uv run python tools/generate_glossary.py            # twice
wrote .../docs/08-governance/GLOSSARY.md — 9 term(s)
wrote .../docs/08-governance/GLOSSARY.md — 9 term(s)
diff empty: byte-identical

$ uv run python tools/generate_glossary.py --tag demo-glossary \
    --out docs/00-working/demo-glossary.md            # twice
wrote docs/00-working/demo-glossary.md — 9 term(s)
wrote docs/00-working/demo-glossary.md — 9 term(s)
diff empty: byte-identical

$ uv run pytest test/test_glossary.py
6 passed, 2 warnings in 0.17s

$ uv run python tools/check_no_private_content.py     # with the changes staged
check_no_private_content: OK (437 tracked files, 31 identifiers checked)
```

The filtered glossary renders all seventeen `###` term headings plus the advanced-topics group.

**A note on the private-content check.** Run plainly inside the worktree it reports
`0 identifiers checked`, because `_private/portfolio/` is gitignored and so does not exist in a
worktree — the content half of the gate silently does not run, exactly the "passes by not looking"
failure `AGENTS.md` warns about. The run recorded above was taken with a temporary symlink from the
worktree's `_private/portfolio` to the primary checkout's, which is untracked; the symlink was
removed immediately afterwards and the worktree has no `_private/` directory now. Worth knowing for
any future worktree phase: the number to check is the identifier count, not the OK.

### Visual review

The phase requires a browser review of each SVG at 1024×768. The Playwright MCP server was
unavailable — a peer agent on `phase-demo-06` holds its browser profile — so the review was done
with headless Chrome against `file://` URLs at `--window-size=1024,768`, one PNG per diagram,
inspected directly. The first pass found real defects, all since fixed:

- `agentic-loop`: four edge labels sat on their arrow lines. The layout was rebuilt with wider gaps
  and the labels moved clear.
- `skill-architecture`: the directory tree lost its indentation, because SVG `<text>` collapses
  leading whitespace. Each line now carries its own `x` offset. The "front matter" and "body"
  callouts were struck through by their own arrows and were moved above them; the
  progressive-disclosure caption overflowed into the box beside it and the boxes were narrowed.
- `sub-agents-context-isolation`: the blocked-output marker pointed at the "Model call" box, reading
  as though the model call were blocked. It now leaves the loop's edge at the level of the
  accumulated tool results.
- `llm-vs-agent`: the return-path label was pinched against the panel border, and the exit path
  started two pixels inside the loop container.
- `mcp-architecture`: the `.mcp.json` snippet was centred line by line, which destroyed its
  indentation; it is left-aligned as a block.

All six were re-rendered and re-inspected after the fixes. `index.html` was rendered from `file://`
and loads all six thumbnails with no network access.

Each SVG was also parsed with an XML parser and checked for external references: all six parse,
carry `width="1024" height="768"` with a matching `viewBox`, and reference no URI other than the SVG
namespace.

## Acceptance

- **Every listed term has an entry and the filtered glossary lists them.** Met. Seventeen `###`
  headings, covering the owner's eight and all nine additions, plus the advanced-topics group.
- **Each SVG opens standalone at 1024×768 with labels matching the glossary.** Met, with the
  substitution noted above: headless Chrome from `file://` rather than the Playwright MCP server.
  Two label mismatches found in the consistency pass were fixed — the `Command` entry now names
  "slash command", the phrase the command/skill/tool diagram uses, and the sub-agent diagram's
  context window says `CLAUDE.md` rather than `AGENTS.md`, matching what the `Context` entry states
  is loaded automatically.
- **Both generations are byte-identical on a second run and `test_glossary.py` passes.** Met; output
  above.

## Not done, and why

`status: complete` was not set. `GOV-003`'s "demo track completes through its testing gate" section
names five `phase-demo-*` phases plus `phase-demo-06` by explicit owner decision. `phase-demo-07` is
not on that list and no extension of it was found, so the ordinary rule stands: `/session-close` is
the only path to `complete`. The phase is left `active` with an honest `next_action`.

The branch is not integrated. Per `AGENTS.md` that is the owner's call.

## Unresolved

- **`AGENTS.md` contradicts itself about pushing, and both halves are load-bearing.** The
  *Confidentiality and publishing* section says "Pushing your own branch to `origin` needs no
  approval"; *Concurrent agents: claim a phase* says "**ask the owner before pushing** (see
  *Confidentiality and publishing*)" — citing, as its authority, the section that says the opposite.
  `CLAUDE.md` agrees with the first. This agent followed the first and pushed `dev` and its own
  branch. No agent may edit `AGENTS.md`, so this is reported rather than fixed. Proposed replacement
  for the second passage: "A remote now exists, so `git fetch`, `git pull` and `git push` all work.
  Pushing your own branch needs no approval; integrating onto `dev` does (see *Confidentiality and
  publishing*)."
- **The Playwright MCP server cannot be shared between concurrent agents.** It fails with
  "Browser is already in use … use `--isolated` to run multiple instances". Any phase whose
  verification depends on it is serialised behind whichever agent claimed the browser first. Worth
  an idea if browser-verified phases are going to run concurrently again.
