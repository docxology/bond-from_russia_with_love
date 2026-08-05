# Testing Philosophy — LURES

LURES is tested entirely with **real computation**. There is no mock framework
anywhere in the tree — no `MagicMock`, no `mocker.patch`, no `unittest.mock`,
and no hand-rolled stand-in that pretends to be an engine. Every assertion
runs the actual code over actual inputs.

This is cheap to do here because the domain is arithmetic: a logistic surface,
a knapsack, an XOR keystream, a least-squares iteration, a subset DP, and a
SHA-256 comparison. None of them need a network, a clock, or a database, so
there is nothing to fake.

## Determinism first

Every engine is deterministic, and determinism is asserted directly rather
than assumed:

- the bite probability is closed-form, and lure generation folds its seed and
  id into a local RNG;
- SIGINT derives a seeded keystream and seeded noise (seed 0 makes capture
  exactly lossless), so a given `(plaintext, key, seed, SNR)` always produces
  the same capture;
- TDOA timing noise is seeded;
- the knapsack, the scheduler and the handoff protocol contain no randomness
  at all.

Tests assert **byte-identical** artifacts (`test_plot_lure_surface_deterministic`
and `test_plot_tdoa_geometry_deterministic` compare raw PNG bytes across two
renders) and **exact round-trips** (`encipher` → `decipher`,
`bytes_to_symbols` → `symbols_to_bytes`). `generate_variables` takes an
injectable `now`, so token maps can be compared for equality without the clock
defeating the comparison.

## A test must be able to fail

The recurring failure mode in a suite like this is not a wrong assertion — it
is an assertion that could never have been false. Several tests here exist
specifically to prove a gate is live:

- **`test_config_scenario_drift_is_detected`** feeds
  `validate_mission_config` a deliberately mismatched config and requires it to
  raise. Without it, the drift guard would be green by construction and would
  keep passing even if it checked nothing.
- **`test_greedy_is_not_optimal_pinned_counterexample`** pins a concrete
  three-meet instance where the earliest-deadline-first heuristic completes one
  meet and the true optimum is two. It is what stops anyone re-asserting that
  the scheduler is optimal.
- **`test_exact_solver_matches_independent_brute_force`** checks the subset DP
  against an exhaustive permutation search written a deliberately different
  way, so a shared bug cannot make both agree.
- **`test_exact_dominates_greedy_strict_separation`** uses a hand-built
  knapsack instance where greedy provably loses. On the *canonical* scenario
  the two happen to tie, so the canonical test only asserts `exact >= greedy`;
  the strict separation is claimed only where it is true.
- **`test_schedule_takes_windows_in_deadline_order`** guards its own
  non-triviality: it asserts the canonical schedule is neither empty nor
  complete, so the ordering check cannot pass vacuously.

A previous version of the schedule-ordering test compared a list sorted by a
key against that key sorted — true by construction for any input. It was
replaced rather than kept as decoration.

## Real data, real branches

- Unit tests cover each module's happy paths *and* its error and edge branches
  (empty inputs, out-of-range values, illegal transitions, terminal-state
  blocking, oversized instances) with genuine inputs.
- Subprocess smoke tests execute the thin CLIs with `sys.executable` and assert
  real exit codes and real artifacts on disk
  (`output/data/manuscript_variables.json`, both figure PNGs).
- A live cross-reference test scans every numbered manuscript section for token
  references and fails if any is not produced by `generate_variables()`. This
  is the gate that keeps the prose bound to the code, and it fires in practice
  — it caught a literal token example written into prose during this pass.
- The mission adapter is checked against the frozen `bond_api` protocol with a
  runtime `isinstance` check plus a full `run_mission` flow, and the pure core
  is proved `bond_api`-free by reading each module's source.

## Coverage gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

The floor is 90% line-and-branch on `src/`; the suite currently runs well
above it (see `docs/_generated/COUNTS.md` for the measured figure from the
last run). Coverage is a floor, not the goal — the tests above matter more
than the percentage.

A small number of defensive numeric branches are deliberately left uncovered
and documented rather than forced with artificial inputs: the singular-Jacobian
and coincident-site guards in `direction_finding.py`, and the unreachable
insertion-index fallback in `bait_allocation.py`. Forcing them would mean
constructing states the public API cannot produce, which buys a percentage
point and costs honesty about what is actually exercised.
