# TODO — LURES (From Russia with Love, 1963 · mission codename LURES)

## Phase 2 — built

- [x] Pure domain core: `entrapment_engine.py` (bait profiles, logistic bite
  surface, trap state machine), `sigint.py` (layered XOR ciphers, noisy
  capture, decipher, SNR, traffic), `handoff_protocol.py` (meet/challenge/
  confirm/abort, SHA-256 confirm).
- [x] `mission.py` with the frozen `bond_api` `MissionProvider` + gadgets.
- [x] Thin CLIs, manuscript + tokens + figure, 75 tests, 100% coverage.

## Phase 4 — deep improvement (current)

- [x] `scenario.py` — canonical single source of truth shared by the mission,
  manuscript tokens, and figures (kills cross-module drift).
- [x] `bait_allocation.py` — exact 0/1 knapsack lure budgeting + greedy
  baseline (entrapment ops).
- [x] `direction_finding.py` — TDOA Gauss–Newton transmitter geolocation
  (SIGINT).
- [x] `courier_schedule.py` — earliest-finish-first handoff-window scheduling.
- [x] `sigint.segment_bursts` — energy-threshold burst segmentation.
- [x] `handoff_protocol.run_red_path` — abort drill (wrong confirm ends ABORT).
- [x] `figures/tdoa_geometry.py` — TDOA geometry figure.
- [x] Deepened `mission.py` `execute()` (six engines, richer results; public
  protocol shape unchanged) and `manuscript_variables.py` (new tokens).
- [x] Manuscript methodology/results/conclusion/abstract + real references
  (Chan & Ho 1994, Martello & Toth 1990, Kleinberg & Tardos 2005).

## Declared integration points

- [ ] **BOND-UTILITIES (Q-BRANCH) provenance**: once `bond_utilities.mission_io`
  ships as an importable package, delegate outcome persistence to
  `record_provenance_outcome(mission_id, seed, version, input_payload,
  outcome, path)` instead of the local `Provenance` payload; acceptance: an
  outcome written through it round-trips and carries the derived `seed`.
- [ ] **BOND-COORDINATOR fleet specs**: bind discovery via
  `bond_api.discovery.discover(slugs=["from_russia_with_love"], ...)` once the
  coordinator reads fleet mission specs; acceptance: a reconcile consumes the
  LURES provider by slug, treating module-level `GADGETS` (dict shape) as one
  of the supported polymorphism branches.
- [ ] **BOND-CLI / BOND-OPS**: surface `run_mission.py` phases as suite CLI
  subcommands once those packages convert; acceptance: `bond ops run
  from_russia_with_love deploy` reproduces the phase output.

## Notes

- Kept the pure core infra-free so the fallback (no `bond_api`) still works;
  `tests/test_mission.py` proves isolation by importing each pure module with
  `bond_api` never loaded.
- `output/` is regenerable and git-ignored; rerun
  `scripts/z_generate_manuscript_variables.py` to reproduce
  `output/data/manuscript_variables.json` + both figures.
- Defensive numeric branches (singular Jacobian, coincident site) are left
  uncovered and documented rather than forced by artificial tests; coverage
  sits comfortably above the 90% gate.
