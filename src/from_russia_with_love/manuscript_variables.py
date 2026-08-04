"""Manuscript {{TOKEN}} hydration for the LURES package.

Computes every ``{{TOKEN}}`` the manuscript references from
``manuscript/config.yaml`` plus live, deterministic output of the three pure
engines. Result-derived values (bite probability, intercept round-trip,
handoff confirm code) are never hand-authored — they come from the actual
computation so the manuscript cannot drift from the code.

The strict contract: every ``{{TOKEN}}`` appearing in ``manuscript/[0-9]*.md``
must be present in the dict returned by :func:`generate_variables`. The live
cross-reference test enforces this.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

import yaml

from from_russia_with_love.entrapment_engine import (
    generate_bait_profile,
    run_bait_campaign,
)
from from_russia_with_love.handoff_protocol import HandoffProtocol
from from_russia_with_love.sigint import CipherLayer, intercept_channel

__all__ = [
    "PACKAGE_VERSION",
    "load_mission_config",
    "generate_variables",
]

PACKAGE_VERSION = "0.1.0"
_SEED = 11
_PLAINTEXT = "LURES inbound relay: defector green for handoff"
_CIPHERS = (CipherLayer(key=b"VALENKA", seed=3), CipherLayer(key=b"GRANT", seed=5))
_SNR_DB = 80.0


def load_mission_config(project_root: Path) -> dict[str, object]:
    """Load ``manuscript/config.yaml`` as a plain dict (raises on absence)."""
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"mission config not found at {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        return cast_dict(yaml.safe_load(handle))


def _cast_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError("manuscript/config.yaml must contain a mapping")
    return {str(k): v for k, v in value.items()}


cast_dict = _cast_dict  # alias for typing clarity


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

    lure = generate_bait_profile("honey-trap-alpha", seed=_SEED)
    campaign = run_bait_campaign(lure, engagement_threshold=0.5)
    channel = intercept_channel(_PLAINTEXT, _CIPHERS, snr_db=_SNR_DB, seed=_SEED)
    handoff = HandoffProtocol(
        call_sign="ROZA", challenge="the cow jumped over the moon"
    ).run_green()

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
        "LURES_NUM_OBJECTIVES": 3,
        "LURES_NUM_BAIT_PROFILES": 3,
        "LURES_BITE_PROBABILITY": f"{campaign['bite_probability']:.3f}",
        "LURES_FINAL_STAGE": str(campaign["final_stage"]),
        "LURES_SNR_DB": f"{_SNR_DB:.1f}",
        "LURES_RECOVERED_EXACT": str(bool(channel["recovered_exact"])),
        "LURES_HANDOFF_STATE": handoff.state.value,
        "LURES_CONFIRM_CODE": handoff.confirm_code,
        "NUMPY_VERSION": __numpy_version(),
        "PYTHON_VERSION": platform.python_version(),
        "PLATFORM": sys.platform,
        "GENERATION_TIMESTAMP": now,
    }


def __numpy_version() -> str:
    import numpy

    return numpy.__version__
