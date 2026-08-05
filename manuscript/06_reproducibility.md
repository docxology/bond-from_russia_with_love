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

No tracked artifact depends on wall-clock time. `GENERATION_TIMESTAMP` is the
only clock-derived token and is overridable, which is how the token tests
assert byte-for-byte reproducibility.

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
