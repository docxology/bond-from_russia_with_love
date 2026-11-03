# src/ — the domain engines, the adapter and the tokens

`from_russia_with_love/`: `bait_allocation.py`, `courier_schedule.py`, `direction_finding.py`,
`entrapment_engine.py`, `handoff_protocol.py`, `scenario.py`, `sigint.py`, `figures/`, plus
`mission.py`, `manuscript_variables.py` and `__init__.py`.

## Rules

- **The engines are pure**: no `infrastructure.*` and no `bond_api` imports, so the package's core
  imports and tests without the sibling checkout. `mission.py` is the adapter to the frozen
  `bond_api` protocol.
- **The adapter's public surface is frozen** — `film`, the five stages, `register_gadgets` and
  `GADGET_REGISTRY` are consumed by bond-cli, the coordinator and the orchestrator.
- **Determinism has no exceptions here**: fixed seeds, no untracked RNG, and **no wall-clock read
  anywhere**, not in tracked files and not in generated `output/`.
  `tests/test_regeneration_determinism.py` runs the generator twice and compares bytes.
- **Manuscript metrics arrive as generated tokens** from `manuscript_variables.py`; paper metadata
  comes from `manuscript/config.yaml`. Double-brace only: a single-brace `{TOKEN}` does not substitute.
- **Coverage floor 90% line and branch on `src/`**; `ruff check`, `ruff format --check` and `mypy`
  clean on `src/` and `scripts/`.
- **Publishing state as observed**: `origin` is the private mirror
  `github.com/docxology/bond-from_russia_with_love`, default branch `main`; never force-push. The
  suite copy of this film under the BOND working tree has no remote of its own — that is a different
  tree, not a claim about this repository.
- **Deeper context lives in `docs/`**: `agent_instructions.md`, then `architecture.md` before
  changing module boundaries and `testing_philosophy.md` before touching `tests/`.
