# Agent Instructions — LURES (From Russia with Love, 1963)

Mission codename **LURES** is a PROJECT BOND film package. Work ONLY inside
this directory. This tree is **local-only** — there is no remote, never push.

## Operational constraints

- Scope = EXACTLY this package. Never touch siblings, the bond root, or the
  template repo.
- Path-scoped commits inside this package's own git repo only.
- No mock framework. Real data + real computation only.
- Coverage floor: 90% line-and-branch on `src/`
  (`uv run pytest tests/ --cov=src --cov-fail-under=90`).
- Deterministic: fixed seeds; no untracked RNG; no wall-clock read anywhere,
  in tracked files or in generated `output/`, so regeneration is byte-for-byte
  identical (`output/` is regenerable and git-ignored). Dates that must appear
  in the manuscript come from `manuscript/config.yaml` (`paper.date`), never
  from `datetime.now()`.
- Thin orchestrators in `scripts/`; business logic in `src/`.
- Type hints and docstrings on every public function. `ruff check`,
  `ruff format --check` and `mypy` clean on `src/` and `scripts/`.

## Layer contract

| Surface | Rule |
|---|---|
| `src/from_russia_with_love/{entrapment_engine,bait_allocation,sigint,direction_finding,courier_schedule,handoff_protocol,scenario}.py` | Pure domain core — **no** `bond_api` / `infrastructure` imports |
| `src/from_russia_with_love/mission.py` | Thin adapter — the only file importing the frozen `bond_api` protocol |
| `src/from_russia_with_love/manuscript_variables.py`, `figures/` | Consume the canonical `scenario.py`; no `bond_api` |
| `scripts/` | Thin CLIs (mission phases, preflight, manuscript variables) |

Scenario constants live ONLY in `scenario.py`, the single source of truth
shared by `mission.py`, `manuscript_variables.py` and the figure generators.
Never duplicate a mission metric in two places. `manuscript/config.yaml`
restates the headline parameters for human readers, and
`validate_mission_config()` fails the manuscript build if the restatement ever
disagrees — so if you change a constant in `scenario.py`, mirror it in the
config or the build will tell you.

## The frozen surface — do not break it

`mission.py` exposes a public shape that other suite packages bind to across
the fleet: the class named `MissionProvider`, its `film` attribute, the five
stage methods `brief` / `recon` / `plan` / `execute` / `debrief`, the
module-level `GADGETS` dict, and `register_gadgets()`. `bond-cli`, the
coordinator's reconcile pass and the orchestrator all consume these.

**Deepen inside the package — new engines, richer `execute()` internals, more
result fields — but never rename these, change the stage signatures, or change
`GADGETS` from a module-level dict.**

## Mission lifecycle

`scripts/run_mission.py` exposes each phase:

```bash
uv run python scripts/run_mission.py brief
uv run python scripts/run_mission.py recon "<goal>"
uv run python scripts/run_mission.py plan
uv run python scripts/run_mission.py execute
uv run python scripts/run_mission.py debrief
uv run python scripts/run_mission.py run "<goal>"   # full five-stage flow
```

Exit code is 0 iff the phase succeeded; `execute` and `run` return 1 when the
mission outcome is not a success.

## Manuscript tokens

Every token referenced in `manuscript/[0-9]*.md` is computed by
`generate_variables()` in `src/from_russia_with_love/manuscript_variables.py`
from `scenario.py` plus live engine output. Paper metadata (title, authors,
keywords) comes from `manuscript/config.yaml`.

**Never hand-author a metric in prose.** To report a new number: add it to
`generate_variables()`, then reference the token from the section. The live
cross-reference test scans the numbered sections and fails on any token that
is not generated — including, in practice, a literal token example written
into prose by accident.

Regenerate the token map and both figures with:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

## Writing tests here

Read `testing_philosophy.md` first. The short version: no mocks, real inputs,
and every gate must be able to fail. If you add a check, ask what input would
make it fail and — where it is cheap — add that input as a positive control.
A test that cannot fail is worse than no test, because it reads as coverage.

## Verify before you say done

1. `uv run pytest tests/ --cov=src --cov-fail-under=90`
2. `uv run ruff check src/ scripts/ tests/` and
   `uv run ruff format --check src/ scripts/ tests/`
3. `uv run mypy src/ scripts/`
4. `uv run python scripts/00_preflight.py`
5. `rg -n "template[_]code_project" .` — expect zero hits
6. `git status` clean after your commit
7. Report modules touched, measured coverage, test count, and the commit SHA.
   Refresh `docs/_generated/COUNTS.md` from the run you actually did.
