# docs/ — LURES

Agent-facing documentation for the **LURES** package (From Russia with Love,
1963 · mission codename LURES), a film package in the PROJECT BOND suite.
Package-level orientation lives in the root `README.md`; this directory holds
the working detail.

| File | What it holds |
|---|---|
| `agent_instructions.md` | Hard constraints, layer contract, mission lifecycle, token protocol, verify-before-done checklist |
| `architecture.md` | Module-by-module description of `src/`, how the pieces compose, and how `mission.py` implements the frozen `bond_api` `MissionProvider` |
| `testing_philosophy.md` | The no-mock / real-data / determinism doctrine, and which tests exist specifically to prove a gate can fail |
| `AGENTS.md` | How to work inside this docs directory; rules for editing these files |
| `_generated/COUNTS.md` | Measured test count and coverage from the last verification run — generated, not hand-written |

## Where to start

- **Changing an algorithm** → `architecture.md` for the module's contract, then
  `testing_philosophy.md` before you touch its tests.
- **Changing the mission adapter or gadget registry** → `architecture.md`,
  section "How `mission.py` implements the frozen `MissionProvider`". That
  surface is consumed by `bond-cli`, the coordinator and the orchestrator, and
  its public shape is frozen.
- **Adding a reported number** → `agent_instructions.md`, the manuscript-token
  section. Numbers reach the prose as generated tokens or not at all.
- **Just running the gates** → `agent_instructions.md`, "Verify before you say
  done".

## Standing facts about this package

- Six deterministic concept modules plus a canonical `scenario.py`, a
  `mission.py` adapter, token generation, and two figure generators.
- The pure core imports no `bond_api` and no infrastructure; a test enforces
  this by reading each module's source.
- Every mission constant lives in `scenario.py`, and `manuscript/config.yaml`
  is checked against it at manuscript-build time.
- Coverage floor is 90% line-and-branch on `src/`; zero mock framework usage.
