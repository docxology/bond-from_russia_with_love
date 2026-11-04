# LURES — Generated counts (From Russia with Love, 1963)

Measured by the verification gates. Do not hand-edit — regenerate from an
actual run of the commands in the last column.

| Metric | Value | Measured by |
|---|---|---|
| Tests passing | 174 | `uv run pytest tests/ --cov=src --cov-fail-under=90` |
| Tests failing / skipped | 0 / 0 | same run |
| src line+branch coverage | 99.48% | same run |
| Coverage gate | >=90% (`--cov-fail-under=90`) | pyproject `fail_under` |
| Uncovered statements in `src/` | 2 (+3 partial branches) | same run |
| Lint | 1 finding — `tests/test_manuscript_variables.py:338` E501 | `uv run ruff check src/ scripts/ tests/` |
| Format | clean (36 files) | `uv run ruff format --check src/ scripts/ tests/` |
| Types | clean (17 source files) | `uv run mypy src/ scripts/` |
| Mock framework usage | none | `rg -n -e MagicMock -e 'unittest\.mock' -e 'mocker\.patch' . --glob '*.py'` (0 hits) |
| Legacy lineage strings (`template[_]code_project`) | 0 | `rg -n "template[_]code_project" .` |
| Domain concept modules | 6 (+ `scenario.py`, `mission.py`, 2 figures) | `src/from_russia_with_love/` |
| Manuscript tokens generated | 62 | `scripts/z_generate_manuscript_variables.py` |

## Where the uncovered lines are

All remaining uncovered statements are defensive branches that the public API
cannot reach, documented rather than forced with artificial inputs:

- `direction_finding.py:183` — the non-finite step guard inside the
  Gauss–Newton loop.
- `direction_finding.py:317` and branch `176->191` — the coincident
  receiver/transmitter Jacobian guard and the singular normal-equation solve
  fall-through.

The `bait_allocation._index` insertion-index fallback that was previously
unreachable (and listed here) is gone: round 2 (C4) removed `_index` by
sorting indices instead of records, so `bait_allocation.py` is now 100%.

Last measured: Python 3.14.9, numpy 2.5.1, darwin.
