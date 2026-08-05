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
from from_russia_with_love.courier_schedule import (
    max_completed_handoffs,
    schedule_handoffs,
)
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
    "validate_mission_config",
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


def _float_field(channel: dict[str, object], field: str) -> float:
    """Pull one float field out of an intercept result dict."""
    value = channel[field]
    if not isinstance(value, (int, float)):
        raise TypeError(f"intercept {field!r} must be numeric")
    return float(value)


def _traffic_field(channel: dict[str, object], field: str) -> int:
    """Pull one integer field out of an intercept's traffic profile."""
    traffic = channel["traffic"]
    if not isinstance(traffic, dict):
        raise TypeError("intercept 'traffic' must be a mapping")
    return int(traffic[field])


def validate_mission_config(config: dict[str, object]) -> None:
    """Assert the config's ``mission`` block agrees with :mod:`scenario`.

    ``scenario.py`` is the single source of truth for every executed number,
    but ``manuscript/config.yaml`` restates the headline mission parameters so
    a reader of the config sees the real scenario. Two copies of a number is
    exactly how documentation drifts, so the copies are checked rather than
    trusted: any disagreement raises ``ValueError`` and fails the manuscript
    build. Keys absent from the config are not invented — only declared keys
    are compared.
    """
    mission = config.get("mission")
    if mission is None:
        return
    if not isinstance(mission, dict):
        raise TypeError("config 'mission' block must be a mapping")

    expected: dict[str, object] = {
        "codename": "LURES",
        "objectives": len(scenario.OBJECTIVES),
        "bait_profiles": len(scenario.BAIT_PROFILE_IDS),
        "engagement_threshold": scenario.ENGAGEMENT_THRESHOLD,
        "snr_db": scenario.SNR_DB,
        "call_sign": scenario.HANDOFF_CALL_SIGN,
        "challenge": scenario.CHALLENGE,
        "seed": scenario.SEED,
    }
    mismatches = [
        f"{key}: config={mission[key]!r} scenario={value!r}"
        for key, value in expected.items()
        if key in mission and mission[key] != value
    ]
    if mismatches:
        raise ValueError(
            "manuscript/config.yaml disagrees with scenario.py (the single "
            "source of truth): " + "; ".join(sorted(mismatches))
        )


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
    validate_mission_config(config)
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

    # Courier schedule (heuristic) scored against the exact optimum + handoff.
    schedule = schedule_handoffs(
        scenario.RENDEZVOUS, start_time=scenario.SCHEDULE_START
    )
    schedule_optimum = max_completed_handoffs(
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
        "LURES_NUM_OBJECTIVES": len(scenario.OBJECTIVES),
        "LURES_NUM_BAIT_PROFILES": len(scenario.BAIT_PROFILE_IDS),
        "LURES_SEED": scenario.SEED,
        "LURES_ENGAGEMENT_THRESHOLD": f"{scenario.ENGAGEMENT_THRESHOLD:.2f}",
        "LURES_BITE_PROBABILITY": f"{campaign['bite_probability']:.3f}",
        "LURES_FINAL_STAGE": str(campaign["final_stage"]),
        "LURES_ALLOC_TARGETS": len(scenario.ALLOC_TARGETS),
        "LURES_ALLOC_LURE_STRENGTH": f"{scenario.ALLOC_LURE_STRENGTH:.2f}",
        "LURES_ALLOC_BUDGET": scenario.ALLOC_BUDGET,
        "LURES_ALLOC_CHOSEN": allocation.budget_used,
        "LURES_ALLOC_COUNT": len(allocation.chosen),
        "LURES_ALLOC_VALUE": f"{allocation.expected_value:.3f}",
        "LURES_GREEDY_VALUE": f"{greedy.expected_value:.3f}",
        "LURES_ALLOC_UTILIZATION": f"{allocation_utilization:.0f}",
        "LURES_OPTIMAL_DOMINATES_GREEDY": str(
            allocation.expected_value >= greedy.expected_value - 1e-12
        ),
        "LURES_MESSAGE_BYTES": len(scenario.PLAINTEXT.encode("utf-8")),
        "LURES_CIPHER_LAYERS": len(scenario.CIPHERS),
        "LURES_SNR_DB": f"{scenario.SNR_DB:.1f}",
        "LURES_EMPIRICAL_SNR_DB": f"{_float_field(channel, 'empirical_snr_db'):.1f}",
        "LURES_TRAFFIC_DISTINCT": int(_traffic_field(channel, "distinct_symbols")),
        "LURES_RECOVERED_EXACT": str(bool(channel["recovered_exact"])),
        "LURES_BURST_COUNT": len(bursts),
        "LURES_NUM_RECEIVERS": len(scenario.TDOA_RECEIVERS),
        "LURES_TDOA_NOISE_STD": f"{scenario.TDOA_NOISE_STD:.2f}",
        "LURES_TDOA_ERROR": f"{tdoa_error:.3f}",
        "LURES_TDOA_ITERATIONS": estimate.iterations,
        "LURES_TDOA_CONVERGED": str(bool(estimate.converged)),
        "LURES_SCHEDULE_COUNT": schedule.scheduled_count,
        "LURES_SCHEDULE_OPTIMUM": schedule_optimum,
        "LURES_SCHEDULE_GAP": schedule_optimum - schedule.scheduled_count,
        "LURES_SCHEDULE_FINISH": f"{schedule.finish_time:.1f}",
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
