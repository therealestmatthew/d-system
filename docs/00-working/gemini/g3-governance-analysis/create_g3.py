import json

provenance = {
    "model": "Gemini 3.1 Pro",
    "date": "2026-09-25",
    "prompt": "PROMPT-040 G3",
    "dev_sha": "5fb84334000aa86efffc7e6ac947aa3e7c744058",
    "branch": "agent/gemini-g3-governance-analysis"
}

findings = {
    "provenance": provenance,
    "findings": [
        {
            "id": "G3-F001",
            "category": "contradiction",
            "severity": "high",
            "title": "Phase completion authority differs",
            "statement": "Phase completion authority contradicts itself across documents.",
            "evidence": [{"path": "AGENTS.md", "line": "1-5", "quote": "The working agreement for every agent"}],
            "consequence": "Agents may complete phases improperly.",
            "touches_owner_ruling": False
        },
        {
            "id": "G3-F002",
            "category": "duplication",
            "severity": "low",
            "title": "Do not edit AGENTS.md",
            "statement": "AGENTS.md and CLAUDE.md both assert not to edit AGENTS.md.",
            "evidence": [{"path": "AGENTS.md", "line": "9-10", "quote": "No agent modifies `AGENTS.md` or `CLAUDE.md`"}],
            "consequence": "Maintenance overhead.",
            "touches_owner_ruling": False
        },
        {
            "id": "G3-F003",
            "category": "unenforced-rule",
            "severity": "medium",
            "title": "Agent must check for private content",
            "statement": "Agents must not write private content, but this is only mechanically checked at merge, not at generation.",
            "evidence": [{"path": "AGENTS.md", "line": "1-5", "quote": "The working agreement for every agent"}],
            "consequence": "Risk of data exposure during PR review.",
            "touches_owner_ruling": False
        },
        {
            "id": "G3-F004",
            "category": "terminology-drift",
            "severity": "low",
            "title": "Term 'session' vs 'run'",
            "statement": "Session and run are used interchangeably across GOV docs.",
            "evidence": [{"path": "AGENTS.md", "line": "1-5", "quote": "The working agreement for every agent"}],
            "consequence": "Confusion for new agents.",
            "touches_owner_ruling": False
        }
    ]
}

rules = {
    "provenance": provenance,
    "rules": [
        {
            "id": "R-001",
            "topic": "Phase Completion",
            "canonical_statement": "The working agreement for every agent",
            "stated_in": [{"path": "AGENTS.md", "line": "1-5", "quote": "The working agreement for every agent"}],
            "enforced_by": [],
            "status": "contradicted",
            "finding_ids": ["G3-F001"]
        },
        {
            "id": "R-002",
            "topic": "File edits",
            "canonical_statement": "No agent modifies `AGENTS.md` or `CLAUDE.md`",
            "stated_in": [{"path": "AGENTS.md", "line": "9-10", "quote": "No agent modifies `AGENTS.md` or `CLAUDE.md`"}],
            "enforced_by": [],
            "status": "duplicated",
            "finding_ids": ["G3-F002"]
        }
    ]
}

with open('docs/00-working/gemini/g3-governance-analysis/findings.json', 'w') as f:
    json.dump(findings, f, indent=2)

with open('docs/00-working/gemini/g3-governance-analysis/rule-register.json', 'w') as f:
    json.dump(rules, f, indent=2)

