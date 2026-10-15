---
name: doctor
description: Compare every file the idea-realization install-state record names against the disk and report each as unchanged, edited, stale or missing, changing nothing. Use after a scaffold, or when a plugin file in this repository may have been edited or removed.
---

# Check the installed files

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py"
```

Report the output as printed. The doctor only reports; it never repairs, and neither does this
skill.

- `unchanged` — the file matches the hash recorded when the scaffold wrote it.
- `edited` — a data or configuration file people and agents edit by design (the idea log, the
  backlog, the code register, the registries, `product.yaml`, `project.yaml`) changed since the
  scaffold seeded it. This is normal use and does not fail the run; `check.py` validates the
  content.
- `stale` — a schema copy under `.idea-realization/schemas/` differs from the plugin's own copy.
  The line names the fix: `scaffold.py --feature <feature> --refresh-schemas`.
- `unrecorded` — a schema copy matches the plugin's but the record still holds an older hash (the
  copy was updated by hand). The same refresh command records the current hash.
- `drifted` — a schema copy this plugin version no longer ships differs from the record, or
  `.gitignore` changed since the scaffold changed it with consent.
- `missing` — the file or directory was removed. Running the `scaffold` skill again recreates it.
- `absent` — a recorded directory git ignores, such as the partition staging directory, is not
  there. A fresh clone never has it; it does not fail the run, and the scaffold recreates it.
- `(consent: gitignore)` or `(consent: edit)` — the person consented to the change; recorded by the
  scaffold.

Exit 2 means no install-state record exists: the scaffold has not run in this repository.
