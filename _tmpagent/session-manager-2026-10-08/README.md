# Session Manager hand-off bundle (workbench run, 2026-10-08)

Tracked copy of the Session Manager's `_working/session-manager/` material, committed here because
`_working/` is gitignored and a new cloud session starts from a fresh clone. Read `HANDOFF.md`
first. The tools and briefs assume the files live at `/home/user/d-system/_working/session-manager/`,
so the first step of a resumed session is:

    mkdir -p _working/session-manager/{briefs,reviews,review-replies,verdicts-pending,report}
    cp -r _tmpagent/session-manager-2026-10-08/* _working/session-manager/
    mv _working/session-manager/contract.md _working/session-manager/briefs/contract.md
    mkdir -p _working/session-manager/report && cp _tmpagent/session-manager-2026-10-08/artifact-url.txt _working/session-manager/report/

Deviation from this directory's one-file convention: this is a directory bundle; the ledger line
names `session-manager-2026-10-08/HANDOFF.md` as the file. The bundle is a snapshot; the live copy
is `_working/session-manager/` in whichever session resumes. Delete the bundle (ledger `removed`)
once the run's remaining phases are done and the owner has merged the trunk to dev.
