"""TDOA direction-finding geometry figure for the LURES mission.

Renders the four fixed intercept sites, the true transmitter, and the
Gauss–Newton estimate recovered from the deterministic noisy TDOA
measurements. Pure matplotlib, Agg-safe, deterministic.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib import pyplot as plt

from from_russia_with_love import scenario
from from_russia_with_love.direction_finding import (
    estimate_position,
    tdoa_measurements,
)

__all__ = ["plot_tdoa_geometry"]


def plot_tdoa_geometry(out_path: Path) -> Path:
    """Write the TDOA geometry PNG to ``out_path`` and return it."""
    pairs, tdoa = tdoa_measurements(
        scenario.TDOA_RECEIVERS,
        scenario.TDOA_TRANSMITTER,
        speed=scenario.TDOA_SPEED,
        noise_std=scenario.TDOA_NOISE_STD,
        seed=scenario.TDOA_SEED,
    )
    estimate = estimate_position(
        scenario.TDOA_RECEIVERS,
        pairs,
        tdoa,
        speed=scenario.TDOA_SPEED,
    )

    fig, ax = plt.subplots(figsize=(6.5, 6.5), dpi=110)
    receiver_x = [r.position[0] for r in scenario.TDOA_RECEIVERS]
    receiver_y = [r.position[1] for r in scenario.TDOA_RECEIVERS]
    ax.scatter(
        receiver_x, receiver_y, marker="s", color="tab:blue", label="intercept site"
    )
    for receiver in scenario.TDOA_RECEIVERS:
        ax.annotate(
            receiver.receiver_id,
            receiver.position,
            xytext=(3, 3),
            textcoords="offset points",
        )

    truth = scenario.TDOA_TRANSMITTER
    ax.scatter(
        [truth[0]],
        [truth[1]],
        marker="*",
        color="tab:red",
        s=180,
        label="true transmitter",
    )
    estimate_pos = estimate.position
    ax.scatter(
        [estimate_pos[0]],
        [estimate_pos[1]],
        marker="x",
        color="tab:green",
        s=120,
        label="TDOA estimate",
    )
    ax.plot(
        [truth[0], estimate_pos[0]],
        [truth[1], estimate_pos[1]],
        color="tab:gray",
        linestyle="--",
        linewidth=1,
    )
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")
    ax.set_title("LURES: TDOA transmitter geolocation")
    ax.set_aspect("equal")
    ax.legend(loc="upper right", fontsize="small")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path
