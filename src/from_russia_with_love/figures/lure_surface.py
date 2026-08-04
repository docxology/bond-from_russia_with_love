"""Lure-effectiveness surface figure for the LURES mission.

Renders the deterministic bite-probability decision surface
:func:`~from_russia_with_love.entrapment_engine.bait_bite_probability` across
lure strength and target susceptibility, plus the three fixed scenario lures
as markers. Pure matplotlib, Agg-safe, deterministic.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

from from_russia_with_love.entrapment_engine import (
    bait_bite_probability,
    generate_bait_profile,
)

__all__ = ["plot_lure_surface"]

_LURES = ("honey-trap-alpha", "relay-decoy-7", "cipher-clerk-config-3")


def plot_lure_surface(out_path: Path, *, seed: int = 11) -> Path:
    """Write the lure-effectiveness surface PNG to ``out_path`` and return it."""
    strength = np.linspace(0.0, 1.0, 120)
    susceptibility = np.linspace(0.0, 1.0, 120)
    strength_grid, susceptibility_grid = np.meshgrid(strength, susceptibility)
    surface = np.vectorize(bait_bite_probability)(strength_grid, susceptibility_grid)

    fig, ax = plt.subplots(figsize=(7.0, 5.5), dpi=110)
    contour = ax.contourf(
        strength_grid, susceptibility_grid, surface, levels=20, cmap="viridis"
    )
    fig.colorbar(contour, ax=ax, label="bite probability")

    for lure_id in _LURES:
        profile = generate_bait_profile(lure_id, seed=seed)
        ax.scatter(
            profile.lure_strength,
            profile.target_susceptibility,
            color="red",
            marker="x",
            zorder=5,
            label=lure_id,
        )

    ax.set_xlabel("lure strength")
    ax.set_ylabel("target susceptibility")
    ax.set_title("LURES: bait bite-probability surface")
    ax.legend(loc="lower right", fontsize="small")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path
