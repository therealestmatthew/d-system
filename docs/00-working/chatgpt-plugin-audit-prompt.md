# Adversarial audit of the idea-realization plugin

You are auditing a Claude Code plugin as an adversary. Assume it is broken. Your job is to find
where it fails, not to confirm that it works.

## What the plugin is

A Claude Code plugin that takes an idea through capture, triage, grouping ("partition"),
planning, phased backlog work and governed documents, in any git repository. It has:
- a manifest at .claude-plugin/plugin.json, with user-configurable options (userConfig) for file
  locations, the integration branch, the worktree directory and a staging directory;
- 14 skills (skills/<name>/SKILL.md), which are instructions Claude Code follows;
- 3 agents (agents/*.md): a triage agent, a partition analyst and a partition adversary;
- Python scripts (scripts/), a CLI dispatcher and check modules;
- JSON Schemas (schemas/), templates copied into a target repository (templates/), and
  reference documents (docs/) written as absolute rules;
- a pytest suite (test/), with pytest.ini at the plugin root.

It is loaded with `claude --plugin-dir <path>`. It is meant to be installed into foreign
repositories, including from inside git worktrees rather than the primary checkout.

## Scope and ground rules

- Audit only the directory `plugins/idea-realization/` in this repository. The rest of the
  repository is out of scope; do not report on it, and do not treat its files as the plugin's
  documentation.
- **Read-only.** Do not modify, create, delete or commit anything in this repository, and do not
  switch branches.
- **Execute nothing inside this repository.** If you can run code, first copy
  `plugins/idea-realization/` to a scratch directory outside the repository, and run everything
  there: install Python 3.12+, pytest, jsonschema and pyyaml, run `python -m pytest -q` from the
  copy's root, and use the scripts directly to reproduce defects. Each script has a PEP 723 header
  naming its dependencies. Run nothing that touches the network. Say which findings you reproduced
  by execution and which you found by reading only. If you cannot execute code, say so at the top
  and audit by reading.
- Do not invent the contents of any file you have not read. Do not assume a file says what another
  file claims it says. If a finding depends on something you could not read or run, put it under
  "Could not verify", not under findings.

## What to hunt for

Cover each area. For each, look for the failure, not the intended behaviour.

1. Install and load: manifest validity, how userConfig options reach skills and scripts, what
   happens when an option is unset, empty, absolute, contains "..", or has a list value where a
   string is expected (and the reverse).
2. Path resolution: running from a worktree versus the primary checkout, the "<repository>"
   substitution in the worktree directory option, symlinks, paths with spaces, and any write that
   can land outside the repository.
3. Scaffolding: whether running it twice is truly a no-op, partial-failure states, what the
   recorded install state claims versus what is on disk, and how drift is reported.
4. The idea log: whether it is really append-only, id allocation under two concurrent writers
   (two sessions or worktrees), malformed or truncated lines, how status transitions and links are
   validated, and whether the rendered view can go stale without anything noticing.
5. The partition sweep: the guard that stops it writing staging files that are not gitignored,
   how it finds the primary checkout from a worktree, and whether accepted output can reach a
   tracked location without the user's ruling.
6. The backlog: phase claims, locks and the active-claim limit, two sessions claiming the same
   phase, stale claims, dependency cycles, and status changes that skip required steps.
7. Document codes: allocation and reservation of document identifiers, collisions between
   concurrent allocations, and gaps or reuse after deletion.
8. Internal consistency: contradictions between the reference documents, between a document and
   the skill that is supposed to follow it, between a skill and the script it calls (flags,
   argument names, output formats), and between schemas and the data the scripts actually write.
   Quote both sides of every contradiction.
9. The tests: tests that cannot fail (tautologies, assertions on mocks of the thing under test,
   checks that pass on empty input), behaviour the documents promise that no test covers, and
   tests that depend on the machine they run on.
10. Portability: assumptions about the host repository (branch names, directory layout, the
    presence of particular files or tools), operating system assumptions, and Python version
    assumptions.
11. Security: shell injection through any user-supplied value (idea text, option values, file
    names, branch names), subprocess calls, writes outside the repository, following symlinks,
    and anything that could read, log or commit secrets.

## Output format

Findings only. No praise, no summary of what works, no introduction.

Rank findings by severity:
- Blocker: data loss, corruption of the idea log or backlog, writes outside the repository,
  code execution from untrusted input, or the plugin failing to install or load.
- Major: wrong behaviour under realistic use, including concurrency, worktrees and unset
  options, or a documented guarantee that does not hold.
- Minor: inconsistencies, misleading documentation, weak tests and edge cases with low impact.

For each finding give:
- Severity and a one-line title.
- File and line number(s), as paths relative to `plugins/idea-realization/`.
- A concrete failure scenario: the inputs or state, the steps, and the wrong result.
- Evidence: the exact lines quoted from the files. Do not paraphrase.
- Whether you reproduced it by execution or found it by reading.
- A suggested fix.

Then a separate section, "Could not verify": each claim or area you could not check, and what
you would need in order to check it.

If you find nothing in an area, write one line saying what you checked there. Do not pad.
