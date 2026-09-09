-- d-system DuckDB schema
-- Source of truth: _data/ JSON files + brain/ Markdown. Applied by: tools/rebuild_db.py

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
CREATE TABLE interactions (
    id                  VARCHAR PRIMARY KEY,
    date                DATE NOT NULL,
    type                VARCHAR NOT NULL,
    summary             VARCHAR NOT NULL,
    project_id          VARCHAR,
    participants        VARCHAR[],
    participant_names   VARCHAR[],
    tags                VARCHAR[],
    notes               VARCHAR DEFAULT ''
);

-- A dated choice, its reasoning and who was involved. See schemas/decision.schema.json.
CREATE TABLE decisions (
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

-- Idea event log. Source: _data/ideas.jsonl (one JSON event per line, append-only).
--
-- idea_events is the record; ideas is a convenience folded from it. RETAIN idea_events IN
-- FULL, PERMANENTLY. Because every transition carries its own timestamp, the state of every
-- idea at any past moment is reconstructible by replaying events up to that instant — how
-- many were open on a given date, what was under review during a quarter, how the shape of
-- the list moved over months. Discarding events in favour of the folded state, as a size
-- optimisation or because current state looks sufficient, destroys that silently and
-- unrecoverably: the events are the only record that the intermediate states ever existed.
-- `identity` is `src.db.ideas.identity(event)`: the event's own `eid` when it carries one,
-- else a digest of its bytes for the 19 events written before `eid` existed. It replaces
-- `(idea, seq)` as the primary key because `seq` is a rebuild-assigned ordinal, not a stored
-- fact — an `amends` pointer naming one would reference a value the log does not contain and
-- the rebuild recomputes on every run. `seq` is retained as an ordinary sortable column: it
-- still orders one idea's own events for display, it is just no longer anyone's address.
-- `author`/`kind`/`text` are populated only on an `annotated` event (and, for `text`, on an
-- `amended` event correcting one); `link_type`/`target` only on a `linked` event (and, for
-- `target`, on an `amended` event retracting one — always to NULL, never to a different idea,
-- phase-idea-08). `promoted_to` is an array so a promotion can name several documents at once;
-- the 19 events written before it was one carry a single-element array once loaded, per
-- `src.db.ideas._as_promoted_to`.
CREATE TABLE idea_events (
    idea         VARCHAR NOT NULL,
    identity     VARCHAR NOT NULL,
    seq          INTEGER NOT NULL,
    -- `at` is reserved in DuckDB and `event` is not; only the timestamp needed renaming.
    event        VARCHAR NOT NULL,
    occurred_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    title        VARCHAR,
    body         VARCHAR,
    status_from  VARCHAR,
    status_to    VARCHAR,
    promoted_to  VARCHAR[],
    -- Populated only on an `amended` event: the identity of the event it corrects.
    amends       VARCHAR,
    author       VARCHAR,
    kind         VARCHAR,
    text         VARCHAR,
    link_type    VARCHAR,
    target       VARCHAR,
    PRIMARY KEY (identity)
);

-- Current state, folded from idea_events by replaying them in order. Derived, never edited,
-- and never a replacement for the events above.
CREATE TABLE ideas (
    id           VARCHAR PRIMARY KEY,
    title        VARCHAR NOT NULL,
    body         VARCHAR NOT NULL,
    status       VARCHAR NOT NULL,
    created      TIMESTAMP WITH TIME ZONE NOT NULL,
    updated      TIMESTAMP WITH TIME ZONE NOT NULL,
    revisits     INTEGER NOT NULL DEFAULT 0,
    promoted_to  VARCHAR[]
);

-- Effective annotations, folded from idea_events: a later amendment's correction, never both.
-- One row per annotation, keyed by its own identity so an amendment target resolves directly.
CREATE TABLE idea_annotations (
    idea      VARCHAR NOT NULL,
    identity  VARCHAR PRIMARY KEY,
    author    VARCHAR NOT NULL,
    kind      VARCHAR NOT NULL,
    text      VARCHAR NOT NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Effective links, folded from idea_events. `target` is NULL and `retracted` TRUE once a
-- link_retraction amendment has been applied — the row stays, because a link is retracted,
-- never deleted. The inverse edge is derived at query time and never stored here.
CREATE TABLE idea_links (
    idea      VARCHAR NOT NULL,
    identity  VARCHAR PRIMARY KEY,
    type      VARCHAR NOT NULL,
    target    VARCHAR,
    retracted BOOLEAN NOT NULL DEFAULT FALSE,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL
);
