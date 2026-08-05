# docs/ — Agent work area

The agent-facing documentation hub for **LURES** (From Russia with Love, 1963),
a film package in the PROJECT BOND suite.

## Reading order

1. `agent_instructions.md` — hard constraints, the layer contract, the mission
   lifecycle, and the verify-before-done checklist. Read this first, always.
2. `architecture.md` — what each module in `src/from_russia_with_love/`
   actually computes, and how `mission.py` implements the frozen `bond_api`
   `MissionProvider`. Read before touching module boundaries or the adapter.
3. `testing_philosophy.md` — the no-mock / real-data / determinism doctrine and,
   more importantly, which tests exist to prove a gate can fail. Read before
   writing or modifying anything under `tests/`.
4. `_generated/COUNTS.md` — the last measured test count and coverage figure.

## Rules for editing anything in this directory

- **Every claim here must be verifiable against the code.** If you write that a
  module does something, a reader must be able to open that module and see it.
  Prefer naming the function to describing it vaguely.
- **Never hand-author a metric in prose.** Test counts and coverage
  percentages belong in `_generated/COUNTS.md`, regenerated from a real run.
  Elsewhere, describe the *gate* ("the floor is 90%") rather than quoting a
  figure that will rot.
- **Do not describe intended behaviour as shipped behaviour.** If something is
  planned, it goes in the root `TODO.md` as an open item, not here in the
  present tense.
- When you change code that these documents describe, update them in the same
  commit. Documentation drift is treated as a defect in this package, and the
  config/scenario drift guard exists because of exactly that failure mode.

## What does not belong here

- Mission results or metrics — those are manuscript tokens, generated from
  `src/from_russia_with_love/manuscript_variables.py`.
- Suite-wide policy — that lives at the bond root and in the shared fleet
  preamble; this directory covers only what is specific to LURES.
- Anything about a sibling package. Scope is exactly this directory tree.
