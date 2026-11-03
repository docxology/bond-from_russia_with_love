---
name: from-russia-with-love
description: Build/maintain the LURES PROJECT BOND film package (entrapment, allocation, SIGINT, TDOA, courier, handoff).
---

# from_russia_with_love — LURES (From Russia with Love, 1963)

PROJECT BOND film package, mission codename **LURES**. Repository:
`docxology/bond-from_russia_with_love`, default branch `main`.

## Concepts

- `entrapment_engine.py` — bait profiles + logistic bite-probability surface +
  validated trap state machine.
- `bait_allocation.py` — exact 0/1 knapsack lure-budget allocation + greedy baseline.
- `sigint.py` — layered XOR keystream ciphers, Gaussian-noise capture, symbol
  decision, deciphering, empirical SNR, traffic profile, burst segmentation.
- `direction_finding.py` — TDOA measurements + Gauss-Newton transmitter geolocation.
- `courier_schedule.py` — earliest-deadline-first handoff-window *heuristic*
  (`schedule_handoffs`) plus the exact subset-DP optimum
  (`max_completed_handoffs`) it is scored against.
- `handoff_protocol.py` — meet/challenge/confirm/abort state machine (SHA-256
  confirm) with a red-path abort drill.
- `scenario.py` — canonical single source of truth shared by mission + tokens + figures.
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
  `mission.py` may import bond_api; `tests/test_mission.py` proves isolation.
- Deterministic: fixed seed 11; clean-channel SNR 80 dB for exact recovery
  (the byte-grid model needs >=~60 dB to be lossless).
- Scenario constants live ONLY in `scenario.py` — the mission, manuscript
  tokens, and figures must all consume it to avoid metric drift.
  `manuscript/config.yaml` mirrors the headline parameters and
  `validate_mission_config()` fails the build if the two disagree.
- `output/` is git-ignored (regenerable); rerun the vars script to reproduce.
- Every manuscript token must exist in `generate_variables()` — the live
  cross-reference test enforces it, and it also fires on a token written into
  prose as an illustration, so describe the mechanism in words instead.
- TDOA needs >=3 receivers; collinear sites leave the normal equations
  singular (defensive branch, documented rather than force-tested).
- `schedule_handoffs` is a HEURISTIC and is NOT optimal — maximising completed
  meets with release times and deadlines is NP-hard. Do not re-describe it as
  optimal; a counterexample is pinned in `tests/test_courier_schedule.py`.
- `Rendezvous` is a frozen dataclass, so value-equal meets compare equal.
  Track them by index, never by set membership (this was a real bug: a
  duplicate meet vanished from the scheduled/unscheduled ledger entirely).
