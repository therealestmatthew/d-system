# Document codes

How every governed document gets its permanent code. The code register (`codes.yaml` at the
document root, shape `schemas/codes.schema.json`) defines the series; the `next-code` skill
allocates from them.

## 1. Series and the code register

- Every governed document carries a permanent code from its kind's series. The code prefixes the
  filename as `<code>-<slug>.md`.
- The code register is the only source of truth for each series' prefix, kind, numbering and
  locations.
- The register has one series per kind, with no duplicate prefix or kind, and every kind covered.
  A dated series never allows sub-codes. A held code is never both reserved and retired, and is
  well-formed in a known series.
- A document fails the check if its kind has no series, its code belongs to another series, or its
  code uses the wrong numbering.

The default register (`templates/codes.yaml`), with locations relative to the document root:

| Series | Kind | Location | Numbering |
|---|---|---|---|
| `PLAN` | `plan` | `plans/` | counter, with sub-codes |
| `REQ` | `requirement` | `requirements/` | counter |
| `ADR` | `adr` | `decisions/` | counter |
| `ARCH` | `architecture` | `architecture/` | counter |
| `PROMPT` | `prompt` | `prompts/` | counter |
| `OPS` | `operation` | `governance/` | counter |
| `GOV` | `governance` | `governance/` | counter |
| `SESS` | `session` | `sessions/` | dated |
| `WALK` | `walkthrough` | `sessions/` | dated |

- A counter code reads `<SERIES>-NNN`, optionally with a sub-code `.NN`.
- A dated code reads `<SERIES>-YYYY-MM-DD-NN`, and its date equals the document's `created`.

## 2. Allocation

- A code is allocated with the `next-code` skill (`next-code <kind> [--parent <plan id>]`), which
  prints one code. A code is never chosen by hand or from a directory listing, and the register is
  never edited to take one.
- The next counter code is the highest number among documents, register reservations, retirements
  and pre-merge reservations, plus one.
- The next sub-code is the parent's highest sub-code plus one. The parent holds a top-level code in
  a series that allows sub-codes.
- A dated code takes today's date and the highest same-day sequence plus one, and takes no parent.
  Dated series contend only within one date, which is why the kinds several sessions write at once
  are dated.
- Allocation takes the code: computing it and holding it are one operation from a peer's point of
  view.
- Allocation runs only on a clean document tree. On failure nothing is reserved.

## 3. Multi-file plans and sub-codes

- A plan set lives in a folder named `<parent code>-<slug>` under the plan location. The overview
  holds the parent code. Each child holds a sub-code and a `parent` naming the overview.
- A sub-code and `parent` imply each other. A sub-code without a parent fails; a child with a
  top-level code fails; the sub-code's stem matches the parent's code.
- An area folder sits at most one level inside a plan folder, carries a reader-facing name, and
  holds only sub-coded children. The overview stays at the plan folder's root.
- A flat plan folder is the default. An area folder is used only when the child list is too long to
  show its shape.

## 4. Register reservations and retirements

- A code for a planned, unwritten document (typically a phase deliverable) is reserved under
  `reserved` in the register, with a `reason` naming the planned document and any claiming phase.
- Allocation skips a reserved code. A document using one fails until the same change removes the
  reservation.
- A code whose document is deleted is retired under `retired`. A retired code is never reissued,
  and a document using one fails.
- Held codes appear in the catalog with their state and reason.

## 5. Permanence and renumbering

- Once a code reaches the integration branch it is never reused or renumbered. Superseded and
  deprecated documents keep their codes. Renaming the slug is allowed; changing the code is not.
- A code is free before merge and permanent after. When two branches carry the same code, whoever
  integrates second allocates again, renames the file and updates every reference.
- A duplicate code arises only between allocations on different machines, which share no git
  directory, or from a pre-merge reservation that expired before its document was written.
- The register is the ledger and the check is the check.

## 6. Pre-merge reservations

| | Register reservation | Pre-merge reservation |
|---|---|---|
| Where | `reserved` in the code register | A file under `<git common dir>/code-reservations/` |
| Tracked | Yes | No |
| Made by | A deliberate edit | Every allocation, automatically |
| Lasts | Until its document is written | Until it expires |
| Visible | Everywhere the repository is cloned | Every worktree on the machine |

- Each allocation creates one file named for the code with an exclusive create
  (`O_CREAT | O_EXCL`). Exactly one racer wins, and the loser tries the next candidate, up to 50
  attempts.
- The git common directory is shared by the primary checkout and every linked worktree, so peers
  see a reservation before any merge. A tracked file cannot provide that.
- An empty or unreadable reservation still holds its code and expires by the file's modification
  time.
- Expiry after 14 days is the only automatic release. Allocation prunes expired reservations first.
- `release-code <code>` releases a reservation taken for a document that will not be written. With
  no argument it lists reservations and their holders.
- A reservation is never released because its document exists. It stands until expiry at no cost,
  because allocation skips the code anyway.
