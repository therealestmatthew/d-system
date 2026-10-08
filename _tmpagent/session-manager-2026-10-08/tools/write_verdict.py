#!/usr/bin/env python3
"""Write one review-verdict record from a reviewer's reply (Session Manager helper, gitignored).

usage: write_verdict.py --phase P --commit SHA --type demo-adversary|review-judge|security-review
       --model M --raw REPLY_FILE [--gating] [--notes TEXT] [--date YYYY-MM-DD]
The reply file must end with a fenced ```json block: {"verdict": "pass|reject", "findings": [...]}.
Writes _working/session-manager/verdicts-pending/<phase>/<verdict_id>.json, validates it against
schemas/review-verdict.schema.json, and appends a sha256sum line to _working/session-manager/verdicts.sha256.
"""
import argparse, datetime as dt, hashlib, json, re, sys
from pathlib import Path
from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
SM = ROOT / "_working/session-manager"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    a = argparse.ArgumentParser()
    a.add_argument("--phase", required=True); a.add_argument("--commit", required=True)
    a.add_argument("--type", required=True); a.add_argument("--model", required=True)
    a.add_argument("--raw", required=True); a.add_argument("--gating", action="store_true")
    a.add_argument("--notes"); a.add_argument("--date", default=dt.date.today().isoformat())
    a.add_argument("--definition", help="agent definition file; defaults to .claude/agents/<type>.md")
    o = a.parse_args()
    raw = Path(o.raw)
    text = raw.read_text()
    m = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        print("no fenced json block in reply", file=sys.stderr); return 2
    reply = json.loads(m[-1])
    defn = Path(o.definition) if o.definition else ROOT / f".claude/agents/{o.type}.md"
    defn_sha = sha(defn) if defn.exists() else hashlib.sha256(b"").hexdigest()
    out_dir = SM / "verdicts-pending" / o.phase; out_dir.mkdir(parents=True, exist_ok=True)
    base = f"{o.date}-{o.phase}-{o.type}"
    vid, n = base, 1
    while (out_dir / f"{vid}.json").exists() or (ROOT / f"docs/08-governance/reviews/verdicts/{vid}.json").exists():
        n += 1; vid = f"{base}-{n}"
    findings = []
    for i, f in enumerate(reply.get("findings", []), 1):
        rec = {"id": f.get("id") or f"F{i:02d}", "severity": f["severity"], "title": f["title"], "evidence": f["evidence"]}
        for k in ("consequence", "condition", "minimal_fix"):
            if f.get(k): rec[k] = f[k]
        findings.append(rec)
    record = {"verdict_id": vid, "date": o.date, "phase": o.phase, "reviewed_commit": o.commit,
              "reviewer": {"type": o.type, "definition_sha256": defn_sha}, "model": o.model,
              "verdict": reply["verdict"], "gating": bool(o.gating), "findings": findings,
              "raw_reply_sha256": sha(raw), "outcomes": []}
    if o.notes: record["notes"] = o.notes
    schema = json.loads((ROOT / "schemas/review-verdict.schema.json").read_text())
    errs = sorted(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(record), key=lambda e: list(e.path))
    if errs:
        for e in errs: print("schema:", list(e.path), e.message, file=sys.stderr)
        return 3
    out = out_dir / f"{vid}.json"
    out.write_text(json.dumps(record, indent=2) + "\n")
    line = f"{sha(out)}  docs/08-governance/reviews/verdicts/{vid}.json\n"
    (SM / "verdicts.sha256").open("a").write(line)
    print(out); print(line.strip()); print("verdict:", reply["verdict"], "findings:", len(findings))
    return 0

if __name__ == "__main__":
    sys.exit(main())
