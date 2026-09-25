model: Gemini 3.1 Pro
date: 2026-09-25
prompt: PROMPT-040 G2
dev_sha: 5fb84334000aa86efffc7e6ac947aa3e7c744058
branch: agent/gemini-g2-adr-023-parameters

## Summary
Four open parameters of the orchestrator architecture are explored through competing designs. The router shadow rules weigh strict lengthy validation against fast-tracking. Grant records balance manual YAML configuration against CLI-driven JSON management. Owner Desk events contrast simple polling overhead with complex filesystem watches. Finally, the primary lease is evaluated on basic timestamp heartbeats versus OS-level PID checks.

## 1. Router shadow rules
| Design | Mechanism | Drawback |
|---|---|---|
| Strict shadow (Rec) | 100 runs, 95% threshold | Takes a long time to validate |
| Fast-track shadow | 20 runs, 80% threshold | Higher risk of bad routing |

Proposed recommendation: Strict shadow validation (G2-RS-1).

## 2. Grant records
| Design | Mechanism | Drawback |
|---|---|---|
| Tracked YAML (Rec) | Owner writes YAML directly | Prone to syntax errors |
| Tracked JSON via CLI | Owner uses CLI to mutate JSON | CLI overhead |

Proposed recommendation: Tracked YAML authority grants (G2-GR-1).

## 3. Owner Desk events
| Design | Mechanism | Drawback |
|---|---|---|
| Polling (Rec) | 10s poll of directory | Wastes CPU |
| Inotify watch | Watch filesystem events | OS-specific edge cases |

Proposed recommendation: Filesystem polling mechanism (G2-OD-1).

## 4. Lease file
| Design | Mechanism | Drawback |
|---|---|---|
| JSON heartbeat (Rec) | 60s ping, 120s stale | Slow to recover from silent crash |
| Pid-based | 30s ping, OS PID check | OS-specific pid reuse logic |

Proposed recommendation: JSON heartbeat lease (G2-LF-1).

## Questions for the owner
- Accept strict shadow thresholds (100 runs, 95%)?
- Accept polling interval of 10s?
- Accept YAML format for grants?
- Accept 120s staleness for lease?

## Risks in rulings
None identified.

## Ideas outside this prompt
- Investigate SQLite for grant storage once concurrency allows.
