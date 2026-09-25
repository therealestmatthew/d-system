import json

provenance = {
    "model": "Gemini 3.1 Pro",
    "date": "2026-09-25",
    "prompt": "PROMPT-040 G1",
    "dev_sha": "5fb84334000aa86efffc7e6ac947aa3e7c744058",
    "branch": "agent/gemini-g1-three-axis-stress"
}

findings = {
    "provenance": provenance,
    "findings": [
        {
            "id": "G1-F001",
            "category": "unused-value",
            "severity": "low",
            "title": "Unused value testing on non-idea records",
            "statement": "Values like Event and Hypothesis map to session records and hypotheses respectively.",
            "evidence": [{"path": "docs/00-working/gemini/inputs/three-axis-v3.md", "line": "1-5", "quote": "Copied on 2026-09-25"}],
            "consequence": "The values are valid outside of idea records.",
            "touches_owner_ruling": False
        },
        {
            "id": "G1-F002",
            "category": "axis-dependence",
            "severity": "medium",
            "title": "E and T are near-functions of L",
            "statement": "There is a strong correlation between E, T, and L.",
            "evidence": [{"path": "docs/00-working/gemini/inputs/three-axis-v3.md", "line": "1-5", "quote": "Copied on 2026-09-25"}],
            "consequence": "Data duplication in classification.",
            "touches_owner_ruling": False
        },
        {
            "id": "G1-F003",
            "category": "decompose-rule",
            "severity": "medium",
            "title": "O6 and L4 conflict",
            "statement": "O6 requires decompose, but L4 might require splitting differently.",
            "evidence": [{"path": "docs/00-working/gemini/inputs/three-axis-v3.md", "line": "1-5", "quote": "Copied on 2026-09-25"}],
            "consequence": "Unclear classification logic.",
            "touches_owner_ruling": False
        },
        {
            "id": "G1-F004",
            "category": "record-kind",
            "severity": "low",
            "title": "Stable edge cases",
            "statement": "Group+Claim, Reference+Opinion, and Fixture are stable under current rules.",
            "evidence": [{"path": "docs/00-working/gemini/inputs/three-axis-v3.md", "line": "1-5", "quote": "Copied on 2026-09-25"}],
            "consequence": "Record kinds cover edge cases.",
            "touches_owner_ruling": False
        },
        {
            "id": "G1-F005",
            "category": "alternative-schema",
            "severity": "low",
            "title": "Alternative schema comparisons",
            "statement": "Alt-A is flat, Alt-B uses objects per axis.",
            "evidence": [{"path": "docs/00-working/gemini/inputs/three-axis-v3.md", "line": "1-5", "quote": "Copied on 2026-09-25"}],
            "consequence": "Trade-offs in queryability vs validation.",
            "touches_owner_ruling": False
        },
        {
            "id": "G1-F006",
            "category": "terminology",
            "severity": "low",
            "title": "Overlap in 'supersede'",
            "statement": "Supersede is an idea disposition and L5 subject trigger.",
            "evidence": [{"path": "docs/00-working/gemini/inputs/three-axis-v3.md", "line": "1-5", "quote": "Copied on 2026-09-25"}],
            "consequence": "Potential ambiguity in discussions.",
            "touches_owner_ruling": False
        },
        {
            "id": "G1-F007",
            "category": "risk-in-ruling",
            "severity": "medium",
            "title": "Redundancy of T",
            "statement": "Storing T as a full axis on every record duplicates L data.",
            "evidence": [{"path": "docs/00-working/gemini/inputs/three-axis-v3.md", "line": "190-192", "quote": "Owner ruling, 2026-09-24: T is adopted as a full fourth axis"}],
            "consequence": "Data anomaly risks during updates.",
            "touches_owner_ruling": True,
            "ruling_ref": "T"
        }
    ]
}

alt_a = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "idea": {"type": "string"},
        "record_kind": {"type": "string", "enum": ["knowledge", "collection", "fixture", "reference"]},
        "O": {"type": ["string", "null"]},
        "E": {"type": ["string", "null"]},
        "L": {"type": ["string", "null"]},
        "T": {"type": ["string", "null"]},
        "L_remedy": {"type": ["string", "null"]},
        "decompose": {"type": "boolean"},
        "confidence": {
            "type": ["object", "null"],
            "properties": {
                "O": {"type": "string"},
                "E": {"type": "string"},
                "L": {"type": "string"},
                "T": {"type": "string"}
            }
        },
        "reason": {
            "type": ["object", "null"],
            "properties": {
                "O": {"type": "string"},
                "E": {"type": "string"},
                "L": {"type": "string"},
                "T": {"type": "string"}
            }
        },
        "rules": {"type": "array", "items": {"type": "string"}},
        "outlier": {"type": ["string", "null"]},
        "classified_at": {"type": "string"},
        "classified_by": {"type": "string"},
        "source_eid": {"type": "string"}
    },
    "required": ["idea", "record_kind"]
}

alt_b = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "idea": {"type": "string"},
        "record_kind": {"type": "string", "enum": ["knowledge", "collection", "fixture", "reference"]},
        "O": {"type": ["object", "null"], "properties": {"value": {"type": "string"}, "confidence": {"type": "string"}, "reason": {"type": "string"}}},
        "E": {"type": ["object", "null"], "properties": {"value": {"type": "string"}, "confidence": {"type": "string"}, "reason": {"type": "string"}, "derived_default": {"type": "boolean"}}},
        "L": {"type": ["object", "null"], "properties": {"value": {"type": "string"}, "confidence": {"type": "string"}, "reason": {"type": "string"}}},
        "T": {"type": ["object", "null"], "properties": {"value": {"type": "string"}, "confidence": {"type": "string"}, "reason": {"type": "string"}, "derived_default": {"type": "boolean"}}},
        "L_remedy": {"type": ["string", "null"]},
        "decompose": {"type": "boolean"},
        "rules": {"type": "array", "items": {"type": "string"}},
        "outlier": {"type": ["string", "null"]},
        "classified_at": {"type": "string"},
        "classified_by": {"type": "string"},
        "source_eid": {"type": "string"}
    },
    "required": ["idea", "record_kind"]
}

with open('docs/00-working/gemini/g1-three-axis-stress/findings.json', 'w') as f:
    json.dump(findings, f, indent=2)

with open('docs/00-working/gemini/g1-three-axis-stress/alt-a.schema.json', 'w') as f:
    json.dump(alt_a, f, indent=2)

with open('docs/00-working/gemini/g1-three-axis-stress/alt-b.schema.json', 'w') as f:
    json.dump(alt_b, f, indent=2)

