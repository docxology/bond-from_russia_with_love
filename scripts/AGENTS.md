# scripts/ — preflight, the mission driver and the manuscript generator

`00_preflight.py`, `run_mission.py`, `z_generate_manuscript_variables.py`.

## Rules

- **Thin wrappers**: they bootstrap `sys.path` and forward to `src/from_russia_with_love/`. The
  engines live in the package.
- **`00_preflight.py` checks protocol sanity** and is part of the gate; run it before the mission.
- **`run_mission.py brief` runs one phase; `run_mission.py run "<goal>"` runs the full five-stage
  flow.** Exit code is 0 iff the phase succeeded — report the code rather than describing a failed
  phase as done.
- **`z_generate_manuscript_variables.py` writes tokens and figures.** Never hand-author into prose a
  value that a generated token should carry.
- **`output/` is regenerable and git-ignored**; never hand-edit anything in it.
- **Scope is this package directory**: do not write to siblings, the bond root or the template
  repository.
- `mission.py`, `run_mission.py`, `00_preflight.py` and `tests/test_mission.py` need the sibling
  `bond-api`; the pure core and its tests do not.
