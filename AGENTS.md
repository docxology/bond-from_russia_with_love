# AGENTS.md — LURES (From Russia with Love, 1963)

Mission codename **LURES** — a PROJECT BOND film package implementing an
entrapment/deception playbook engine, lure-budget allocation, SIGINT channel
interception, TDOA direction finding, courier handoff scheduling, and a
defector handoff protocol.

## Hard constraints (shared BOND preamble)

- Scope = EXACTLY this package dir. Never touch siblings, the bond root, or
  the template repo.
- **Local-only**: no remote, never push.
- Path-scoped commits inside YOUR own git repo only.
- No mock framework. Real data + computation only; deterministic fakes
  implement the REAL protocol.
- ≥90% line+branch coverage on `src/` (currently ~99%).
- Deterministic: fixed seeds, no untracked RNG, no wall-clock in tracked files.
- Thin `scripts/`; business logic in `src/`.
- `ruff check+format` and `mypy` clean on `src/` and `scripts/`.
- Manuscript variables injected from `manuscript/config.yaml` +
  `src/.../manuscript_variables.py`, never hand-authored.
- README/AGENTS/TODO describe THIS package.

## Layer contract

| Surface | Rule |
|---|---|
| `entrapment_engine.py`, `bait_allocation.py`, `sigint.py`, `direction_finding.py`, `courier_schedule.py`, `handoff_protocol.py`, `scenario.py` | Pure — no `bond_api`/`infrastructure` imports |
| `mission.py` | Thin adapter; the only module importing `bond_api` |
| `manuscript_variables.py`, `figures/` | pure core + yaml/matplotlib; consume `scenario.py` |
| `scripts/` | thin orchestrators |

The public protocol shape is **stable** and consumed cross-package: the
`MissionProvider` class (film + brief/recon/plan/execute/debrief) and the
module-level `GADGETS` dict + `register_gadgets()` hook. Deepen inside the
package; do not break discovery.

## Verification (before done)

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . || echo Clean   # zero lineage strings
```
