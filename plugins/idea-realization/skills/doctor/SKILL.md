---
name: doctor
description: Compare every file the idea-realization install-state record names against the disk and report each as unchanged, drifted or missing, changing nothing. Use after a scaffold, or when a plugin file in this repository may have been edited or removed.
---

# Check the installed files

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py"
```

Report the output as printed. The doctor only reports; it never repairs, and neither does this
skill.

- `unchanged` — the file matches the hash recorded when the scaffold wrote it.
- `drifted` — the file was edited since. For a data file such as the idea log or the backlog this is
  expected once work has started; for a copied schema it means the local copy differs from the
  plugin's.
- `missing` — the file was removed. Running the `scaffold` skill again recreates it.
- `(consent: gitignore)` — a file the scaffold changed with the person's consent; people edit it,
  so drift there is usually expected.

Exit 2 means no install-state record exists: the scaffold has not run in this repository.
