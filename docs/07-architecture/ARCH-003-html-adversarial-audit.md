---
schema_version: 1
id: doc-html-adversarial-audit
code: ARCH-003
title: HTML generation adversarial design audit
kind: architecture
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-html, sys-contracts, sys-api, sys-ui, sys-delivery, sys-backlog]
depends_on: [doc-html-00-overview, doc-backlog-decisions]
---

# HTML generation adversarial design audit

**Date:** 2026-09-05. **Review:** dedicated adversarial-review agent, with independent reproduction of schema/model/converter failures by the primary agent.

**Verdict:** start with contract and plan reconciliation, not by copying the existing implementation snippets. The architecture is appropriate for the intended system, but four high-priority design defects should be resolved before the affected implementation phases begin. The current app remains scaffolding; these are defects in proposed behavior and acceptance criteria, not claims of deployed vulnerabilities.

The review covered all seven [HTML design documents](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003-overview.md), HTML and prerequisite reliability phases in the [backlog](../09-backlog/backlog.yaml), [accepted user choices](../08-governance/GOV-003-backlog-decisions.md), governance rules, actual Python/React scaffolds, package declarations and CI. The raw answers, application code and phase states were not changed by this audit.

## Findings at a glance

| ID | Priority | Finding | Affected HTML phases |
|---|---|---|---|
| H1 | High | Copyable schema/model examples contradict strict runtime validation | 01, 03, 06 |
| H2 | High | Generation has no complete publication, ownership or freshness contract | 01, 02, 04, 09 |
| H3 | High | Route identity and cross-file site integrity are underspecified | 01, 02, 04, 06 |
| H4 | High | Phase deliverables cannot build in their declared order | 05, 06, 07, 08 |
| M1 | Medium | Configured links/images lack a bounded URL and asset policy | 01, 07, 08, 09 |
| M2 | Medium | API failure classification and bootstrap recovery are incomplete | 04, 06 |
| M3 | Medium | A successful frontend build does not establish a runnable release | 01, 09, 10 |
| M4 | Medium | Responsive and accessible behavior has concrete gaps | 06, 08, 10 |
| M5 | Medium | Verification has false expectations and no repeatable browser regressions | 02, 04, 06, 08, 10 |
| L1 | Low | Templates, theming and some styling claims have no defined behavior | 01, 05, 08, 09 |

High means likely to invalidate core behavior, data publication or the one-session execution sequence. Medium identifies correctness, reliability or exposure assumptions that should be settled in the mapped phase. These are engineering priorities, not vulnerability scores.

## H1 — Contracts contradict the accepted validation decision

**Evidence:** [Build tooling](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.01-build-tooling.md), line 163, makes every block's `content` an unconstrained object. [Backend](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.02-backend.md), lines 49–84, uses `extra="allow"`, arbitrary block/template strings, and explicitly delegates content safety to TypeScript. [Frontend setup](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.03-frontend-setup.md), line 122, assigns fetched JSON a static type; [components](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.04-frontend-components.md), line 179, returns JSON without runtime checking.

**Failure:** a columns block with `content: {}` passes the proposed JSON Schema and Pydantic model, then cannot satisfy `content.columns.length`. A hero with an integer headline and duplicate block IDs also passes. The backend accepts an entirely unknown block type. The accepted choice and newer backlog already require stricter behavior, but an implementer following the detailed examples would still build the wrong contract.

**Proposed update:** replace the permissive examples. Define discriminated block schemas, required fields and unknown-field behavior throughout nested objects. Choose one canonical contract with a reproducible TypeScript derivation or drift check. Specify absent versus null fields, CTA text/link pairing, allowed templates, nonempty identifiers, column-count bounds and uniqueness of block IDs. Backend runtime validation is mandatory; an independently handwritten third browser validator is not automatically necessary. Any browser decoding should derive from the same contract.

**Acceptance:** a shared positive/negative fixture corpus runs against JSON Schema and Pydantic; TypeScript alignment is checked in CI. Include unknown type/template, missing content, wrong scalar types, unknown nested keys, null/optional cases and duplicate block IDs.

## H2 — Publication must cover a whole generation

**Evidence:** [Build tooling](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.01-build-tooling.md), lines 53–85, loads and writes files individually, silently skips a missing site file and discovers both `.yaml` and `.yml`. It never invokes the supplied schemas.

**Reproduced failures:** `same.yaml` and `same.yml` overwrite the same JSON output; an earlier valid file publishes before a later invalid YAML file fails. Duplicate YAML keys silently replace a value. `.nan` becomes a `NaN` token in generated output, which is not interoperable JSON.

**Additional design failures:** removing `site.yaml` can preserve old routing output. A broad stale-output deletion pass could delete files the generator does not own. Even individually atomic file replacements do not guarantee that site configuration and page files come from one generation. A long-lived browser can retain a route table whose page disappears during publication.

**Proposed update:** specify required source files, duplicate-stem/case handling, YAML duplicate-key and JSON-value rules, bounded aliases/nesting if supported, and generator-owned output boundaries. Select either immutable generations with an explicit publication boundary or a simpler documented stop/build/start boundary for v1. State reader/writer assumptions and preserve the previous good output on rejected input. Define stale-browser behavior and owned-output cleanup. Keep the HTML publication design independent of DuckDB's publication mechanism.

**Acceptance:** duplicate sources/keys, missing site input, invalid late input, non-JSON values, injected write failure, stale page removal, preservation of unrelated/authored files and deterministic repeated builds. Verify reader behavior during whatever publication operation v1 claims to support. Use temporary directories.

## H3 — Site integrity requires more than per-file schemas

**Evidence:** [Build tooling](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.01-build-tooling.md), lines 116–117, permits any path beginning with `/` and permits page ID `site-config`. [Backend](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.02-backend.md), line 121, reserves `/pages/site-config`. [Frontend setup](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.03-frontend-setup.md), lines 124–139, turns configured paths into router definitions.

**Failures:** a page named `site-config` requests site configuration instead of page data. Duplicate `/about` routes, missing referenced pages and navigation to undeclared routes are unchecked. `//example.com`, wildcard/parameter syntax, case differences and trailing slashes have no declared policy. Duplicate block IDs become duplicate React keys.

**Proposed update:** define a small static local-route grammar and canonicalization policy. Reserve endpoint IDs or separate the site endpoint namespace. Validate route uniqueness, route-to-page references, navigation-to-route references and block ID uniqueness before publication. Decide explicitly whether several route paths may intentionally alias one page. Do not confuse path uniqueness with page-reference uniqueness.

**Acceptance:** reserved IDs, unresolved references, conflicting routes, noncanonical paths, duplicate block IDs and a valid intentional alias case if aliases are supported. Diagnostics identify the source file and field.

## H4 — The current session order contains missing-artifact dependencies

**Evidence:** the [backlog](../09-backlog/backlog.yaml) assigns `ts/src/types/schema.ts` to `phase-html-06`, but `phase-html-07` imports those types and depends only on 03/05. The planned router in [frontend setup](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.03-frontend-setup.md), lines 114–116, imports DynamicPage/pageLoader and NotFoundPage. DynamicPage/BlockRenderer are delivered in 08, which depends on 06. NotFoundPage is missing from phase deliverables. The planned deletion of App also invalidates the required `sys-ui` evidence path in [systems.yaml](../08-governance/systems.yaml).

**Failure:** the dependency graph is acyclic by ID, yet the intermediate artifacts cannot pass their own build checks. A green structural backlog check does not discover this semantic dependency problem.

**Proposed update:** move shared frontend types into the earlier foundation phase. Make 06 own a buildable page loader/shell and NotFoundPage, then have 08 complete rendering. Assign every imported file to the phase that first needs it. Update the component registry when App is deleted or replaced. Do not repair a missing-artifact dependency by introducing a phase cycle.

The dependency of HTML conversion on `phase-rel-02` is permissible sequencing, but that phase promises entity/memory validation, not a reusable HTML validator. Name the shared helper if one is intended; do not couple page tooling to DuckDB just to satisfy the dependency.

**Acceptance:** after each phase, type checking, frontend build and governance validation pass with all later phase artifacts still absent.

## M1 — Define the URL, asset and exposure boundaries

**Evidence:** [components](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.04-frontend-components.md), lines 127, 323 and 364, insert configured navigation/CTA/image values into browser destinations. The proposed schemas do not constrain the URI policy.

**Scenario:** protocol-relative or external navigation can leave the site; an external image causes the visitor's browser to contact another host. An arbitrary URI is accepted without a documented policy. Acceptance of `javascript:` in a schema is not proof that a particular React/browser combination executes it. This is not server-side SSRF: the backend does not fetch images.

**Proposed update:** separate internal navigation from optional external CTA/image URLs. Specify permitted schemes, local asset location/packaging and internal CTA navigation behavior. Preserve escaped plain-text rendering. State the supported exposure model—such as a local single-user demo—without adding authentication or public multi-user hosting merely because they might someday be useful.

**Acceptance:** allowed internal/external URLs, disallowed schemes, protocol-relative/malformed URLs, literal HTML-like text, missing images, meaningful versus decorative image alternatives, and internal CTA navigation without a full reload.

## M2 — Complete the failure and recovery contracts

**Evidence:** [backend](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.02-backend.md), lines 114–135, checks existence before reading, leaves read/JSON/schema failures unclassified, uses blocking file reads inside async routes, and uses Unicode `isalnum` while claiming an ASCII policy. [Frontend setup](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.03-frontend-setup.md), lines 145 and 189–200, creates the router promise once and offers no retry in the initial failure UI.

**Proposed update:** use one exact ID policy across discovery, schema, server and browser. Define invalid-request, missing-page and corrupt/unavailable-configuration responses, with useful logs and controlled public error details. Use synchronous routes or an appropriate file-access approach for the selected scale. A bootstrap retry must rerun the fetch. Describe cancellation and stale-config recovery. Character filtering alone does not address symlinks: choose a controlled generated root or explicit containment checks and test the guarantee actually made.

**Acceptance:** Unicode/case policy, malformed IDs, missing site/page output, corrupt JSON, schema-invalid JSON, controlled read failure, initial outage followed by retry, failed page-load retry and cancelled navigation. Test containment if it is part of the supported boundary.

## M3 — Define what a runnable v1 release means

**Evidence:** current [Vite configuration](../../ts/vite.config.ts) defines a development proxy only. [FastAPI](../../src/main.py) does not serve frontend assets. [Packaging](../../pyproject.toml) includes `src`, while the proposed API locates repository-relative `_data`. Generated JSON will intentionally be ignored by Git.

**Failure scenario:** copying `ts/dist` and starting the backend does not supply ignored page configs, same-origin API forwarding or a browser-history fallback. `/` can work while a direct `/about` load or refresh fails.

**Proposed update:** name the supported topology: a documented local dual-server workflow or a concrete production arrangement. Specify source/output roots, generated configs and asset packaging, API origin, direct-link handling and startup behavior without built output. No additional service is inherently necessary.

**Acceptance:** a clean checkout can follow the documented install/build/start sequence, make API requests, load/refresh `/about` directly, and handle missing assets/configs. A production-shaped promise requires a smoke test of the actual production serving arrangement, not just `vite build`.

## M4 — Test actual responsive and accessible behavior

**Evidence:** [components](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.04-frontend-components.md), line 391, unconditionally sets inline `gridTemplateColumns`; the line 406 claim that `grid-cols-1` remains the mobile fallback is incorrect. Navigation is a nonwrapping flex row. Heading levels are fixed regardless of block order. The browser document title stays at the static entry document value.

**Proposed update:** implement a real breakpoint-aware columns layout and bounds on column counts, long-text/navigation handling, coherent heading levels, current-navigation indication, keyboard focus/route-change behavior, accessible loading/error status and page-specific document titles.

**Acceptance:** several columns and long labels/text at desktop and narrow widths, keyboard-only navigation/retry, usable headings, correct image alternatives, no unintended horizontal overflow and document-title changes. These checks do not require adopting a large accessibility framework.

## M5 — Repair verification expectations and automate representative interactions

**Evidence:** [verification](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003.06-verification.md), lines 39–45, repeatedly changes into `ts` within one shell block, so the second change targets `ts/ts`. It installs without the development extras needed by checks, assumes a normalized traversal URL reaches one handler and returns 400, and expects invalid authored YAML to cause a browser error. Existing CI compiles/builds TypeScript but does not exercise browser behavior.

**Proposed update:** provide commands runnable as written—use root-relative `npm --prefix ts ...` or one subshell directory change, and explicit development dependencies/locked frontend installs. Test the invariant that traversal cannot escape the output root without requiring every rejected URL to reach the same handler. Separate rejected source builds from separately injected corrupt runtime artifacts.

**Acceptance:** invalid YAML fails the build and leaves the last good page usable; runtime-error tests corrupt generated output only in temporary fixtures. Add representative navigation, retry, direct-link and responsive/block browser checks early enough to prevent regressions, rather than deferring all behavior testing to phase 10. TypeScript compilation alone is not rendering verification.

## L1 — Make product promises observable

The schema supports `landing` and `standard`, but DynamicPage ignores `template`. The overview promises configuration-driven theming while tokens are static CSS. The overview says merge into App while the manifest deletes it. Samples cover hero/text but not image/columns. `prose` is used without declared typography styling support.

**Proposed update:** define actual template differences or explicitly reserve the field; describe theming as compile-time CSS unless configurable theming is deliberately added; choose one entry-point strategy; provide fixtures for all four block types; remove unsupported styling claims or implement the intended styling. These are bounded product clarifications, not reasons to introduce SSR, executable HTML/Markdown, or a generic plugin framework.

## Recommended amendments to the existing ten phases

These are **proposed changes for review**, not silently adopted backlog scope or completed work. All ten HTML phases link to this audit as source material.

| Phase | Proposed amendment | Exit condition |
|---|---|---|
| html-01 | Replace conflicting examples; define strict contract, route/URL rules, output ownership, publication and supported hosting assumptions | ADR + shared positive/negative fixtures cover H1–H3 and the relevant medium findings |
| html-02 | Validate the whole discovered site graph; deterministic generation and publication within the chosen boundary | Collision, late failure, cleanup, strict YAML/JSON and publication tests pass |
| html-03 | Implement discriminated backend models against the shared corpus | Model/schema agreement and invalid-block rejection |
| html-04 | Resolve reserved IDs, corruption/read failures, containment and generation access | API behavior tests include valid, missing, malformed and corrupt cases |
| html-05 | Own shared types before any consumer; define styling foundation and entry-point transition | Types available and app builds before 06/07 exist |
| html-06 | Own loader, buildable page shell and NotFoundPage; implement real bootstrap retry and accessible navigation | A working route shell passes type/build/governance checks without phase 08 |
| html-07 | Consume earlier shared types and apply CTA/text policy | Hero/text cases pass against the shared contract |
| html-08 | Complete rendering, template behavior and responsive image/columns; update registry if App is removed | Four block variants work across widths without breaking the prior shell |
| html-09 | Supply all-block fixtures, assets and reproducible build/start packaging | Clean-checkout workflow and ignored-output ownership verified |
| html-10 | Repair the checklist and run a browser/release smoke suite with actual evidence | Invalid source retains last good output; corruption, recovery, deep links and interactions verified |

Preserve the current stable phase IDs. The proposed sequencing repair does not require a dependency cycle or a new architecture. If the expanded contract phase cannot fit one session, split it into a contract/decision phase and a separately tracked shared-fixture phase before conversion/models. Likewise, split publication mechanics from conversion if needed. Add such phases and dependencies to the backlog before implementation; do not claim a larger scope still fits one session merely by retaining `session_budget: 1`.

## Decisions already settled versus remaining design work

Do not reopen canonical YAML, ignored generated JSON, strict shared runtime validation or phased delivery: the user already selected them. The exact publication mechanism, route grammar, URL policy, output root, template behavior and minimal hosting profile are ordinary implementation choices to resolve and record during the contract phase. A proposed expansion into public multi-user hosting, executable rich content, SSR/static export or another new product capability would be a separate scope decision.

The review recommends a small and explicit v1 boundary rather than unqualified safety or deployment claims. Authentication, a CDN, a schema registry service and live concurrent publishing are not automatically required by these findings.

## Reproduction evidence and limits

The primary agent extracted the literal JSON Schema, Pydantic and converter code blocks from the reviewed Markdown and exercised them with synthetic inputs. Converter paths were redirected to a temporary directory under `/tmp`; the repository `_data/`, `data/` and `_private/` were not read or modified by the experiments.

| Experiment | Observed result |
|---|---|
| Page schema: missing columns, integer headline, duplicate block IDs, unchecked CTA URI | Accepted |
| Site schema: duplicate `//external.example` routes, reserved/missing page references, external navigation and extra navigation key | Accepted |
| Proposed Pydantic model: malformed known content and unknown block type | Accepted |
| `all(c.isalnum() or c in '-_' for c in 'café')` | True, contradicting the claimed ASCII rule |
| `yaml.safe_load('title: first\ntitle: second\n')` | Last value silently wins |
| `same.yaml` and `same.yml` in the same input directory | Both target `same.json`; `.yml` value wins |
| Valid `a.yaml` followed by syntactically invalid `z.yaml` | Build fails after `a.json` is published |
| YAML `.nan` through the sample converter | Emits a nonstandard `NaN` JSON token |

A compact reproduction of the schema defect, from the repository root:

```bash
uv run python - <<'PY'
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator

plan = Path('docs/01-plans/PLAN-003-dynamic-html-generation/PLAN-003.01-build-tooling.md')
schemas = [json.loads(s) for s in re.findall(r'```json\n(.*?)\n```', plan.read_text(), re.S)]
payload = {
    'title': 'Fixture', 'template': 'landing',
    'blocks': [{'id': 'x', 'type': 'columns', 'content': {}}],
}
print(list(Draft202012Validator(schemas[1]).iter_errors(payload)))
# At audit time: [] -- although ColumnsBlock requires content.columns.
PY
```

Browser execution, a real deployment and full implementation tests were not performed because the feature does not exist yet. CSS precedence, file ownership, missing-artifact dependencies and recovery/hosting gaps were reviewed statically. URL acceptance is not reported as a demonstrated XSS exploit, and remote image loading is not reported as server-side SSRF. A temporary-module setup issue in the initial model experiment was corrected before recording model results; it was an audit-harness issue, not a plan defect.
