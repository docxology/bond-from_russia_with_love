# LURES — Generated counts (From Russia with Love, 1963)

Measured by the verification gates. Do not hand-edit — regenerate from an
actual run of the commands in the last column.

| Metric | Value | Measured by |
|---|---|---|
| Tests passing | 140 | `uv run pytest tests/ --cov=src --cov-fail-under=90` |
| Tests failing / skipped | 0 / 0 | same run |
| src line+branch coverage | 99.25% | same run |
| Coverage gate | >=90% (`--cov-fail-under=90`) | pyproject `fail_under` |
| Uncovered statements in `src/` | 3 (+4 partial branches) | same run |
| Lint | clean | `uv run ruff check src/ scripts/ tests/` |
| Format | clean (27 files) | `uv run ruff format --check src/ scripts/ tests/` |
| Types | clean (16 source files) | `uv run mypy src/ scripts/` |
| Mock framework usage | none | no `MagicMock` / `mocker.patch` / `unittest.mock` in tree |
| Legacy lineage strings (`template[_]code_project`) | 0 | `rg -n "template[_]code_project" .` |
| Domain concept modules | 6 (+ `scenario.py`, `mission.py`, 2 figures) | `src/from_russia_with_love/` |
| Manuscript tokens generated | 56 | `scripts/z_generate_manuscript_variables.py` |

## Where the uncovered lines are

All remaining uncovered statements are defensive branches that the public API
cannot reach, documented rather than forced with artificial inputs:

- `bait_allocation.py:176` — the insertion-index fallback in `_index`, which
  only fires if a target is not a member of the tuple it came from.
- `direction_finding.py:182, 273` and branch `175->190` — the singular
  normal-equation solve, the non-finite step guard, and the coincident
  receiver/transmitter Jacobian guard.

Last measured: Python 3.14.6, numpy 2.5.1, darwin.
