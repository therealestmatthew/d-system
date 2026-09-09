"""Read-only implementation review; writes synthetic fixtures only into /tmp.
Run from repository root: uv run python research/evidence/review_probes.py
"""
from pathlib import Path
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import duckdb
from src.db.ideas import fold
from src.db.source_validation import validate_sources
from src.capture.raw import scan_inbox
from fastapi.testclient import TestClient
from src.main import app


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / f'{name}.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

writer = module('append_idea')
rebuild = module('rebuild_db')
context = module('load_context')
results = {}
# Ensure no inherited override reaches any real portfolio, including _private.
os.environ.pop('D_SYSTEM_DATA_ROOT', None)
with tempfile.TemporaryDirectory(prefix='d-system-review-', dir='/tmp') as temporary:
    base = Path(temporary)
    def tree(name):
        p = base / name
        p.mkdir()
        shutil.copytree(ROOT / 'schemas', p / 'schemas')
        (p / '_data').mkdir()
        return p
    def put(p, directory, name, value):
        dest = p / '_data' / directory / (name + '.json')
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(json.dumps(value))
    def build(p):
        with contextlib.redirect_stdout(io.StringIO()):
            rebuild.rebuild(p)
    def connect(p):
        return duckdb.connect(str(p / 'data/d_system.duckdb'))

    # Current-state projection drops valid source fields and permits dangling parents.
    p = tree('projection')
    project = {'id':'p-one','name':'Synthetic','status':'active','category':'system','type':'system',
               'repository':'/synthetic/repository','stakeholders':['unknown-person']}
    task = {'id':'t-1','description':'Synthetic task','status':'complete','created':'2026-09-01',
            'project_id':'missing-project','commitment_id':'missing-commitment',
            'capture':{'capture_id':'missing-capture','assumed_fields':['due_date']}}
    put(p,'projects','one',project)
    put(p,'tasks','one',task)
    results['dangling_source_errors'] = [str(x) for x in validate_sources(p)]
    build(p)
    with connect(p) as c:
        results['task_loaded_with_dangling_parents'] = c.execute('SELECT project_id,commitment_id,completed FROM tasks').fetchone()
        results['projection_missing_fields'] = {
            'projects': sorted({'repository','stakeholders'} - {row[1] for row in c.execute("PRAGMA table_info('projects')").fetchall()}),
            'tasks': sorted({'capture'} - {row[1] for row in c.execute("PRAGMA table_info('tasks')").fetchall()}),
        }
        results['project_people_from_stakeholders'] = c.execute('SELECT count(*) FROM project_people').fetchone()[0]

    # Duplicate identity passes per-file preflight but fails after destructive rebuild.
    p = tree('duplicate')
    put(p,'projects','original',dict(project,id='old'))
    build(p)
    put(p,'projects','original',dict(project,id='new'))
    put(p,'projects','duplicate',dict(project,id='new'))
    results['duplicate_source_errors'] = [str(x) for x in validate_sources(p)]
    try:
        build(p)
    except Exception as exc:
        results['duplicate_rebuild_exception'] = type(exc).__name__
    with connect(p) as c:
        results['old_projection_after_failed_rebuild'] = c.execute("SELECT count(*) FROM projects WHERE id='old'").fetchone()[0]
        results['partial_projection_after_failed_rebuild'] = c.execute('SELECT count(*) FROM projects').fetchone()[0]

    # Retrieval uses project nullability rather than stored scope; --all still limits.
    p = tree('context')
    build(p)
    with connect(p) as c:
        for i in range(12):
            project_id = 'other-project' if i == 0 else None
            scope = 'global' if i == 0 else 'session'
            c.execute('INSERT INTO memories VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                      [f'mem-{i}',f'Synthetic memory {i}','concept',[],[],'human',project_id,
                       '2026-09-01',None,'high',[],scope,'Synthetic content',f'brain/concepts/{i}.md'])
    context.DB_PATH = p / 'data/d_system.duckdb'
    all_text = context.load(all_memories=True)
    selected = context.load(project='requested-project',limit=100)
    results['all_count_of_12'] = all_text.count('### [CONCEPT]')
    results['global_scope_other_project_included'] = 'id:mem-0 |' in selected
    results['session_scope_null_project_included_as_global'] = 'id:mem-1 | global' in selected

    # Amendment history retains both payloads but timestamps do not mark corrections.
    events = [writer.build_created('000001','Original','Body','2026-09-01T00:00:00Z','e1')]
    events.append(writer.build_amended('000001','e1','2026-09-02T00:00:00Z','e2',title='Corrected'))
    results['amendment_current'] = {k:fold(events)['000001'][k] for k in ('title','updated')}
    results['amendment_prefix'] = fold(events[:1])['000001']['title']
    malformed = events[:1]+[writer.build_linked('000001','extends','999999','2026-09-03T00:00:00Z','e3')]
    for e in malformed: writer.validate(e)
    results['dangling_link_fold_accepted'] = fold(malformed)['000001']['links'][0]['target']
    log = base / 'synthetic-ideas.jsonl'
    writer.append(events[0],log)
    bad_annotation = writer.build_annotated('000001','agent-synthetic','assessment','Synthetic judgement','2026-09-02T00:00:00Z','e4')
    writer.append(bad_annotation,log)
    results['low_level_append_non_owner_assessment'] = fold(writer.load_events(log))['000001']['annotations'][0]['kind']
    status = writer.build_status('000001','open','promoted','2026-09-03T00:00:00Z','e5',['NONEXISTENT-DOC'])
    writer.validate(status)
    results['promotion_target_not_resolved'] = fold([events[0],status])['000001']['promoted_to']
    inverted = writer.build_status('000001','open','triaged','2026-08-01T00:00:00Z','e6')
    writer.validate(inverted)
    results['time_reversal_accepted'] = fold([events[0],inverted])['000001']['updated']

    # Inbox input is text decoded with universal-newline conversion, not byte-preserving.
    inbox = base / 'inbox'; inbox.mkdir()
    original = b'Synthetic line 1\r\nSynthetic line 2\r\n'
    (inbox / 'note.txt').write_bytes(original)
    records, failures = scan_inbox(inbox,base / 'raw')
    results['inbox_crlf_bytes_preserved'] = records[0]['content'].encode() == original
    results['processed_original_crlf_preserved'] = (inbox / 'processed/note.txt').read_bytes() == original
    (inbox / 'note.txt').write_text('Replacement synthetic input')
    scan_inbox(inbox,base / 'raw')
    results['processed_same_filename_preserves_original'] = (inbox / 'processed/note.txt').read_bytes() == original
    results['raw_records_after_two_inbox_inputs'] = len(list((base/'raw').glob('*.json')))

    with TestClient(app) as c:
        results['health'] = {'status':c.get('/health').status_code,'body':c.get('/health').json()}
        results['api_projects_status'] = c.get('/api/v1/projects').status_code

print(json.dumps(results, indent=2))
