---
name: from-russia-with-love
description: Build/maintain the LURES PROJECT BOND film package (entrapment engine, SIGINT, defector handoff).
---

# from_russia_with_love — LURES (From Russia with Love, 1963)

PROJECT BOND film package, mission codename **LURES**. Local-only tree, no remote.

## Concepts

- `entrapment_engine.py` — bait profiles + logistic bite-probability surface +
  validated trap state machine.
- `sigint.py` — layered XOR keystream ciphers, Gaussian-noise capture, symbol
  decision, deciphering, empirical SNR, traffic profile.
- `handoff_protocol.py` — meet/challenge/confirm/abort state machine with a
  SHA-256-derived confirm code.
- `mission.py` — the only `bond_api` importer; implements the frozen
  `MissionProvider` and registers gadgets.

## Quick reference

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/run_mission.py run "assess the LURES cover posture"
uv run python scripts/z_generate_manuscript_variables.py
```

## Pitfalls

- Keep the pure core importable WITHOUT bond_api (fallback). Only
  `mission.py` may import bond_api.
- Deterministic: fixed seed 11; clean-channel SNR 80 dB for exact recovery
  (the byte-grid model needs >=~60 dB to be lossless).
- `output/` is git-ignored (regenerable); rerun the vars script to reproduce.
- All `{{TOKEN}}`s must exist in `generate_variables()` — the live
  cross-reference test enforces it.
