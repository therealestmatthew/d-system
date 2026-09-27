# Core protocol

The rules every governed document, agent and session in the repository follows. The backlog's own
rules are in `backlog-protocol.md`, document codes in `document-codes.md`, and how agents report
to the owner in `reporting.md`. Configured names (`integration_branch`, `worktree_dir`,
`docs_root`, `backlog_path`, `exempt_files`) are the plugin options described in `tools.md`; the
working-agreement template fills `{{data_root}}` and `{{confidential_dir}}` when it is rendered.

## 1. Authority and sources of truth

- What works is established by executable code plus observed verification. A plan's existence
  never establishes that its feature exists.
- The schemas define the data shapes. The plugin's scripts validate against the plugin's own
  schemas; the copies the scaffold writes into the repository are for reference only.
- The reason for an architectural choice is recorded in an accepted decision record (kind `adr`).
- A plan states what might be built. Draft content is a proposal.
- Who maintains a capability is given by the `owner` and `systems` of the systems registry.
- The owner's and the session's instructions, together with the working agreement, govern an
  agent. A plan never overrides them.
- No service, scheduler or lock daemon runs. Versioned files plus the check are the whole
  mechanism.

## 2. Ownership

- An owner key names an accountable role, not a person's approval. Git records authorship. An AI
  model is an author, never an owner.
- Every owner key a document or phase uses exists in the systems registry's `owners` map before it
  is used.
- An agent id is a claim label, not an owner. A phase's `owner` stays accountable whichever agent
  executes it.

## 3. Agent instruction files

- The working agreement (`AGENTS.md`) governs how agents work. A framework orientation file
  (`CLAUDE.md`) says what the project is and where things live. Where the two disagree, the
  working agreement wins.
- `CLAUDE.md` holds only pointers, the instructions an agent needs before anything else, and the
  few facts worth duplicating. Shared conventions live in the working agreement and are linked,
  not copied.
- The agent instruction files change only with the owner's explicit approval of that change. An
  agent that finds one wrong quotes the passage, proposes wording and stops.

The plugin's `templates/AGENTS.md` and `templates/CLAUDE.md` carry these rules.

## 4. Document kinds and placement

- Every governed document is one of nine kinds: `plan`, `adr`, `architecture`, `requirement`,
  `prompt`, `session`, `walkthrough`, `operation`, `governance`.
- A document lives only under a location its series names in the code register, relative to the
  document root.
- For any non-trivial change, a requirement document and a plan document are written before
  implementation code. Approving one plan does not exempt the next piece of work.
- A plan carries these sections: context and scope, design, work and dependencies, acceptance and
  verification, out of scope, and open questions. It adds requirement coverage when it depends on
  a requirement, and execution order when it names two or more phases. The `plan-check` skill
  checks the headings; `templates/plan.md` is the starting point.
- A requirement states each observable requirement with its verification method, and what each
  requirement is not. `templates/requirement.md` is the starting point.
- Every document body is nonempty. Whether the body carries what its kind needs (a decision
  record's context, decision, alternatives, consequences and revisit trigger; an operation's
  trigger, command and recovery) is a reviewer's judgement.
- A decision record is written whenever a design choice is not obvious.

## 5. Front matter

Every Markdown file under the document root is a governed document whose front matter satisfies
`schemas/document.schema.json`, except the catalog and the files listed in `exempt_files`. Naming a
file `README.md` does not exempt it. Files outside the document root are not scanned; scratch work
that something will rely on is moved into a governed location first.

| Field | Rule |
|---|---|
| `schema_version` | Exactly `1`. |
| `id` | A `doc-` kebab id, unique across governed documents and independent of path. |
| `code` | From the kind's series, unique and permanent; it prefixes the filename (`document-codes.md`). |
| `title` | The document's title. |
| `kind` | One of the nine kinds. |
| `status` | A status the kind allows (section 6). |
| `owner` | An owner key from the systems registry. |
| `created`, `updated` | ISO dates, `created` ≤ `updated` ≤ today. Quoted and unquoted dates are both accepted. |
| `systems` | Unique, existing `sys-` ids; may be empty. |
| `depends_on` | Existing documents that are prerequisites, not related topics. |
| `parent` | Optional. Valid only between two plans. |
| `supersedes` | Optional. Every target has status `superseded`, and every superseded document is named in some document's `supersedes`. |
| `review_after` | Optional advisory date. |
| `completion_evidence` | Required on a complete document: existing repository-relative files. |

- The fields above are the whole set; any other field fails.
- `depends_on`, `supersedes` and `parent` never name the document itself and form no cycle.
- These fail: duplicate YAML keys, a malformed or non-mapping header, delimiters not on their own
  lines, invalid dates, an empty body.
- Schema defaults are descriptive and are never written back into files.
- The namespaces are distinct: `sys-` systems, `doc-` documents, `phase-` phases, `agent-` claim
  labels.

## 6. Document lifecycle

| Kind | Statuses |
|---|---|
| `plan` | `draft`, `approved`, `active`, `complete`, `deprecated`, `superseded` |
| `adr` | `draft`, `accepted`, `deprecated`, `superseded` |
| every other kind | `draft`, `active`, `deprecated`, `superseded` |

- A plan moves from draft to approved when the owner accepts it, and from approved to active when
  implementation starts. It moves from active to complete once its acceptance and evidence are
  reviewed. It moves to deprecated from draft, approved or active when withdrawn, cancelled or
  abandoned, and to superseded from complete or deprecated once its successor is linked. The check
  validates the current status only; the transitions are the reviewer's to confirm.
- A draft is edited freely. An accepted decision is reversed by a new decision record whose
  `supersedes` names the old one, and the old record is kept.
- The owner approves a concrete diff. An `approved` or `accepted` status never manufactures
  approval. Completion means the acceptance criteria are met; a written plan or an empty evidence
  file does not count.
- Before a document is accepted or activated, its facts are checked against the cited sources,
  proposed and current behaviour are kept apart, its dependencies are resolved, and the check
  runs.
- On completion, `completion_evidence` lists the implementation and verification files and the
  body summarises the actual results. On cancellation the reason is kept. When a document is
  superseded, its status and its successor's `supersedes` change in the same change. Several
  documents may each supersede a stated portion of one.

## 7. What enforces what

The `check.py` script runs every installed feature's check and exits nonzero on any problem. It
exits 0 before any hand-off.

| Rule | Enforced by |
|---|---|
| Metadata shape, dates, unknown fields | The schemas |
| Ids, owners, references to systems, documents and plans | The document scan |
| No cycle in dependency, parent, supersession, system or phase graphs | The document scan and the backlog check |
| No overlapping or unclaimed concurrent active phases | The backlog check |
| Declared paths are repository-relative, never escape the repository, and never pass through `.git`, `.venv`, `node_modules` or a symlink; missing system and evidence paths fail | The document scan and the backlog check |
| Work stays inside a phase's declared systems and deliverables; prose is accurate | The owner's diff review |

- The check reads only the document root, its two registers, the backlog and git metadata, and
  loads its schemas locally. A feature that was never set up has nothing to check.
- The backlog is checked only when the document tree is clean.
- Approval authenticity, identifier permanence and evidence quality are human review
  responsibilities, not automated guarantees. The checks cover current-state consistency only.

## 8. The systems registry

- The systems registry (`systems.yaml` at the document root) holds the `owners` map plus one entry
  per independently changeable capability: `id`, `name`, `domain`, `status`, `owner`, `paths`,
  `depends_on`, `description`. It is not a portfolio or a per-file list.
- `domain` groups systems and adds no second hierarchy.
- A system's maturity is `implemented`, `scaffold`, `planned` or `retired`, independent of document
  status. Implemented and scaffold systems list paths, and every listed path exists.
- A system's `depends_on` names existing systems and is acyclic. It records current dependencies
  for implemented systems and intended ones for planned systems. A plan path is not implementation
  evidence.
- The registry changes only when a capability's responsibility, maturity, paths, owner or
  dependencies change. Maturity is reassessed when a plan completes.

## 9. Generated files and the catalog

- A generated file is never edited by hand: its source is changed and it is regenerated. It is
  committed only when a check regenerates it and fails on any difference.
- A conflict in a generated file is resolved by regenerating the file.
- The catalog (`catalog.md` at the document root) lists every governed document's code, kind,
  status, owner and path; every plan with its queued, active and complete phase counts and agents
  when a backlog exists; every held code with its state and reason; and a count per kind.
- The catalog is regenerated with the `catalog` skill and committed after any change to a governed
  document, the code register or the backlog. The check renders it in memory and fails when the
  committed file differs.
- The catalog command writes only when the document tree is clean, and prints the file it wrote
  and its document count.

## 10. The data root and confidentiality

- The data root (`{{data_root}}` in the working agreement) holds the repository's data. Anything
  generated from it is regenerated, never edited.
- The confidential directory (`{{confidential_dir}}`) is never tracked. It is read or written only
  when the owner directs.
- A confidential identifier is never written into a tracked file: not in code, a document, a
  commit message, or a record that describes the identifiers.
- Structure is tracked and confidential content is not. The test for an unclear file is whether
  it would still be correct if a different person adopted the system.
- A fresh clone, with nothing from the confidential directory, passes the check and the tests.
- Pushing your own branch needs no approval. Backing up your own work is not publishing.
- Pushed history is not rewritten. If it seems to need rewriting, the agent says so and stops.

## 11. Worktrees

- Every session works in its own worktree on its own branch, whatever the work touches, and the
  primary checkout's branch is never switched. The only work in the primary checkout is the claim
  commit plus the catalog regeneration it forces, committed together, and the fast-forward that
  integrates a branch.
- The branch is `agent/<phase-id>` and the worktree is `<worktree directory>/<phase-id>`. The
  worktree directory sits outside the repository, so no scan or test walks a second copy.
- Ignored directories (virtual environments, databases, `node_modules`) belong to one worktree.
  Each worktree creates its own and never links a peer's.
- Ignored content never travels through a merge, and removing a worktree destroys it. It is copied
  out by hand first.
- A server started from a worktree uses a free port chosen explicitly.
- Diffs are narrow, one concern per commit, on the session's own branch only.
- A session rebases onto the integration branch whenever a peer integrates, and never merges the
  integration branch in.

The `session-start` skill carries these steps.

## 12. Integration

- Integration onto the integration branch needs the owner's explicit yes for every phase. A green
  branch is ready to integrate, not cleared to.
- A branch qualifies for integration only when the check and the tests pass after rebasing onto
  the current integration branch. A red rebase is never integrated.
- Before every fast-forward the primary checkout is confirmed clean (`backlog-protocol.md`,
  section 11).
- Integration is a fast-forward made from the primary checkout. A non-fast-forward means rebase
  again and re-run the check, never a merge commit.
- After integration the worktree is removed and the branch deleted.
- Without the owner's yes the branch stays unmerged and is reported ready for review, with
  `git diff <integration branch>..agent/<phase-id>`.
- A branch that fails after rebase is fixed on that branch against the current integration branch.
  A peer's commit is never reverted.
