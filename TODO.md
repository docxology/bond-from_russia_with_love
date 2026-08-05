# TODO — LURES (From Russia with Love, 1963 · mission codename LURES)

Open work only. Completed phases are recorded in the git history, not here —
a checklist of finished items is a stale document waiting to happen.

## Open — package quality

- [ ] **Calibrate or explicitly disclaim the bite-probability surface.** The
  logistic `p(q, s) = 1/(1 + exp(-4(q + s - 1)))` is a modelling choice with an
  arbitrary steepness constant of 4. The manuscript now says so, but the
  constant should either become a named, documented parameter in `scenario.py`
  with a stated rationale, or the surface should be reframed as a pure ranking
  function whose absolute values are not meaningful. Acceptance: no reader can
  mistake the output for a calibrated probability.

- [ ] **Make the canonical scenario exercise the optimality gaps it advertises.**
  On the shipped scenario the knapsack greedy ties the exact solver and the
  schedule gap is 0, so both "gap" tokens currently report the uninteresting
  case. The genuinely separating instances live only in the tests. Consider a
  second, deliberately adversarial scenario reported alongside the canonical
  one. Acceptance: the manuscript shows at least one non-zero measured gap
  without inventing numbers.

- [ ] **Cover or remove the unreachable fallback in `bait_allocation._index`.**
  The `return len(targets)` fallback cannot be reached through the public API
  (`greedy_allocate` only ever passes objects drawn from the same tuple). It is
  the only genuinely dead line in `src/`. Acceptance: either a caller exists
  that can hit it, or the function is restructured so the branch does not.

- [ ] **Decide whether `CipherLayer.key` should default to `None`.** A cipher
  layer with no key is invalid and raises at use time in `encipher`/`decipher`.
  Making `key` required would move that failure to construction time. Acceptance:
  either the default is removed, or a comment explains why deferred validation
  is wanted.

## Open — declared integration points

These are blocked on sibling packages, not on this one.

- [ ] **BOND-UTILITIES (Q-BRANCH) provenance**: once `bond_utilities.mission_io`
  ships as an importable package, delegate outcome persistence to
  `record_provenance_outcome(mission_id, seed, version, input_payload, outcome,
  path)` instead of the local `Provenance` payload. Acceptance: an outcome
  written through it round-trips and carries the derived `seed`.

- [ ] **BOND-COORDINATOR fleet specs**: bind discovery via
  `bond_api.discovery.discover(slugs=["from_russia_with_love"], ...)` once the
  coordinator reads fleet mission specs. Acceptance: a reconcile consumes the
  LURES provider by slug, treating the module-level `GADGETS` dict as one of
  the supported polymorphism branches.

- [ ] **BOND-CLI / BOND-OPS**: surface `run_mission.py` phases as suite CLI
  subcommands once those packages convert. Acceptance:
  `bond ops run from_russia_with_love deploy` reproduces the phase output.

## Standing notes

- The pure core is kept infra-free so it imports without `bond_api`;
  `tests/test_mission.py::test_import_without_bond_api_fallback` enforces this
  by reading each pure module's source.
- `output/` is regenerable and git-ignored. Rerun
  `scripts/z_generate_manuscript_variables.py` to reproduce
  `output/data/manuscript_variables.json` and both figures.
- Defensive numeric branches in `direction_finding.py` (singular Jacobian,
  coincident intercept site) are deliberately left uncovered and documented
  rather than forced with artificial inputs.
- `courier_schedule.schedule_handoffs` is a heuristic and is **not** optimal.
  Do not re-describe it as optimal; `max_completed_handoffs` is the exact
  reference, and a counterexample is pinned in the test suite.
