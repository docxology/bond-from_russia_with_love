# Agent Instructions — LURES (From Russia with Love, 1963)

Mission codename **LURES** is a PROJECT BOND film package. Work ONLY inside
this directory. This tree is **local-only** — there is no remote, never push.

## Operational constraints

- Scope = EXACTLY this package. Never touch siblings, the bond root, or the
  template repo.
- Path-scoped commits inside YOUR own git repo only (`git add -A` here).
- No mock framework. Real data + computation only.
- >=90% line+branch coverage on `src/`:
  `uv run pytest tests/ --cov=src --cov-fail-under=90`
- Deterministic: fixed seeds; no untracked RNG; no wall-clock in tracked
  artifacts (`output/` is regenerable and git-ignored).
- Thin orchestrators in `scripts/`; business logic in `src/`.
- Type hints + docstrings. `ruff check + format` and `mypy` clean on
  `src/` and `scripts/`.

## Layer contract

| Surface | Rule |
|---|---|
| `src/from_russia_with_love/{entrapment_engine,sigint,handoff_protocol}.py` | Pure domain core — **no** `bond_api`/`infrastructure` imports |
| `src/from_russia_with_love/mission.py` | Thin adapter — the only file importing the frozen `bond_api` protocol |
| `scripts/` | Thin CLIs (brief/recon/plan/execute/debrief, preflight, manuscript vars) |

## Mission lifecycle

`scripts/run_mission.py` exposes each phase: `brief`, `recon "<goal>"`,
`plan`, `execute`, `debrief`, and `run "<goal>"` (full five-stage flow via
`bond_api.protocol.run_mission`). Exit code 0 iff the phase succeeded.

## Manuscript tokens

All `{{TOKEN}}`s in `manuscript/[0-9]*.md` are computed by
`src/from_russia_with_love/manuscript_variables.py` from
`manuscript/config.yaml` plus live engine output — never hand-author metrics.
The live cross-reference test enforces completeness.

## Verify before you say done

1. `uv run pytest tests/ --cov=src --cov-fail-under=90`
2. `uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/`
3. `uv run mypy src/ scripts/`
4. `rg -n "template[_]code_project" .` (aim zero; only allowed in docs
   describing the lineage check itself)
5. `git status` clean after your commit
6. Report modules + concepts, coverage %, commit SHA.
