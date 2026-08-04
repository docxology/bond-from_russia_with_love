# Reproducibility

## Determinism

Every engine is deterministic. The entrapment engine uses a fixed logistic
model and seeded lure generation; SIGINT uses a seeded keystream and seeded
noise (seed 0 = noise-free); TDOA timing noise is seeded; the courier and
handoff engines use no randomness at all (SHA-256 only). Fixed seed:
config `mission.seed`.

## Verification Gates

- `uv run pytest tests/ --cov=src --cov-fail-under=90`
- `uv run ruff check src/ scripts/ tests/`
- `uv run mypy src/ scripts/`
- `rg -n "template[_]code_project" .` → zero surviving lineage strings

## Artifact Inventory

| Artifact | Path |
|---|---|
| LURE surface figure | `output/figures/lure_surface.png` |
| TDOA geometry figure | `output/figures/tdoa_geometry.png` |
| Manuscript variable map | `output/data/manuscript_variables.json` |
