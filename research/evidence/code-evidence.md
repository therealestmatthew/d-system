# Repository evidence register

Snapshot: the commit “Document the recommended build order for the idea-node classification work”, reviewed 2026-09-09.

Each review citation resolves to the original repository-relative location and this exact excerpt. Confidence is confidence in the local interpretation, not in the proposed architecture or source truth. Negative claims are bounded to the inspected implementation and inventory. Research references are hypotheses. No private portfolio content is reproduced.

## E01

Location: `src/main.py:6-20`

```text
app = FastAPI(title="D-System API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

Interpretation: The application mounts an empty domain router and serves a static health response; health is not a database readiness check.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E02

Location: `src/api/__init__.py:1-7`

```text
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

# Register route modules here as they are created:
# from src.api.routes import people, projects
# router.include_router(people.router)
```

Interpretation: Domain route registration is commented out; no domain CRUD contract is implemented.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E03

Location: `ts/src/App.tsx:1-3`

```text
export default function App() {
  return <h1>D-System</h1>
}
```

Interpretation: The UI renders only a heading; no business workflow is exposed here.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E04

Location: `tools/rebuild_db.py:103-130`

```text
def rebuild(root: Path | None = None) -> None:
    root = ROOT if root is None else root
    # tags.json and ideas.jsonl are shared structure (ADR-009) and always read from the
    # tracked _data/. Entity content honours D_SYSTEM_DATA_ROOT via entities below.
    data = root / "_data"
    entities = data_root(root)
    brain = root / "brain"
    db_path = root / "data" / "d_system.duckdb"

    # Before mkdir and before connect: a failed validation must leave the filesystem
    # exactly as it found it, including not creating data/ on a first run.
    errors = validate_sources(root)
    if errors:
        print(f"Source validation failed — {len(errors)} problem(s), nothing written:")
        print(format_errors(errors))
        raise SystemExit(1)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db_path))

    # Full drop + recreate — deterministic rebuild. Views first: DuckDB refuses to drop
    # a table a view still references.
    for view in VIEWS_DROP_ORDER:
        conn.execute(f"DROP VIEW IF EXISTS {view}")
    for table in TABLES_DROP_ORDER:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    _execute_sql_file(conn, SCHEMA_SQL)
    _execute_sql_file(conn, CAPTURE_VIEWS_SQL)
```

Interpretation: Preflight precedes drop/recreate, but there is no encompassing transaction or swap. Duplicate IDs can pass per-file validation and fail after old tables are removed.

Confidence: HIGH. Alternative/limit: Preflight protects against many malformed sources; source files still permit recovery of a failed derived database.

## E05

Location: `src/db/source_validation.py:136-174`

```text

def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def validate_entities(root: Path, validators: _Validators) -> list[SourceError]:
    """Every JSON file under the entity content root, against the schema its directory
    implies. `tags.json` is shared taxonomy (ADR-009) and always read from the tracked
    `_data/`, independent of `data_root()`.
    """
    errors: list[SourceError] = []
    data = data_root(root)

    tags_path = root / "_data" / "tags.json"
    if tags_path.exists():
        name = _relative(tags_path, root)
        try:
            tags = json.loads(tags_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(SourceError(name, "", f"invalid JSON: {exc}"))
        else:
            if not isinstance(tags, list):
                errors.append(SourceError(name, "", "expected a list of tags"))
            else:
                for index, tag in enumerate(tags):
                    errors.extend(
                        _validate(validators, "tag", tag, f"{name}[{index}]")
                    )

    for directory, schema in ENTITY_DIRECTORIES.items():
        source = data / directory
        if not source.is_dir():
            continue
        for path in sorted(source.glob("*.json")):
            name = _relative(path, root)
            try:
```

Interpretation: Entity validation is per file and per schema, with no referential or cross-file identity pass in this loop.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E06

Location: `sql/001_schema.sql:4-80`

```text
CREATE TABLE projects (
    id                  VARCHAR PRIMARY KEY,
    name                VARCHAR NOT NULL,
    status              VARCHAR NOT NULL,   -- active|inactive|planning|blocked|complete|archived
    category            VARCHAR NOT NULL,   -- work|learning|system|personal
    type                VARCHAR NOT NULL,   -- project|activity|goal|system|certification
    description         VARCHAR DEFAULT '',
    tags                VARCHAR[],
    started             DATE,
    target_date         DATE,
    last_reviewed       DATE,
    review_cadence      VARCHAR,
    notes               VARCHAR DEFAULT ''
);

CREATE TABLE people (
    id              VARCHAR PRIMARY KEY,
    name            VARCHAR NOT NULL,
    role            VARCHAR,
    organization    VARCHAR,
    email           VARCHAR,
    notes           VARCHAR DEFAULT ''
);

CREATE TABLE project_people (
    project_id  VARCHAR,
    person_id   VARCHAR,
    PRIMARY KEY (project_id, person_id)
);

CREATE TABLE tags (
    id          VARCHAR PRIMARY KEY,
    label       VARCHAR NOT NULL,
    category    VARCHAR NOT NULL,
    description VARCHAR DEFAULT '',
    related     VARCHAR[],
    deprecated  BOOLEAN DEFAULT false
);

CREATE TABLE project_tags (
    project_id  VARCHAR,
    tag_id      VARCHAR,
    PRIMARY KEY (project_id, tag_id)
);

CREATE TABLE commitments (
    id          VARCHAR PRIMARY KEY,
    project_id  VARCHAR,
    description VARCHAR NOT NULL,
    promised_to VARCHAR,
    due_date    DATE,
    status      VARCHAR NOT NULL,
    priority    VARCHAR NOT NULL,
    created     DATE NOT NULL,
    completed   DATE,
    notes       VARCHAR DEFAULT ''
);

-- Tasks are first-class records loaded from _data/tasks/, not unpacked from a
-- commitment's embedded array (ADR-008: an entity that can exist without a parent
-- cannot be stored inside one). Both parents are optional.
CREATE TABLE tasks (
    id              VARCHAR PRIMARY KEY,
    commitment_id   VARCHAR,
    project_id      VARCHAR,
    description     VARCHAR NOT NULL,
    status          VARCHAR NOT NULL,
    priority        VARCHAR,
    due_date        DATE,
    created         DATE NOT NULL,
    completed       DATE,
    sort_order      INTEGER DEFAULT 0,
    tags            VARCHAR[],
    notes           VARCHAR DEFAULT ''
);

-- A dated meeting, call or exchange. See schemas/interaction.schema.json.
```

Interpretation: Projects, people, tags, commitments and tasks are relational projections with primary keys and nullable references, but no foreign keys or enum CHECK constraints.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E07

Location: `sql/001_schema.sql:95-158`

```text
    id                  VARCHAR PRIMARY KEY,
    date                DATE NOT NULL,
    decision            VARCHAR NOT NULL,
    rationale           VARCHAR NOT NULL,
    project_id          VARCHAR,
    interaction_id      VARCHAR,
    decided_by          VARCHAR[],
    decided_by_names    VARCHAR[],
    alternatives        VARCHAR[],
    status              VARCHAR NOT NULL DEFAULT 'active',
    supersedes          VARCHAR,
    tags                VARCHAR[],
    notes               VARCHAR DEFAULT ''
);

-- Something another party owes the owner — the mirror of a commitment. See
-- schemas/waiting-on.schema.json.
CREATE TABLE waiting_on (
    id              VARCHAR PRIMARY KEY,
    description     VARCHAR NOT NULL,
    owed_by         VARCHAR,
    project_id      VARCHAR,
    requested       DATE NOT NULL,
    due_date        DATE,
    status          VARCHAR NOT NULL,
    last_chased     DATE,
    received        DATE,
    priority        VARCHAR,
    tags            VARCHAR[],
    notes           VARCHAR DEFAULT ''
);

-- A training, certification, talk or milestone. See schemas/development-event.schema.json.
CREATE TABLE development_events (
    id              VARCHAR PRIMARY KEY,
    date            DATE NOT NULL,
    type            VARCHAR NOT NULL,
    title           VARCHAR NOT NULL,
    description     VARCHAR DEFAULT '',
    project_id      VARCHAR,
    provider        VARCHAR,
    credential      VARCHAR,
    hours           DOUBLE,
    tags            VARCHAR[],
    notes           VARCHAR DEFAULT ''
);

-- Shared model-agnostic memory. Source: brain/**/*.md (YAML frontmatter + Markdown body)
CREATE TABLE memories (
    id           VARCHAR PRIMARY KEY,
    title        VARCHAR NOT NULL,
    type         VARCHAR NOT NULL,
    tags         VARCHAR[],
    systems      VARCHAR[],
    source_model VARCHAR,
    project_id   VARCHAR,
    created      DATE NOT NULL,
    updated      DATE,
    confidence   VARCHAR DEFAULT 'medium',
    related      VARCHAR[],
    scope        VARCHAR DEFAULT 'global',
    content      VARCHAR NOT NULL,
    file_path    VARCHAR
);
```

Interpretation: Decisions, waiting-on, development events and memories are current-state rows, not versioned reasoning states.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E08

Location: `tools/rebuild_db.py:146-178`

```text
    # --- Projects ---
    for path in _glob(entities / "projects", "*.json"):
        p = _load_json(path)
        conn.execute(
            "INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                p["id"], p["name"], p["status"], p["category"], p["type"],
                p.get("description", ""),
                p.get("tags", []),
                p.get("started"), p.get("target_date"), p.get("last_reviewed"),
                p.get("review_cadence"),
                p.get("notes", ""),
            ],
        )
        for tag_id in p.get("tags", []):
            conn.execute("INSERT INTO project_tags VALUES (?, ?)", [p["id"], tag_id])

    # --- People ---
    for path in _glob(entities / "people", "*.json"):
        person = _load_json(path)
        conn.execute(
            "INSERT INTO people VALUES (?, ?, ?, ?, ?, ?)",
            [
                person["id"], person["name"], person.get("role"),
                person.get("organization"), person.get("email"),
                person.get("notes", ""),
            ],
        )
        for project_id in person.get("projects", []):
            conn.execute(
                "INSERT INTO project_people VALUES (?, ?)",
                [project_id, person["id"]],
            )
```

Interpretation: Projects load selected fields; stakeholder edges are loaded only from people.projects, not project.stakeholders.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E09

Location: `tools/rebuild_db.py:180-256`

```text
    # --- Commitments ---
    for path in _glob(entities / "commitments", "*.json"):
        c = _load_json(path)
        conn.execute(
            "INSERT INTO commitments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                c["id"], c.get("project_id"), c["description"],
                c.get("promised_to"), c.get("due_date"),
                c.get("status", "open"), c.get("priority", "medium"),
                c["created"], c.get("completed"), c.get("notes", ""),
            ],
        )

    # --- Tasks (_data/tasks/) — first-class records, no longer unpacked from a
    # commitment's embedded array. sort_order has no source once tasks are independent
    # files, so it is always 0; nothing orders by it.
    for path in _glob(entities / "tasks", "*.json"):
        t = _load_json(path)
        conn.execute(
            "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                t["id"], t.get("commitment_id"), t.get("project_id"),
                t["description"], t.get("status", "open"), t.get("priority"),
                t.get("due_date"), t["created"], t.get("completed"),
                0, t.get("tags", []), t.get("notes", ""),
            ],
        )

    # --- Interactions ---
    for path in _glob(entities / "interactions", "*.json"):
        i = _load_json(path)
        conn.execute(
            "INSERT INTO interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                i["id"], i["date"], i["type"], i["summary"], i.get("project_id"),
                i.get("participants", []), i.get("participant_names", []),
                i.get("tags", []), i.get("notes", ""),
            ],
        )

    # --- Decisions ---
    for path in _glob(entities / "decisions", "*.json"):
        d = _load_json(path)
        conn.execute(
            "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                d["id"], d["date"], d["decision"], d["rationale"],
                d.get("project_id"), d.get("interaction_id"),
                d.get("decided_by", []), d.get("decided_by_names", []),
                d.get("alternatives", []), d.get("status", "active"),
                d.get("supersedes"), d.get("tags", []), d.get("notes", ""),
            ],
        )

    # --- Waiting-on (_data/waiting-on/) ---
    for path in _glob(entities / "waiting-on", "*.json"):
        w = _load_json(path)
        conn.execute(
            "INSERT INTO waiting_on VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                w["id"], w["description"], w.get("owed_by"), w.get("project_id"),
                w["requested"], w.get("due_date"), w["status"],
                w.get("last_chased"), w.get("received"), w.get("priority"),
                w.get("tags", []), w.get("notes", ""),
            ],
        )

    # --- Development events (_data/development-events/) ---
    for path in _glob(entities / "development-events", "*.json"):
        e = _load_json(path)
        conn.execute(
            "INSERT INTO development_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                e["id"], e["date"], e["type"], e["title"], e.get("description", ""),
                e.get("project_id"), e.get("provider"), e.get("credential"),
                e.get("hours"), e.get("tags", []), e.get("notes", ""),
            ],
```

Interpretation: Entity insertion omits capture metadata; commitments also omit source tags. Source retention is stronger than queryable projection fidelity.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E10

Location: `tools/rebuild_db.py:259-328`

```text
    # --- Ideas (_data/ideas.jsonl) ---
    #
    # idea_events is loaded in file order and kept in full; `ideas` is folded from it below.
    ideas_path = data / "ideas.jsonl"
    if ideas_path.exists():
        events = [
            json.loads(line)
            for line in ideas_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        counters: dict[str, int] = {}
        for event in events:
            idea = event["idea"]
            counters[idea] = counters.get(idea, 0) + 1
            # `title`/`body`/`text` are plain strings on the event that introduces them, but a
            # field_shape object on `amended` ({"set": ..., "value": ...}) — unwrap to the value
            # for the record, same as the effective fold does when it applies the amendment.
            # `target` is a plain string on `linked`, or a link_retraction shape on `amended`
            # ({"set": true, "value": null}) — unwrapping it the same way always yields None,
            # which is exactly what a retraction records.
            title = event.get("title")
            body = event.get("body")
            text = event.get("text")
            target = event.get("target")
            promoted_to = event.get("promoted_to")
            conn.execute(
                "INSERT INTO idea_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    idea, idea_identity(event), counters[idea], event["event"], event["at"],
                    title.get("value") if isinstance(title, dict) else title,
                    body.get("value") if isinstance(body, dict) else body,
                    event.get("from"), event.get("to"),
                    [promoted_to] if isinstance(promoted_to, str) else promoted_to,
                    event.get("amends"),
                    event.get("author"), event.get("kind"),
                    text.get("value") if isinstance(text, dict) else text,
                    event.get("type"),
                    target.get("value") if isinstance(target, dict) else target,
                ],
            )

        # Folded here, not read from source, with the same replay tools/append_idea.py
        # applies before deciding whether a transition is legal — writer and projection
        # cannot disagree about what state an idea is in. validate_sources() has already
        # run this same fold as part of the preflight above, so it cannot raise here.
        folded = fold_ideas(events)
        for idea, state in folded.items():
            conn.execute(
                "INSERT INTO ideas VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    idea, state["title"], state["body"], state["status"],
                    state["created"], state["updated"],
                    state["revisits"], state["promoted_to"],
                ],
            )
            for annotation in state["annotations"]:
                conn.execute(
                    "INSERT INTO idea_annotations VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        idea, annotation["eid"], annotation["author"], annotation["kind"],
                        annotation["text"], annotation["at"],
                    ],
                )
            for link in state["links"]:
                conn.execute(
                    "INSERT INTO idea_links VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        idea, link["eid"], link["type"], link["target"],
                        link["retracted"], link["at"],
                    ],
```

Interpretation: Raw idea event rows and effective idea/annotation/link projections coexist; field-shape flags are flattened in SQL, so SQL rows are not lossless raw JSON events.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E11

Location: `src/db/ideas.py:45-92`

```text
    """A refusal the caller can act on, printed without a traceback."""


def canonical_bytes(event: dict[str, Any]) -> bytes:
    """A deterministic encoding of an event, independent of key order or whitespace."""
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def identity(event: dict[str, Any]) -> str:
    """The identity an `amends` pointer names: `eid` when present, else a digest of the event.

    The 19 events written before `eid` existed have no way to carry one without rewriting an
    append-only log, so their identity is a pure function of bytes that are already permanent.
    Two events resolving to the same identity — a digest collision for a legacy line, a writer
    bug for a new one — is a fold-time error (`_identity_index`), never a silent merge.
    """
    eid = event.get("eid")
    if eid:
        return str(eid)
    return hashlib.sha256(canonical_bytes(event)).hexdigest()[:16]


def new_eid() -> str:
    """A short, lexicographically sortable identity for a newly written event.

    Nanosecond epoch time, zero-padded to a fixed width: fixed-width zero-padded hex sorts
    identically to the numeric value it encodes, so identities sort in write order without
    parsing them. Collision would require two events on the same process to be built in the
    same nanosecond, which nothing here does.
    """
    return f"e{time.time_ns():016x}"


def _schema() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return data


def legal_transitions() -> set[tuple[str, str]]:
    """Read the transition table out of the schema rather than restating it here.

    Two copies of a rule is one copy and one liability. The schema is where the machine is
    declared, so the writer, the projection and the tests all read the same statement.
    """
    for branch in _schema()["allOf"]:
        if branch.get("if", {}).get("properties", {}).get("event", {}).get("const") != "status":
```

Interpretation: Explicit event IDs and deterministic legacy hashes address amendments; legal transitions are read from the schema.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E12

Location: `src/db/ideas.py:133-163`

```text
        index[ident] = (position, event)
    return index


def _amendments_by_target(
    events: list[dict[str, Any]], id_index: dict[str, tuple[int, dict[str, Any]]]
) -> dict[str, list[dict[str, Any]]]:
    """Group `amended` events by the identity they target, validating each target.

    A target must exist, must appear earlier in the log than the amendment naming it, and
    must belong to the same idea. All three are refused here — before any append, and before
    the rebuild writes a row — rather than left for whatever later reads `amends` to notice.
    """
    by_target: dict[str, list[dict[str, Any]]] = {}
    for position, event in enumerate(events):
        if event.get("event") != "amended":
            continue
        target = event["amends"]
        if target not in id_index:
            raise IdeaError(
                f"{event['idea']}: amendment targets {target!r}, which is not in the log"
            )
        target_position, target_event = id_index[target]
        if target_position >= position:
            raise IdeaError(
                f"{event['idea']}: amendment targets {target!r}, which does not appear "
                "earlier in the log — an amendment cannot target itself or a later event"
            )
        if target_event["idea"] != event["idea"]:
            raise IdeaError(
                f"{event['idea']}: amendment targets {target!r}, which belongs to idea "
```

Interpretation: Amendment targets must be earlier and on the same idea. This guarantees acyclic correction references, not a general reasoning graph.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E13

Location: `src/db/ideas.py:166-205`

```text
            )
        by_target.setdefault(target, []).append(event)
    return by_target


def _effective_fields(
    ident: str,
    id_index: dict[str, tuple[int, dict[str, Any]]],
    by_target: dict[str, list[dict[str, Any]]],
    memo: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """The field_shape each amendable field resolves to, after every amendment targeting it.

    Starts from the event's own contribution (`{"set": True, "value": v}` for whichever of
    `AMENDABLE_FIELDS` it carries), then applies each amendment targeting it in append order,
    recursing first into amendments of amendments so a correction is itself correctable
    (`effective(e)` in PLAN-017.03). Because `_amendments_by_target` already proved every
    target strictly precedes its amendment, this recursion cannot cycle.
    """
    if ident in memo:
        return memo[ident]
    _, event = id_index[ident]
    if event.get("event") == "amended":
        fields = {field: event[field] for field in AMENDABLE_FIELDS if field in event}
    else:
        fields = {
            field: {"set": True, "value": event[field]}
            for field in AMENDABLE_FIELDS
            if field in event
        }
    result = dict(fields)
    for amender in by_target.get(ident, []):
        amender_fields = _effective_fields(identity(amender), id_index, by_target, memo)
        for field, shape in amender_fields.items():
            if shape.get("set"):
                result[field] = shape
    memo[ident] = result
    return result


```

Interpretation: Corrections recursively resolve in append order; later competing values win in effective state while source events survive.

Confidence: HIGH. Alternative/limit: This preserves recoverable disagreement as history but does not maintain concurrently accepted actor-specific stances.

## E14

Location: `src/db/ideas.py:225-316`

```text
    if isinstance(value, str):
        return [value]
    return list(value)


def fold(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Replay events into current state, validating history as it goes.

    A schema checks one line in isolation; this is what checks a line against the ones
    before it. Every rule that needs more than one line lives here: a `created` event is
    unique per idea and precedes everything else about it, a `status` event's `from` equals
    the status this replay has actually reached — the single highest-value check, because
    without it a hand-edited or replayed line can silently rewrite history — the `from -> to`
    pair is in the schema's transition table, and `revisited` fires only from `discarded`
    and at most once. It runs before any append and before the rebuild drops a table.

    `amended` events never advance the machine themselves — they correct what a `created`,
    `status`, `revisited`, `annotated` or `linked` event resolves to (`_effective_event`), so
    only those five kinds are replayed here. `annotated` and `linked` are permitted regardless
    of status, terminal included (`PLAN-017.04`): they extend the record, not the state machine.
    """
    transitions = legal_transitions()
    id_index = _identity_index(events)
    by_target = _amendments_by_target(events, id_index)
    memo: dict[str, dict[str, dict[str, Any]]] = {}
    state: dict[str, dict[str, Any]] = {}
    for raw_event in events:
        if raw_event["event"] == "amended":
            continue
        event = _effective_event(raw_event, id_index, by_target, memo)
        idea = event["idea"]
        kind = event["event"]
        if kind == "created":
            if idea in state:
                raise IdeaError(f"{idea} was already created — a second created event follows it")
            state[idea] = {
                "title": event["title"],
                "body": event["body"],
                "status": "open",
                "created": event["at"],
                "updated": event["at"],
                "revisits": 0,
                "promoted_to": None,
                "annotations": [],
                "links": [],
            }
            continue
        if idea not in state:
            raise IdeaError(f"event for unknown idea {idea} — no created event precedes it")
        current = state[idea]
        if kind == "status":
            source, target = event["from"], event["to"]
            if source != current["status"]:
                raise IdeaError(
                    f"{idea}: status event declares from={source!r} but the replay had "
                    f"already reached {current['status']!r}"
                )
            if (source, target) not in transitions:
                raise IdeaError(f"{idea}: illegal transition {source} -> {target}")
            current["status"] = target
            current["updated"] = event["at"]
            if target == "promoted":
                current["promoted_to"] = _as_promoted_to(event.get("promoted_to"))
        elif kind == "revisited":
            if current["status"] != "discarded":
                raise IdeaError(
                    f"{idea}: revisited but the replay had reached {current['status']!r}, "
                    "not discarded"
                )
            if current["revisits"] >= 1:
                raise IdeaError(f"{idea} was already revisited once — a second revisit follows it")
            current["status"] = "reviewing"
            current["updated"] = event["at"]
            current["revisits"] += 1
        elif kind == "annotated":
            current["annotations"].append({
                "eid": identity(raw_event),
                "author": event["author"],
                "kind": event["kind"],
                "text": event["text"],
                "at": event["at"],
            })
            current["updated"] = event["at"]
        elif kind == "linked":
            target_idea = event.get("target")
            current["links"].append({
                "eid": identity(raw_event),
                "type": event["type"],
                "target": target_idea,
                "retracted": target_idea is None,
                "at": event["at"],
            })
```

Interpretation: Replay skips amendment events and assigns updated from non-amendment timestamps. Amendments can change effective content without updating the recency field; prefix replay remains possible.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E15

Location: `src/db/ideas.py:319-376`

```text


def link_diagnostics(state: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Fold-time diagnostics, keyed by the idea each is reported against (per-idea, `PLAN-017.04`).

    Never raises: a cycle or a stale supersession is a modelling mistake worth surfacing, not a
    reason to refuse the append that revealed it (`ADR-010`'s capture-always-wins principle,
    extended to links). Two checks: an `extends` cycle is flagged against every idea on it, and
    a `supersedes` edge whose target is not `discarded` is flagged against the idea asserting it.
    """
    diagnostics: dict[str, list[str]] = {}

    def flag(idea: str, message: str) -> None:
        diagnostics.setdefault(idea, []).append(message)

    graph: dict[str, list[str]] = {
        idea: [
            link["target"] for link in entry["links"]
            if link["type"] == "extends" and not link["retracted"]
        ]
        for idea, entry in state.items()
    }
    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(graph, WHITE)

    def visit(node: str, stack: list[str]) -> None:
        color[node] = GRAY
        stack.append(node)
        for target in graph.get(node, []):
            if target not in color:
                continue
            if color[target] == WHITE:
                visit(target, stack)
            elif color[target] == GRAY:
                cycle = stack[stack.index(target):] + [target]
                message = "extends cycle: " + " -> ".join(cycle)
                for member in cycle[:-1]:
                    flag(member, message)
        stack.pop()
        color[node] = BLACK

    for idea in graph:
        if color[idea] == WHITE:
            visit(idea, [])

    for idea, entry in state.items():
        for link in entry["links"]:
            if link["retracted"] or link["type"] != "supersedes":
                continue
            target_entry = state.get(link["target"])
            if target_entry is not None and target_entry["status"] != "discarded":
                flag(
                    idea,
                    f"{idea} marks {link['target']} as superseded, but {link['target']} is "
                    f"{target_entry['status']!r}, not discarded",
                )

    return diagnostics
```

Interpretation: Extends cycles and supersession of non-discarded targets are warnings; supersession does not mutate the target lifecycle.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E16

Location: `tools/append_idea.py:190-195`

```text
def append(event: dict[str, Any], log: Path = LOG) -> None:
    """Validate, then append one line. Nothing already in the file is read or rewritten."""
    validate(event)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
```

Interpretation: Low-level append validates one event and writes a line without locking or history checks. High-level operations add selected checks.

Confidence: HIGH. Alternative/limit: This is a trusted local CLI convention, not an authenticated multi-writer service; do not claim a remote security exploit.

## E17

Location: `tools/append_idea.py:222-252`

```text
def add(title: str, body: str, log: Path = LOG) -> dict[str, Any]:
    state = fold(load_events(log))
    event = build_created(_next_id(state), title.strip(), body.strip(), _now(), new_eid())
    append(event, log)
    return event


def change_status(
    idea: str, target: str, promoted_to: list[str] | None = None, log: Path = LOG
) -> dict[str, Any]:
    state = fold(load_events(log))
    current = _require(state, idea)
    source = current["status"]

    if source == "discarded" and current["revisits"] >= 1:
        raise IdeaError(
            f"idea {idea} was discarded after being revisited — that is permanent. "
            "An idea worth a third look is a new idea; record it separately."
        )
    if (source, target) not in legal_transitions():
        raise IdeaError(
            f"illegal transition for idea {idea}: {source} -> {target}. "
            f"Legal from {source}: "
            + (", ".join(sorted(t for f, t in legal_transitions() if f == source)) or "none")
        )
    if target == "promoted" and not promoted_to:
        raise IdeaError("--promoted-to is required when promoting: name what the idea became")

    event = build_status(idea, source, target, _now(), new_eid(), promoted_to)
    append(event, log)
    return event
```

Interpretation: ID allocation reads current log then appends; promotion requires a nonempty target but not a real governed document.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E18

Location: `tools/append_idea.py:311-345`

```text
def annotate(
    idea: str, author: str, kind: str, text: str, log: Path = LOG
) -> dict[str, Any]:
    """Add a note, finding or assessment to `idea` — permitted whatever its status.

    A non-owner `author` (an agent) is restricted to `kind: finding`, so the owner's own
    voice in the log stays unambiguous (`PLAN-017.04`, settled 2026-09-08).
    """
    state = fold(load_events(log))
    _require(state, idea)
    if kind not in ANNOTATION_KINDS:
        raise IdeaError(f"unknown annotation kind {kind!r} — expected one of {ANNOTATION_KINDS}")
    if author != "repository-owner" and kind != "finding":
        raise IdeaError(
            f"agent author {author!r} may only write kind=finding, not {kind!r} — "
            "note and assessment stay the owner's own voice"
        )
    event = build_annotated(idea, author, kind, text.strip(), _now(), new_eid())
    append(event, log)
    return event


def amend_annotation(idea: str, eid: str, text: str, log: Path = LOG) -> dict[str, Any]:
    """Correct one annotation's text by its own identity; the others are untouched."""
    events = load_events(log)
    state = fold(events)
    _require(state, idea)
    if not any(
        e["idea"] == idea and e["event"] == "annotated" and identity(e) == eid for e in events
    ):
        raise IdeaError(f"no annotation {eid!r} on idea {idea}")
    event = build_amended(idea, eid, _now(), new_eid(), text=text.strip())
    validate(event)
    fold(events + [event])
    append(event, log)
```

Interpretation: High-level annotate restricts non-owner kind to finding, but author is a caller-supplied string and amendment lacks separate actor attribution.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E19

Location: `tools/append_idea.py:349-385`

```text
def link(idea: str, type_: str, target: str, log: Path = LOG) -> tuple[dict[str, Any], list[str]]:
    """Assert a typed edge from `idea` to `target`.

    Never refused for a cycle or a stale supersession — those are fold-time diagnostics
    (`link_diagnostics`), returned alongside the appended event rather than blocking it
    (`ADR-010`'s capture-always-wins principle, extended to links).
    """
    events = load_events(log)
    state = fold(events)
    _require(state, idea)
    if type_ not in LINK_TYPES:
        raise IdeaError(f"unknown link type {type_!r} — expected one of {LINK_TYPES}")
    if target == idea:
        raise IdeaError(f"idea {idea} cannot link to itself")
    if target not in state:
        raise IdeaError(f"link target {target!r} is not a known idea")
    event = build_linked(idea, type_, target, _now(), new_eid())
    validate(event)
    new_state = fold(events + [event])
    diagnostics = link_diagnostics(new_state).get(idea, [])
    append(event, log)
    return event, diagnostics


def retract_link(idea: str, eid: str, log: Path = LOG) -> dict[str, Any]:
    """Clear a link's target by its own identity — the one legal amendment to a link."""
    events = load_events(log)
    state = fold(events)
    _require(state, idea)
    if not any(
        e["idea"] == idea and e["event"] == "linked" and identity(e) == eid for e in events
    ):
        raise IdeaError(f"no link {eid!r} on idea {idea}")
    event = build_amended(idea, eid, _now(), new_eid(), retract_target=True)
    validate(event)
    fold(events + [event])
    append(event, log)
```

Interpretation: High-level links check target existence/self-links and retractions preserve old event bytes; low-level imports do not share every guard.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E20

Location: `schemas/idea.schema.json:6-24`

```text
  "type": "object",
  "required": ["idea", "event", "at"],
  "additionalProperties": false,
  "properties": {
    "idea": {
      "type": "string",
      "pattern": "^[0-9]{6}$",
      "description": "Six-digit identifier, assigned by tools/append_idea.py and never reused. Shared by every event about the same idea."
    },
    "event": {
      "type": "string",
      "enum": ["created", "status", "revisited", "amended", "annotated", "linked"],
      "description": "created=the idea was captured | status=its status moved | revisited=a discarded idea was reopened, returning it to reviewing | amended=a prior event's field was corrected without rewriting it | annotated=a note, finding or assessment was added, permitted on terminal ideas | linked=a typed relationship to another idea was asserted"
    },
    "at": {
      "type": "string",
      "format": "date-time",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$",
      "description": "When the event happened, RFC 3339 with a mandatory offset — a naked local time cannot be ordered against one written in another zone, and ordering is the whole point of the log. The pattern carries the enforcement rather than the format keyword: jsonschema only checks date-time when rfc3339-validator is installed, and it is not a dependency here (see phase-rel-11). The format keyword stays as the declaration of intent and starts enforcing the moment that phase lands. Generated by the writer from the real clock; there is deliberately no way to supply one."
```

Interpretation: Idea events use created/status/revisited/amended/annotated/linked; three proposed knowledge classification dimensions are absent and additional fields are forbidden.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E21

Location: `schemas/idea.schema.json:42-100`

```text
      "description": "Status before this event."
    },
    "to": {
      "$ref": "#/definitions/status",
      "description": "Status after this event."
    },
    "promoted_to": {
      "oneOf": [
        { "type": "string", "minLength": 1 },
        { "type": "array", "items": { "type": "string", "minLength": 1 }, "minItems": 1 }
      ],
      "description": "What the idea became — one or more governed document codes, named by id. Required when moving to promoted, because a terminal state that does not say what it produced cannot be audited. Newly written promotions are a non-empty array, so one idea can name several documents; the scalar form on the 19 events written before this was an array is read as a singleton, without rewriting them (phase-idea-08)."
    },
    "eid": {
      "type": "string",
      "minLength": 1,
      "description": "Explicit event identity, generated by the writer for every newly appended event. An amendment names its target by this identity rather than by position, so the pointer survives a rebase or a merge that interleaves two branches' appended lines. Absent on the 19 events written before this field existed; src.db.ideas.identity() falls back to a digest of the event's own bytes for those, so every event has a resolvable identity whether or not it carries one."
    },
    "amends": {
      "type": "string",
      "minLength": 1,
      "description": "The identity (see `eid`) of the event this amendment corrects. Must name an event on the same idea that appears earlier in the log; the writer refuses an absent, forward or foreign target before appending, and the fold refuses one on import."
    },
    "author": {
      "type": "string",
      "minLength": 1,
      "description": "Who wrote this annotation: `repository-owner` or an agent name. The writer restricts a non-owner author to `kind: finding`, so the owner's own voice in the log stays unambiguous."
    },
    "kind": {
      "type": "string",
      "enum": ["note", "finding", "assessment"],
      "description": "note=the owner thinking aloud | finding=what a triage agent writes | assessment=a judgement, itself correctable by a later assessment without either being deleted. An unknown kind fails validation rather than being accepted as free text."
    },
    "text": {
      "oneOf": [
        { "type": "string", "minLength": 1 },
        { "$ref": "#/definitions/field_shape" }
      ],
      "description": "On `annotated`, the contribution itself. On `amended`, the replace/inherit shape correcting it (see `field_shape`); like title and body, an annotation's text can never be cleared — a textless annotation is not a thing. Annotations accumulate: correcting one never touches the others."
    },
    "type": {
      "type": "string",
      "enum": ["extends", "supersedes", "relates_to"],
      "description": "extends=this idea builds on the target | supersedes=this idea replaces the target (does not discard it — that is a separate, explicit status event) | relates_to=a symmetric relationship, reciprocal by construction. Each edge is stored once, on the idea that asserts it; the inverse is derived at fold time and never stored, so the two halves cannot disagree."
    },
    "target": {
      "oneOf": [
        { "type": "string", "pattern": "^[0-9]{6}$" },
        { "$ref": "#/definitions/link_retraction" }
      ],
      "description": "On `linked`, the idea this edge points to. On `amended`, the only legal correction is retraction (see `link_retraction`) — a link never mutates its target; there is no shape that repoints one."
    }
  },
  "definitions": {
    "status": {
      "type": "string",
      "enum": ["open", "triaged", "reviewing", "promoted", "discarded"],
      "description": "open=captured, nothing has looked at it | triaged=scouting finished, awaiting the owner | reviewing=the owner is actively considering it | promoted=became a plan, requirement or phase, terminal | discarded=rejected, terminal unless revisited once"
    },
```

Interpretation: Idea statuses, annotation kinds and semantic edge types are distinct fields; promotion references are unvalidated strings; author is annotation-specific.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E22

Location: `schemas/memory.schema.json:17-69`

```text
    },
    "type": {
      "type": "string",
      "enum": ["concept", "entity", "procedure", "episode", "decision"],
      "description": "concept=how something works | entity=facts about a thing | procedure=how to do something | episode=what happened | decision=why something was chosen"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "Tag IDs from _data/tags.json — enables cross-system filtering"
    },
    "systems": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "System IDs from docs/08-governance/systems.yaml — mirrors what governed documents already carry, and answers 'everything about this subsystem' directly rather than through tags or brain/ folder structure."
    },
    "source_model": {
      "type": "string",
      "description": "Model or human that authored or last substantively edited this entry. Format: provider/model-id or 'human'. Examples: anthropic/claude-sonnet-4-6, openai/gpt-4o, google/gemini-2.0-flash, human"
    },
    "project": {
      "type": ["string", "null"],
      "description": "Project ID this memory belongs to, or null for global memories"
    },
    "created": {
      "type": "string",
      "format": "date"
    },
    "updated": {
      "type": ["string", "null"],
      "format": "date"
    },
    "confidence": {
      "type": "string",
      "enum": ["high", "medium", "low", "uncertain"],
      "default": "medium",
      "description": "How reliable this memory is. Uncertain = needs verification before acting on it."
    },
    "related": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "IDs of related memory entries (mem-*)"
    },
    "scope": {
      "type": "string",
      "enum": ["global", "project", "session"],
      "default": "global",
      "description": "global=applies everywhere | project=scoped to one project | session=temporary, review for promotion to global"
    }
  }
```

Interpretation: Memory type, confidence, related IDs and scope are stored metadata; no memory supersession, actor stance or valid-time model exists in this closed schema.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E23

Location: `tools/load_context.py:29-70`

```text
def build_where(
    query: str | None,
    project: str | None,
    mem_type: str | None,
    tags: list[str],
    system: str | None = None,
) -> tuple[str, list[object]]:
    clauses: list[str] = []
    params: list[object] = []

    if query:
        clauses.append("(LOWER(title) LIKE LOWER(?) OR LOWER(content) LIKE LOWER(?))")
        pattern = f"%{query}%"
        params.extend([pattern, pattern])

    if project:
        clauses.append("(project_id = ? OR project_id IS NULL)")
        params.append(project)

    if mem_type:
        clauses.append("type = ?")
        params.append(mem_type)

    for tag in tags:
        clauses.append("list_contains(tags, ?)")
        params.append(tag)

    if system:
        clauses.append("list_contains(systems, ?)")
        params.append(system)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params


def format_memory(row: tuple) -> str:  # type: ignore[type-arg]
    id_, title, type_, confidence, project_id, created, content, file_path = row
    scope_line = f"project:{project_id}" if project_id else "global"
    header = f"### [{type_.upper()}] {title}"
    meta = f"*id:{id_} | {scope_line} | confidence:{confidence} | {file_path}*"
    body = textwrap.indent(content.strip(), "  ")
    return f"{header}\n{meta}\n\n{body}"
```

Interpretation: Selection uses SQL substring matching and intersected filters. Project nullability determines global eligibility and display; stored scope is ignored.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E24

Location: `tools/load_context.py:73-116`

```text
def load(
    query: str | None = None,
    project: str | None = None,
    mem_type: str | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
    all_memories: bool = False,
    system: str | None = None,
) -> str:
    if not DB_PATH.exists():
        return "Database not found. Run: uv run python tools/rebuild_db.py"

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    if all_memories:
        where, params = "", []
    else:
        where, params = build_where(query, project, mem_type, tags or [], system)

    sql = f"""
        SELECT id, title, type, confidence, project_id, created, content, file_path
        FROM memories
        {where}
        ORDER BY
            CASE confidence WHEN 'high' THEN 0 WHEN 'medium' THEN 1 WHEN 'low' THEN 2 ELSE 3 END,
            created DESC
        LIMIT {limit}
    """
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    if not rows:
        return "No memories matched the query."

    parts = [
        "## Loaded Context — d-system Brain",
        f"*Retrieved: {len(rows)} {'memory' if len(rows) == 1 else 'memories'} | {date.today()}*",
        f"*Query: query={query!r} project={project!r} type={mem_type!r} "
        f"tags={tags} system={system!r}*",
        "---",
    ]
    parts.extend(format_memory(r) for r in rows)
    parts.append("---\n*End of loaded context*")
    return "\n\n".join(parts)
```

Interpretation: Only memories are queried; confidence then created determines order. All-mode removes filters but retains LIMIT. Full bodies are formatted without compression or automatic model invocation.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E25

Location: `tools/rebuild_db.py:331-353`

```text
    # --- Brain memories (brain/**/*.md) ---
    for path in sorted(brain.rglob("*.md")) if brain.exists() else []:
        if path.name == "index.md":
            continue
        mem = _parse_memory(path, root)
        if not mem or "id" not in mem:
            continue
        conn.execute(
            "INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                mem["id"], mem["title"], mem["type"],
                mem.get("tags", []),
                mem.get("systems", []),
                mem.get("source_model"),
                mem.get("project"),
                mem["created"],
                mem.get("updated"),
                mem.get("confidence", "medium"),
                mem.get("related", []),
                mem.get("scope", "global"),
                mem["content"],
                mem["file_path"],
            ],
```

Interpretation: Memory bodies and metadata are snapshots imported from brain Markdown; changes require a rebuild to reach this retrieval path.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E26

Location: `schemas/task.schema.json:5-44`

```text
  "description": "A unit of work, stored in _data/tasks/ as its own record. Both parents are optional: a task may hang off a commitment, off a project, off both, or off neither. Per ADR-008 an entity that can exist without a parent cannot be stored inside one, which is why tasks are no longer an array embedded in commitment JSON. Parentless tasks are real and intended; they must stay visible through the unfiled view or they become a write-only pile.",
  "type": "object",
  "required": ["id", "description", "status", "created"],
  "additionalProperties": false,
  "properties": {
    "id": { "type": "string", "pattern": "^t-[0-9]+" },
    "commitment_id": {
      "type": ["string", "null"],
      "default": null,
      "description": "Commitment this task fulfils, or null when the task stands alone"
    },
    "project_id": {
      "type": ["string", "null"],
      "default": null,
      "description": "Project this task belongs to, or null when unfiled. Not derived from the commitment; set it when it is known."
    },
    "description": { "type": "string" },
    "status": {
      "type": "string",
      "enum": ["open", "in_progress", "complete", "blocked", "cancelled"],
      "default": "open"
    },
    "priority": {
      "type": ["string", "null"],
      "enum": ["high", "medium", "low", null],
      "default": null
    },
    "created": { "type": "string", "format": "date" },
    "due_date": { "type": ["string", "null"], "format": "date" },
    "completed": { "type": ["string", "null"], "format": "date" },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "Tag IDs — must exist in _data/tags.json"
    },
    "notes": { "type": "string", "default": "" },
    "capture": { "$ref": "evidence.schema.json#/definitions/capture_source" }
  }
}
```

Interpretation: Task has optional commitment/project parents and its own status, but no phase or plan reference. Complete does not require completed date.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E27

Location: `schemas/commitment.schema.json:5-45`

```text
  "description": "An obligation the owner made, to themselves or to another person. The outbound half of the owner's first priority — zero broken promises; the inbound mirror is waiting-on. Child tasks are no longer embedded here: tasks are first-class records in _data/tasks/ that point back with commitment_id, because per ADR-008 an entity that can exist without a parent cannot be stored inside one.",
  "type": "object",
  "required": ["id", "description", "status", "priority", "created"],
  "additionalProperties": false,
  "properties": {
    "id": { "type": "string", "pattern": "^c-[0-9]+" },
    "project_id": {
      "type": ["string", "null"],
      "default": null,
      "description": "Project this commitment belongs to, or null when it stands alone. Parentless commitments are visible through the unfiled view."
    },
    "description": { "type": "string" },
    "promised_to": {
      "type": ["string", "null"],
      "default": null,
      "description": "Person ID if the identity is confirmed, otherwise the name as written; null for a self-commitment. Protected: an agent never invents who a promise was made to."
    },
    "due_date": {
      "type": ["string", "null"],
      "format": "date",
      "description": "Protected: an agent never invents a deadline."
    },
    "status": {
      "type": "string",
      "enum": ["open", "in_progress", "complete", "blocked", "cancelled"]
    },
    "priority": {
      "type": "string",
      "enum": ["high", "medium", "low"]
    },
    "created": { "type": "string", "format": "date" },
    "completed": {
      "type": ["string", "null"],
      "format": "date",
      "description": "Protected: an agent never invents completion of anything."
    },
    "tags": { "type": "array", "items": { "type": "string" }, "default": [] },
    "notes": { "type": "string", "default": "" },
    "capture": { "$ref": "evidence.schema.json#/definitions/capture_source" }
  }
}
```

Interpretation: Commitments encode outbound obligation, potentially to a free-text name or self. They share task status strings without being the same entity.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E28

Location: `schemas/decision.schema.json:5-54`

```text
  "description": "A dated choice, its reasoning, and who was involved. Answers 'what did we decide and why', traceable in retrospect. Decisions are the only high-stakes record type under ADR-007, so every decision record routes to flagged review regardless of evidence level.",
  "type": "object",
  "required": ["id", "date", "decision", "rationale"],
  "additionalProperties": false,
  "properties": {
    "id": { "type": "string", "pattern": "^d-[0-9]+" },
    "date": { "type": "string", "format": "date" },
    "decision": {
      "type": "string",
      "description": "The choice that was made. Protected: an agent never invents a decision's existence."
    },
    "rationale": {
      "type": "string",
      "description": "Why it was made. Protected: an agent never invents a decision's reasoning. A decision without its reasoning is not retrievable in retrospect, which is the point of the record."
    },
    "project_id": { "type": ["string", "null"], "default": null },
    "interaction_id": {
      "type": ["string", "null"],
      "default": null,
      "description": "Interaction this decision was made in, when it is known"
    },
    "decided_by": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "Person IDs from _data/people/ — confirmed identities only"
    },
    "decided_by_names": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "Names mentioned but not yet resolved to a person record"
    },
    "alternatives": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "Options considered and not taken"
    },
    "status": {
      "type": "string",
      "enum": ["active", "superseded", "reversed"],
      "default": "active"
    },
    "supersedes": { "type": ["string", "null"], "default": null },
    "tags": { "type": "array", "items": { "type": "string" }, "default": [] },
    "notes": { "type": "string", "default": "" },
    "capture": { "$ref": "evidence.schema.json#/definitions/capture_source" }
  }
}
```

Interpretation: A decision is a dated choice with mandatory rationale, optional participants, alternatives and supersedes; not an explicit from/to transition.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E29

Location: `schemas/evidence.schema.json:20-94`

```text
    },
    "level": {
      "type": "string",
      "enum": ["explicit", "inferred", "guessed"],
      "description": "explicit=the raw text states it | inferred=supported by surrounding context but not stated | guessed=pattern match with no support in the text"
    },
    "provenance": {
      "type": "object",
      "description": "Where in the raw capture the value came from. Required, not optional: a confidence marker that cannot be traced back to its source cannot be verified.",
      "required": ["capture_id"],
      "additionalProperties": false,
      "properties": {
        "capture_id": {
          "type": "string",
          "minLength": 1,
          "$comment": "Identifier of the raw capture record. Its format is fixed by phase-cap-03, which owns schemas/capture.schema.json; this contract requires only that it be non-empty and resolvable."
        },
        "quote": {
          "type": ["string", "null"],
          "description": "The supporting span of raw text, verbatim. Required at explicit and inferred; null is only valid at guessed, which by definition has no support."
        },
        "start": { "type": ["integer", "null"], "minimum": 0 },
        "end": { "type": ["integer", "null"], "minimum": 0 }
      }
    },
    "field_evidence": {
      "type": "object",
      "required": ["level", "provenance"],
      "additionalProperties": false,
      "properties": {
        "level": { "$ref": "#/definitions/level" },
        "provenance": { "$ref": "#/definitions/provenance" },
        "reason": {
          "type": ["string", "null"],
          "description": "Why the agent read the text this way. Required whenever the level is not explicit, because REQ-002 R14 requires review to show the reason for each assumption."
        },
        "review_flag": {
          "type": "boolean",
          "default": false,
          "description": "True when this field must be decided by the owner before promotion."
        }
      },
      "allOf": [
        {
          "if": { "required": ["level"], "properties": { "level": { "enum": ["explicit", "inferred"] } } },
          "then": {
            "properties": {
              "provenance": {
                "required": ["capture_id", "quote"],
                "properties": { "quote": { "type": "string", "minLength": 1 } }
              }
            }
          }
        },
        {
          "if": { "required": ["level"], "properties": { "level": { "enum": ["inferred", "guessed"] } } },
          "then": {
            "required": ["reason"],
            "properties": { "reason": { "type": "string", "minLength": 1 } }
          }
        }
      ]
    },
    "protected_field_evidence": {
      "description": "A protected field additionally requires an explicit review flag whenever its evidence level is not explicit. An unflagged non-explicit value in a protected field is a validation failure, not a style problem (ADR-007 section 4, REQ-002 R7).",
      "allOf": [
        { "$ref": "#/definitions/field_evidence" },
        {
          "if": { "required": ["level"], "properties": { "level": { "enum": ["inferred", "guessed"] } } },
          "then": {
            "required": ["review_flag"],
            "properties": { "review_flag": { "const": true } }
          }
        }
      ]
```

Interpretation: Staging evidence distinguishes explicit/inferred/guessed and protects selected assumed fields with review flags. This is contract enforcement, not a shipped extraction/routing engine.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E30

Location: `schemas/evidence.schema.json:96-113`

```text
    "capture_source": {
      "type": ["object", "null"],
      "description": "What a PROMOTED record in _data/ keeps of its origin, per GOV-003: a pointer to the raw capture plus the names of the fields that were non-explicit at promotion time. Null on records the owner authored by hand rather than through capture. Keeping every field's evidence level forever would roughly double the field count on every entity; keeping nothing would leave a bulk-approved record with no memory of what was assumed.",
      "required": ["capture_id"],
      "additionalProperties": false,
      "properties": {
        "capture_id": { "type": "string", "minLength": 1 },
        "assumed_fields": {
          "type": "array",
          "items": { "type": "string" },
          "default": [],
          "description": "Names of the fields that were inferred or guessed when this record was promoted. Empty means every field was explicit."
        },
        "promoted": { "type": ["string", "null"], "format": "date" }
      }
    }
  }
}
```

Interpretation: Promoted-source provenance is deliberately reduced to capture_id and assumed_fields; full scoring is not promised in entity source records.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E31

Location: `schemas/staged-record.schema.json:5-44`

```text
  "description": "A candidate entity record proposed by structuring, wrapped with its raw source, its route and its per-field evidence, before any owner review (ADR-007 sections 5-7). Stored under _capture/staging/, one file per record, named `<id>.json`. Nothing here is promoted yet — only an explicit owner action (REQ-002 R12, R13) moves a record's `entity` into `_data/` and drops this wrapper. This schema validates the wrapper shape and that the source reference is present and well-formed; it does not validate `entity` against the target type's own schema (that belongs to structuring, phase-cap-05) and it does not check that `capture_id` actually resolves to a file under _capture/raw/ (that belongs to the code that reads staging, and its tests, since a JSON Schema cannot see the filesystem).",
  "type": "object",
  "required": ["id", "capture_id", "entity_type", "route", "entity"],
  "additionalProperties": false,
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^staged-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}$",
      "description": "Same shape as a raw capture id (capture.schema.json), assigned when the record is staged rather than when it was captured. The two ids are independent: one capture can yield zero, one, or several staged records (for example, a transcript naming two commitments)."
    },
    "capture_id": {
      "type": "string",
      "minLength": 1,
      "description": "The raw capture this record derives from (REQ-002 R3). Every structured record names its source; a staged record with no resolvable source reference is rejected."
    },
    "entity_type": {
      "type": "string",
      "minLength": 1,
      "description": "What kind of record `entity` proposes to become. Expected to be one of the nine entity types (project, person, commitment, task, tag, interaction, decision, waiting-on, development-event) or a structural identity (new person, new project, new tag, new tag category) per ADR-007's stakes table. Left as an open string rather than a closed enum here: ADR-007 also names a `raw note` tier with no schema of its own yet, and settling exactly what that maps to is structuring's decision (phase-cap-05), not this contract's."
    },
    "route": {
      "type": "string",
      "enum": ["clean", "flagged", "held"],
      "description": "clean=every field explicit, stakes low or medium, promoted in bulk | flagged=any field inferred or guessed, or stakes high, one owner decision | held=a new durable identity, an identity call the agent may not make (ADR-007 section 5). Whether a given entity_type/evidence combination produced the *correct* route is checked by structuring's own fixtures (REQ-002 R8); this schema only requires the value to be one of the three."
    },
    "entity": {
      "type": "object",
      "description": "The candidate field values for the proposed entity, in the shape its own schema will eventually require. Deliberately not validated against that schema here — staging exists precisely so an incomplete or provisional interpretation can be reviewed rather than rejected outright."
    },
    "evidence": {
      "$ref": "evidence.schema.json",
      "description": "Per-field evidence and provenance for every agent-filled field in `entity` (REQ-002 R6), keyed by field name. Optional in this schema and defaulting to empty only because a record every field of which came verbatim from a structural fixture is conceivable; structuring is what actually populates it, and evidence.schema.json is what makes a protected field's unflagged assumption a validation failure."
    },
    "staged_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$",
      "default": null,
      "description": "When structuring produced this record, RFC 3339 with a mandatory offset, same convention as capture.schema.json's captured_at. Null is only for hand-built fixtures; the writer is expected to always set it."
    }
```

Interpretation: Staging validates wrapper shape but leaves entity type open, entity content unconstrained by its domain schema, evidence optional and reference existence unchecked.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E32

Location: `src/capture/raw.py:63-128`

```text
def write_raw_capture(
    content: str,
    channel: str,
    source_path: str | None = None,
    raw_dir: Path = RAW_DIR,
) -> dict[str, Any]:
    """Validate and write one raw capture record verbatim. Returns the record written."""
    now = dt.datetime.now(dt.UTC)
    record: dict[str, Any] = {
        "id": _new_id(now),
        "captured_at": _iso_utc(now),
        "channel": channel,
        "content": content,
    }
    if source_path is not None:
        record["source_path"] = source_path

    _validate(record)

    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{record['id']}.json"
    if path.exists():
        raise CaptureError(f"raw capture id collision: {path}")
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def scan_inbox(
    inbox_dir: Path = INBOX_DIR, raw_dir: Path = RAW_DIR
) -> tuple[list[dict[str, Any]], list[tuple[Path, str]]]:
    """Turn every unprocessed file in `inbox_dir` into a raw capture record.

    A converted file is moved to `<inbox_dir>/processed/` so a later scan never recaptures
    it — the inbox itself then shows exactly what is still waiting. A file that fails to
    convert (empty content, unreadable bytes) is left where it is rather than moved, so it
    stays visible as something needing attention; the scan continues with the rest, per
    REQ-002 R9 — one bad item never blocks the others.

    Returns `(records written, [(path, error message) for files that failed])`.
    """
    if not inbox_dir.exists():
        return [], []

    processed_dir = inbox_dir / INBOX_PROCESSED_SUBDIR
    records: list[dict[str, Any]] = []
    failures: list[tuple[Path, str]] = []

    for path in sorted(inbox_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        try:
            content = path.read_text(encoding="utf-8")
            record = write_raw_capture(
                content,
                channel="inbox",
                source_path=str(path.relative_to(inbox_dir)),
                raw_dir=raw_dir,
            )
        except (CaptureError, OSError, UnicodeDecodeError) as exc:
            failures.append((path, str(exc)))
            continue
        processed_dir.mkdir(parents=True, exist_ok=True)
        path.rename(processed_dir / path.name)
        records.append(record)

    return records, failures
```

Interpretation: Raw capture writer stores text in new JSON files. Inbox read_text normalizes line endings; rename can replace a same-named processed file; raw captures remain separate.

Confidence: HIGH. Alternative/limit: Unicode text fidelity can be the intended contract, but it is narrower than the documented byte-identical input guarantee.

## E33

Location: `schemas/backlog.schema.json:57-142`

```text
          "title",
          "plan",
          "sources",
          "systems",
          "owner",
          "status",
          "priority",
          "session_budget",
          "depends_on",
          "scope",
          "acceptance",
          "verification",
          "deliverables",
          "next_action"
        ],
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1,
            "description": "Stable phase ID; never renumber existing items.",
            "pattern": "^phase-[a-z]+-[0-9]{2}$"
          },
          "title": {
            "type": "string",
            "minLength": 1,
            "description": "One concrete outcome achievable in one session."
          },
          "plan": {
            "type": "string",
            "minLength": 1,
            "description": "Primary parent plan document ID.",
            "pattern": "^doc-[a-z0-9]+(?:-[a-z0-9]+)*$"
          },
          "sources": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "description": "Referenced value.",
              "pattern": "^doc-[a-z0-9]+(?:-[a-z0-9]+)*$"
            },
            "uniqueItems": true,
            "minItems": 0,
            "description": "Other source document IDs, including child plan coverage and accepted decisions."
          },
          "systems": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "description": "Referenced value.",
              "pattern": "^sys-[a-z0-9]+(?:-[a-z0-9]+)*$"
            },
            "uniqueItems": true,
            "minItems": 1,
            "description": "Affected existing system IDs."
          },
          "owner": {
            "type": "string",
            "minLength": 1,
            "description": "Owner key from systems.yaml."
          },
          "status": {
            "type": "string",
            "minLength": 1,
            "description": "Execution state; readiness is derived from dependencies.",
            "enum": [
              "queued",
              "active",
              "blocked",
              "deferred",
              "complete",
              "cancelled"
            ]
          },
          "priority": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "1=foundation, 2=capability, 3=composition, 4=conditional extension."
          },
          "session_budget": {
            "type": "integer",
            "const": 1,
            "description": "Exactly one focused work session, including verification and handoff."
          },
```

Interpretation: Phases have plans, sources, systems, statuses and a constant one-session budget; these are machine-readable planning boundaries.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E34

Location: `schemas/backlog.schema.json:144-240`

```text
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "description": "Referenced value.",
              "pattern": "^phase-[a-z]+-[0-9]{2}$"
            },
            "uniqueItems": true,
            "minItems": 0,
            "description": "Prerequisite phase IDs; all must be complete before starting."
          },
          "scope": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "description": "Referenced value."
            },
            "uniqueItems": true,
            "minItems": 1,
            "description": "Bounded implementation or decision steps for this phase."
          },
          "acceptance": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "description": "Referenced value."
            },
            "uniqueItems": true,
            "minItems": 2,
            "description": "Observable conditions required for completion."
          },
          "verification": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "description": "Referenced value."
            },
            "uniqueItems": true,
            "minItems": 1,
            "description": "Commands or concrete review checks to verify the result."
          },
          "deliverables": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "description": "Referenced value."
            },
            "uniqueItems": true,
            "minItems": 1,
            "description": "Planned repository paths; existence is required only in completion_evidence."
          },
          "next_action": {
            "type": "string",
            "minLength": 1,
            "description": "First useful action for the next session."
          },
          "agent": {
            "type": "string",
            "minLength": 1,
            "description": "Claim identity of the working agent; names its branch agent/<phase-id>.",
            "pattern": "^agent-[a-z0-9]+(?:-[a-z0-9]+)*$"
          },
          "blocked_reason": {
            "type": "string",
            "minLength": 1,
            "description": "Required explanation for blocked, deferred or cancelled phases."
          },
          "resume_when": {
            "type": "string",
            "minLength": 1,
            "description": "Required condition for releasing a blocked or deferred phase."
          },
          "session": {
            "type": "string",
            "minLength": 1,
            "description": "Governed session or walkthrough record; required on completion.",
            "pattern": "^doc-[a-z0-9]+(?:-[a-z0-9]+)*$"
          },
          "completion_evidence": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "description": "Referenced value."
            },
            "uniqueItems": true,
            "minItems": 1,
            "description": "Existing files proving completion; separate from future deliverables."
          },
          "result": {
            "type": "string",
            "minLength": 1,
            "description": "Actual verification result and outcome; required on completion."
```

Interpretation: Scope, acceptance, commands, deliverables, claims and one session reference form a handoff contract; tasks and captured context manifests are absent.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E35

Location: `src/governance/backlog.py:30-84`

```text
        if node in seen or node not in items:
            continue
        seen.add(node)
        stack.extend(items[node]["depends_on"])
    return seen


def collisions(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    """Reasons two phases cannot be worked simultaneously; empty means they are disjoint."""
    shared = sorted(set(left["systems"]) & set(right["systems"]))
    reasons = [f"share system {system}" for system in shared]
    reasons += [
        f"share deliverable path {path}"
        for path in sorted(
            {
                max(first, second, key=len)
                for first in left["deliverables"]
                for second in right["deliverables"]
                if path_conflict(first, second)
            }
        )
    ]
    return reasons


def concurrency_errors(items: dict[str, Any], active: list[str], max_active: int) -> list[str]:
    """Allow several active phases only while their work areas cannot overlap."""
    errors = []
    if len(active) > max_active:
        errors.append(
            f"backlog: at most {max_active} phases may be active at once; {len(active)} found"
        )
    for agent, count in sorted(Counter(items[key].get("agent", "") for key in active).items()):
        if not agent:
            if max_active > 1:
                errors.append("backlog: every concurrent active phase requires an agent claim")
        elif count > 1:
            errors.append(f"backlog: agent {agent} holds {count} active phases; claim only one")
    for left, right in combinations(active, 2):
        errors += [
            f"{left}/{right}: concurrent phases {reason}"
            for reason in collisions(items[left], items[right])
        ]
        if right in dependency_closure(left, items) or left in dependency_closure(right, items):
            errors.append(f"{left}/{right}: concurrent phases are dependency-linked")
    return errors


def claim_conflicts(item: dict[str, Any], items: dict[str, Any]) -> list[str]:
    """Active phases that a candidate phase would collide with if claimed now."""
    return sorted(
        key
        for key, other in items.items()
        if other["status"] == "active" and key != item["id"] and collisions(item, other)
    )
```

Interpretation: Declared system/path overlap and dependency closures constrain concurrent active claims. This is scheduling/coordination, not epistemic impact analysis.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E36

Location: `src/governance/backlog.py:116-190`

```text
        for system in item["systems"]:
            if system not in systems:
                errors.append(f"{key}: unknown system {system}")
        plan = documents.get(item["plan"])
        if not plan or plan["kind"] != "plan":
            errors.append(f"{key}: primary plan must reference a plan document")
        for source in [item["plan"], *item["sources"]]:
            if source not in documents:
                errors.append(f"{key}: unknown source document {source}")
            elif documents[source]["kind"] == "plan":
                if item["status"] != "cancelled":
                    covered.add(source)
                if documents[source]["status"] in {"complete", "deprecated", "superseded"}:
                    if item["status"] not in {"complete", "cancelled"}:
                        errors.append(f"{key}: unfinished work belongs to closed plan {source}")
        for dependency in item["depends_on"]:
            if dependency not in items or dependency == key:
                errors.append(f"{key}: unresolved or self dependency {dependency}")
            elif item["status"] in {"active", "complete"}:
                if items[dependency]["status"] != "complete":
                    errors.append(f"{key}: prerequisite {dependency} is not complete")
        if item["status"] == "active":
            active.append(key)
        if item.get("agent") and item["status"] not in CLAIMED_STATES:
            errors.append(f"{key}: {item['status']} phase must release its agent claim")
        if item["status"] in {"blocked", "deferred", "cancelled"}:
            if not item.get("blocked_reason", "").strip():
                errors.append(f"{key}: {item['status']} requires blocked_reason")
        if item["status"] in {"blocked", "deferred"}:
            if not item.get("resume_when", "").strip():
                errors.append(f"{key}: {item['status']} requires resume_when")
        if item.get("session"):
            session = documents.get(item["session"])
            if not session or session["kind"] not in {"session", "walkthrough"}:
                errors.append(f"{key}: session must reference a session or walkthrough")
        if item["status"] == "complete":
            if not item.get("session") or not item.get("completion_evidence"):
                errors.append(f"{key}: complete phase requires session and completion_evidence")
            if not item.get("result", "").strip():
                errors.append(f"{key}: complete phase requires actual verification result")
        elif item["status"] not in CLAIMED_STATES and (
            item.get("completion_evidence") or item.get("result")
        ):
            # A checkpoint may record real interim evidence while a claim is held (active/blocked);
            # only a released phase (queued/deferred/cancelled) has no claim left to justify it.
            errors.append(
                f"{key}: completion evidence/results require an active, blocked or complete phase"
            )
        try:
            for path in item["deliverables"]:
                check_file(path)  # Validate public path, but planned files need not exist yet.
            for path in item.get("completion_evidence", []):
                if not check_file(path):
                    errors.append(f"{key}: missing completion evidence {path}")
        except ValueError as exc:
            errors.append(f"{key}: {exc}")
    errors.extend(concurrency_errors(items, sorted(active), catalog.get("max_active", 1)))
    try:
        tuple(
            TopologicalSorter(
                {key: item["depends_on"] for key, item in items.items()}
            ).static_order()
        )
    except CycleError:
        errors.append("backlog: phase dependency cycle")
    for key, document in documents.items():
        if document["kind"] == "plan" and document["status"] in OPEN_PLANS and key not in covered:
            errors.append(f"backlog: open plan has no non-cancelled phase: {key}")
    return sorted(errors)


def queue_order(
    items: dict[str, Any], next_up: list[str]
) -> list[dict[str, Any]]:
    """Promoted phases first, in the order listed; everything else by priority then ID."""
```

Interpretation: Completion requires real file paths, a session and nonempty result text; validator does not run verification or judge acceptance. Draft-plan work is not rejected here.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E37

Location: `src/governance/__main__.py:227-301`

```text
                    memory = folder == "brain"
                    if not validate(meta, "memory" if memory else "document", location):
                        continue
                    check_dates(meta, location)
                    collection = memories if memory else documents
                    if meta["id"] in collection:
                        errors.append(f"{location}: duplicate ID {meta['id']}")
                    collection[meta["id"]] = {"path": location, **meta}
                    for tag in meta.get("tags", []):
                        if tag not in tags:
                            errors.append(f"{location}: unknown tag {tag}")
                    if memory:
                        expected = f"brain/{MEMORY_DIRS[meta['type']]}/"
                        if not location.startswith(expected):
                            errors.append(f"{location}: memory type requires {expected}")
                        if meta.get("project") and meta["project"] not in projects:
                            errors.append(f"{location}: unknown project {meta['project']}")
                        if meta.get("scope") == "project" and not meta.get("project"):
                            errors.append(f"{location}: project scope requires project")
                        for system in meta.get("systems", []):
                            if system not in systems:
                                errors.append(f"{location}: unknown system {system}")
                        continue
                    states = {"draft", "active", "deprecated", "superseded"}
                    if meta["kind"] == "plan":
                        states |= {"approved", "complete"}
                    if meta["kind"] == "adr":
                        states = {"draft", "accepted", "deprecated", "superseded"}
                    if meta["status"] not in states:
                        errors.append(f"{location}: invalid status for kind {meta['kind']}")
                    if meta["owner"] not in owners:
                        errors.append(f"{location}: unknown owner {meta['owner']}")
                    for system in meta["systems"]:
                        if system not in systems:
                            errors.append(f"{location}: unknown system {system}")
                    if meta["status"] == "complete" and not meta.get("completion_evidence"):
                        errors.append(f"{location}: complete plan requires completion_evidence")
                    for value in meta.get("completion_evidence", []):
                        if not public_path(root, value).is_file():
                            errors.append(f"{location}: missing evidence file {value}")
                except (ValueError, yaml.YAMLError) as exc:
                    errors.append(f"{location}: {exc}")
        for key, meta in documents.items():
            for ref in (
                meta["depends_on"]
                + meta.get("supersedes", [])
                + ([meta["parent"]] if meta.get("parent") else [])
            ):
                if ref not in documents or ref == key:
                    errors.append(f"{meta['path']}: unresolved or self document reference {ref}")
            parent = documents.get(meta.get("parent"))
            if parent and (parent["kind"] != "plan" or meta["kind"] != "plan"):
                errors.append(f"{meta['path']}: parent is only valid between plans")
            for ref in meta.get("supersedes", []):
                if ref in documents and documents[ref]["status"] != "superseded":
                    errors.append(f"{meta['path']}: replaced document {ref} must be superseded")
            if meta["status"] == "superseded" and not any(
                key in other.get("supersedes", []) for other in documents.values()
            ):
                errors.append(f"{meta['path']}: superseded document has no replacement")
        for relation in ("depends_on", "supersedes", "parent"):
            graph = {
                key: ([meta["parent"]] if meta.get("parent") else [])
                if relation == "parent"
                else meta.get(relation, [])
                for key, meta in documents.items()
            }
            errors.extend(cycle_errors(graph, f"documents {relation}"))
        errors.extend(inspect_codes(register, documents, strict=True))
        for meta in memories.values():
            for ref in meta.get("related", []):
                if ref not in memories:
                    errors.append(f"{meta['path']}: unknown related memory {ref}")
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        errors.append(f"governance inputs: {exc}")
```

Interpretation: Document kind/status, reference resolution and supersession cycles are checked. Memory related IDs resolve but do not become retrieval traversal.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E38

Location: `schemas/document.schema.json:37-128`

```text
      "type": "string",
      "minLength": 1,
      "description": "Human-readable title."
    },
    "kind": {
      "type": "string",
      "minLength": 1,
      "description": "Document role.",
      "enum": [
        "plan",
        "adr",
        "architecture",
        "prompt",
        "session",
        "requirement",
        "walkthrough",
        "operation",
        "governance"
      ]
    },
    "status": {
      "type": "string",
      "minLength": 1,
      "description": "Lifecycle state; valid states also depend on kind.",
      "enum": [
        "draft",
        "approved",
        "active",
        "accepted",
        "complete",
        "deprecated",
        "superseded"
      ]
    },
    "owner": {
      "type": "string",
      "minLength": 1,
      "description": "Accountable owner key in systems.yaml; authorship is recorded by Git."
    },
    "created": {
      "type": "string",
      "minLength": 1,
      "description": "Date this document was created or first registered; ISO date.",
      "format": "date"
    },
    "updated": {
      "type": "string",
      "minLength": 1,
      "description": "Date last substantively changed or reviewed; ISO date.",
      "format": "date"
    },
    "systems": {
      "type": "array",
      "uniqueItems": true,
      "description": "System IDs affected by this document.",
      "items": {
        "type": "string",
        "minLength": 1,
        "description": "Referenced identifier or path.",
        "pattern": "^sys-[a-z0-9]+(?:-[a-z0-9]+)*$"
      }
    },
    "depends_on": {
      "type": "array",
      "uniqueItems": true,
      "description": "Prerequisite document IDs; must form an acyclic graph.",
      "items": {
        "type": "string",
        "minLength": 1,
        "description": "Referenced identifier or path.",
        "pattern": "^doc-[a-z0-9]+(?:-[a-z0-9]+)*$"
      }
    },
    "parent": {
      "type": "string",
      "minLength": 1,
      "description": "Parent plan ID for a multi-file plan.",
      "pattern": "^doc-[a-z0-9]+(?:-[a-z0-9]+)*$"
    },
    "supersedes": {
      "type": "array",
      "uniqueItems": true,
      "description": "Documents replaced by this document.",
      "items": {
        "type": "string",
        "minLength": 1,
        "description": "Referenced identifier or path.",
        "pattern": "^doc-[a-z0-9]+(?:-[a-z0-9]+)*$"
      }
    },
    "review_after": {
      "type": "string",
```

Interpretation: Governed document kinds include requirement, architecture, plan and ADR, but no distinct specification kind; depends_on is generic prerequisite linkage.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E39

Location: `.claude/agents/idea-triage.md:15-41`

```text

## What you do

1. Read the idea's title and body (given to you in the prompt).
2. Get every idea's **effective** state — title and body with amendments applied, plus
   resolved annotations and links — via `fold`, never by reading `_data/ideas.jsonl`
   directly. A raw `created` event can be stale: `amend` corrects title/body without
   rewriting the line, so the raw event is exactly the text that got superseded.

   ```bash
   uv run python -c "
   from src.db.ideas import load_events, fold
   state = fold(load_events())
   for idea_id, s in sorted(state.items()):
       print(idea_id, '|', s['title'], '|', [l['type'] + '->' + str(l['target']) for l in s['links']])
   "
   ```

   Skim every other idea's effective title/body, plus this idea's own `links` — you are
   looking for **overlap with other ideas**, not re-discovering a relationship someone
   already recorded.
3. Search the governed document set for material this idea plausibly relates to: grep
   `docs/01-plans/`, `docs/06-requirements/`, `docs/04-decisions/` and
   `docs/09-backlog/backlog.yaml` for the idea's distinctive terms. You are looking for an
   existing plan, requirement, ADR or backlog phase that already covers ground this idea
   touches — not for a place to file it.
4. Write a short finding: what you found, and why it's relevant. Name specific documents by
```

Interpretation: Triage reads effective ideas then searches plans/requirements/ADRs/backlog using terms. This is prompt-directed repository retrieval rather than a graph retrieval implementation.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E40

Location: `.claude/agents/idea-triage.md:72-94`

```text
   confident the idea's actual ask is done, not merely that a document touches the same area
   — that weaker case is what step 4's ordinary finding prose is for.

## What you must never do

- **Never conclude the idea overlaps enough to be declined or merged.** State the overlap;
  do not act on it. `phase-idea-02`'s acceptance is explicit: an overlap is recorded as a
  finding, never used to decline or merge.
- **Never write a `linked` event, even for a link you propose.** `PLAN-017.04` reserves
  asserting a relationship for a human decision — "extraction may propose; only a written
  `linked` event asserts." A `PROPOSED LINK:` line is exactly that permitted proposal; it must
  never be followed by actually calling `tools/append_idea.py link`.
- **Never call `status ... promoted`, even for a promotion you propose.** A
  `PROPOSED PROMOTION:` line is a proposal for the owner to execute or reject, exactly like
  `PROPOSED LINK:` — it must never be followed by actually calling
  `tools/append_idea.py status ... promoted`. Promotion is the one transition `phase-idea-02`'s
  acceptance names explicitly as owner judgement that must not be automated.
- **Never call `status`, `revisit`, `amend` or anything besides `annotate`.** The driver
  (`/idea-triage`) owns moving the idea from `open` to `triaged` after your finding is
  written; you write the finding and stop.
- **Never invent a relationship you have not actually verified by reading the target.** A
  plausible-sounding title match is a lead to name and let the owner check, not a confirmed
  finding — say "possibly related to X, based on title only" if you have not read X's body.
```

Interpretation: Human judgment over links and promotion is protected by instructions. Tool rights include Bash; this is not a hard permission boundary.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E41

Location: `.claude/commands/idea-triage.md:62-91`

```text
   from src.db.ideas import load_events, fold
   state = fold(load_events())
   anns = state['<id>']['annotations']
   print(anns[-1]['text'][:200] if anns else 'NO ANNOTATION FOUND')
   "
   ```

   Read the printed text. If it opens by naming a *different* six-digit idea id as its own
   subject (e.g. idea `<id>`'s newest annotation starts "Idea 000012 proposes..." when `<id>`
   is not `000012`), the write landed on the wrong idea — stop, do not move status to
   `triaged`, and fix it with `amend-annotation` (see `.claude/agents/idea-triage.md`'s
   corrected-entry precedent) before continuing to the next idea.
4. Only once verified, move the idea to `triaged`:

   ```bash
   uv run python tools/append_idea.py status <id> triaged
   ```

5. If the subagent found nothing to report, it still writes a finding saying so — every
   triaged idea has at least one finding annotation, even an empty-handed one. Do not skip
   the annotation step because there was nothing notable to find.

**Do not batch multiple ideas into one subagent call.** Each idea gets its own dispatch, so
a finding never accidentally conflates two ideas' overlap.

## 3. Afterwards

Regenerate the markdown view and leave the tree green:

```bash
```

Interpretation: Driver verifies an annotation before moving to triaged and renders proposals for owner review. No durable triaging state exists.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E42

Location: `.claude/skills/checkpoint/SKILL.md:51-65`

```text

Each checkpoint run **regenerates sections 2 through 6 from scratch**, from the state actually
observed at run time. It does not append a new block per run and does not keep a log of past runs —
that is what makes a no-op run produce a no-op diff, and what keeps the file readable after the
tenth checkpoint instead of the first.

1. `# <title>` — matches the front matter title.
2. `## Phase` — one line per phase this record covers: the id and title, e.g.
   `` `phase-ses-03` — Build the checkpoint skill. `` A record normally covers one phase; note here if
   it genuinely covers more (e.g. a phase whose acceptance requires an adjacent tidy-up).
3. `## Verification` — for each entry in the phase's `verification` list that is a runnable command,
   the literal command and the literal output actually produced just now. For a verification entry
   written in prose rather than as a command (a behavioural check), one line stating what was
   actually done and observed. Never paraphrase a failure into a pass.
4. `## Acceptance` — one line per entry in the phase's `acceptance` list: `Met` or `Not met`, with a
```

Interpretation: Checkpoint overwrites the current session sections rather than appending a per-run history. The latest record is not a complete execution event stream.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E43

Location: `.claude/commands/session-close.md:6-19`

```text
# Close the session

Finishes the session record `checkpoint` (`.claude/skills/checkpoint/SKILL.md`) created or updated,
adds the depth a checkpoint deliberately skips, and is the **only** place a phase reaches
`status: complete`.

## This command is owner-only, on purpose

**An agent must never invoke this on its own judgement that a session is finished.** That decision
belongs to the owner. If you are an agent and you believe a session is done, say so and run
`checkpoint` to record where things stand — do not reach for this command yourself, and do not
reproduce its completion step inside `checkpoint` or anywhere else. The whole reason `session-close`
is a command rather than a skill is that a command is something the owner types; nothing here should
be restructured to make it agent-reachable.
```

Interpretation: Owner-only closure is an instruction-level workflow boundary.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E44

Location: `.claude/commands/session-close.md:82-110`

```text
- `## Left undone` — what remains, and why it was left rather than finished, for whoever picks this up
  next.

Write these as narrative, the way an owner would want to read them in six months — not as a
restatement of the backlog's `scope` bullets.

## 6. Decide completion — the only step that may write `status: complete`

Mark the phase complete **only if both hold**:

- The checkpoint procedure's own step 4 (redone in step 1 above) found every `acceptance` condition
  `Met`.
- The sub-agent review in step 3 corroborates that and raised no unresolved discrepancy.

If both hold: set `status: complete`, `session:`, `completion_evidence:` (real files), and `result:`
(the actual verification and review outcome) on the phase in `backlog.yaml`. Remove it from
`next_up` if present.

**If either does not hold, the phase stays `queued` or `active`.** This is not a failure state to
paper over — write an exact `next_action` that names precisely what remains, including anything the
sub-agent review surfaced, and say so plainly in your final report. A session that closes honestly
incomplete is the correct outcome the acceptance conditions were written to allow.

## 7. Regenerate the catalog and confirm governance is green

```bash
uv run python -m src.governance --catalog > docs/08-governance/catalog.md
uv run python -m src.governance
uv run pytest
```

Interpretation: Closure assesses acceptance and records existing evidence after independent review; this describes a protocol rather than an autonomous runtime service.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E45

Location: `docs/06-requirements/REQ-002-capture-requirements.md:10-22`

```text
updated: '2026-09-08'
systems: [sys-capture, sys-contracts, sys-portfolio, sys-projection]
depends_on: [doc-governance-protocol, doc-capture-routing, doc-record-types]
---

# Capture and structuring requirements

Observable requirements for getting information into this system. Each states what must be true and
how to verify it. The decisions behind them are in [ADR-007](../04-decisions/ADR-007-capture-routing.md)
and [ADR-008](../04-decisions/ADR-008-record-types.md); the build order is in
[PLAN-009](../01-plans/PLAN-009-capture-build.md). **R1, R2 and R5 are implemented** (raw-only CLI
and inbox intake, `phase-cap-04`); everything else — structuring, routing, review, promotion and
the entity model — is still proposed only.
```

Interpretation: Capture requirements explicitly depend on decision documents; the implementation-status introduction is stale for the entity projection.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E46

Location: `docs/06-requirements/REQ-002-capture-requirements.md:48-64`

```text
| Entities | Nine types; tasks first-class with optional parents |
| Cadence | `review_cadence` is policy, `last_touched` is derived, `ongoing` retired |

## Requirements

### Capture

**R1 — Raw text survives interpretation.** Every capture is written to the raw store with an
identifier and a timestamp before any structuring runs, and is byte-identical to what was submitted.
*Verify:* submit a capture through each channel; assert the stored raw record matches the input
exactly and predates any derived record.

**R2 — Raw text is never mutated.** No code path edits or deletes a raw capture. A correction to a
derived record leaves its raw source unchanged.
*Verify:* apply a correction to a structured record; assert the referenced raw record's content hash
is unchanged.

```

Interpretation: R1 promises byte-identical capture input; R5 ties quick capture to an operations command.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E47

Location: `docs/01-plans/PLAN-009-capture-build.md:10-34`

```text
updated: '2026-09-06'
systems: [sys-capture, sys-contracts, sys-portfolio, sys-projection]
depends_on: [doc-capture-system, doc-capture-routing, doc-record-types, doc-capture-requirements]
---

# Build the capture and structuring system

## Context and scope

[PLAN-007](PLAN-007-capture-and-structuring-system.md) was a discovery plan: its single phase ran the
definition session and deferred everything else until the owner's answers existed. They now do. This
plan is that session's output — the build work, in dependency order.

The decisions are fixed by [ADR-007](../04-decisions/ADR-007-capture-routing.md) and
[ADR-008](../04-decisions/ADR-008-record-types.md); the contract is
[REQ-002](../06-requirements/REQ-002-capture-requirements.md). This plan does not restate them. It
says what gets built, in what order, and why that order.

Scope is intake through promotion: raw capture, structuring, routing, review, promotion into
`_data/`, and the projection of the expanded entity model. Out of scope: scheduled prompting,
durable off-disk storage, and any signal or synthesis output, all of which have their own tracks.

## Ordering rationale

Contracts precede code because every later phase validates against them, and because the schema
```

Interpretation: Capture plan explicitly references the routing ADR, entity ADR and requirements, and separates raw intake from downstream interpretation.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E48

Location: `docs/09-backlog/backlog.yaml:2598-2648`

```text
- id: phase-cap-04
  title: Build raw intake through the CLI and inbox
  plan: doc-capture-build
  sources:
  - doc-capture-routing
  - doc-capture-requirements
  systems:
  - sys-capture
  owner: repository-owner
  agent: agent-cap04
  status: complete
  priority: 1
  session_budget: 1
  depends_on:
  - phase-cap-03
  scope:
  - Add a single-command CLI quick capture that writes one raw record.
  - Add inbox intake that turns any file-shaped input into raw records.
  - Write raw records only; no interpretation or structuring in this phase.
  acceptance:
  - Captured text is stored byte-identical to the input through both paths.
  - No code path in this phase edits or deletes an existing raw record.
  - Nothing is written to _data/ or to staging.
  verification:
  - uv run pytest test/test_capture_intake.py
  - uv run ruff check src/ test/ tools/
  deliverables:
  - tools/capture.py
  - src/capture/raw.py
  - test/test_capture_intake.py
  next_action: Complete. phase-cap-05 (structuring and routing) can now build against
    this raw-only intake.
  session: doc-session-capture-intake
  completion_evidence:
  - src/capture/raw.py
  - tools/capture.py
  - test/test_capture_intake.py
  - docs/08-governance/OPS-008-capture.md
  result: Built src/capture/raw.py (write_raw_capture, the only writer for _capture/raw/,
    and scan_inbox, shared by both intake channels) and tools/capture.py, the CLI,
    taking a single positional text argument or stdin, plus --inbox to drain the inbox
    directory. Both write raw records only, validated against schemas/capture.schema.json
    before every write. A converted inbox file moves to _capture/inbox/processed/
    so a later scan never recaptures it; a file that fails to convert is left in place
    and the scan continues with the rest. Added 19 tests in test/test_capture_intake.py,
    all passing; ruff and mypy clean; full suite at 365 passed. Also added docs/08-governance/OPS-008-capture.md
    (a new tools/*.py ships with its own paired OPS-* doc per AGENTS.md, enforced
    by test_tool_docs.py) and corrected REQ-002 R5's stale verification pointer and
    its now-outdated "nothing implemented" line. Independent sub-agent review corroborated
    all three acceptance conditions with no discrepancies beyond a stale document-count
    in a pasted transcript. Full detail in SESS-2026-09-08-05.
```

Interpretation: Real completed raw-intake phase links decision/requirement/plan to code, tests, an operations document and a session.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E49

Location: `test/test_capture_intake.py:1-65`

```text
"""Tests for raw-only capture intake — REQ-002 R1/R2/R5/R9/R12, ADR-007 sections 1-2.

phase-cap-04 builds two channels, both writing through the single `write_raw_capture`
function phase-cap-03's schema already governs: the CLI (`tools/capture.py`) and the inbox
scanner (`src.capture.raw.scan_inbox`). Neither interprets a capture — that is
phase-cap-05's job — so these tests care about fidelity (byte-identical, never mutated,
never lost to a bad neighbour) and the write boundary (nothing lands outside
`_capture/raw/`), not about meaning.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "capture.schema.json").read_text(encoding="utf-8"))

from src.capture import raw as capture_raw  # noqa: E402


def _load(name: str) -> Any:
    """Import a tools/ script by path — tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


capture_cli = _load("capture")


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    return tmp_path / "raw"


@pytest.fixture
def inbox_dir(tmp_path: Path) -> Path:
    return tmp_path / "inbox"


def _records(raw_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(path.read_text(encoding="utf-8")) for path in sorted(raw_dir.glob("*.json"))
    ]


# --- write_raw_capture: R1 (byte-identical), R2 (never mutated) --------------------------


def test_write_raw_capture_stores_content_byte_identical(raw_dir: Path) -> None:
    content = "Call John about the Q3 deliverable by Friday."
    record = capture_raw.write_raw_capture(content, channel="cli", raw_dir=raw_dir)

    assert record["content"] == content
```

Interpretation: Executable synthetic tests exercise verbatim string capture and immutability of previously written raw records.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E50

Location: `docs/03-sessions/SESS-2026-09-08-05-capture-intake.md:19-65`

```text
`phase-cap-04` — Build raw intake through the CLI and inbox.

## Verification

```
$ uv run pytest test/test_capture_intake.py
19 passed, 2 warnings
```

```
$ uv run ruff check src/ test/ tools/
All checks passed!
```

Also ran, since the phase touched `docs/06-requirements/REQ-002-capture-requirements.md` and
`docs/08-governance/systems.yaml` alongside its own deliverables:

```
$ uv run mypy src/
Success: no issues found in 14 source files
$ uv run python -m src.governance
Governance OK: 16 systems, 88 documents, 13 memories, 97 backlog phases
$ uv run pytest
365 passed, 2 warnings
```

Also ran the actual documented command from `docs/08-governance/OPS-008-capture.md` by hand, once,
against the real (gitignored) `_capture/` tree in this worktree, then removed the resulting files:

```
$ uv run python tools/capture.py "Call John about the Q3 deliverable by Friday."
captured raw-20260908T100014Z-9e7b08
$ echo "A pasted note from a meeting." > _capture/inbox/meeting-note.txt
$ uv run python tools/capture.py --inbox
captured raw-20260908T100019Z-d72433 from meeting-note.txt
$ uv run python tools/capture.py --inbox
inbox empty — nothing to capture
```

Both raw files matched `schemas/capture.schema.json` and held their input byte-identical; the inbox
file moved to `_capture/inbox/processed/meeting-note.txt`; the second `--inbox` run confirmed no
recapture. `git status --short` before and after this manual run was identical (clean).

## Acceptance

- Captured text is stored byte-identical to the input through both paths. — Met:
  `test_write_raw_capture_stores_content_byte_identical` and
```

Interpretation: Historical session reports test results and a manual CLI run, giving an explicit local outcome trace; it is not deployment telemetry.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E51

Location: `docs/09-backlog/backlog.yaml:2649-2719`

```text
- id: phase-cap-05
  title: Implement structuring, evidence scoring and routing
  plan: doc-capture-build
  sources:
  - doc-capture-routing
  - doc-capture-requirements
  systems:
  - sys-capture
  owner: repository-owner
  status: queued
  priority: 1
  session_budget: 1
  depends_on:
  - phase-cap-04
  scope:
  - Score each agent-filled field as explicit, inferred or guessed with provenance.
  - Enforce the never-invent rules for promised_to, due_date, decision and completion.
  - Route staged records to clean, flagged or held on stakes crossed with evidence.
  - Hold every new person, project, tag or tag category rather than creating it.
  acceptance:
  - A fixture set covering each cell of the stakes-by-evidence matrix produces the
    stated route.
  - An ambiguous capture completes non-interactively and yields a flagged record.
  - A capture naming an unknown person creates no person record anywhere.
  - The same fixture through all three channels produces identical routing and evidence.
  verification:
  - uv run pytest test/test_capture_routing.py
  - uv run mypy src/
  deliverables:
  - src/capture/structure.py
  - src/capture/routing.py
  - test/test_capture_routing.py
  next_action: Build the routing table and the never-invent validation against the
    matrix fixtures.
- id: phase-cap-06
  title: Build review and promotion into the source of truth
  plan: doc-capture-build
  sources:
  - doc-capture-routing
  - doc-capture-requirements
  systems:
  - sys-capture
  - sys-portfolio
  owner: repository-owner
  status: queued
  priority: 1
  session_budget: 1
  depends_on:
  - phase-cap-05
  scope:
  - Promote all clean staged records in one owner action and no flagged or held ones.
  - Present flagged items with raw text, proposed record, assumed fields and reasons,
    ordered by stakes.
  - Take the identity decision for held people, projects, tags and tag categories.
  - Append dated correction entries to promoted records without touching raw captures.
  acceptance:
  - Bulk promotion moves only clean records; a mixed batch leaves flagged and held
    staged.
  - No capture path other than promotion writes to _data/.
  - A correction records the field, the previous value and the new one, and the prior
    value stays readable.
  verification:
  - uv run pytest test/test_capture_review.py
  - uv run pytest test/test_capture_promotion.py
  deliverables:
  - src/capture/review.py
  - src/capture/promote.py
  - tools/review.py
  - test/test_capture_review.py
  - test/test_capture_promotion.py
  next_action: Build promotion first, then the review presentation that feeds it.
```

Interpretation: Structuring, routing, review, promotion and dated entity corrections remain queued deliverables, not implemented code.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E52

Location: `docs/09-backlog/backlog.yaml:2720-2774`

```text
- id: phase-cap-07
  title: Project the expanded entity model into DuckDB
  plan: doc-capture-build
  sources:
  - doc-record-types
  - doc-capture-requirements
  systems:
  - sys-projection
  owner: repository-owner
  agent: agent-cap07
  status: complete
  priority: 2
  session_budget: 1
  depends_on:
  - phase-cap-02
  scope:
  - Add tables for interaction, decision, waiting_on and development_event.
  - Drop NOT NULL from commitments project_id and from tasks commitment_id and project_id.
  - Load tasks from _data/tasks/ instead of unpacking them from commitment JSON.
  - Derive last_touched at rebuild and add the unfiled view for parentless records.
  acceptance:
  - Fixtures for each new type load and survive a rebuild unchanged.
  - A task loads with neither parent, with either, and with both.
  - last_touched exists only in the projection and advances when an interaction is
    added.
  - last_reviewed is unchanged by activity.
  - The unfiled view returns exactly the parentless fixtures (REQ-002 R19).
  verification:
  - uv run pytest test/test_rebuild.py
  - uv run python tools/rebuild_db.py
  deliverables:
  - sql/001_schema.sql
  - sql/003_capture_views.sql
  - tools/rebuild_db.py
  - test/test_rebuild.py
  next_action: Complete.
  session: doc-session-expanded-entity-projection
  completion_evidence:
  - sql/001_schema.sql
  - sql/003_capture_views.sql
  - tools/rebuild_db.py
  - test/test_rebuild.py
  - docs/03-sessions/SESS-2026-09-08-11-expanded-entity-projection.md
  result: Added interactions/decisions/waiting_on/development_events tables, dropped
    NOT NULL from commitments.project_id and tasks.commitment_id/project_id, switched
    tasks to load from _data/tasks/, and added sql/003_capture_views.sql with a
    project_last_touched view (derived, never stored) and an unfiled view (REQ-002
    R19, added to this phase's own acceptance list after a scope-gap review). 14
    new tests in test/test_rebuild.py pass; 386 pass overall; governance exits 0;
    a real rebuild against the actual repository succeeds. Independent sub-agent
    review reran everything itself and found all five acceptance conditions
    genuinely held, no discrepancies.
- id: phase-cap-08
  title: Seed the portfolio through the capture pipeline
  plan: doc-capture-build
```

Interpretation: Expanded projection is recorded complete with code and tests. This contradicts the requirement introduction that says the entity model is still proposed.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E53

Location: `docs/06-requirements/REQ-003-idea-plan-lifecycle.md:30-67`

```text
are covered through sources, with counts 3/3/2/3/1/2. No zero-phase repair project is warranted.

## Observable requirements and verification

| ID | Required observable behavior | Verification method | Delivery |
|---|---|---|---|
| R01 | Existing log bytes, identifiers and writer-issued timestamps remain unchanged; the known corrupted record remains evidence | Compare byte prefix against pre-change source; inspect scoped diff; no live repair/capture in this architecture session | Every phase |
| R02 | Supported prose input preserves backticks, dollar substitutions, quotes, newlines and Unicode as data | Run the real CLI in an isolated synthetic fixture with a quoted-heredoc/file input, compare decoded prose with input and assert no sentinel command executed | First fix |
| R03 | Writer, renderer, rebuild and projection tests consume one validating replay implementation and one schema transition table | Trace imports/call sites; synthetic corpus includes every existing transition/revisit branch and refusal; no production replay copied into tests | First fix |
| R04 | Duplicate creation, unknown idea, mismatched from, illegal transition and second revisit fail before append or database mutation | Negative fixtures bypass high-level writer then call replay/preflight directly; assert unchanged log/database and absent data directory on failed first rebuild | First fix |
| R05 | Every event resolves to a unique identity — a written `eid`, or a digest of a legacy line's own bytes — and an amendment names its target by that identity; direct amendments compose without reverting earlier unrelated fields | Synthetic sibling title/body corrections; nested chain; absent, forward and foreign target refusal; two events resolving to one identity fail the fold; a merge fixture interleaving two worktrees' appends leaves every pointer resolvable | Amendments |
| R06 | Flags obey replace/clear/inherit exactly; an amendment changes one record's contribution, never the accumulated collection | Exhaustive truth-table and event-field fixtures; required clears fail, optional contribution clears succeed; siblings survive | Amendments |
| R07 | Effective replay rechecks the whole corrected history, including from and revisit invariants | Correct an early transition into one inconsistent with a later from; refuse proposal before append, reject imported bad history before rebuild writes | Amendments |
| R08 | Raw history and effective current state remain separately queryable; past knowledge excludes later amendments | Synthetic cutoff before/after correction gives different known states; raw row count equals log event count, including retracted contributions | Amendments |
| R09 | Annotations carry owner or agent-name author, minimal kind and text; terminal states admit notes; assessments remain timestamped notes | Every author/kind fixture, promoted/discarded notes, text replacement/clear, status unchanged | Notes |
| R10 | Agent findings ship with collapsed rendering and complete accessible details; current prose displays final values without amendment badges | Golden render with 100 findings, owner note, corrected title; reload/refold in different processes/hash seeds; --check detects stale output | Notes/amendments |
| R11 | Triage enters triaging, writes findings through the sanctioned writer, and ends at triaged; promotion remains owner judgment | Synthetic end-to-end execution of existing triage phase; interrupted run remains observable; no automatic reviewing/promotion/discard | Existing triage phase |
| R12 | Three link types are stored once, inverses derived, contributors retained, and directional cycles flagged at fold time without rejecting capture | Reciprocal relates_to accepted; extends/supersedes cycle flagged; duplicate contributors and selective retraction tested | Relationships |
| R13 | Promotion supports one idea to several governed documents and several ideas to one; unresolved current targets fail validation, historical closures remain auditable | Code-to-document lookup fixtures for multiplicity, missing/reserved/retired codes, renamed paths and later deprecated targets; reverse lookup | Relationships |
| R14 | Plan attribution is plan OR sources, deduplicated; every plan has at least one historical phase and open plans retain noncancelled coverage | Coverage fixtures and existing six HTML child counts; zero/all-cancelled cases across every plan status | First fix/matrix |
| R15 | Work cannot begin under draft/approved affected plans; activation precedes the claim, and approval is never fabricated | Command-mode review and fixtures; draft/approved plus active/completed phases fail; first fix reconciles actual affected plans | First fix |
| R16 | All plans receive consistency reports; active/all-complete passes pending review, complete/unfinished fails, and complete with complete-or-cancelled phases warns unless completion evidence explains the cancellations | Full disjoint distribution matrix; existing evidence-path tests retained; owner-intent review separate from counts | First fix/matrix |
| R17 | Supported metrics declare population, cutoff, time axis and missing-data treatment; corrections/notes do not create new capture counts | Synthetic SQL results with known durations and denominators; skew flagged; no inferred duplication or session count reported as measured | Integrated verification |
| R18 | Architecture is one parent plus category children in the four requested folders; each category has six sections, coverage, open choices and conflicts | Document review, allocator output, catalog byte comparison and governance exit 0 | This session |

R02 promises the sanctioned input path, not recovery of prose already altered by an arbitrary caller's
shell. R05–R08 use the nested precedence recommendation in the event contract, whose decision is
visible before implementation. R16's cancelled-phase cell is decided: `complete` with a mix of
complete and cancelled phases **warns**, and the warning clears when `completion_evidence` states why
those phases were dropped. `GOV-002`'s complete-or-cancelled closure is unchanged, so this requirement
adds a check without reversing a standing policy.

## Boundaries and open questions

Tags and classification remain deferred until at least 60 captured ideas or a documented failed
retrieval, followed by a boundary decision against links. No vocabulary, registry or schema is designed
now. Mandatory idea provenance for plans is excluded: record genuine promotion and never fabricate
captures. A future proposal would need prospective evidence of lost provenance and a capture process
```

Interpretation: Draft requirements propose stronger trace, triage, plan activation and cutoff guarantees than the present code; gaps must not be called regressions against a completed whole plan.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E54

Location: `docs/07-architecture/ARCH-005-idea-node-classification.md:17-40`

```text
Recorded from the owner's proposal (2026-09-09) as a durable reference for the classifications
themselves, ahead of any decision about how — or whether — they are implemented. This document
is `status: draft`: it defines the taxonomy so it can be discussed and evaluated against the
existing idea corpus; it does not commit the system to a schema change. The originating idea is
`000061` in `_data/ideas.jsonl` (recorded verbatim per [ADR-010](../04-decisions/ADR-010-idea-staging.md));
this document is the properly-structured counterpart the owner asked for once the idea itself was
captured.

## Why a classification, not another tag

[ARCH-001](ARCH-001-tagging-system.md) already gives ideas a tagging axis — open-vocabulary,
additive, answers "what is this about." Idea `000018` (tagging and plan-mapping system for ideas)
and `000053` (idea-to-document links) both extend that same additive-metadata model: more tags,
richer link targets.

This taxonomy is a different kind of thing. It proposes a **small, closed set of node types**
along independent axes, so that graph traversal can partition on *kind of node* the way a
database partitions on a typed column — not by string-matching an open tag vocabulary. The
motivating query is structural, not topical: "every Strategic Directive resting on an Assumption
rather than an Axiom" is a join across two axes, not a keyword search. A tag vocabulary can grow
to describe this after the fact; a closed type system supports the query by construction.

Three axes are proposed, each orthogonal to the other two and to tags/links. An idea is expected
to carry at most one classification per axis (not one overall "type") — see Open Questions for
```

Interpretation: The three-axis taxonomy is explicitly draft and undecided for implementation; classification absence is an implementation gap relative to research, not a hidden working feature.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E55

Location: `docs/02-prompts/PROMPT-001-artifact-code-generation-system.md:45-74`

```text
- `tags` must reference existing IDs in `_data/tags.json`; propose new tags if needed and add them
- `last_reviewed` always set to today's date (ISO 8601)
- `review_cadence` — choose from: `daily | weekly | biweekly | monthly | quarterly | ad-hoc`. It is a review rhythm, not a commitment count; `ongoing` is retired.
- `description` — 1–2 sentences, plain language, no jargon unless domain-specific

### 2. SQL DDL (`sql/`)
- Table names: plural, snake_case
- Primary key: always `id VARCHAR PRIMARY KEY` unless junction table
- Junction tables: composite PK only, no surrogate key
- All VARCHAR columns with user-visible text get `DEFAULT ''`
- DATE columns never get defaults — null means unknown, not a default date
- No inline foreign key constraints (DuckDB behavior; rely on application logic)
- Add a comment block at top: table purpose + which JSON file feeds it

### 3. Pydantic Model (`src/models/<entity>.py`)
- One file per domain entity
- Base model: `<Entity>Base` — shared fields
- Create model: `<Entity>Create(Base)` — fields required at creation
- Read model: `<Entity>(Base)` — includes `id`, mirrors DB shape
- Use `model_config = ConfigDict(from_attributes=True)`
- Date fields: `datetime.date`, not `str`
- Optional fields use `field_name: str | None = None`

### 4. FastAPI Route (`src/api/routes/<entity>.py`)
- Router prefix: `/<entities>` (plural)
- Standard endpoints: `GET /`, `GET /{id}`, `POST /`, `PATCH /{id}`, `DELETE /{id}`
- All endpoints are async
- Use `Annotated[duckdb.DuckDBPyConnection, Depends(get_db)]` for DB injection
- Return types are always explicit (no bare `dict`)
- HTTP 404 on not-found, 409 on conflict, never 500 for expected states
```

Interpretation: Code-generation prompt asks for no SQL foreign keys and application enforcement, plus standard CRUD. Current implementation has no domain CRUD and incomplete reference enforcement.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E56

Location: `brain/concepts/terms-plans-and-work.md:31-87`

```text
`docs/01-plans/PLAN-015-ephemeral-working-plans.md`.

### Phase

One entry in `docs/09-backlog/backlog.yaml` (`phase-<track>-NN`) naming one independently verifiable
outcome sized to a single session. Not a governed document itself — it references a governed `plan`
and carries its own schema (`schemas/backlog.schema.json`), separate from `document.schema.json`. See
`docs/08-governance/GOV-002-backlog-protocol.md`.

### Track

The shared prefix grouping phases from one plan or work stream — `phase-rel-*`, `phase-term-*`, and
so on. Not a schema field; it is a naming convention read off the phase ID, glossed in
`docs/09-backlog/README.md`.

### next_up

The catalog-level ordered list of phase IDs that jump the queue — the front of the backlog. Not a
ranking of everything; phases absent from it fall back to priority, then ID. See
`docs/08-governance/GOV-002-backlog-protocol.md`.

### Session budget

The phase field `session_budget`, always exactly `1`. Not an automatic timing guarantee — a review
promise that the phase's scope fits one focused session, enforced by the schema constant rather than
by a clock.

### Next action

The phase field naming the first useful action for the next session, or a precise resume instruction.
Not a summary of the whole phase — it is the single next step, read by whichever agent picks the
phase up next.

### Acceptance

The phase field listing at least two observable conditions that must hold for the phase to be
complete. Not verification — acceptance states *what* must be true; verification states *how* that
gets checked.

### Verification

The phase field listing commands or specific review/experiment checks, run and recorded during
execution. Not a promise of correctness by itself — the governance check confirms the field exists
and is followed by a session record; it does not run the commands for you or judge the output.

### Deliverable

An expected file path named on a phase, which may not exist yet when the phase is claimed. Not
completion evidence — a deliverable is what the phase expects to produce; completion evidence is what
is confirmed to exist, with real results, once the phase is done.

### Completion evidence

The phase fields (`session`, `completion_evidence`, `result`) recorded only at close: a governed
session ID, existing evidence file paths, and an actual-results summary. Not written at claim time,
and never a placeholder — an empty evidence file does not satisfy this field. See
`docs/08-governance/GOV-001-protocol.md`.
```

Interpretation: Operational vocabulary distinguishes phases from tasks, but its completion-evidence wording is stale relative to checkpoint support.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E57

Location: `brain/concepts/terms-memory-and-retrieval.md:55-72`

```text
A memory describing why something was chosen. Not an ADR — an ADR is a governed document with a code
and a lifecycle; a decision memory is informal and needs neither to be recorded.

### Scope (memory field)

Whether a memory applies `global`ly, to one `project`, or is `session`-scoped pending review for
promotion to global. Not the same as a document's `status`, which tracks lifecycle rather than where
a memory applies.

### Confidence

How reliable a memory is: `high`, `medium`, `low`, or `uncertain`. Not a lifecycle state and not proof
that whatever the memory describes is implemented — mutable claims are verified against code
regardless of confidence.

### Source model

The `source_model` field recording which model or human authored or last substantively edited a
```

Interpretation: Memory glossary separates scope, confidence and source model; the query ignores scope and omits source model from formatted context.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E58

Location: `sql/003_capture_views.sql:5-37`

```text
-- REQ-002 R21: last_touched is computed, never stored. No _data/ file carries it; it
-- exists only here, derived as the latest activity across a project's interactions,
-- commitments, tasks and decisions (waiting-on is excluded — R21 names only these four).
-- A project with no activity in any of them has no row, not a stale sentinel date.
CREATE VIEW project_activity AS
SELECT project_id, date AS activity_date FROM interactions WHERE project_id IS NOT NULL
UNION ALL
SELECT project_id, created AS activity_date FROM commitments WHERE project_id IS NOT NULL
UNION ALL
SELECT project_id, created AS activity_date FROM tasks WHERE project_id IS NOT NULL
UNION ALL
SELECT project_id, date AS activity_date FROM decisions WHERE project_id IS NOT NULL;

CREATE VIEW project_last_touched AS
SELECT project_id, MAX(activity_date) AS last_touched
FROM project_activity
GROUP BY project_id;

-- REQ-002 R19: parentless records — no project_id — stay visible rather than becoming
-- a write-only pile. Covers every entity that carries an optional project_id.
CREATE VIEW unfiled AS
SELECT 'commitment' AS record_type, id, project_id FROM commitments WHERE project_id IS NULL
UNION ALL
SELECT 'task' AS record_type, id, project_id FROM tasks WHERE project_id IS NULL
UNION ALL
SELECT 'interaction' AS record_type, id, project_id FROM interactions WHERE project_id IS NULL
UNION ALL
SELECT 'decision' AS record_type, id, project_id FROM decisions WHERE project_id IS NULL
UNION ALL
SELECT 'waiting_on' AS record_type, id, project_id FROM waiting_on WHERE project_id IS NULL
UNION ALL
SELECT 'development_event' AS record_type, id, project_id
FROM development_events WHERE project_id IS NULL;
```

Interpretation: Project activity means dates of interactions/decisions and creation of tasks/commitments, not last mutation; unfiled includes every nullable-project entity family.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E59

Location: `test/test_ideas.py:724-744`

```text
def test_no_committed_line_in_the_log_is_ever_altered() -> None:
    """The committed file must remain a line-for-line prefix of the current one.

    This is the guarantee the whole design rests on, so it is checked against git rather than
    against a recorded digest — a digest has to be updated on every append, and a check that
    is routinely updated is a check that will be updated over a real change.
    """
    committed = subprocess.run(
        ["git", "show", "HEAD:_data/ideas.jsonl"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if committed.returncode != 0:
        pytest.skip("_data/ideas.jsonl is not committed yet")

    was = [line for line in committed.stdout.splitlines() if line.strip()]
    now = _lines(LOG)

    assert now[: len(was)] == was, (
        "a committed line changed. The log is append-only: a status change appends an event, "
        "and nothing already written is ever edited or removed."
    )
```

Interpretation: Prefix comparison protects uncommitted edits against HEAD, not tamper-proof retention across arbitrary commits/history rewrites.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E60

Location: `test/test_ideas.py:997-1010`

```text
def test_any_past_moment_is_reconstructible(
    projected: duckdb.DuckDBPyConnection,
) -> None:
    """The reason idea_events is retained in full and never folded away."""
    at_fifteen_hundred = projected.execute(
        """
        SELECT count(*) FROM idea_events
        WHERE event = 'created' AND occurred_at <= TIMESTAMPTZ '2026-09-06 15:00:00-04:00'
        """
    ).fetchone()
    assert at_fifteen_hundred is not None
    assert at_fifteen_hundred[0] == 8, "eight ideas existed at that instant"


```

Interpretation: The named historical reconstruction test counts creations at a time; it does not prove complete amended state reconstruction.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E61

Location: `.github/workflows/ci.yaml:1-41`

```text
name: CI

on:
  push:
    branches: [dev, main]
  pull_request:

jobs:
  python:
    name: Python lint & test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --extra dev
      - name: No private content leaked into the tracked tree
        run: uv run python tools/check_no_private_content.py
      - run: uv run python -m src.governance
      - name: Catalog is current
        run: |
          uv run python -m src.governance --catalog > /tmp/catalog.md
          diff -u docs/08-governance/catalog.md /tmp/catalog.md
      - run: uv run ruff check src/ test/
      - run: uv run mypy src/
      - run: uv run pytest

  frontend:
    name: TypeScript build check
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ts
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: ts/package-lock.json
      - run: npm ci
      - run: npm run build
```

Interpretation: CI lint/test/build configuration exists, but no deployment job or runtime outcome ingestion is specified.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E62

Location: `research/architecture/architecture.md:23-68`

```text

Each knowledge state is classified across three independent dimensions.

### 2.1 Ontological classification — What is this?

1. **Concepts & Mental Models**  
   Theoretical constructs, principles, paradigms, abstractions, or conceptual models.

2. **Artifacts & Entities**  
   Concrete digital or physical outputs/entities, including systems, reports, code artifacts, commits, architectures, datasets, etc.

3. **Processes & Workflows**  
   Sequential operations, methods, and procedures describing how something is performed.

4. **Events**  
   Distinct occurrences in time, such as failures, deployments, meetings, or observed changes.

### 2.2 Epistemic classification — What is its truth status?

1. **Axioms & Ground Truths**  
   Claims currently accepted as verified/reliable within the applicable scope.

2. **Hypotheses & Assumptions**  
   Untested or provisionally accepted claims requiring validation.

3. **Anti-Patterns & Falsified Concepts**  
   Disproven theories, failed approaches, known dead ends, or explicitly rejected propositions retained to prevent cyclic mistakes.

> Open research issue: temporal validity should likely be represented separately from epistemic status. A proposition can have been true within a prior interval without becoming a falsified proposition.

### 2.3 Lifecycle classification — Where is it in its evolution?

1. **Generative Seeds**  
   Raw or developing ideas under consideration before commitment.

2. **Strategic Directives**  
   High-level commitments, goals, or plans that consolidate prior evaluation into direction.

3. **Operational Tasks**  
   Executable actions derived from strategic direction.

4. **Retrospective Insights**  
   Post-execution learning, gaps, technical debt, observations, or context discovered after action.

The lifecycle is not assumed to be strictly linear. Retrospective insights may trigger reconsideration and produce new generative seeds.

```

Interpretation: Proposed O/E/L classifications are independent conceptual dimensions, not the present memory or idea schema.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E63

Location: `research/architecture/architecture.md:105-179`

```text
    v
Generative Seed
```

Important interpretation:

- A **decision** need not be a node classification; `DECIDE` can be the transition that produces a Strategic Directive.
- A prior state is not overwritten when a new state appears.
- The reasoning lineage remains available for historical reconstruction and later challenge.

---

## 4. Two families of graph relationships

### 4.1 Semantic relationships

These describe relationships in the represented domain.

Examples:

- `ALTERNATIVE_TO`
- `DEPENDS_ON`
- `PART_OF`
- `IMPLEMENTS`
- `RELATES_TO`
- `USES`

### 4.2 State-transition relationships

These describe the evolution of knowledge or action.

Examples:

- `CONSIDER`
- `HYPOTHESIZE`
- `EVALUATE`
- `VALIDATE`
- `FALSIFY`
- `DECIDE`
- `DECOMPOSE`
- `EXECUTE`
- `OBSERVE`
- `REFLECT`
- `RECONSIDER`
- `SUPERSEDE`

This distinction is foundational: semantic edges model the world; transition edges model the history of reasoning and action.

---

## 5. Provenance

A transition is a first-class research object even if exposed ergonomically as a graph edge.

Proposed transition record:

```yaml
transition_id:
verb:
from_nodes: []
to_nodes: []

actors:
  initiator: []
  participants: []
  approvers: []

actor_types:
  - human
  - agent
  - group
  - system

evidence: []
rationale:
```

Interpretation: Proposed semantic edges, transition records, actors, authority and lineage exceed the present idea-link/event structure.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E64

Location: `research/architecture/architecture.md:221-294`

```text

- **Evidence strength**
- **Domain-specific actor authority**
- **Historical actor/system reliability**
- **Independence of supporting paths**
- **Degree of corroboration/convergence**
- **Temporal relevance / recency**
- **Applicability to the current context**
- **Strength of contradictory evidence**
- **Formal authorization where decisions are organizational**

A useful conceptual form is:

```text
Weight = f(Evidence,
           DomainAuthority,
           Reliability,
           Independence,
           Convergence,
           TemporalRelevance,
           Contradiction)
```

This is intentionally not yet a finalized mathematical formula.

### Convergence

Repeated arrival at the same conclusion strengthens confidence only to the extent that the paths are meaningfully independent.

Five agents repeating one source should not be treated as five independent confirmations.

Independent human reasoning, separate experiments, telemetry, and distinct agents using non-overlapping evidence may constitute stronger convergence.

---

## 7. Memory interpretation

Working hypothesis:

> Nodes preserve states; transition lineage preserves much of what should be understood as memory.

A single frozen state is not sufficient to reconstruct change. Historical meaning often resides in the delta between states and in the transition that produced the delta.

This does **not** claim that all memory must literally be implemented as graph edges. It is a conceptual hypothesis to test against work in memory systems, temporal knowledge representation, event sourcing, provenance, and cognitive models.

---

## 8. Append-only principle

Prior states and transitions are retained.

Instead of mutating:

```text
Hypothesis -> Ground Truth
```

and losing the former state, D-System records a new state and the transition between them.

This permits:

- historical reconstruction,
- reasoning provenance,
- contradiction analysis,
- supersession chains,
- post-hoc audits,
- counterfactual analysis,
- reliability measurement,
- and knowledge transfer with rationale.

---

## 9. Knowledge transfer / retrieval

```

Interpretation: Proposed reasoning memory, append-only state retention and topology-aware retrieval are research hypotheses, not observed runtime functionality.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E65

Location: `research/architecture/phase_context_contract.md:1-94`

```text
# Phase Context Contract

## 1. Working hypothesis

A D-System **Phase** is the smallest planned unit of work intended to be completed during one bounded agentic development session.

Its deeper purpose is to provide a stable contract between persistent knowledge and ephemeral agent context.

```text
Persistent Knowledge
       |
       | context construction
       v
PHASE CONTEXT PACKAGE
       |
       | agentic execution
       v
Phase Outputs
       |
       | consolidation
       v
Persistent Knowledge
```

## 2. Phase input contract

A phase should be executable without requiring the agent to rediscover the entire project history.

Candidate inputs:

```yaml
phase_id:
plan_id:
objective:

upstream_intent:
  decisions: []
  requirements: []
  constraints: []
  acceptance_criteria: []

context:
  relevant_knowledge: []
  prior_phase_outputs: []
  relevant_artifacts: []
  code_locations: []
  known_failures: []
  unresolved_questions: []

execution:
  permitted_tools: []
  permissions: []
  expected_tasks: []
  dependencies: []

expected_outputs:
  artifacts: []
  tests: []
  documentation: []
  state_changes: []

completion_definition:
  acceptance_criteria: []
  verification_required: []
```

## 3. Phase output contract

After execution, the session should return more than code.

Candidate output:

```yaml
status:
actual_actions: []

artifacts_created: []
artifacts_modified: []
tests_run: []
verification_results: []

decisions_made_during_execution: []
new_assumptions: []
observations: []
new_evidence: []
failures: []
unexpected_findings: []
open_questions: []
technical_debt: []

requirements_satisfied: []
requirements_partially_satisfied: []
requirements_unsatisfied: []

```

Interpretation: Proposed phase inputs/outputs include explicit upstream intent and context plus returned observations and evidence; current backlog only partially embodies this.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E66

Location: `research/architecture/development_traceability_model.md:143-181`

```text
- artifacts,
- functionality,
- observed outcomes.

### Which code depends on this assumption?
Traverse dependency/provenance paths from assumption through decisions and specifications to artifacts.

### Which requirements are unimplemented?
Find requirements with no verified realization path.

### Which implemented functions have no current justification?
Find functionality whose upstream requirement/decision has been superseded, retracted, or lost.

### Which decisions have not been realized?
Find authorized decisions with no downstream verified implementation.

### Which runtime observations challenge design assumptions?
Connect telemetry/observations back to assumptions and claims.

### What changed because of this retrospective insight?
Traverse the next cycle from insight into revised decisions, plans, and artifacts.

## 5. Trace integrity

A trace should not be considered complete merely because a path exists.

Candidate integrity properties:

- provenance is known,
- relationship type is explicit,
- temporal order is coherent,
- decision authority is known,
- requirement scope is known,
- artifact version is identified,
- verification evidence exists,
- deployment/environment is identified,
- observed outcome refers to the correct deployed version.

These properties should be researched before formalization.
```

Interpretation: Trace integrity requires provenance, artifact version, deployment/environment and outcome-version alignment, beyond a path through document IDs.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E67

Location: `research/architecture/two_system_architecture.md:3-56`

```text
## 1. Architectural premise

D-System should not collapse cognition/knowledge management and software execution into one undifferentiated graph model.

They solve different problems.

### System A — Knowledge Construction & Management System (KCMS)

Concerned with:

- information,
- ideas,
- questions,
- observations,
- claims,
- evidence,
- assumptions,
- hypotheses,
- beliefs,
- alternatives,
- inference,
- conclusions,
- decisions,
- provenance,
- memory,
- context,
- conflict,
- convergence,
- authority,
- learning.

Its central question is:

> **What do we currently think/know, why, and how did we get here?**

### System B — Implementation & Experience System (IES)

Concerned with:

- requirements,
- constraints,
- acceptance criteria,
- specifications,
- plans,
- phases,
- tasks,
- dependencies,
- artifacts,
- code,
- configuration,
- tests,
- deployments,
- functionality,
- runtime events,
```

Interpretation: Two conceptual systems separate knowledge justification from intent and realization; the repository instead has cooperating file-based operational subsystems.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E68

Location: `research/hypotheses/novelty_hypotheses.md:11-54`

```text
## H1 — Multi-dimensional state model

A knowledge state classified independently by ontological nature, epistemic status, and idea/action lifecycle may provide a useful typed state representation that is not commonly integrated in existing agent-memory systems.

### Falsification condition
Find an established framework that uses equivalent orthogonal dimensions for essentially the same purpose.

## H2 — Typed transition semantics as reasoning memory

Explicit transitions between append-only knowledge states may provide a useful representation of reasoning history distinct from ordinary semantic graph relationships.

### Falsification condition
Find prior work that already models equivalent typed reasoning-state transitions with comparable semantics and use cases.

## H3 — Provenance as a conflict-resolution input

Transition provenance, including human/agent identity, domain authority, evidence, method, lineage, and delegation, may be usable as an input to epistemic conflict resolution.

### Falsification condition
Find an existing system/formalism that already provides materially equivalent provenance-aware arbitration.

## H4 — Independence-aware convergence

Repeated independent arrival at equivalent states may act as a graph-topological epistemic signal, while derivative agreement should be discounted based on shared lineage.

### Falsification condition
Find prior work that already calculates equivalent convergence over provenance/derivation topology for mixed human-agent knowledge.

## H5 — Topology-aware context transfer

Retrieval for agents may be improved by selecting not only semantically relevant content but also current state, reasoning lineage, evidence, dissent, authority, convergence, and unresolved uncertainty.

### Falsification condition
Find an existing agent-memory/retrieval architecture that already performs materially equivalent context assembly.

## H6 — Integrated human-agent collective knowledge evolution

The full synthesis may form a distinct architecture for shared human-agent knowledge evolution even if every individual primitive exists independently.

### Falsification condition
Find a system or research framework whose end-to-end architecture and purpose substantially subsume D-System.

## Required outcome categories

```

Interpretation: H1-H6 are falsifiable prior-art hypotheses; a code review can assess implementation support but cannot settle novelty.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E69

Location: `research/protocols/research_expansion.md:1-10`

```text
# Literature Review Expansion: Ideation to Reality

## 1. Objective

Extend the existing D-System literature review beyond knowledge/memory into the complete path from reasoning to implemented systems and observed reality.

The review must search for prior art that already provides all or part of:

```text
Idea
```

Interpretation: The expansion extends the original research boundary toward knowledge-to-reality traceability.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E70

Location: `schemas/project.schema.json:14-57`

```text
    },
    "name": { "type": "string" },
    "status": {
      "type": "string",
      "enum": ["active", "inactive", "planning", "blocked", "complete", "archived"]
    },
    "category": {
      "type": "string",
      "enum": ["work", "learning", "system", "personal"],
      "description": "work=client/employer | learning=certifications/study | system=meta-frameworks | personal=life"
    },
    "type": {
      "type": "string",
      "enum": ["project", "activity", "goal", "system", "certification"],
      "description": "project=scoped+bounded | activity=ongoing habit | goal=aspirational target | system=framework being built | certification=credentialing path"
    },
    "description": { "type": "string", "default": "" },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Tag IDs — must exist in _data/tags.json"
    },
    "stakeholders": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Person IDs from _data/people/"
    },
    "started": { "type": ["string", "null"], "format": "date" },
    "target_date": { "type": ["string", "null"], "format": "date" },
    "last_reviewed": {
      "type": ["string", "null"],
      "format": "date",
      "description": "When the owner deliberately sat down and assessed this project. Hand-set, and distinct from the derived last_touched, which only says activity happened. Both questions are worth answering; do not collapse them."
    },
    "review_cadence": {
      "type": ["string", "null"],
      "enum": ["daily", "weekly", "biweekly", "monthly", "quarterly", "ad-hoc", null],
      "description": "Policy the owner sets: how often this project should be touched. The threshold staleness is measured against — a project is stale when today minus the derived last_touched exceeds this rhythm. 'ongoing' is retired: it described activity status, which project.status already carries, and gave the staleness check nothing to compute against. ad-hoc declares no rhythm, so the project never becomes stale on a schedule."
    },
    "repository": {
      "type": "string",
      "description": "Where this project's own code or content actually lives, when it is not this repository — a local path or a remote URL. d-system tracks that a project exists; this field is how it says where the project went, instead of a free-text note that drifts."
    },
    "notes": { "type": "string", "default": "" }
```

Interpretation: Project status/category/type are distinct operational dimensions; stakeholders and repository are valid source fields absent from the project row.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E71

Location: `schemas/waiting-on.schema.json:5-50`

```text
  "description": "Something another party owes the owner. The mirror of a commitment, not a status on one: here the owner is the creditor rather than the debtor, so the staleness question, the follow-up behaviour and the person's role all differ. This is the inbound half of the owner's second priority — nothing went quiet.",
  "type": "object",
  "required": ["id", "description", "requested", "status"],
  "additionalProperties": false,
  "properties": {
    "id": { "type": "string", "pattern": "^w-[0-9]+" },
    "description": { "type": "string" },
    "owed_by": {
      "type": ["string", "null"],
      "default": null,
      "description": "Person ID if the identity is confirmed, otherwise the name as written. Per ADR-008 a name in a note creates no person record."
    },
    "project_id": { "type": ["string", "null"], "default": null },
    "requested": {
      "type": "string",
      "format": "date",
      "description": "When the owner asked. This is the clock 'gone quiet' is measured against."
    },
    "due_date": { "type": ["string", "null"], "format": "date" },
    "status": {
      "type": "string",
      "enum": ["open", "chased", "received", "abandoned"],
      "description": "open=asked, waiting | chased=followed up at least once | received=delivered | abandoned=stopped waiting without delivery"
    },
    "last_chased": {
      "type": ["string", "null"],
      "format": "date",
      "default": null,
      "description": "Date of the most recent follow-up, so a chase that also went quiet is visible"
    },
    "received": {
      "type": ["string", "null"],
      "format": "date",
      "default": null,
      "description": "When it actually arrived. Protected: an agent never invents completion of anything."
    },
    "priority": {
      "type": ["string", "null"],
      "enum": ["high", "medium", "low", null],
      "default": null
    },
    "tags": { "type": "array", "items": { "type": "string" }, "default": [] },
    "notes": { "type": "string", "default": "" },
    "capture": { "$ref": "evidence.schema.json#/definitions/capture_source" }
  }
}
```

Interpretation: Inbound obligations use a separate status/actor/time vocabulary; owed_by may be an ID or unresolved text.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E72

Location: `schemas/development-event.schema.json:5-44`

```text
  "description": "A training, certification, talk or milestone — the record type that makes personal development countable over time. Kept separate from interaction because a training is not an exchange with a stakeholder, and folding it in would corrupt every meeting metric.",
  "type": "object",
  "required": ["id", "date", "type", "title"],
  "additionalProperties": false,
  "properties": {
    "id": { "type": "string", "pattern": "^de-[0-9]+" },
    "date": { "type": "string", "format": "date" },
    "type": {
      "type": "string",
      "enum": ["training", "certification", "course", "talk", "reading", "milestone", "other"],
      "description": "talk=one the owner gave or attended, recorded either way in notes | milestone=a marked step that is not itself a course or credential"
    },
    "title": { "type": "string" },
    "description": { "type": "string", "default": "" },
    "project_id": {
      "type": ["string", "null"],
      "default": null,
      "description": "Usually a learning or certification project, when one exists"
    },
    "provider": {
      "type": ["string", "null"],
      "default": null,
      "description": "Organization or platform that delivered it"
    },
    "credential": {
      "type": ["string", "null"],
      "default": null,
      "description": "Credential or certificate identifier, when the event produced one"
    },
    "hours": {
      "type": ["number", "null"],
      "minimum": 0,
      "default": null,
      "description": "Effort in hours, when it is known and worth counting"
    },
    "tags": { "type": "array", "items": { "type": "string" }, "default": [] },
    "notes": { "type": "string", "default": "" },
    "capture": { "$ref": "evidence.schema.json#/definitions/capture_source" }
  }
}
```

Interpretation: Development events are personal training/certification records, not deployment or software telemetry events.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E73

Location: `schemas/tag.schema.json:17-39`

```text
    },
    "category": {
      "type": "string",
      "enum": ["client", "platform", "tech", "domain", "methodology", "context"],
      "description": "Grouping axis: client=specific org | platform=named product/service | tech=language/library/tool | domain=knowledge area | methodology=approach/framework | context=situational"
    },
    "description": {
      "type": "string",
      "default": "",
      "description": "One sentence clarifying scope and distinguishing from similar tags"
    },
    "related": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "IDs of semantically related tags — used for discovery, not hierarchy"
    },
    "deprecated": {
      "type": "boolean",
      "default": false,
      "description": "True if this tag is being phased out. Deprecated tags remain valid on existing projects but must not be added to new ones."
    }
  }
```

Interpretation: Tags are topical categories, related IDs and a deprecated flag; deprecation restricts intended new use in prose, not a relationship migration mechanism.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E74

Location: `docs/09-backlog/backlog.yaml:3574-3626`

```text
- id: phase-idea-02
  title: Build the idea triage agent
  plan: doc-idea-record-system
  sources:
  - doc-idea-record-system
  systems:
  - sys-portfolio
  - sys-memory-agents
  owner: repository-owner
  status: complete
  agent: agent-claude
  priority: 3
  session_budget: 1
  depends_on:
  - phase-idea-01
  - phase-idea-08
  scope:
  - Build the agent that scouts each open idea for related plans, phases and documents.
  - Have it move ideas from open to triaged with findings attached, never past that.
  acceptance:
  - The agent writes only through the tool from phase-idea-01, using the finding-kind
    annotated event phase-idea-08 adds.
  - It never advances an idea beyond triaged; owner judgement is not automated.
  - An overlap it finds is recorded on the entry as a finding annotation, never used
    to decline or merge one.
  verification:
  - uv run pytest
  deliverables:
  - .claude/
  next_action: Complete. A full sweep of the remaining ~44 open ideas, and idea
    000049's own triage, are out of scope for this phase and left for a future
    session (see SESS-2026-09-08-18's Left undone).
  session: doc-session-idea-triage-agent
  completion_evidence:
  - .claude/agents/idea-triage.md
  - .claude/commands/idea-triage.md
  - _data/ideas.jsonl
  result: Built the idea-triage subagent and its /idea-triage driver command.
    Exercised end-to-end against three real ideas (000046, 000047, 000048) -
    each produced exactly one finding annotation via
    `tools/append_idea.py annotate --kind finding` and moved open -> triaged,
    never further. Extended at the owner's direction with two non-executing
    proposal mechanisms in the finding text (PROPOSED LINK, PROPOSED PROMOTION)
    that the owner reviews and runs by hand. Backfilled idea 000007's own
    missed promotion (promoted -> PLAN-016) as a related correctness fix.
    Independent sub-agent review corroborated all three acceptance conditions
    Met from its own diff/log inspection and pytest run; its one substantive
    caveat (enforcement is instructional via prompt, not a hard tool-permission
    wall) is recorded in SESS-2026-09-08-18's Left undone, not a blocker.
- id: phase-idea-03
  title: Synthesize the idea and plan lifecycle architecture
  plan: doc-ephemeral-working-plans
  sources:
```

Interpretation: Completed triage phase links PLAN-016 to the agent and driver; its result explicitly describes the later backfill of idea 000007 promotion.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E75

Location: `src/governance/backlog.py:195-216`

```text
        key=lambda item: (item["priority"], item["id"]),
    )
    return promoted + rest


def readiness(item: dict[str, Any], items: dict[str, Any]) -> str:
    if item["status"] != "queued":
        return str(item["status"])
    if all(items[dependency]["status"] == "complete" for dependency in item["depends_on"]):
        return "ready"
    return "waiting"


def render_backlog(
    catalog: dict[str, Any], documents: dict[str, Any], ready_only: bool = False
) -> str:
    """Render deterministic Markdown. The YAML catalog remains the only editable state."""
    items = {item["id"]: item for item in catalog["items"]}
    next_up = catalog.get("next_up", [])
    ordered = queue_order(items, next_up)
    counts = Counter(readiness(item, items) for item in ordered)

```

Interpretation: Readiness and queue position are derived; they are not persisted status transitions or epistemic priority scores.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E76

Location: `src/db/connection.py:7-17`

```text
DB_PATH = Path("data/d_system.duckdb")


@contextmanager
def get_db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    try:
        yield conn
    finally:
        conn.close()
```

Interpretation: The generic database helper is cwd-relative and writable; loader/context tools are repository-root-relative. Current API does not use this helper.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.

## E77

Location: `pyproject.toml:5-27`

```text
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "duckdb>=1.1",
    # DuckDB needs pytz to hand a TIMESTAMP WITH TIME ZONE back to Python. Without it,
    # any query returning idea_events.occurred_at or ideas.created raises rather than
    # returning a row. Nothing in this repository imports pytz directly, so it looks
    # unused — it is not.
    "pytz>=2024.1",
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "jsonschema>=4.23",
    "ruff",
    "mypy",
    "pytest",
    "pytest-asyncio",
    "httpx",
```

Interpretation: Python >=3.12 and direct DuckDB/FastAPI dependencies are declared; jsonschema is in dev extras although runtime tools import it.

Confidence: HIGH. Alternative/limit: The supported developer workflow installs dev extras; a minimal packaged runtime would need separate validation of its dependency contract.

## E78

Location: `docs/08-governance/GOV-003-backlog-decisions.md:132-139`

```text
**`waiting_on.owed_by` stays unprotected.** It is the structural mirror of `commitment.promised_to`,
which ADR-007 protects, and the surface argument — an agent should not decide who owes the owner
something — reads the same. The owner chose not to widen the protected set anyway. The stakes are
not symmetric: `promised_to` guards the owner's first priority, zero *broken promises*, where a
wrong name means a promise made to nobody. An inbound item is the second priority, and `waiting_on`
is already a medium-stakes type, so under ADR-007's routing table every one of these records reaches
flagged review regardless of evidence level. The protected-field rule would add a second flag on a
record the owner is going to read anyway. ADR-007's set stays at four things.
```

Interpretation: The decision rationale incorrectly says medium-stakes waiting-on always routes to flagged, conflicting with clean routing for all-explicit medium records.

Confidence: HIGH. Alternative/limit: No routing engine yet exists, so this is a concrete policy contradiction affecting future implementation, not observed misrouting.

## E79

Location: `docs/04-decisions/ADR-007-capture-routing.md:77-96`

```text
### 5. Routing on stakes × evidence

Stakes are a property of the record type:

| Tier | Record types |
|---|---|
| Low | raw note, task |
| Medium | commitment, interaction, waiting-on, development event |
| High | decision |
| Structural | new person, new project, new tag, new tag category |

The routing table is the whole policy:

| Route | Condition | What it costs the owner |
|---|---|---|
| **clean** | every field explicit, and stakes low or medium | Nothing; promoted in bulk |
| **flagged** | any inferred or guessed field, or stakes high | One per-item decision |
| **held** | structural — a new durable identity | An identity call the agent may not make |

Reversibility does not appear as a factor because staging already guarantees it; channel does not
```

Interpretation: Explicit low/medium records route clean; only high stakes or non-explicit values require flagged review.

Confidence: HIGH. Alternative/limit: The code establishes this local behavior; it does not establish the value of a future broader architecture.
