# Testing Philosophy — LURES

The LURES suite is tested entirely with **real computation**; there is no mock
framework (no `MagicMock`, `mocker.patch`, or `unittest.mock`).

## Determinism first

Every engine is deterministic and is tested for reproducibility directly:

- the entrapment engine's bite probability is a closed-form logistic, and
  lure generation is seeded;
- SIGINT derives a seeded keystream and seeded noise (seed 0 = noise-free),
  so a given (plaintext, key, seed, SNR) always yields the same capture;
- the handoff protocol uses SHA-256 only — no randomness at all.

Tests assert *byte-identical* outputs (e.g. `test_plot_lure_surface_deterministic`)
and *exact round-trips* (`encipher`→`decipher`, `bytes_to_symbols`→`symbols_to_bytes`).

## Real data, real branches

- Unit tests cover each module's happy paths *and* every error/edge branch
  (empty inputs, out-of-range values, illegal transitions, terminal-state
  blocking) using genuine inputs — no fakes.
- Subprocess smoke tests run the thin CLIs with `sys.executable` and assert
  exit codes and real artifacts (`output/data/manuscript_variables.json`,
  `output/figures/lure_surface.png`).
- A live cross-reference test scans `manuscript/[0-9]*.md` for every
  `{{TOKEN}}` and asserts each exists in `generate_variables()` — the gate
  that keeps prose in sync with code.
- The mission adapter is verified against the frozen `bond_api` protocol via
  the runtime-checkable `MissionProvider` isinstance check and a full
  `run_mission` flow.

## Coverage gate

`uv run pytest tests/ --cov=src --cov-fail-under=90` — the suite reaches
100% line+branch on `src/`.
