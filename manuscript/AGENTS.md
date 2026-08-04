# Manuscript directory — LURES (From Russia with Love, 1963)

Mission codename **LURES**. Agent-facing rules for this package live in
[`../docs/agent_instructions.md`](../docs/agent_instructions.md); this file
covers manuscript-specific editing.

## {{VARIABLE}} token protocol

- Values that come from analysis outputs **must** use `{{TOKEN}}` syntax.
- Pipeline: `scripts/z_generate_manuscript_variables.py` →
  `src/from_russia_with_love/manuscript_variables.py::generate_variables()` →
  `output/data/manuscript_variables.json` + the figures.
- Adding a token: add it to the `generate_variables()` dict, add an assertion
  in `tests/test_manuscript_variables.py` (the live cross-reference test
  `test_all_manuscript_tokens_are_generated` fails automatically if a
  manuscript token is missing), then reference it in a numbered section.

## Figure protocol

| Label | Filename | Generator |
|---|---|---|
| `{#fig:lure_surface}` | `output/figures/lure_surface.png` | `src/from_russia_with_love/figures/lure_surface.py::plot_lure_surface` |
| `{#fig:tdoa_geometry}` | `output/figures/tdoa_geometry.png` | `src/from_russia_with_love/figures/tdoa_geometry.py::plot_tdoa_geometry` |

Reference figures with Pandoc-crossref `@fig:lure_surface` / `[@fig:tdoa_geometry]`.

## Section inventory

| Section | Tokens |
|---|---|
| `00_abstract.md` | BOND_TITLE, BOND_CODENAME, CONFIG_KEYWORDS |
| `01_introduction.md` | LURES_NUM_BAIT_PROFILES |
| `02_methodology.md` | (math only; cites martello/chan/kleinberg) |
| `03_results.md` | LURES_BITE_PROBABILITY, LURES_FINAL_STAGE, LURES_ALLOC_*, LURES_SNR_DB, LURES_RECOVERED_EXACT, LURES_BURST_COUNT, LURES_TDOA_*, LURES_SCHEDULE_*, LURES_RED_PATH_STATE, LURES_HANDOFF_STATE, LURES_CONFIRM_CODE, figures |
| `05_experimental_setup.md` | LURES_NUM_OBJECTIVES, LURES_NUM_BAIT_PROFILES, LURES_SNR_DB, PYTHON_VERSION, PLATFORM, NUMPY_VERSION, GENERATION_TIMESTAMP |
| `06_reproducibility.md` | (gate documentation) |
