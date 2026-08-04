"""Generate the manuscript {{TOKEN}} map for the LURES package.

Writes ``output/data/manuscript_variables.json`` (regenerable; output/ is
git-ignored) and renders the lure-surface figure. Strict by default: any
unresolved token is a failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    from from_russia_with_love.figures.lure_surface import plot_lure_surface
    from from_russia_with_love.figures.tdoa_geometry import plot_tdoa_geometry
    from from_russia_with_love.manuscript_variables import generate_variables

    allow_draft = "--allow-draft" in (argv or sys.argv[1:])
    out_dir = PROJECT_ROOT / "output" / "data"
    fig_dir = PROJECT_ROOT / "output" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    variables = generate_variables(PROJECT_ROOT, allow_draft=allow_draft)
    tokens_path = out_dir / "manuscript_variables.json"
    with tokens_path.open("w", encoding="utf-8") as handle:
        json.dump(variables, handle, indent=2, sort_keys=True)
    plot_lure_surface(fig_dir / "lure_surface.png")
    plot_tdoa_geometry(fig_dir / "tdoa_geometry.png")

    print(f"wrote {len(variables)} manuscript tokens -> {tokens_path}")
    print(f"figures -> {fig_dir / 'lure_surface.png'}, {fig_dir / 'tdoa_geometry.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
