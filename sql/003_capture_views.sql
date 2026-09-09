-- Views over the expanded capture entity model (phase-cap-07).
-- Applied by tools/rebuild_db.py, right after 001_schema.sql creates the tables these
-- views reference.

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
