# Architecture — LURES

## Package layout

```
src/from_russia_with_love/
  __init__.py            public API barrel
  entrapment_engine.py   pure: bait profiles, bite-probability surface, trap state machine
  sigint.py              pure: keystream ciphers, noisy capture, decipher, SNR, traffic
  handoff_protocol.py    pure: meet/challenge/confirm/abort state machine (SHA-256 confirm)
  mission.py             thin adapter -> frozen bond_api MissionProvider (only bond_api importer)
  manuscript_variables.py  {{TOKEN}} hydration from config + live engine output
  figures/lure_surface.py  matplotlib lure-surface figure
scripts/
  run_mission.py            phase CLI (brief/recon/plan/execute/debrief/run)
  00_preflight.py           protocol + pure-core sanity check
  z_generate_manuscript_variables.py  writes output/data + figure
```

## Layer contract

| Surface | Imports |
|---|---|
| Pure core (`entrapment_engine`, `sigint`, `handoff_protocol`) | stdlib + numpy only. **No `bond_api`, no `infrastructure`.** Importable standalone (fallback if the path dep ever fails). |
| `mission.py` | imports `bond_api.protocol` + `bond_api.registry`, and the pure core. The only adapter. |
| `manuscript_variables.py`, `figures/` | pure core + yaml/matplotlib/numpy. |
| `scripts/` | bootstrap `src/` onto `sys.path`, then call `src` / `bond_api`. |

## Data flow

`brief` → `recon(request)` → `plan(brief)` → `execute(plan)` → `debrief(outcome)`,
driven by `bond_api.protocol.run_mission`. `execute` runs the three pure
engines deterministically (fixed seed 11, 80 dB clean channel, green-pathed
handoff) and packages results with `Provenance`. The film registers its
gadgets with `bond_api.GadgetRegistry` on import.

## Determinism

- seeds fixed at module level (`_SEED = 11`); no wall-clock in tracked files;
- `output/` is regenerable and git-ignored; `z_generate_manuscript_variables.py`
  regenerates `output/data/manuscript_variables.json` + the lure figure.

## Deciding module boundaries

Add pure logic to the concept modules; add protocol wiring to `mission.py`;
add thin entry points under `scripts/`. Do not import `bond_api` from the
pure core.
