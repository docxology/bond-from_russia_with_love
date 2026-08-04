"""Manuscript {{TOKEN}} hydration for the LURES package.

Computes every ``{{TOKEN}}`` the manuscript references from
``manuscript/config.yaml`` plus live, deterministic output of the six pure
engines (entrapment, bait allocation, SIGINT, TDOA direction finding,
courier scheduling, handoff). Result-derived values are never hand-authored —
they come from the actual computation so the manuscript cannot drift from the
code. All scenario constants come from :mod:`~from_russia_with_love.scenario`
(the single source of truth shared with ``mission.py`` and the figures).

The strict contract: every ``{{TOKEN}}`` appearing in ``manuscript/[0-9]*.md``
must be present in the dict returned by :func:`generate_variables`. The live
cross-reference test enforces this.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

import numpy as np
import yaml

from from_russia_with_love import scenario
from from_russia_with_love.bait_allocation import allocate_lures, greedy_allocate
from from_russia_with_love.courier_schedule import schedule_handoffs
from from_russia_with_love.direction_finding import (
    estimate_position,
    localization_error,
    tdoa_measurements,
)
from from_russia_with_love.entrapment_engine import (
    generate_bait_profile,
    run_bait_campaign,
)
from from_russia_with_love.handoff_protocol import HandoffProtocol
from from_russia_with_love.sigint import intercept_channel, segment_bursts

__all__ = [
    "PACKAGE_VERSION",
    "load_mission_config",
    "generate_variables",
]

PACKAGE_VERSION = "0.1.0"


def load_mission_config(project_root: Path) -> dict[str, object]:
    """Load ``manuscript/config.yaml`` as a plain dict (raises on absence)."""
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"mission config not found at {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        return _cast_dict(yaml.safe_load(handle))


def _cast_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError("manuscript/config.yaml must contain a mapping")
    return {str(k): v for k, v in value.items()}


def generate_variables(
    project_root: Path,
    *,
    allow_draft: bool = False,
    now: str | None = None,
) -> dict[str, object]:
    """Compute the full {TOKEN: value} mapping for the manuscript.

    ``now`` overrides the generation timestamp for deterministic tests; when
    omitted the current UTC time (ISO-8601, ``Z`` suffix) is used.
    ``allow_draft`` is accepted for interface compatibility with the strict
    dry-run contract but LURES always computes live results (no draft
    fallbacks).
    """
    del allow_draft  # LURES computes live results; kept for signature parity
    config = load_mission_config(project_root)
    paper = _cast_dict(config.get("paper", {}))
    keywords = config.get("keywords", [])
    if not isinstance(keywords, (list, tuple)):
        keywords = []

    # Entrapment + allocation.
    lure = generate_bait_profile("honey-trap-alpha", seed=scenario.SEED)
    campaign = run_bait_campaign(
        lure, engagement_threshold=scenario.ENGAGEMENT_THRESHOLD
    )
    allocation = allocate_lures(
        scenario.ALLOC_TARGETS,
        scenario.ALLOC_BUDGET,
        scenario.ALLOC_LURE_STRENGTH,
    )
    greedy = greedy_allocate(
        scenario.ALLOC_TARGETS,
        scenario.ALLOC_BUDGET,
        scenario.ALLOC_LURE_STRENGTH,
    )

    # SIGINT + burst segmentation.
    channel = intercept_channel(
        scenario.PLAINTEXT,
        scenario.CIPHERS,
        snr_db=scenario.SNR_DB,
        seed=scenario.SEED,
    )
    envelope = np.abs(np.asarray(channel["captured_samples"], dtype=np.float64))
    threshold = float(np.mean(envelope)) * 0.5
    bursts = segment_bursts(envelope, threshold=threshold, min_gap=1)

    # Direction finding.
    pairs, tdoa = tdoa_measurements(
        scenario.TDOA_RECEIVERS,
        scenario.TDOA_TRANSMITTER,
        speed=scenario.TDOA_SPEED,
        noise_std=scenario.TDOA_NOISE_STD,
        seed=scenario.TDOA_SEED,
    )
    estimate = estimate_position(
        scenario.TDOA_RECEIVERS, pairs, tdoa, speed=scenario.TDOA_SPEED
    )
    tdoa_error = localization_error(estimate.position, scenario.TDOA_TRANSMITTER)

    # Courier schedule + handoff.
    schedule = schedule_handoffs(
        scenario.RENDEZVOUS, start_time=scenario.SCHEDULE_START
    )
    allocation_utilization = 100.0 * allocation.budget_used / scenario.ALLOC_BUDGET
    handoff = HandoffProtocol(
        call_sign=scenario.HANDOFF_CALL_SIGN, challenge=scenario.CHALLENGE
    ).run_green()
    red = HandoffProtocol(
        call_sign=scenario.HANDOFF_CALL_SIGN, challenge=scenario.CHALLENGE
    ).run_red_path()

    if now is None:  # pragma: no cover - wall-clock fallback
        from datetime import datetime, timezone

        now = (
            datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )

    return {
        "BOND_IDENTITY": "LURES",
        "BOND_CODENAME": "LURES",
        "BOND_VERSION": str(paper.get("version", PACKAGE_VERSION)),
        "BOND_TITLE": str(paper.get("title", "From Russia with Love: LURES")),
        "BOND_SUBTITLE": str(paper.get("subtitle", "Special-Agent Mission Software")),
        "CONFIG_KEYWORDS": ", ".join(str(k) for k in keywords),
        "LURES_NUM_OBJECTIVES": len(
            (
                "lure campaign",
                "bait allocation",
                "sigint intercept",
                "tdoa geolocation",
                "courier schedule",
                "handoff",
            )
        ),
        "LURES_NUM_BAIT_PROFILES": len(scenario.BAIT_PROFILE_IDS),
        "LURES_BITE_PROBABILITY": f"{campaign['bite_probability']:.3f}",
        "LURES_FINAL_STAGE": str(campaign["final_stage"]),
        "LURES_ALLOC_BUDGET": scenario.ALLOC_BUDGET,
        "LURES_ALLOC_CHOSEN": allocation.budget_used,
        "LURES_ALLOC_VALUE": f"{allocation.expected_value:.3f}",
        "LURES_ALLOC_UTILIZATION": f"{allocation_utilization:.0f}",
        "LURES_OPTIMAL_DOMINATES_GREEDY": str(
            allocation.expected_value >= greedy.expected_value - 1e-12
        ),
        "LURES_SNR_DB": f"{scenario.SNR_DB:.1f}",
        "LURES_RECOVERED_EXACT": str(bool(channel["recovered_exact"])),
        "LURES_BURST_COUNT": len(bursts),
        "LURES_NUM_RECEIVERS": len(scenario.TDOA_RECEIVERS),
        "LURES_TDOA_ERROR": f"{tdoa_error:.3f}",
        "LURES_TDOA_CONVERGED": str(bool(estimate.converged)),
        "LURES_SCHEDULE_COUNT": schedule.scheduled_count,
        "LURES_SCHEDULE_TOTAL": len(scenario.RENDEZVOUS),
        "LURES_RED_PATH_STATE": red.state.value,
        "LURES_HANDOFF_STATE": handoff.state.value,
        "LURES_CONFIRM_CODE": handoff.confirm_code,
        "NUMPY_VERSION": numpy_version(),
        "PYTHON_VERSION": platform.python_version(),
        "PLATFORM": sys.platform,
        "GENERATION_TIMESTAMP": now,
    }


def numpy_version() -> str:
    """The installed numpy version string."""
    return np.__version__
