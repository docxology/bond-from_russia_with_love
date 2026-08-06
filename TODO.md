# TODO — from_russia_with_love (LURES)

LURES implements the operational concepts of *From Russia with Love* (1963) as
a deterministic mission-software package in the PROJECT BOND suite: six pure
engines (entrapment playbook, 0/1-knapsack lure allocation, SIGINT channel
interception, TDOA Gauss–Newton direction finding, courier-handoff scheduling,
defector handoff protocol) behind the frozen `bond_api` `MissionProvider`
adapter, plus a token-hydrated manuscript. **Verified state, measured
2026-08-05 in this tree:** `uv run pytest tests/ --cov=src --cov-fail-under=90`
→ **146 passed, 0 failed, 0 skipped, 99.25% line-and-branch coverage on
`src/`** (Python 3.14.6, numpy 2.5.1, darwin); `ruff check`, `ruff format
--check` (27 files), `mypy src/ scripts/` (16 files) and
`scripts/00_preflight.py` all clean; `rg -n "template[_]code_project" .` zero
hits; `git status` clean. All four findings from the adversarial audit
(`output/verify/from_russia_with_love.json`) are resolved and are **not**
repeated below; the two residual limitations its remediation pass named are
recorded under *Known limitations*.

## Open work

### Correctness

**C1 — Mission constants live outside `scenario.py`, breaking the package's own
declared invariant.** `AGENTS.md` ("Every mission constant lives in
`scenario.py` and nowhere else") and `docs/architecture.md` ("A new mission
constant → `scenario.py` (never a second copy elsewhere)") state an invariant
that four literals currently violate, each duplicated across the two call sites
that must agree:

| Literal | Sites | Why it matters |
|---|---|---|
| `"honey-trap-alpha"` | `src/from_russia_with_love/mission.py:153`, `:195`; `src/from_russia_with_love/manuscript_variables.py:174` | Equals `scenario.BAIT_PROFILE_IDS[0]` today; nothing binds them, so renaming the profile silently splits the executed lure from the published one |
| Burst threshold factor `0.5` and `min_gap=1` | `mission.py:218-219`; `manuscript_variables.py:211-212` | These two unnamed numbers alone determine the published `{{LURES_BURST_COUNT}}` (§3.2) |
| Success thresholds `tdoa_error < 0.5`, `scheduled_count >= 1` | `mission.py:277-278` | README, `docs/architecture.md` and `experiment_plan.yaml` all restate them in prose |
| `input_hash="lures-mission-input-v2"` | `mission.py:286` | Hand-versioned provenance string; nothing recomputes or checks it |

*Done when:* each literal is a named constant in
`src/from_russia_with_love/scenario.py`, listed in `scenario.__all__`, and both
call sites read it.
*Demonstrate:*
`rg -n 'honey-trap-alpha|\* 0\.5|min_gap=1|< 0\.5|lures-mission-input' src/from_russia_with_love/ | rg -v 'scenario\.py'`
returns nothing, then `uv run pytest tests/ --cov=src --cov-fail-under=90`.

**C2 — The package version is hand-copied to seven places with nothing binding
them.** `pyproject.toml:11`, `CITATION.cff:13`, `codemeta.json:7`,
`.zenodo.json:20`, `manuscript/config.yaml:7`,
`src/from_russia_with_love/manuscript_variables.py:51` (`PACKAGE_VERSION`) and
`src/from_russia_with_love/mission.py:54` (`_PACKAGE_VERSION`) all read
`"0.1.0"`. `validate_mission_config()` (`manuscript_variables.py:85-121`)
compares eight mission keys but *not* `version`, so bumping `pyproject.toml`
leaves `Provenance.package_version` and the `{{BOND_VERSION}}` token reporting
the old number with every gate green.
*Done when:* one source of truth (e.g. `importlib.metadata.version`, or a
single module constant the others are checked against) plus a test that fails
when any copy disagrees.
*Demonstrate:* change only `pyproject.toml`'s version, then
`uv run pytest tests/ -k version -v` → fails.

**C3 — The bite-surface steepness is an unnamed literal.** `z = 4.0 * (...)` at
`src/from_russia_with_love/entrapment_engine.py:125` sets the slope of the
logistic that produces `{{LURES_BITE_PROBABILITY}}` and every knapsack profit.
The manuscript now disclaims calibration (§07, recorded below as an accepted
limitation), but the constant itself is still a bare number inside an
expression.
*Done when:* it is a named module- or scenario-level constant with a one-line
rationale, referenced by name in `bait_bite_probability`'s docstring rather
than inlined.
*Demonstrate:* `rg -n '4\.0 \*' src/from_russia_with_love/` returns nothing;
`uv run pytest tests/test_entrapment_engine.py -v`.

**C4 — Dead fallback in `bait_allocation._index`.**
`src/from_russia_with_love/bait_allocation.py:176` (`return len(targets)`)
cannot be reached through the public API: `greedy_allocate` (`:148-155`) only
ever passes objects drawn from the same tuple it searches. It is the only
unreachable statement in `src/` that is not a numeric guard.
*Done when:* either a caller exists that can reach it, or `greedy_allocate` is
restructured to sort indices (as `courier_schedule.schedule_handoffs:123-125`
already does) so `_index` disappears.
*Demonstrate:* `uv run pytest tests/ --cov=src --cov-fail-under=90` shows
`bait_allocation.py` at 100.00% with an empty `Missing` column.

**C5 — `CipherLayer.key` defaults to `None`.**
`src/from_russia_with_love/sigint.py:175` declares `key: bytes | None = None`,
so a keyless layer constructs fine and only fails later inside
`encipher`/`decipher`. Making `key` required moves the failure to construction
time, where the caller can act on it.
*Done when:* either the default is removed (and `scenario.CIPHERS` still
constructs), or a comment at `sigint.py:175` states why deferred validation is
wanted.
*Demonstrate:* `uv run pytest tests/test_sigint.py -v`.

### Verification

**V1 — The mission pipeline is implemented twice and nothing binds the two
copies.** `MissionProvider.execute()`
(`src/from_russia_with_love/mission.py:191-244`) and `generate_variables()`
(`src/from_russia_with_love/manuscript_variables.py:146-214`) each run the same
six engines against `scenario.py` through independently written call sequences.
`tests/test_mission.py` asserts the outcome's *shape* and determinism;
`tests/test_manuscript_variables.py` asserts the tokens against `scenario`.
**No test asserts that the manuscript's numbers equal the mission's
`results`** — so `{{LURES_TDOA_ERROR}}`, `{{LURES_ALLOC_VALUE}}`,
`{{LURES_SCHEDULE_COUNT}}`, `{{LURES_BURST_COUNT}}` and
`{{LURES_HANDOFF_STATE}}` could come to describe a mission the adapter no
longer runs.
*Done when:* a test computes both and asserts field-by-field equality for every
overlapping quantity, and fails if one call site is edited alone.
*Demonstrate:* edit only `mission.py:218` (`* 0.5` → `* 0.9`), then
`uv run pytest tests/ -v` → the new test fails.

**V2 — Four declarative registries are inert; no code or test reads them.**
`experiment_plan.yaml`, `data/claim_ledger.yaml`, `domain_profile.yaml` and
`manuscript/layer_contract.yaml` are referenced only from prose
(`grep -rn "experiment_plan\|claim_ledger\|domain_profile\|layer_contract" --include="*.py" .`
→ zero hits). `experiment_plan.yaml` restates `seed: 11`, `budget: 5`,
`lure_strength: 0.6`, `snr_db: 80.0`, `receivers: 4`, `noise_std: 0.1`,
`rendezvous: 5` and the four success thresholds — a fourth unchecked copy of
`scenario.py`. `data/claim_ledger.yaml` names nine tokens, none checked to
exist in `generate_variables()`.
*Done when:* each file is either consumed by a test that fails on drift (the
model to copy is `validate_mission_config`, positive-controlled by
`tests/test_manuscript_variables.py:115`) or deleted.
*Demonstrate:* change `experiment_plan.yaml`'s `seed: 11` → `seed: 12`, then
`uv run pytest tests/ -v` → fails.

**V3 — The "every mission constant lives in `scenario.py`" invariant has no
gate.** It is asserted in `AGENTS.md` (Layer contract) and
`docs/architecture.md` (Deciding where new code goes) and enforced by nothing;
C1 lists the violations it currently misses. A source-reading gate is the
established pattern here — `tests/test_mission.py:126-149` reads each pure
module's text to enforce the no-`bond_api` rule.
*Done when:* a test reads `mission.py` and `manuscript_variables.py` and fails
on mission literals not sourced from `scenario`.
*Demonstrate:* reintroduce any C1 literal, then `uv run pytest tests/ -v` →
fails.

### Documentation

**D1 — README's gate block is missing a gate.** `README.md` § "Gates" lists
five commands; `AGENTS.md` § "Verify (before you say done)" lists the same five
plus `uv run python scripts/00_preflight.py` — a real gate, and the only one
that proves the pure core imports without `bond_api` and that the wired
protocol runs to success.
*Done when:* the two blocks list the same commands.
*Demonstrate:* `rg -n '00_preflight' README.md` returns a hit inside the Gates
block.

### Extension

**E1 — Give the scheduler the witness instance the allocator already has.** The
knapsack case was fixed by adding `scenario.GREEDY_WITNESS_TARGETS`
(`src/from_russia_with_love/scenario.py:111-117`), so §3.1 reports a strictly
positive measured gap (`{{LURES_WITNESS_GAP}}` = 2.642 today). The scheduler
has no counterpart: `{{LURES_SCHEDULE_GAP}}` is 0 on the canonical
`scenario.RENDEZVOUS`, and the instance where the heuristic provably loses
exists only inside
`tests/test_courier_schedule.py:123` (`test_greedy_is_not_optimal_pinned_counterexample`),
invisible to the manuscript.
*Done when:* `scenario.py` carries a `SCHEDULE_WITNESS_*` instance, tokens
report the heuristic and exact counts on it, and §3.4 shows a non-zero measured
gap.
*Demonstrate:* `uv run python scripts/z_generate_manuscript_variables.py`, then
`rg -n 'SCHEDULE_WITNESS' output/data/manuscript_variables.json`.

**E2 — BOND-UTILITIES (Q-BRANCH) provenance.** Blocked on the sibling package.
Once `bond_utilities.mission_io` is importable, delegate outcome persistence
from the local `Provenance` payload (`mission.py:283-288`) to
`record_provenance_outcome(mission_id, seed, version, input_payload, outcome, path)`.
*Done when:* an outcome written through it round-trips and carries the derived
`seed`. *Demonstrate:* `uv run pytest tests/test_mission.py -v`.

**E3 — BOND-COORDINATOR fleet specs.** Blocked on the sibling package. Bind
discovery via `bond_api.discovery.discover(slugs=["from_russia_with_love"], ...)`
once the coordinator reads fleet mission specs.
*Done when:* a coordinator reconcile consumes the LURES provider by slug,
treating the module-level `GADGETS` dict (`mission.py:84`) as a supported
polymorphism branch. *Demonstrate:* run the coordinator's reconcile against
this package and see the slug listed.

**E4 — BOND-CLI / BOND-OPS subcommands.** Blocked on the sibling packages.
Surface `scripts/run_mission.py` phases as suite CLI subcommands.
*Done when:* `bond ops run from_russia_with_love deploy` reproduces the phase
output of `uv run python scripts/run_mission.py brief`.

## Known limitations (not bugs)

- **The remaining uncovered code in `src/` is defensive and unreachable through
  the public API**, documented rather than forced with artificial inputs:
  `direction_finding.py:182` (singular normal-equation solve), `:273`
  (non-finite step guard) and branch `175->190` (coincident
  receiver/transmitter Jacobian guard), plus `bait_allocation.py:176` — that
  last one is listed above as C4 because it is *removable*, not merely
  unreachable. Measured this session: 3 missed statements, 4 partial branches,
  99.25% total.
- **The method-attribution gate is lexical, not semantic.**
  `tests/test_manuscript_variables.py:302` and `:322` scan for the specific
  retired Chan & Ho phrasings and for the presence of the correct
  Foy/Torrieri citation. That catches regression to the known-wrong wording; it
  cannot detect a novel misattribution phrased differently. A citation's
  correctness is not machine-checkable and the gate does not claim to prove it.
- **The bite-probability surface is a modelling choice, not a calibrated
  probability.** The audit forced this claim to be softened: `manuscript/07`
  now states plainly that the bounded logistic is "not an empirically fitted
  model of anything, and its parameters are not calibrated against data". Only
  the *naming* of its steepness constant remains open (C3); the calibration
  question is settled — there is none, and the manuscript says so.
- **The XOR keystream cipher is pedagogical.** It derives from a seeded PRNG
  and is unsuitable as cryptography (`manuscript/07`, `sigint.py` module
  docstring). Nothing in this package is a security claim.
- **`courier_schedule.schedule_handoffs` is a heuristic and is not optimal.**
  Maximising completed meets with release times and deadlines
  (`1 | r_j, d_j | sum U_j`) is strongly NP-hard. `max_completed_handoffs` is
  the exact reference, the gap is published as a measured quantity, and a
  counterexample is pinned in the suite. Do not re-describe it as optimal.
- **On the canonical scenario both optimality gaps are zero, reported as zero
  on purpose.** The greedy allocator genuinely ties the exact knapsack on
  `scenario.ALLOC_TARGETS` (both 19.526), and the EDF heuristic genuinely
  reaches the optimum on `scenario.RENDEZVOUS` (4 of 5, optimum 4). E1 adds a
  witness for the second case; it does not change what the canonical instance
  shows.
- **The exact scheduler is exponential and bounded.**
  `MAX_EXACT_RENDEZVOUS = 20` (`courier_schedule.py:55`); above it the solver
  raises rather than running. Timed this session at the bound: n=16 0.06 s,
  n=18 0.30 s, n=20 1.17 s — the bound is adequate, not aspirational.
- **`output/` is regenerable and git-ignored.** Rerun
  `scripts/z_generate_manuscript_variables.py` to reproduce
  `output/data/manuscript_variables.json` (56 tokens) and both figures. Nothing
  under `output/` is ever hand-edited.
- **The pure core is kept `bond_api`-free by a source-reading test**
  (`tests/test_mission.py::test_import_without_bond_api_fallback`). Adding an
  infrastructure import to any of the seven pure modules fails the suite.
- **This tree is local-only.** There is no remote; never push. Commits are
  path-scoped to this package's own git repo.

## Verification

Run from `projects/working/bond/from_russia_with_love`. Expected outcomes are
what this session actually observed.

```bash
uv sync --extra dev                                    # wires the local bond-api path dependency
uv run pytest tests/ --cov=src --cov-fail-under=90     # 146 passed, 99.25% coverage
uv run ruff check src/ scripts/ tests/                 # All checks passed!
uv run ruff format --check src/ scripts/ tests/        # 27 files already formatted
uv run mypy src/ scripts/                              # no issues in 16 source files
uv run python scripts/00_preflight.py                  # preflight PASS
rg -n "template[_]code_project" .                      # zero hits (exit 1)
git status                                             # clean after your commit
```

Regenerating artifacts (never hand-edit them):

```bash
uv run python scripts/z_generate_manuscript_variables.py   # output/data + both figures
```

`docs/_generated/COUNTS.md` records the measured test count and coverage.
Regenerate it from a run you actually performed — never hand-edit the numbers.

---

# Round-2 (2026-08-06) — deep improvement: correctness + manuscript

**Baseline (measured this round before any edit):**
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **146 passed, 0 failed,
0 skipped, 99.25%** line-and-branch on `src/`; `ruff check`, `ruff format
--check` (28 files) and `mypy src/ scripts/` (16 files) clean; preflight PASS.

**Final (measured this round after all edits):**
**167 passed, 0 failed, 0 skipped, 99.48%** line-and-branch on `src/`; `ruff
check` clean; `ruff format --check` clean (31 files); `mypy src/ scripts/` clean
(16 files); `scripts/00_preflight.py` PASS; `rg -n "template[_]code_project" .`
zero hits. `docs/_generated/COUNTS.md` regenerated from the real run.

## Findings and fixes (each with a regression/positive-control test)

- **C1 — mission constants now live in `scenario.py`.** The literals
  `"honey-trap-alpha"`, burst `* 0.5`, `min_gap=1`, `tdoa_error < 0.5`,
  `scheduled_count >= 1` and `input_hash="lures-mission-input-v2"` were
  duplicated across `mission.py` and `manuscript_variables.py`. Added named
  scenario constants `PRIMARY_BAIT_PROFILE`, `BURST_THRESHOLD_FRACTION`,
  `BURST_MIN_GAP`, `TDOA_SUCCESS_MAX_ERROR`, `SCHEDULE_SUCCESS_MIN_COUNT`,
  `INPUT_HASH`; both call sites now read them.
  *Evidence:* `tests/test_mission_constants_in_scenario.py` (V3 gate) scans
  both adapters and fails if any literal reappears. The exact demo command
  `rg -n 'honey-trap-alpha|\* 0\.5|min_gap=1|< 0\.5|lures-mission-input' src/ | rg -v scenario.py`
  now returns nothing.
- **C2 — one version source of truth.** `__version__ = "0.1.0"` now lives in
  `src/from_russia_with_love/__init__.py`; `mission._PACKAGE_VERSION`,
  `manuscript_variables.PACKAGE_VERSION` and the `{{BOND_VERSION}}` token all
  read it. `validate_mission_config()` now also rejects a drifted
  `paper.version`, and the declarative copies (pyproject, CITATION.cff,
  codemeta.json, .zenodo.json, config.yaml) are checked.
  *Evidence:* `tests/test_version.py` (all copies agree + drift positive
  control), `tests/test_manuscript_variables.py::test_validate_mission_config_rejects_version_drift`.
  Editing only `pyproject.toml`'s version now fails the suite.
- **C3 — bite-surface steepness named.** `BITE_STEEPNESS = 4.0` is now a
  documented module constant in `entrapment_engine.py` (referenced in the
  `bait_bite_probability` docstring), not a bare number in an expression.
  *Evidence:* `rg -n '4\.0 \*' src/` returns nothing; existing behaviour tests
  still pass.
- **C4 — dead `_index` fallback removed.** `greedy_allocate` now sorts
  indices (the idiom `courier_schedule` uses) rather than records via an
  identity scan with an unreachable `return len(targets)` fallback.
  *Evidence:* `bait_allocation.py` is now **100.00%** (was 98.11% with `176`
  misslisted) and `tests/test_bait_allocation.py::test_greedy_tie_break_is_deterministic_and_ordered`
  pins the insertion-order tie-break.
- **C5 — `CipherLayer.key` required at construction.** The type is now
  `bytes` (no `None` default) and `__post_init__` rejects a missing/empty key,
  so a keyless layer fails where the caller can see it, not deep inside
  encipher/decipher.
  *Evidence:* `tests/test_sigint.py::test_cipher_layer_requires_key_at_construction`.
- **V1 — adapter and token generator bound to each other.** New
  `tests/test_mission.py::test_mission_execute_agrees_with_manuscript_variables`
  runs `execute()` and `generate_variables()` and asserts field-by-field
  equality on every overlapping quantity; editing one call site alone (e.g. the
  burst factor in `mission.py`) now fails the suite. `execute()` also exposes
  `confirm_code` in `results` so the binding is complete.
- **V2 — the four declarative registries are no longer inert.**
  `experiment_plan.yaml`, `data/claim_ledger.yaml`, `domain_profile.yaml` and
  `manuscript/layer_contract.yaml` are now consumed by
  `tests/test_declarative_registries.py`, failing on drift. **Bonus defect
  found:** `experiment_plan.yaml` was not even parseable YAML (its `baseline`
  block contained `key: value` prose); it is now valid YAML and is checked
  against `scenario.py`.
- **V3 — constants-in-scenario invariant now has a gate** (see C1 evidence).
- **D1 — README Gates block now matches AGENTS.** Added
  `uv run python scripts/00_preflight.py` to the README Gates block.
- **E1 — scheduler witness instance.** Added `scenario.SCHEDULE_WITNESS`
  (the long/short-a/short-b instance) plus tokens `LURES_SCHEDULE_WITNESS_*`;
  §3.4 now reports a strictly positive heuristic-vs-exact gap on it, mirroring
  the allocation witness.
  *Evidence:* `tests/test_courier_schedule.py::test_scheduler_witness_instance_separates_the_solvers`,
  `tests/test_manuscript_variables.py::test_schedule_witness_tokens_report_the_separation`.
- **New analysis capability — TDOA uncertainty quantification.** Added
  `direction_finding.crlb_error()`, the Cramér–Rao lower-bound RMS position
  error from the Fisher information matrix at the true transmitter. It returns
  `inf` for a degenerate (exactly singular) geometry rather than fabricating a
  confidence. New tokens `LURES_TDOA_CRLB` and `LURES_TDOA_ERROR_ABOVE_CRLB`;
  §3.3 and a new "Uncertainty and limitations" section (§7) report the bound,
  and the conclusion now states that the package discloses its uncertainty.
  *Evidence:* `tests/test_direction_finding.py` (`test_crlb_*`, four tests).

## Manuscript (round 2)

Regenerated `output/data/manuscript_variables.json` (56 → **62 tokens**) and
both figures via `scripts/z_generate_manuscript_variables.py`. Added: a §3.0
"At a glance" results table bound to live tokens; a Cramér–Rao uncertainty
framing in §3.3; the scheduler-witness separation in §3.4; and an explicit
"Uncertainty and limitations" section in §7. `manuscript/AGENTS.md` section
inventory updated for the new tokens.

## Left for a future round

- **E2/E3/E4 remain blocked** on the sibling `bond-utilities`, `bond-coordinator`
  and `bond-cli`/`bond-ops` packages (provenance persistence, fleet specs,
  CLI subcommands). Not touched this round.
- The two remaining uncovered statements in `src/` are documented defensive
  guards (`direction_finding.py:183` non-finite step, `:317` coincident
  receiver/transmitter raise) — see `docs/_generated/COUNTS.md`.
- `experiment_plan.yaml` is now parseable and checked; a future round could
  deepen the claim-ledger check to validate claim *values*, not just token
  existence.

