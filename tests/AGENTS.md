# tests/ — per-engine real-data tests and determinism

One module per engine (`test_bait_allocation.py`, `test_courier_schedule.py`,
`test_direction_finding.py`, `test_entrapment_engine.py`, `test_handoff_protocol.py`, `test_sigint.py`,
`test_scenario.py` alongside `test_mission*.py`), plus `test_figures.py`,
`test_manuscript_variables.py`, `test_declarative_registries.py`,
`test_mission_constants_in_scenario.py`, `test_regeneration_determinism.py`, `test_scripts_smoke.py`,
`test_version.py` and `conftest.py`.

## Rules

- **Zero mocks** — no `MagicMock`, `mocker.patch` or `unittest.mock`. Real data and real computation
  only.
- **The full gate is `uv run pytest tests/ --cov=src --cov-fail-under=90`**; a single module or a
  single test can be run during work, but the floor is the offline gate.
- **Determinism is tested by regenerating**: the generator runs twice and the bytes are compared,
  with no clock injected. A new persisted artifact joins that comparison or the claim is weakened.
- **`test_mission_constants_in_scenario.py` and `test_declarative_registries.py` are structural
  contracts**: keep the single scenario and the registries declarative.
- **`test_scripts_smoke.py` covers the CLI wrappers**; a new script needs a smoke path.
- **Measured counts live in `docs/_generated/COUNTS.md`**, regenerated from a run you actually
  performed — never hand-edited.
- **Read `docs/testing_philosophy.md` before changing test structure.**
