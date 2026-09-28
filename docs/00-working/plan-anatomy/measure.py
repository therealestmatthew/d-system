"""Measurements behind docs/00-working/plan-anatomy/inventory.md. Read-only.

Run from the repository root:

    uv run python docs/00-working/plan-anatomy/measure.py plans      # every kind: plan document
    uv run python docs/00-working/plan-anatomy/measure.py folders    # what each plan folder holds
    uv run python docs/00-working/plan-anatomy/measure.py trace PLAN-029 [...]  # one plan's artifacts
    uv run python docs/00-working/plan-anatomy/measure.py scatter    # links per artifact kind
    uv run python docs/00-working/plan-anatomy/measure.py prompts    # each prompt's plan links
    uv run python docs/00-working/plan-anatomy/measure.py decisions  # decision-section share
    uv run python docs/00-working/plan-anatomy/measure.py gov003     # GOV-003 sections naming plans

The plan list comes from the catalog rows of kind plan, not from directory names. The entry check
is GOV-018 step 1's script, extracted verbatim from that document at run time. Nothing is written.
"""

from __future__ import annotations

import collections
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from typing import Any

import yaml

CATALOG = "docs/08-governance/catalog.md"
BACKLOG = "docs/09-backlog/backlog.yaml"
GOV018 = "docs/08-governance/GOV-018-three-altitude-review-procedure.md"
GOV003 = "docs/08-governance/GOV-003-backlog-decisions.md"
REVIEWS = "docs/08-governance/reviews"
WORKING = "docs/00-working"
PLAN_CODE = re.compile(r"\bPLAN-\d{3}(?:\.\d{2})?\b")
PHASE_ID = re.compile(r"\bphase-[a-z]+-\d+\b")
DECISION_H2 = re.compile(
    r"^(Decisions|The chosen design|Chosen design|Design|Approach|Owner rulings|Decision: .*"
    r"|Conflicts with other categories|Conflicts between the sources.*)$"
)


def front_matter(text: str) -> dict[str, Any] | None:
    if not text.startswith("---"):
        return None
    try:
        meta = yaml.safe_load(text.split("---", 2)[1])
    except yaml.YAMLError:
        return None
    return meta if isinstance(meta, dict) else None


def governed() -> dict[str, dict[str, Any]]:
    """Every coded document under docs/, keyed by id."""
    docs = {}
    for path in sorted(pathlib.Path("docs").rglob("*.md")):
        text = path.read_text(errors="ignore")
        meta = front_matter(text)
        if meta and meta.get("code") and meta.get("id"):
            docs[meta["id"]] = {**meta, "path": str(path), "text": text}
    return docs


def backlog_items() -> list[dict[str, Any]]:
    return yaml.safe_load(open(BACKLOG))["items"]


def catalog_plans() -> list[tuple[str, str, str]]:
    rows = []
    for line in open(CATALOG):
        if re.match(r"^\| PLAN-[0-9.]+ \| plan \|", line):
            cells = [c.strip() for c in line.split("|")]
            rows.append((cells[1], cells[3], cells[5]))
    return rows


def entry_check_script() -> str:
    text = open(GOV018).read()
    block = text.split("```bash\n", 1)[1].split("\n```", 1)[0]
    handle = tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False)
    handle.write(block + "\n")
    handle.close()
    return handle.name


def families(docs: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    plans = {i: d for i, d in docs.items() if d["kind"] == "plan"}
    fam: dict[str, list[str]] = collections.defaultdict(list)
    for i, d in plans.items():
        fam[d.get("parent") or i].append(i)
    return fam


def cmd_plans() -> None:
    docs = governed()
    by_path = {d["path"]: d for d in docs.values()}
    items = backlog_items()
    script = entry_check_script()
    print("| Code | Path under docs/01-plans/ | Layout | Parent | Status | Created | Phases | Words "
          "| GOV-018 entry check |")
    print("|---|---|---|---|---|---|---|---|---|")
    for code, status, path in catalog_plans():
        meta = by_path[path]
        layout = "folder" if path.count("/") > 2 else "file"
        run = subprocess.run(["bash", script, path], capture_output=True, text=True)
        missing = "; ".join(x.replace("missing: ", "") for x in run.stdout.split("\n") if x)
        created = str(meta["created"])
        result = "pass" if run.returncode == 0 else f"missing {missing}"
        if created < "2026-09-22":
            result = f"exempt ({'would pass' if run.returncode == 0 else 'missing ' + missing})"
        phases = sum(1 for it in items if it.get("plan") == meta["id"])
        parent = docs[meta["parent"]]["code"] if meta.get("parent") else ""
        words = len(meta["text"].split())
        rel = path.removeprefix("docs/01-plans/")
        print(f"| {code} | `{rel}` | {layout} | {parent} | {status} | {created} | {phases} | {words} "
              f"| {result} |")


def cmd_folders() -> None:
    base = pathlib.Path("docs/01-plans")
    tracked = subprocess.run(["git", "ls-files", str(base)], capture_output=True, text=True).stdout
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        print(f"{folder.name}/")
        for line in tracked.splitlines():
            if line.startswith(f"{folder}/"):
                print("  " + line.removeprefix(f"{folder}/"))
    loose = [x for x in tracked.splitlines() if x.count("/") == 2 and not x.startswith("docs/01-plans/PLAN-")]
    print("not a plan document, directly under docs/01-plans/:", loose)


def links(docs: dict[str, dict[str, Any]]) -> tuple[dict, dict, dict]:
    """Structured and prose links from each non-plan document to plan families (by root id)."""
    items = backlog_items()
    plans = {i for i, d in docs.items() if d["kind"] == "plan"}
    root = {i: (docs[i].get("parent") or i) for i in plans}
    struct: dict[str, set] = collections.defaultdict(set)
    prose: dict[str, set] = collections.defaultdict(set)
    for i, d in docs.items():
        if d["kind"] != "plan":
            for dep in d.get("depends_on") or []:
                if dep in plans:
                    struct[i].add((root[dep], "its depends_on names the plan"))
    for pid in plans:
        for dep in docs[pid].get("depends_on") or []:
            if dep in docs and docs[dep]["kind"] != "plan":
                struct[dep].add((root[pid], "plan depends_on names it"))
    for it in items:
        for src in it.get("sources") or []:
            if src in docs and docs[src]["kind"] != "plan" and it.get("plan") in root:
                struct[src].add((root[it["plan"]], "phase sources"))
    codes = {docs[p]["code"]: root[p] for p in plans}
    phase_plan = {it["id"]: root.get(it.get("plan")) for it in items}
    for i, d in docs.items():
        if d["kind"] == "plan":
            continue
        for code in set(PLAN_CODE.findall(d["text"])):
            if code in codes:
                prose[i].add(codes[code])
        for ph in set(PHASE_ID.findall(d["text"])):
            if phase_plan.get(ph):
                prose[i].add(phase_plan[ph])
    return struct, prose, root


def cmd_trace(codes: list[str]) -> None:
    docs = governed()
    items = backlog_items()
    fam = families(docs)
    struct, prose, _ = links(docs)
    working = {str(p): p.read_text(errors="ignore") for p in pathlib.Path(WORKING).rglob("*")
               if p.is_file() and p.suffix in (".md", ".yaml", ".json", ".jsonl")}
    reviews = {str(p): json.load(open(p)) for p in sorted(pathlib.Path(REVIEWS).glob("*.json"))}
    for wanted in codes:
        rid = next(i for i, d in docs.items() if d.get("code") == wanted)
        members = fam[rid]
        mcodes = sorted(docs[m]["code"] for m in members)
        phases = [it for it in items if it.get("plan") in members]
        pids = [it["id"] for it in phases]
        print(f"## {wanted}: {len(members)} document(s) {mcodes}; {len(pids)} phases")
        own_text = "".join(docs[m]["text"] for m in members)
        cited = sorted(set(re.findall(r"\b(?:REQ|ADR|PROMPT|ARCH|GOV|OPS)-\d{3}\b", own_text)))
        print("  cited by code in the plan's own text:", " ".join(cited))
        print("  paths cited in the plan's own text:",
              sorted(set(re.findall(r"(?:_working|docs/00-working|research)/[\w./-]+", own_text))))
        for i, d in sorted(docs.items(), key=lambda kv: kv[1]["code"]):
            if i in members:
                continue
            how = sorted({w for p, w in struct[i] if p == rid})
            if rid in prose[i]:
                how.append("code or phase id in prose")
            if how and d["kind"] in ("requirement", "adr", "prompt", "session", "architecture",
                                     "governance", "operation"):
                print(f"  {d['kind']:12} {d['code']:20} {', '.join(how)}")
        pat = re.compile(r"\b(" + "|".join(map(re.escape, mcodes + pids)) + r")\b")
        for path, text in working.items():
            if pat.search(text):
                print(f"  {'working':12} {path}")
        for path, rec in reviews.items():
            if rec.get("target", {}).get("plan") in mcodes:
                print(f"  {'review':12} {path}")
        deliver = collections.Counter(
            str(pathlib.PurePosixPath(dv).parent) for it in phases for dv in it.get("deliverables") or [])
        print("  phase deliverables by directory:", dict(deliver))


def cmd_scatter() -> None:
    docs = governed()
    struct, prose, _ = links(docs)
    print("| Kind | Total | Plan-side link to one plan | Plan-side link to several | Only the "
          "artifact names the plan | Prose mention only | No link |")
    print("|---|---|---|---|---|---|---|")
    for kind in ["requirement", "adr", "prompt", "session", "architecture", "governance", "operation"]:
        ids = [i for i, d in docs.items() if d["kind"] == kind]
        side = {i: {p for p, w in struct[i] if w != "its depends_on names the plan"} for i in ids}
        one = sum(1 for i in ids if len(side[i]) == 1)
        many = [i for i in ids if len(side[i]) >= 2]
        back = sum(1 for i in ids if not side[i] and struct[i])
        only_prose = sum(1 for i in ids if not struct[i] and prose[i])
        none = [docs[i]["code"] for i in ids if not struct[i] and not prose[i]]
        print(f"| {kind} | {len(ids)} | {one} | {len(many)} | {back} | {only_prose} | {len(none)} |")
        for i in many:
            print(f"|  | {docs[i]['code']} shared by "
                  f"{', '.join(sorted(docs[p]['code'] for p in side[i]))} | | | | | |")
    recs = sorted(pathlib.Path(REVIEWS).glob("*.json"))
    targets = [json.load(open(p)).get("target", {}).get("plan", "") for p in recs]
    coded = [t for t in targets if PLAN_CODE.fullmatch(t)]
    print(f"review records: {len(recs)} under {REVIEWS}/; {len(coded)} target a plan code, "
          f"covering {len(set(coded))} plans {sorted(set(coded))}; others target {sorted(set(targets) - set(coded))}")


def cmd_prompts() -> None:
    docs = governed()
    struct, prose, _ = links(docs)
    for i, d in sorted(docs.items(), key=lambda kv: kv[1]["code"]):
        if d["kind"] != "prompt":
            continue
        s = sorted({docs[p]["code"] for p, _ in struct[i]})
        pr = sorted({docs[p]["code"] for p in prose[i]} - set(s))
        print(f"{d['code']} structured={s} prose-only={pr} | {str(d['title'])[:80]}")
    loose = sorted(str(p) for p in pathlib.Path(WORKING).rglob("*PROMPT*"))
    print("prompt files under docs/00-working/:", loose)


def cmd_decisions() -> None:
    by_path = {d["path"]: d for d in governed().values()}
    for code, _, path in catalog_plans():
        body = by_path[path]["text"].split("---", 2)[2]
        fenced, current = False, None
        words: dict[str, int] = collections.Counter()
        total = 0
        for line in body.splitlines():
            if line.startswith("```"):
                fenced = not fenced
            head = re.match(r"^## (.+)$", line) if not fenced else None
            if head:
                current = head.group(1).strip()
                continue
            n = len(line.split())
            total += n
            if current and DECISION_H2.match(current):
                words[current] += n
        share = sum(words.values())
        print(f"{code} words={total} decision-section words={share} "
              f"({100 * share / max(total, 1):.0f}%) {sorted(words)}")


def cmd_gov003() -> None:
    text = open(GOV003).read()
    sections = [p for p in re.split(r"\n(?=## )", text) if p.startswith("## ")]
    named = 0
    for s in sections:
        codes = sorted(set(PLAN_CODE.findall(s)))
        phases = len(set(PHASE_ID.findall(s)))
        named += bool(codes or phases)
        print(f"{s.splitlines()[0][3:80]} | plan codes {codes} | phase ids {phases}")
    print(f"{len(sections)} sections; {named} name a plan code or a phase id")


if __name__ == "__main__":
    command, *rest = sys.argv[1:] or ["plans"]
    {"plans": cmd_plans, "folders": cmd_folders, "scatter": cmd_scatter, "prompts": cmd_prompts,
     "decisions": cmd_decisions, "gov003": cmd_gov003}.get(command, lambda: cmd_trace(rest))()
