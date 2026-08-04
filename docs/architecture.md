# Architecture — LURES

## Package layout

```
src/from_russia_with_love/
  scenario.py             canonical fixed scenario (single source of truth)
  entrapment_engine.py    pure: bait profiles, bite-probability surface, trap state machine
  bait_allocation.py      pure: 0/1 knapsack lure-budget allocation + greedy baseline
  sigint.py               pure: keystream ciphers, noisy capture, decipher, SNR, traffic, burst seg.
  direction_finding.py    pure: TDOA measurements + Gauss-Newton transmitter geolocation
  courier_schedule.py     pure: earliest-finish-first handoff-window scheduling
  handoff_protocol.py     pure: meet/challenge/confirm/abort state machine (+ red path)
  mission.py              thin adapter -> frozen bond_api MissionProvider (only bond_api importer)
  manuscript_variables.py {{TOKEN}} hydration from config + live engine output
  figures/lure_surface.py, figures/tdoa_geometry.py
scripts/
  run_mission.py            phase CLI (brief/recon/plan/execute/debrief/run)
  00_preflight.py           protocol + pure-core sanity check
  z_generate_manuscript_variables.py  writes output/data + figures
```

## Layer contract

| Surface | Imports |
|---|---|
| Pure core (all concept modules + `scenario.py`) | stdlib + numpy only. **No `bond_api`, no `infrastructure`.** Importable standalone (fallback if the path dep ever fails). |
| `mission.py` | imports `bond_api.protocol` + `bond_api.registry`, and the pure core. The only adapter. |
| `manuscript_variables.py`, `figures/` | pure core + yaml/matplotlib/numpy. |
| `scripts/` | bootstrap `src/` onto `sys.path`, then call `src` / `bond_api`. |

## Data flow

`brief` → `recon(request)` → `plan(brief)` → `execute(plan)` → `debrief(outcome)`,
driven by `bond_api.protocol.run_mission`. `execute` runs the six pure engines
deterministically (fixed seed 11, 80 dB clean channel, 4-site TDOA, windowed
courier schedule, green-pathed handoff + red-path drill) and packages results
with `Provenance`. The film registers its gadgets with `GadgetRegistry` on
import. Every scenario number comes from `scenario.py`, so the mission, the
manuscript tokens, and the figures cannot disagree.

## Determinism

- seeds fixed at module level (`scenario.SEED = 11`); no wall-clock in tracked
  files; `output/` is regenerable and git-ignored.
- TDOA timing noise, lure generation, and SIGINT capture all use seeded RNGs.

## Deciding module boundaries

Add pure logic to the concept modules; add protocol wiring to `mission.py`;
add scenario constants to `scenario.py`; add thin entry points under
`scripts/`. Do not import `bond_api` from the pure core.
