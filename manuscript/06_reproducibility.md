# Reproducibility

## Determinism

Every engine is deterministic. The entrapment engine uses a closed-form
logistic model and seeded lure generation; SIGINT derives a seeded keystream
and seeded noise (seed 0 makes capture exactly noise-free); TDOA timing noise
is seeded; the courier scheduler, the knapsack allocator and the handoff
protocol use no randomness at all (SHA-256 only). The mission seed is
`scenario.SEED` = **{{LURES_SEED}}**, declared in
`src/from_russia_with_love/scenario.py` and mirrored into
`manuscript/config.yaml` under a build-time equality check.

Nothing in the package reads the wall clock. There is no clock-derived token:
the date row in §5 is `{{MANUSCRIPT_DATE}}`, taken verbatim from the committed
`paper.date` field of `manuscript/config.yaml`. Every other value is a function
of `scenario.py`, the engines, and the interpreter/library versions. Two
regenerations on the same tree therefore produce byte-identical artifacts —
the token map and both figures alike.

That claim is bound by a test rather than asserted: `test_regeneration_is_byte_identical`
in `tests/test_regeneration_determinism.py` runs the real generator script twice
as a subprocess and compares the SHA-256 of every persisted artifact. It does
*not* inject a fixed clock — injecting one is precisely how a wall-clock
dependency could hide behind a green suite, and this package shipped that bug
once. `test_no_wall_clock_read_under_src` is the positive control: it
fails if any module under `src/` calls `datetime.now`, `time.time`, or
`date.today`.

## Regenerating everything

```bash
uv sync --extra dev
uv run python scripts/z_generate_manuscript_variables.py
```

That writes `output/data/manuscript_variables.json` and re-renders both
figures. `output/` is disposable and git-ignored; nothing in it is ever
hand-edited.

## Verification Gates

- `uv run pytest tests/ --cov=src --cov-fail-under=90`
- `uv run ruff check src/ scripts/ tests/` and `uv run ruff format --check ...`
- `uv run mypy src/ scripts/`
- `uv run python scripts/00_preflight.py` — protocol + pure-core sanity check
- `rg -n "template[_]code_project" .` → zero surviving lineage strings

Two gates in the suite are positive-controlled rather than merely green: the
manuscript token cross-reference test fails if any token referenced in the
prose is not produced by `generate_variables()`, and the drift guard between
`config.yaml` and `scenario.py` is
exercised with a deliberately mismatched config so that it is known to be able
to fail.

## Artifact Inventory

| Artifact | Path |
|---|---|
| LURE surface figure | `output/figures/lure_surface.png` |
| TDOA geometry figure | `output/figures/tdoa_geometry.png` |
| Manuscript variable map | `output/data/manuscript_variables.json` |
