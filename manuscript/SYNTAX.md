# Manuscript Syntax

- Citation: `[@bond_api]` (parenthetical) or `@bond_api` (narrative).
- Figure: `![caption](output/figures/lure_surface.png){#fig:lure_surface}` then `@fig:lure_surface` / `[@fig:lure_surface]`.
- Tokens: {{TOKEN}} placeholders in `[0-9]*.md` sections are hydrated from
  `src/.../manuscript_variables.py::generate_variables()`. Every literal
  `{{TOKEN}}` in the numbered sections must exist in that mapping (enforced
  by the live cross-reference test).
