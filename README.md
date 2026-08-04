# LURES — From Russia with Love (1963) · PROJECT BOND film package

Mission codename **LURES** implements the operational concepts of *From
Russia with Love* (1963) as a deterministic mission-software package in the
PROJECT BOND suite. This tree is **local-only** — there is no remote, never
push.

## Concepts

1. **Entrapment / deception playbook engine** (`entrapment_engine.py`) —
   bait profile generation and a bounded logistic **bite-probability
   surface**, plus a validated **trap state machine**
   (DISARMED → ARMED → BAITED → ENGAGED → SPRUNG / ABORTED).
2. **SIGINT channel interception simulation** (`sigint.py`) — layered XOR
   keystream ciphers, additive-Gaussian-noise signal capture, symbol
   decision, deciphering, empirical SNR measurement, and traffic profiling.
3. **Defector handoff protocol** (`handoff_protocol.py`) — a
   meet / challenge / confirm / abort state machine whose confirm code is
   derived from challenge + call sign via SHA-256; only an exact confirm
   advances to HANDOFF.

All three are analytical, deterministic models (no real targeting, no live
signals, no wall-clock dependence).

## Architecture

- **Pure core** (`src/from_russia_with_love/`): the three concept modules are
  importable with stdlib + numpy only — no `bond_api` dependency.
- **Adapter** (`src/from_russia_with_love/mission.py`): implements the frozen
  `bond_api` `MissionProvider` protocol and registers gadgets with the
  `GadgetRegistry`.
- **Thin CLIs** (`scripts/`): `run_mission.py` (brief / recon / plan /
  execute / debrief / run), `00_preflight.py`, and
  `z_generate_manuscript_variables.py`.

## Getting started

```bash
cd projects/working/bond/from_russia_with_love
uv sync --extra dev            # wires the local bond-api path dependency
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/run_mission.py run "assess the LURES cover posture"
uv run python scripts/z_generate_manuscript_variables.py  # -> output/data + figure
```

## Gates

- `uv run pytest tests/ --cov=src --cov-fail-under=90` — 100% line+branch (~75 tests).
- `uv run ruff check src/ scripts/ tests/` and `uv run ruff format ...`
- `uv run mypy src/ scripts/`
- `rg -n "template[_]code_project" .` → zero surviving lineage strings.

## Reference

- [Frozen BOND-API protocol](https://github.com/local/bond-api) — `docs/protocol.md`
- `docs/agent_instructions.md` — operational constraints.
