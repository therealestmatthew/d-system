# Fleet fixtures

Used by `test/test_fleet_files.py` (`phase-rep-01`, `REQ-039` R01, R02, R04, R05).

- `valid/` is a small complete fleet: `fleet.yaml`, `definitions.yaml`, one system file, a model
  document and a governing document. Every reference in it resolves.
- `broken/<case>/` holds one or more files that replace the same paths in `valid/`. Each case breaks
  exactly one kind of reference, and the integrity check must report it.
- `invalid/` holds single files that must fail their schema.
- `enum-extra-edge-type.json` is an edge-type list with one value the model document does not define.
