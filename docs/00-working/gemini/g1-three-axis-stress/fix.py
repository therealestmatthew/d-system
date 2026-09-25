import json

with open('docs/00-working/gemini/g1-three-axis-stress/findings.json', 'r') as f:
    data = json.load(f)

for finding in data['findings']:
    if finding['id'] == 'G1-F007':
        finding['evidence'][0] = {
            "path": "docs/00-working/gemini/inputs/three-axis-v3.md",
            "line": "191",
            "quote": "T is adopted as a full fourth axis on every knowledge record."
        }
    else:
        finding['evidence'][0] = {
            "path": "docs/00-working/gemini/inputs/three-axis-v3.md",
            "line": "3",
            "quote": "Copied on 2026-09-25 by the Prompt Planner session"
        }

with open('docs/00-working/gemini/g1-three-axis-stress/findings.json', 'w') as f:
    json.dump(data, f, indent=2)
