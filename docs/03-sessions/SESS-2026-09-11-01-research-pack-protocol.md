---
schema_version: 1
id: doc-session-research-pack-protocol
code: SESS-2026-09-11-01
title: Research pack protocol (GOV-009) and its atlas showcase page
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-governance, sys-html]
depends_on: []
---

# Research pack protocol (GOV-009) and its atlas showcase page

## Phase

**None.** No phase was claimed for this session, and none reached any status as a result of it.

The owner opened the session by asking for a protocol as rigorous as the prompt-pack planning
protocol (`GOV-008`), targeted at literature review and research work in `research/`, then asked
for a showcase page in the atlas template family. Both were produced as direct owner-directed
work on `dev` — documentation and a static page, no `src/`/`ts/`/`test/` changes — without a
backlog claim, the variant `brain/procedures/session-close-with-no-active-phase.md` names (and
the same shape as `SESS-2026-09-10-10`). Active claims throughout, untouched: `phase-demo-07`
(`agent-demo-glossary`) and `phase-wb-03` (`agent-demo-stage`).

This session's commits are exactly two, adjacent on `dev`: `7a05471` (the protocol) and
`0b3f899` (the showcase page), plus the close commit carrying this record and a post-review
fix. The review examined those two commits' own diffs (the reviewer found that `8a62993`,
initially offered as a range base, is a sibling-branch tip rather than an ancestor, so
per-commit diffs — or base `b50d6a6` — are the honest measure). Everything else between
`b50d6a6` and `HEAD` is concurrent peer work.

## Verification

No phase means no declared `verification` list; these are the checks the session's own claims
rest on, rerun at close.

- `uv run python -m src.governance` —
  `Governance OK: 18 systems, 159 documents, 16 memories, 119 backlog phases`
- CSS family parity: the inline `<style>` block of `_public/research-protocol.html` diffed
  against the inline block of `_public/prompt-pack-protocol.html` (the family reference
  rendering) — byte-identical, `CSS-MATCHES-ORIGIN`.
- Browser verification (behavioural, Playwright against a local server, run before `0b3f899`):
  nav builds with all 7 sections and scroll highlighting; masthead stats computed from the
  data arrays; 9 artifact cards and 3 content-doc cards rendered from arrays; both diagrams
  focusable (hovering stage 5 lights s4/s5/s6 and 2 edges); collapse-all 0 open, expand-all 7
  open; no horizontal scroll; only console message a harmless favicon 404. Two SVG text
  overflows found by screenshot in the passes diagram and fixed before commit.
- Post-review edit to the page (the rule-group undercount, see `## Corrections`) re-checked
  statically — the shared Playwright browser was held by a peer session at close: rules
  section carries 7 cards, `RULES` array 7 entries (stats render 8/4/9/7/4 by the
  already-browser-proven `initStats`), summary reads "Seven rule groups", tick list trimmed
  to 3 non-duplicating bullets.
- `uv run pytest` — `3 failed, 546 passed, 2 warnings`. The three failures are
  `test/test_demo_terminal.py` PTY tests (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`). What is established:
  this session's range touches no Python or test file, so they are unrelated to its work.
  Their classification is contested between peer accounts: `SESS-2026-09-10-11` and
  `SESS-2026-09-10-13` recorded them as the recurrent host-wide pyenv-shim environmental
  failure, while `000099` (red demo-terminal PTY tests on the trunk), recorded 2026-09-11 by
  another session, reproduces them deterministically on `origin/dev` and suspects — without
  verifying — the session-registry commit `f0801af`. This record asserts neither account,
  only the non-attribution to this session's diff.

## Acceptance

Not applicable — no phase, so no `acceptance` list. The session's own claims and the
independent review's verdicts on them are in `## Review` below.

## Backlog

No backlog entry was created, claimed, edited or completed by this session. `next_up` untouched.

## Unresolved

- The three PTY test failures remain red; they belong to the demo terminal work
  (`sys-demo-stage`, under `phase-wb-03`'s active claim) and are tracked in the peer session
  records and in `000099` (red demo-terminal PTY tests on the trunk), not here.
- At close, the working tree carried a peer conversation's uncommitted idea-system changes
  (`_data/ideas.jsonl`, `docs/00-working/ideas.md`: the `000094` resolution annotation and
  `000099`'s creation, authored by `agent-readme-audit` shortly after midnight). This
  session's close commit deliberately excludes them — committing another session's in-flight
  work under this session's message would misattribute it. They are left staged/unstaged
  exactly as found, for their own session or the owner to commit.

## Review

Independent sub-agent review (fresh non-fork agent, given the range `8a62993..0b3f899`, both
governed commits' claims, and instructions to rerun the checks itself):

> **Range integrity (preamble check).** `git log --oneline 8a62993..0b3f899` contains exactly
> the two commits `7a05471` and `0b3f899` — CONFIRMED. However, `git diff 8a62993..0b3f899
> --stat` shows 18 files, not 4, because `8a62993` ("Close phase-port-01") is **not an
> ancestor** of `0b3f899` — it is the tip of a sibling branch off `b50d6a6` (later merged as
> PR #2). The two-point diff therefore mixes in reversals of that branch's files. The commits'
> own diffs are the honest measure: `7a05471` touches only
> `docs/08-governance/GOV-009-research-protocol.md` + `docs/08-governance/catalog.md`;
> `0b3f899` touches only `_public/research-protocol.html` + `templates/README.md`. So the
> session changed exactly the four claimed files — CONFIRMED, with the note that `8a62993` is
> a poor diff base and future reviews of this session should diff `b50d6a6..0b3f899` or
> per-commit.
>
> **1. GOV-009 structure — CONFIRMED.** Front matter: `code: GOV-009`, `kind: governance`,
> `depends_on: [doc-prompt-pack-protocol]`, valid schema fields. Read side-by-side with
> GOV-008: same eight-stage pipeline with identical stage roles, gates at stages 3
> (adversarial review of Prompt B), 5 (adversarial audit of the pack), 7 (owner sign-off,
> optional adversarial review), plus per-campaign ratification via AskUserQuestion in stage
> 8. Standing-rules block (research-flavored: Thesis discipline and Evidence hygiene
> replacing GOV-008's build rules) and a five-artifact template appendix mirroring GOV-008's,
> with `K`/`S*`/`X*`/`R`/`G`/`A` replacing `K`/`C*`/`V*`/`G`/`A`/`W`.
>
> **2. Deference to the content methodology — CONFIRMED.** All three named files exist:
> `research/literature-review/CLAUDE.md`, `research/protocols/literature_review_protocol.md`,
> `research/literature-review/HANDOFF.md`. The precedence rule is stated verbatim in GOV-009
> (lines 35–37: methodology files win on content method; the protocol governs where they are
> silent). Spot-checks hold: the four-pass workflow is really in the search protocol (Pass 1
> Broad map / Pass 2 Deep reading / Pass 3 Adversarial novelty test / Pass 4 Synthesis, plus
> search phases A–E and inclusion/exclusion sections); the frozen-baseline rule is really in
> HANDOFF ("Do not modify the frozen pre-literature baseline", following a numbered reading
> sequence); CLAUDE.md really carries the null hypothesis, search domains, similarity
> scoring, and required deliverables.
>
> **3. Nothing under research/ modified — CONFIRMED.** Neither commit touches any path under
> `research/`.
>
> **4. Governance check — CONFIRMED.** `uv run python -m src.governance` at HEAD:
> `Governance OK: 18 systems, 160 documents, 16 memories, 119 backlog phases`, exit 0. (The
> session record says 159 documents — a peer added one since; not a discrepancy against the
> range.) `7a05471`'s catalog diff adds exactly one row: `| GOV-009 | governance | active |
> repository-owner | docs/08-governance/GOV-009-research-protocol.md |`.
>
> **5. Showcase page — CONFIRMED, one minor discrepancy under 5d.**
> - **5a CONFIRMED.** Inline `<style>` blocks of `_public/research-protocol.html` and
>   `_public/prompt-pack-protocol.html` are byte-identical (12,250 bytes each, `diff` clean).
>   Working-tree file is identical to the committed version.
> - **5b CONFIRMED.** `initNav`, `initDiagrams`, `initAnchors`, the `$`/`$$`/`esc` helper
>   lines, and the boot block are all byte-identical between the two pages. Differences are
>   confined to the data arrays, `initStats`, and the page-specific `initContentDocs` (new on
>   this page) — exactly the allowed set.
> - **5c CONFIRMED.** The masthead `<div class="stats">` is empty in the HTML; `initStats`
>   computes all five figures from `STAGES.length`, `GATES.length`, `ARTIFACTS.length`,
>   `RULES.length`, `PASSES.length` (8/4/9/6/4, matching the session record's
>   browser-verification claim). Nothing hand-typed.
> - **5d CONFIRMED with one minor discrepancy.** Stage labels (8), delegation shape (`K` ·
>   `S*`/`X*` pairs · `R` · `G` · `A`), and all five artifact-template table rows match
>   GOV-009's text faithfully (abbreviations only). The authority note is present and
>   correctly double-layered: GOV-009 authoritative over the page, `research/` files
>   authoritative on content method — "This page is a rendering of the protocol, not a second
>   copy of the rules." **Discrepancy (minor):** the page says "Six rule groups" and its
>   RULES array lists 6, but GOV-009 has **seven** headed subsections under Standing rules —
>   "Stop conditions and descope" is the seventh. Its content is not missing (saturation-as-
>   completion appears in section 05's cards; owner-only descope and phase-boundary stop
>   appear in the "And always" list), so nothing is misrepresented — but the count
>   understates the document's own structure. One trivial addition: the "And always" bullet
>   "Every document code comes from the allocator" is stated as a standing rule where GOV-009
>   mentions `--next-code` only in the Prompt B template row; harmless, consistent with repo
>   practice.
> - **5e CONFIRMED.** `templates/README.md`'s atlas row gains `_public/research-protocol.html`
>   as a third rendered reference; the two prior references are unchanged.
>
> **6. Test suite status — CONFIRMED.** The range touches no `.py`, `test/`, `src/`, or `ts/`
> files. Both cited records classify exactly the three named tests:
> `SESS-2026-09-10-11-workbench-backend-api.md` (lines 27–31, pyenv shim rehash lock
> contention, host-environment defect) and
> `SESS-2026-09-10-13-workbench-terminal-panel-rework.md` (lines 31–37, same classification,
> "environmental defect, not a phase finding"). My governance-relevant subset run
> (`test/test_governance.py` + `test/test_codes.py`): 78 passed, 1 failed —
> `test_codes.py::test_committed_catalog_matches_regenerated_output`. That failure is **not
> attributable to the range**: it is caused by the still-**untracked** session record
> `docs/03-sessions/SESS-2026-09-11-01-research-pack-protocol.md` (the regenerator scans the
> filesystem and renders a 54th session row the committed catalog lacks). It will resolve
> when the close commit lands with a regenerated catalog — but the close commit **must
> regenerate `catalog.md`**, or it will leave `dev` red on this test.
>
> **Verdict: PASS.** All six claims hold against the diff and my reruns. Three notes for the
> record: (1) `8a62993` is a sibling-branch tip, not an ancestor — the stated review range is
> only valid via `git log`, not as a two-point `git diff` base; (2) the page's "six standing
> rule groups" undercounts GOV-009's seven headed subsections, though no rule content is
> absent — cosmetic, fix optional; (3) the session-close commit must include a regenerated
> `docs/08-governance/catalog.md` alongside the session record, or
> `test_codes.py::test_committed_catalog_matches_regenerated_output` stays red. The session
> record's own claims (governance output, CSS parity, stats figures, PTY-failure
> classification) are all corroborated, adjusting only the document count for post-range peer
> commits.

**Disposition of the review's notes**, made after the review returned: note 1 is folded into
`## Phase` above; note 2, though marked optional, was fixed — the page's rules section now
carries the seventh group ("Stop conditions and descope") as a card, the `RULES` array counts
7, and the two tick-list bullets the card duplicated were trimmed; note 3 is satisfied by this
close commit, which carries the regenerated catalog. (The review ran before the peer-recorded
`000099` surfaced; its point-6 confirmation is that the *cited records say* what this record
originally claimed, which stands — the contested-classification caveat in `## Verification`
was added on top.)

## Decisions

- **Where the protocol lives and what it is**: the owner ratified, via one AskUserQuestion
  batch before anything was written: a governed sibling of `GOV-008` in `docs/08-governance/`
  (not an ungoverned file in `research/protocols/`); layered on top of the existing content
  methodology (`research/literature-review/CLAUDE.md`,
  `research/protocols/literature_review_protocol.md`, `HANDOFF.md`) with those files staying
  authoritative on content method; general to any research campaign rather than written only
  for the pending D-System novelty review; and following the full two-session pack model with
  a delegation pack, not a gated single-track pipeline. All four answers took the recommended
  option.
- **The precedence rule inside GOV-009**: where the protocol and the `research/` methodology
  files conflict on content method, the methodology files win; where they are silent on
  process, the protocol governs. Chosen so `GOV-009` adds the operational layer (sessions,
  gates, reviews, sign-offs) without duplicating or superseding the prepared review
  instructions.
- **The delegation-pack section shape for research**: `K` kickoff · `S*`/`X*`
  search-and-extraction pairs · `R` collision review · `G` phase gate measured against the
  reproducibility ledger · `A` adversarial synthesis review — the research analogue of
  `GOV-008`'s `K`/`C*`/`V*`/`G`/`A`/`W`.
- **No pointer file in `research/`**: the owner chose the governed-doc-only option, so nothing
  under `research/` was touched or added.
- **Showcase page registration**: added as a third rendered reference on the atlas row of
  `templates/README.md`; the template files' own comments (which name the first two pages as
  the reference renderings) were left unchanged.

## Corrections

- Two SVG text overflows in the showcase page's passes diagram — the `A` node's subtitle
  spilling past its 108px box and Pass 3's subtitle touching its edges — were caught by
  element screenshot during browser verification and fixed (box widened, subtitles shortened)
  before the page was committed. Caught-and-fixed within the session; no owner correction was
  involved.
- The showcase page understated GOV-009's standing-rule structure: "Six rule groups" against
  the document's seven headed subsections (no rule content was missing). Caught by the
  independent close review, fixed in the close commit.
- This record initially asserted the peer sessions' environmental classification of the three
  PTY failures as settled; on finding `000099`'s contrary account in the working tree, the
  claim was narrowed to what this session can actually establish — non-attribution to its own
  diff.

## Left undone

- **The protocol has never been executed.** `GOV-009` is manufactured methodology with no
  proven run behind it — unlike `GOV-008`, which was extracted from two completed builds. Its
  first campaign (the pending adversarial D-System literature review, for which
  `research/literature-review/HANDOFF.md` says external review of the codebase audit must come
  first) will be the test of whether the stage templates and the `K`/`S*`/`X*`/`R`/`G`/`A`
  shape survive contact with real search work. Left because running a campaign was never in
  this session's scope.
- **No backlog phases exist for a research campaign.** Deliberately: `GOV-009` itself says the
  pack-factory session drafts them per campaign, so pre-creating phases now would front-run
  the protocol's own stage 4.
