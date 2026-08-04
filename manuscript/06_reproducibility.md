# Reproducibility

## Determinism

Every engine is deterministic. The entrapment engine uses a fixed logistic
model and seeded lure generation; SIGINT uses a seeded keystream and seeded
noise (seed 0 = noise-free); the handoff protocol uses SHA-256 only — no
random draws, no wall-clock time. Fixed seed: config `mission.seed`.

## Verification Gates

- `uv run pytest tests/ --cov=src --cov-fail-under=90`
- `uv run ruff check src/ scripts/ tests/`
- `uv run mypy src/ scripts/`
- `rg -n "template[_]code_project" .` → zero surviving lineage strings

## Artifact Inventory

| Artifact | Path |
|---|---|
| LURE surface figure | `output/figures/lure_surface.png` |
| Manuscript variable map | `output/data/manuscript_variables.json` |
