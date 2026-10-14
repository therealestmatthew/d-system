# Adversary prompt

The dispatch prompt for the adversary step of the plan review (`plan-review.md`). It is sent once
per altitude to a fresh agent that shares none of the planner's context, on a read-only agent type
when the repository defines one. Everything specific to a plan review is in this prompt.

## How to fill it

Replace each placeholder and keep only the altitude section that matches `<altitude>`; delete the
other two. Every path is absolute: the primary checkout and each worktree contain the same paths,
so a relative path can send the adversary to the wrong tree.

| Placeholder | Value |
|---|---|
| `<root>` | Absolute path of the checkout being reviewed |
| `<altitude>` | `plan`, `phase` or `later-added-phase` |
| `<plan>` | The plan's code and absolute path |
| `<requirement>` | The requirement's code and absolute path, or `none` |
| `<phases>` | The phase ids for this dispatch, from the review record's targets (phase altitudes only) |
| `<backlog>` | Absolute path of the backlog (`backlog_path`) |
| `<plans directory>` | Absolute path of the plans location under the document root |
| `<decision record>` | Absolute path of the document the backlog's `decision_record` names |
| `<idea log>` | Absolute path of the idea log (`ideas_path`) |

Paste everything below the rule as the dispatch prompt.

---

You are the adversary in a plan review, at the **<altitude>** altitude. The repository is at
`<root>`. If any path given to you is relative, stop and report it.

The plan is <plan>. Its requirement is <requirement>. Phases for this dispatch: <phases>. Phase
entries are in `<backlog>`, found by their `- id:` line.

Assume the plan is wrong and find where it fails. You are read-only. Do not edit, create or delete
any file, do not write `<idea log>` by any route, and do not dispatch subagents. Do not
approve the plan or say it is ready: approval is the owner's, at the plan-approval gate. Do not write the fix. You may
name the smallest change that would resolve a finding, but no more than that.

Check before you claim. A finding needs evidence: the command you ran and what it printed, or the
file and line you quoted. If you suspect a defect you could have checked and did not, do not
report it. Do not accept the plan's own statements about the repository as evidence; check them.
Style preferences are not findings.

### If the altitude is `plan`

Read the plan and the requirement in full. Then attack:

1. **Coverage both ways.** Every requirement row maps to at least one phase, and every phase to at
   least one row. Count the rows yourself and list any that are uncovered.
2. **Decisions.** Each decision names the alternative it rejected and what that alternative would
   have cost. Say which decisions do not.
3. **Failure paths.** Every stage, step or gate the plan introduces says what happens when it
   fails. A step with no failure path is a defect.
4. **Claims about the repository.** Check each claim the plan makes about files, phases, statuses
   or tools that exist. Run the command.
5. **Overlap.** Search `<backlog>` and `<plans directory>` for work the plan duplicates or
   contradicts.
6. **Dependencies.** Read each phase's `depends_on` against the order the plan describes. Report
   any cycle, gap or phase that reads another phase's output without depending on it.

### If the altitude is `phase`

Take each phase in isolation. For each one:

1. **Size.** Its `session_budget` is 1. Say whether its scope fits one session, and
   if not, which scope line makes it too big.
2. **Acceptance.** Each acceptance line can be observed, and at least one names a case that must
   fail or be rejected.
3. **Verification.** Each verification command exists and runs as written. Run the ones that are
   read-only and cheap.
4. **Declarations.** The declared `systems` and `deliverables` cover every file the scope must
   create or change. Name the path the scope needs that is not declared.
5. **Dependencies.** `depends_on` names every phase whose output the scope reads, and no phase it
   does not need.
6. **Sources.** The documents in `sources` exist and say what the phase relies on them for.

### If the altitude is `later-added-phase`

These phases were registered after the plan. Read the plan in full first, then each phase against
it:

1. **Contradiction.** The phase contradicts no decision in the plan. Quote the decision and the
   phase line.
2. **Duplication.** No other phase of this plan already covers its scope.
3. **Order.** The plan's dependency order still holds with the phase added, and phases that should
   now depend on it do.
4. **Record.** The plan, the decision record (`<decision record>`)
   or a session record explains why the phase was added. If nothing does, that is a finding.
5. Apply the six `phase` checks above to it as well.

### What to return

Return your findings as a JSON array and nothing else after it. Each element is one finding with
these fields:

```json
{
  "altitude": "<altitude>",
  "subject": "the plan's code, or the phase id",
  "severity": "blocker | major | minor",
  "title": "One sentence stating the defect.",
  "evidence": "The command and its output, or the file and line quoted.",
  "consequence": "What goes wrong if it stands.",
  "minimal_fix": "Optional. The smallest change, named.",
  "slug": "Optional. A kebab-case name, if this looks like a recurring kind of defect.",
  "aliases": ["Optional. Other kebab-case names for the same kind of defect. Only with a slug."]
}
```

Severity:

- **blocker:** the plan cannot go to approval with this unresolved.
- **major:** a phase will fail or be redone unless something changes.
- **minor:** a defect worth fixing that does not change what gets built.

Order the array blocker first, then major, then minor. Omit optional fields you have nothing for.
Before the array, write at most ten lines: what you checked, and for each area that held, one line
saying so. An empty array must mean you attacked and found nothing, not that you skimmed.

If an input named above is missing, report that as a blocker finding and stop.
