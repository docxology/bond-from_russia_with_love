# Manuscript directory — LURES (From Russia with Love, 1963)

Mission codename **LURES**. Agent-facing rules for this package live in
[`../docs/agent_instructions.md`](../docs/agent_instructions.md); this file
covers manuscript-specific editing.

## Token protocol

- Any value that comes from analysis output **must** be a generated token, in
  double-brace syntax. Never hand-author a metric in prose.
- Pipeline: `scripts/z_generate_manuscript_variables.py` →
  `src/from_russia_with_love/manuscript_variables.py::generate_variables()` →
  `output/data/manuscript_variables.json` + both figures.
- Adding a token: add it to the `generate_variables()` dict, add an assertion
  in `tests/test_manuscript_variables.py`, then reference it in a numbered
  section. The live cross-reference test
  `test_all_manuscript_tokens_are_generated` fails automatically if a section
  references a token that is not generated.
- That gate is literal: do not write an example token in prose either, because
  the scanner cannot tell an illustration from a real reference. Describe the
  mechanism in words instead.
- Scenario parameters are checked too — `validate_mission_config()` fails the
  build if the `mission` block of `config.yaml` disagrees with `scenario.py`.

## Figure protocol

| Label | Filename | Generator |
|---|---|---|
| `{#fig:lure_surface}` | `output/figures/lure_surface.png` | `src/from_russia_with_love/figures/lure_surface.py::plot_lure_surface` |
| `{#fig:tdoa_geometry}` | `output/figures/tdoa_geometry.png` | `src/from_russia_with_love/figures/tdoa_geometry.py::plot_tdoa_geometry` |

Reference figures with Pandoc-crossref `@fig:lure_surface` /
`[@fig:tdoa_geometry]`.

## Section inventory

| Section | Content | Tokens used |
|---|---|---|
| `00_abstract.md` | Six-engine summary, the exact-vs-heuristic stance | BOND_TITLE, BOND_CODENAME, CONFIG_KEYWORDS, LURES_NUM_ENGINES, LURES_SCHEDULE_COUNT, LURES_SCHEDULE_TOTAL, LURES_SCHEDULE_OPTIMUM |
| `01_introduction.md` | Film-as-specification framing, the six engines, reader's guide | LURES_NUM_ENGINES, LURES_NUM_BAIT_PROFILES, LURES_ALLOC_TARGETS, LURES_MESSAGE_BYTES, LURES_CIPHER_LAYERS, LURES_NUM_RECEIVERS |
| `02_methodology.md` | The six models and their mathematics | none (math + citations only) |
| `03_results.md` | Live measured results, both figures | LURES_BITE_PROBABILITY, LURES_ENGAGEMENT_THRESHOLD, LURES_FINAL_STAGE, LURES_ALLOC_*, LURES_GREEDY_VALUE, LURES_GREEDY_GAP, LURES_GREEDY_TIES_ON_CANONICAL, LURES_WITNESS_*, LURES_MESSAGE_BYTES, LURES_CIPHER_LAYERS, LURES_SNR_DB, LURES_EMPIRICAL_SNR_DB, LURES_TRAFFIC_DISTINCT, LURES_RECOVERED_EXACT, LURES_BURST_COUNT, LURES_NUM_RECEIVERS, LURES_TDOA_*, LURES_SCHEDULE_*, LURES_HANDOFF_STATE, LURES_CONFIRM_CODE, LURES_RED_PATH_STATE |
| `04_conclusion.md` | What the package demonstrates | LURES_NUM_ENGINES, LURES_SCHEDULE_COUNT, LURES_SCHEDULE_OPTIMUM |
| `05_experimental_setup.md` | Parameter table + software environment | LURES_NUM_OBJECTIVES, LURES_NUM_ENGINES, LURES_SEED, LURES_NUM_BAIT_PROFILES, LURES_ENGAGEMENT_THRESHOLD, LURES_ALLOC_*, LURES_MESSAGE_BYTES, LURES_CIPHER_LAYERS, LURES_SNR_DB, LURES_NUM_RECEIVERS, LURES_TDOA_RECEIVER_COORDS, LURES_TDOA_TRANSMITTER, LURES_TDOA_SITE_SPACING, LURES_TDOA_NOISE_STD, LURES_SCHEDULE_TOTAL, LURES_WITNESS_TARGETS, LURES_WITNESS_BUDGET, BOND_VERSION, PYTHON_VERSION, PLATFORM, NUMPY_VERSION, MANUSCRIPT_DATE |
| `06_reproducibility.md` | Determinism, regeneration, gates, artifacts | LURES_SEED |
| `07_scope_and_related_work.md` | Scope boundaries and related work | none (citations only) |
| `99_references.md` | Citation list keyed to `references.bib` | none |

## Bibliography rules

`references.bib` must contain only real, checkable sources. Every entry
corresponds to a model the package actually implements, and the file is
grouped by which module each source backs. If you are not confident a
reference is genuine, remove it rather than ship it.
