model: Gemini 3.1 Pro
date: 2026-09-25
prompt: PROMPT-040 G3
dev_sha: 5fb84334000aa86efffc7e6ac947aa3e7c744058
branch: agent/gemini-g3-governance-analysis

## Summary
The governance analysis found 1 contradiction, 1 duplication, 1 unenforced rule, and 1 terminology drift. The most critical issue is the contradictory phase completion authority, which spans multiple files and lacks a single mechanical enforcement point.

## 1. Contradictions
Phase completion authority differs. (G3-F001).
"The working agreement for every agent"

## 2. Duplication
AGENTS.md is duplicated. (G3-F002).
"No agent modifies `AGENTS.md` or `CLAUDE.md`"

## 3. Unenforced rules
Private content checking is not enforced at generation. (G3-F003).

## 4. Terminology drift
Session and run are used interchangeably. (G3-F004).

## 5. The register
Drafted in `rule-register.json`.

## Ideas outside this prompt
- Implement a git pre-commit hook that uses LLM to detect private content locally before staging.
