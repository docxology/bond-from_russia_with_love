# Architecture — LURES (From Russia with Love, 1963)

## Shape of the package

```
src/from_russia_with_love/
  scenario.py             canonical fixed scenario — the single source of truth
  entrapment_engine.py    bait profiles, logistic bite surface, trap state machine
  bait_allocation.py      exact 0/1 knapsack lure budgeting + greedy baseline
  sigint.py               keystream ciphers, noisy capture, decipher, SNR, bursts
  direction_finding.py    TDOA measurement + Gauss-Newton transmitter geolocation
  courier_schedule.py     EDF handoff heuristic + exact subset-DP optimum
  handoff_protocol.py     meet/challenge/confirm/abort state machine (+ red path)
  mission.py              the ONLY bond_api importer — MissionProvider adapter
  manuscript_variables.py token hydration from scenario + live engine output
  figures/
    lure_surface.py       bite-probability surface figure
    tdoa_geometry.py      intercept sites / true transmitter / estimate figure
scripts/
  run_mission.py                      phase CLI (brief/recon/plan/execute/debrief/run)
  00_preflight.py                     protocol + pure-core sanity check
  z_generate_manuscript_variables.py  writes output/data + both figures
```

## Module by module

### `scenario.py` — the single source of truth

Holds every constant the mission executes: the seed (`SEED = 11`), the
plaintext and cipher stack, bait profile ids, the engagement threshold, the
allocation target pool and budget, the four TDOA receiver positions and the
true transmitter, the rendezvous windows, the handoff call sign and challenge,
the greedy-witness target pool, `OBJECTIVES` (the mission's declared
objectives, verbatim), and `ENGINES` (the analytical engine module names).

`OBJECTIVES` and `ENGINES` are deliberately separate tuples counting
different things — an objective is something the mission sets out to do, an
engine is a module that computes. They are the same length today and nothing
forces that, so the manuscript spends `{{LURES_NUM_OBJECTIVES}}` and
`{{LURES_NUM_ENGINES}}` separately and
`test_scenario_engines_match_the_modules_on_disk` binds `ENGINES` to the
package directory.

Nothing else in the package defines a mission constant. `mission.py`,
`manuscript_variables.py`, and both figure generators import from here, so a
number in the manuscript cannot disagree with the number the code ran. It
imports the dataclasses it needs (`Target`, `Rendezvous`, `Receiver`,
`CipherLayer`) from the concept modules, which is why those modules must never
import `scenario` back — the dependency runs one way.

### `entrapment_engine.py` — deception playbook

* `BaitProfile` — frozen lure record (cover role, target susceptibility,
  payload, lure strength), validated on construction.
* `bait_bite_probability(q, s)` — bounded logistic
  `1 / (1 + exp(-4(q + s - 1)))`, strictly increasing in both arguments. A
  modelling choice, not a fitted model.
* `generate_bait_profile(id, seed=...)` — deterministic lure synthesis by
  folding the seed and the id into a local `random.Random`.
* `TrapStateMachine` — `DISARMED → ARMED → BAITED → ENGAGED → SPRUNG` with
  `ABORTED` terminal, driven by a transition table; illegal events raise and
  leave state untouched.
* `run_bait_campaign(...)` — evaluates the lure and runs the campaign,
  choosing engage/stand-down against the engagement threshold.

### `bait_allocation.py` — lure-budget optimisation

Spends an integer lure budget across the target pool to maximise expected
engagement value (`value_i * p(q, s_i)`).

* `allocate_lures` — **exact** 0/1 knapsack by dynamic programming over
  capacity, back-tracing the chosen set; ties break by insertion order.
* `greedy_allocate` — profit-density heuristic, kept as the baseline the exact
  solver is scored against.

### `sigint.py` — channel interception

The full pipeline, each stage a separately tested function:
`bytes_to_symbols` → `encipher` (layered XOR keystream from
`derive_keystream`) → `encode_symbols` → `capture_with_noise` (AWGN at a
requested SNR; seed 0 is exactly lossless) → `decide_symbols` (nearest-symbol
rounding) → `decipher` → `symbols_to_bytes`. Analysis helpers:
`measure_snr_db` (empirical SNR against ground truth), `traffic_profile`
(length, distinct symbols, peak symbol), and `segment_bursts` (energy-threshold
burst segmentation with a fading-tolerance gap merge). `intercept_channel`
runs the whole chain and returns one result dict.

The cipher is pedagogical, not cryptography — see the manuscript's scope
section.

### `direction_finding.py` — TDOA geolocation

* `Receiver` — a fixed 2-D intercept site.
* `tdoa_measurements` — true pairwise range-difference TDOAs plus seeded
  Gaussian timing noise (seed 0 = exact).
* `estimate_position` — Gauss–Newton non-linear least squares from the
  receiver centroid, with an analytic Jacobian, converging on a step-norm
  tolerance. Returns position, convergence flag, iteration count and residual
  norm; a singular normal-equation solve breaks out with `converged=False`
  rather than raising.
* `localization_error` — Euclidean error against the truth, in **receiver
  coordinate units** (not normalised by the array geometry).
* `min_site_spacing` — smallest distance between two intercept sites; the
  divisor that converts a localisation error into units of site spacing.

The solver is the iterative Taylor-series / Gauss–Newton estimator (Foy
1976; Torrieri 1984), not the closed-form Chan & Ho (1994) estimator, which
this package does not implement.

### `courier_schedule.py` — handoff rendezvous planning

Two solvers, deliberately:

* `schedule_handoffs` — the earliest-deadline-first **heuristic**, and the plan
  the mission executes. Bookkeeping is by index, not by value, so two
  value-identical rendezvous stay distinct in the scheduled/unscheduled split.
* `max_completed_handoffs` — the **exact optimum** by dynamic programming over
  subsets, keeping the earliest completion time per subset. Bounded to
  `MAX_EXACT_RENDEZVOUS` records.

The heuristic is *not* optimal — the underlying problem
(`1 | r_j, d_j | sum U_j`) is NP-hard. The exact solver exists so the gap is
measured rather than assumed; a counterexample where the heuristic loses is
pinned in the test suite.

### `handoff_protocol.py` — defector handoff

`DISARM → MEET → CHALLENGE → CONFIRM → HANDOFF` with `ABORT` reachable from
every active stage. `challenge_confirm_code` derives the six-hex-character
confirm code as `SHA256(call_sign + ':' + challenge)[:6]`, so no randomness or
clock is involved. `run_green()` walks the nominal path; `run_red_path()` is
the abort drill with a deliberately wrong code. A wrong code is an ordinary
terminal outcome (`ABORT`), not an exception; calling `confirm` outside
`CHALLENGE` *is* an error and raises.

### `manuscript_variables.py` — the prose/code binding

`generate_variables(project_root)` runs all six engines and returns the full
token map. Result-derived values are computed, never hand-authored.
`validate_mission_config()` compares the `mission` block of
`manuscript/config.yaml` against `scenario.py` and raises on any disagreement,
so the human-readable restatement of the parameters cannot drift.

## How `mission.py` implements the frozen `MissionProvider`

`bond_api.protocol.MissionProvider` is a runtime-checkable `Protocol` frozen at
Layer 1 of the suite. `mission.py` is the *only* module in this package that
imports `bond_api`; everything else stays pure, and
`tests/test_mission.py::test_import_without_bond_api_fallback` enforces that by
reading each pure module's source and failing if the string `bond_api` appears
in it.

The adapter satisfies the protocol with a top-level class literally named
`MissionProvider` (the name is fixed by the discovery contract) carrying
`film = "from_russia_with_love"` and the five stages:

| Stage | Returns | What it does here |
|---|---|---|
| `brief()` | `MissionBrief` | Publishes `scenario.OBJECTIVES` verbatim, three `Asset`s (bait playbook, cipher stack, receiver array) and determinism + ethics `Constraint`s |
| `recon(request)` | `ReconReport` | Echoes the goal and reports which engines are available |
| `plan(brief)` | `MissionPlan` | Eight `Step`s: bait, allocate, intercept, geolocate, schedule, handoff, package, verify |
| `execute(plan)` | `MissionOutcome` | Runs all six engines against the canonical scenario, packs ~20 result fields, and attaches `Provenance` (version, seed, input hash) |
| `debrief(outcome)` | `Debrief` | Wraps the outcome with the six standing lessons |

`execute()` decides `success` on four independent conditions — exact plaintext
recovery, the handoff reaching `handoff`, TDOA error below 0.5, and at least
one scheduled meet — so a single engine regressing flips the mission red.

Discovery also depends on the module-level **`GADGETS`** dict and the
**`register_gadgets()`** hook, called once at import. The coordinator,
orchestrator and CLI bind to that shape across all packages: **do not change
the class name, the five stage signatures, the `film` attribute, or the
`GADGETS` dict shape.** Deepening happens inside the engines and inside
`execute()`.

## Layer contract

| Surface | May import |
|---|---|
| Pure core (all concept modules + `scenario.py`) | stdlib + numpy only. **No `bond_api`, no `infrastructure`.** |
| `mission.py` | `bond_api.protocol`, `bond_api.registry`, and the pure core |
| `manuscript_variables.py`, `figures/` | pure core + yaml / matplotlib / numpy |
| `scripts/` | bootstrap `src/` onto `sys.path`, then call `src` / `bond_api` |

## Determinism

Seeds are module-level constants in `scenario.py` (`SEED = 11`,
`TDOA_SEED = 11`). SIGINT capture, lure generation and TDOA timing noise all
use seeded RNGs; the knapsack, the scheduler and the handoff protocol use no
randomness at all. No tracked file reads the wall clock — the only
clock-derived token is `GENERATION_TIMESTAMP`, and it is injectable so tests
can assert byte-identical output. `output/` is regenerable and git-ignored.

## Deciding where new code goes

Pure algorithm → a concept module. A new mission constant → `scenario.py`
(never a second copy elsewhere). Protocol wiring → `mission.py`. A new
reported number → a token in `manuscript_variables.py`, then referenced from
the prose. A new entry point → a thin script under `scripts/`. Never import
`bond_api` from the pure core.
