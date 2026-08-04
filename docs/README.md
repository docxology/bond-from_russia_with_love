# docs/

Agent-facing documentation for the **LURES** package (From Russia with Love,
1963 · mission codename LURES).

| File | Purpose |
|---|---|
| `agent_instructions.md` | Operational constraints + verify-before-done checklist |
| `architecture.md` | Package layout, layer contract, data flow |
| `testing_philosophy.md` | Deterministic, zero-mock testing approach |
| `README.md` | This index |

Start with `agent_instructions.md`. Consult `testing_philosophy.md` before
writing or modifying pytest files; consult `architecture.md` before altering
`scripts/` or `src/` modular boundaries.
