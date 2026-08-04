# TODO — LURES (From Russia with Love, 1963 · mission codename LURES)

## Phase 2 — built (complete)

- [x] Pure domain core in `src/from_russia_with_love/`:
  - `entrapment_engine.py` — bait profiles, bite-probability logistic surface,
    trap state machine (DISARMED→…→SPRUNG / ABORTED).
  - `sigint.py` — layered XOR keystream ciphers, Gaussian-noise capture,
    symbol decision, deciphering, empirical SNR, traffic profile.
  - `handoff_protocol.py` — meet/challenge/confirm/abort state machine,
    SHA-256 confirm code.
- [x] `mission.py` — implements the FROZEN `bond_api` `MissionProvider`
  (brief/recon/plan/execute/debrief) and registers gadgets with
  `GadgetRegistry`. `bond_api` wired via `[tool.uv.sources]` path dependency.
- [x] Thin CLIs: `scripts/run_mission.py` (brief/recon/plan/execute/debrief/
  run), `scripts/00_preflight.py`, `scripts/z_generate_manuscript_variables.py`.
- [x] Manuscript sections + `manuscript_variables.py` ({{TOKEN}} hydration) +
  `figures/lure_surface.py`.
- [x] Tests: 75 real-data tests, 100% line+branch coverage on `src/`, zero mocks.

## Declared integration points

- [ ] **BOND-UTILITIES (Q-BRANCH) provenance**: once `bond_utilities.mission_io`
  ships as an importable package, delegate outcome persistence to
  `record_provenance_outcome(mission_id, seed, version, input_payload,
  outcome, path)` instead of the local `Provenance` payload; acceptance: an
  outcome written through it round-trips and carries the derived `seed`.
- [ ] **BOND-COORDINATOR fleet specs**: bind `MissionProvider` discovery via
  `bond_api.discovery.discover(slugs=["from_russia_with_love"], ...)` once the
  coordinator reads fleet mission specs; acceptance: coordinator drives the
  five-stage flow and lists the LURES provider by slug.
- [ ] **BOND-CLI / BOND-OPS**: surface `run_mission.py` phases as suite CLI
  subcommands once those packages convert; acceptance: `bond ops run
  from_russia_with_love deploy` reproduces the phase output.

## Notes

- Kept the pure core infra-free so the fallback (no `bond_api`) still works.
- `output/` is regenerable and git-ignored; rerun
  `scripts/z_generate_manuscript_variables.py` to reproduce
  `output/data/manuscript_variables.json` + the figure.
