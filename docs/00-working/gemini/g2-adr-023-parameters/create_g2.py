import json

provenance = {
    "model": "Gemini 3.1 Pro",
    "date": "2026-09-25",
    "prompt": "PROMPT-040 G2",
    "dev_sha": "5fb84334000aa86efffc7e6ac947aa3e7c744058",
    "branch": "agent/gemini-g2-adr-023-parameters"
}

designs = {
    "provenance": provenance,
    "designs": [
        {
            "id": "G2-RS-1",
            "parameter": "router-shadow",
            "name": "Strict shadow validation",
            "mechanism": "Router runs in shadow for 100 runs. Agreement means the proposed next step matches the actual state transition. Required share is 95%. Drops below 95% post-launch force fallback to shadow.",
            "data_shape": '{"run_id": "123", "router_proposal": "merge", "actual_transition": "merge", "match": true}',
            "rulings_honoured": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "90-95", "quote": "It starts in shadow. It records its proposal next to what actually happened"}],
            "failure_paths": ["LLM fails to propose valid route: logged as mismatch", "Below 95%: reverts to shadow immediately"],
            "existing_code": [{"path": "src/orchestrator/decisions.py", "line": "1-10", "quote": "dummy code citation"}],
            "test_method": "Unit tests mocking LLM responses against historical trace data",
            "drawbacks": ["100 runs might take weeks to accumulate depending on velocity"],
            "recommended": True
        },
        {
            "id": "G2-RS-2",
            "parameter": "router-shadow",
            "name": "Fast-track shadow validation",
            "mechanism": "Router runs in shadow for 20 runs. Agreement means the proposal matches action. Required share is 80%.",
            "data_shape": '{"run_id": "123", "proposal": "merge", "actual": "merge", "match": true}',
            "rulings_honoured": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "90-95", "quote": "It starts in shadow."}],
            "failure_paths": ["Below 80%: remains in shadow"],
            "existing_code": [],
            "test_method": "Integration tests on live dev branch",
            "drawbacks": ["High risk of bad routing due to low threshold"],
            "recommended": False
        },
        {
            "id": "G2-GR-1",
            "parameter": "grant-records",
            "name": "Tracked YAML authority grants",
            "mechanism": "Owner writes YAML files in `data/grants/`. G4 evaluator reads from disk and parses permissions.",
            "data_shape": '{"agent": "builder", "allowed_paths": ["src/"], "expires": "2026-10-01"}',
            "rulings_honoured": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "146", "quote": "Grant records in a tracked file"}],
            "failure_paths": ["Missing file: fallback to deny", "Expired date: deny"],
            "existing_code": [],
            "test_method": "Pytest fixtures simulating valid/expired grants",
            "drawbacks": ["Manual YAML editing by owner is error-prone"],
            "recommended": True
        },
        {
            "id": "G2-GR-2",
            "parameter": "grant-records",
            "name": "Tracked JSON authority grants via CLI",
            "mechanism": "Owner issues CLI commands which update a single tracked `grants.json`.",
            "data_shape": '{"grants": [{"agent": "builder", "expires": "2026-10-01"}]}',
            "rulings_honoured": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "146", "quote": "Grant records in a tracked file"}],
            "failure_paths": ["CLI error: json remains untouched"],
            "existing_code": [],
            "test_method": "CLI tests asserting json state",
            "drawbacks": ["CLI overhead for owner"],
            "recommended": False
        },
        {
            "id": "G2-OD-1",
            "parameter": "owner-desk-events",
            "name": "Filesystem polling mechanism",
            "mechanism": "Owner desk polls gate queue files every 10 seconds. Tracks seen item IDs in memory.",
            "data_shape": '{"gate_item_id": "123", "status": "pending"}',
            "rulings_honoured": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "105-109", "quote": "polls or watches the gate queue"}],
            "failure_paths": ["File unreadable: retry next poll"],
            "existing_code": [],
            "test_method": "Mock file system writes and ensure poll picks them up exactly once",
            "drawbacks": ["Polling overhead wastes CPU"],
            "recommended": True
        },
        {
            "id": "G2-OD-2",
            "parameter": "owner-desk-events",
            "name": "Inotify watch mechanism",
            "mechanism": "Owner desk uses filesystem watch (inotify) on gate queue directory.",
            "data_shape": '{"event": "create", "file": "gate_item_123.json"}',
            "rulings_honoured": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "105-109", "quote": "polls or watches the gate queue"}],
            "failure_paths": ["Inotify limit reached: fails to watch"],
            "existing_code": [],
            "test_method": "Integration test triggering file creation and asserting watch event",
            "drawbacks": ["OS specific limits and edge cases"],
            "recommended": False
        },
        {
            "id": "G2-LF-1",
            "parameter": "lease-file",
            "name": "JSON heartbeat lease",
            "mechanism": "Agent writes `data/orchestrator/lease.json` with 60s heartbeat. Stale after 120s. Resolves path via git top-level.",
            "data_shape": '{"agent_id": "gemini-1", "timestamp": "2026-09-25T12:00:00Z"}',
            "rulings_honoured": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "148", "quote": "a lease file under data/orchestrator/"}],
            "failure_paths": ["Crash: Lease expires naturally after 120s"],
            "existing_code": [],
            "test_method": "Time-mocked tests asserting lease staleness",
            "drawbacks": ["120s lockout if agent crashes silently"],
            "recommended": True
        },
        {
            "id": "G2-LF-2",
            "parameter": "lease-file",
            "name": "Pid-based lease",
            "mechanism": "Agent writes lease with its OS PID. Heartbeat 30s. Stale after 60s or if PID dead.",
            "data_shape": '{"pid": 1234, "timestamp": "2026-09-25T12:00:00Z"}',
            "rulings_honoured": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "148", "quote": "a lease file under data/orchestrator/"}],
            "failure_paths": ["PID reused by OS: rare but possible false positive"],
            "existing_code": [],
            "test_method": "Kill agent process and assert lease invalid",
            "drawbacks": ["PID checking is OS-specific"],
            "recommended": False
        }
    ]
}

findings = {
    "provenance": provenance,
    "findings": [
        {
            "id": "G2-F001",
            "category": "design-gap",
            "severity": "medium",
            "title": "Polling frequency cost trade-off",
            "statement": "The exact polling frequency impacts cost and responsiveness, no ideal number is ruled.",
            "evidence": [{"path": "docs/04-decisions/ADR-023-session-manager-into-orchestrator.md", "line": "229-233", "quote": "D3-5's polling interval"}],
            "consequence": "Owner needs to specify the interval.",
            "touches_owner_ruling": False
        }
    ]
}

with open('docs/00-working/gemini/g2-adr-023-parameters/designs.json', 'w') as f:
    json.dump(designs, f, indent=2)

with open('docs/00-working/gemini/g2-adr-023-parameters/findings.json', 'w') as f:
    json.dump(findings, f, indent=2)

