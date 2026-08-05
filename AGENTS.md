# AGENTS.md — LURES (From Russia with Love, 1963)

Mission codename **LURES** — a PROJECT BOND film package implementing an
entrapment/deception playbook engine, lure-budget allocation, SIGINT channel
interception, TDOA direction finding, courier handoff scheduling, and a
defector handoff protocol.

Deeper agent documentation lives in [`docs/`](docs/): start with
[`docs/agent_instructions.md`](docs/agent_instructions.md), then
[`docs/architecture.md`](docs/architecture.md) before touching module
boundaries and [`docs/testing_philosophy.md`](docs/testing_philosophy.md)
before touching `tests/`.

## Hard constraints (shared BOND preamble)

- Scope = EXACTLY this package directory. Never touch siblings, the bond root,
  or the template repo.
- **Local-only**: there is no remote. Never push.
- Path-scoped commits inside this package's own git repo only.
- No mock framework — no `MagicMock`, `mocker.patch` or `unittest.mock`. Real
  data and real computation only.
- Coverage floor: 90% line-and-branch on `src/`.
- Deterministic: fixed seeds, no untracked RNG, and **no wall-clock read anywhere** — not in tracked files and not in generated `output/` either, so
  regeneration is byte-for-byte identical
  (`tests/test_regeneration_determinism.py` runs the generator twice and
  compares bytes; it injects no clock).
- Thin `scripts/`; business logic in `src/`.
- `ruff check`, `ruff format --check` and `mypy` clean on `src/` and `scripts/`.
- Manuscript metrics arrive as generated tokens from
  `src/from_russia_with_love/manuscript_variables.py`, never hand-authored in
  prose. Paper metadata comes from `manuscript/config.yaml`.
- README / AGENTS / TODO describe THIS package as it currently is.

## Build

```bash
cd projects/working/bond/from_russia_with_love
uv sync --extra dev     # wires the local bond-api path dependency
```

`bond-api` is consumed as a local path dependency declared under
`[tool.uv.sources]` in `pyproject.toml`. If it is missing, the pure core still
imports and its tests still run; only `mission.py`, `scripts/run_mission.py`,
`scripts/00_preflight.py` and `tests/test_mission.py` need it.

## Test

```bash
# Full gate (the one that matters)
uv run pytest tests/ --cov=src --cov-fail-under=90

# A single module
uv run pytest tests/test_courier_schedule.py -v

# A single test
uv run pytest tests/test_mission.py::test_execute_deterministic_success -v
```

Measured test count and coverage from the last verification run are recorded
in [`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md). Regenerate that
file from a run you actually performed — never hand-edit the numbers.

## Run

```bash
uv run python scripts/00_preflight.py                       # protocol sanity
uv run python scripts/run_mission.py brief                  # single phase
uv run python scripts/run_mission.py run "<goal>"           # full five-stage flow
uv run python scripts/z_generate_manuscript_variables.py    # tokens + figures
```

Exit code is 0 iff the phase succeeded. `output/` is regenerable and
git-ignored; never hand-edit anything in it.

## Verify (before you say done)

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/00_preflight.py
rg -n "template[_]code_project" .        # expect zero hits
git status                               # clean after your commit
```

## Layer contract

| Surface | Rule |
|---|---|
| `entrapment_engine.py`, `bait_allocation.py`, `sigint.py`, `direction_finding.py`, `courier_schedule.py`, `handoff_protocol.py`, `scenario.py` | Pure — no `bond_api` / `infrastructure` imports |
| `mission.py` | Thin adapter; the only module importing `bond_api` |
| `manuscript_variables.py`, `figures/` | Pure core + yaml / matplotlib; consume `scenario.py` |
| `scripts/` | Thin orchestrators only |

Every mission constant lives in `scenario.py` and nowhere else.
`manuscript/config.yaml` restates the headline parameters for human readers,
and `validate_mission_config()` fails the manuscript build if the two
disagree — change `scenario.py` first, then mirror it.

## Frozen public shape

The `MissionProvider` class (`film` + `brief` / `recon` / `plan` / `execute` /
`debrief`), the module-level `GADGETS` dict, and the `register_gadgets()` hook
are consumed cross-package by `bond-cli`, the coordinator reconcile and the
orchestrator. Deepen inside the package — new engines, richer `execute()`
internals, more result fields — but do not break discovery.
