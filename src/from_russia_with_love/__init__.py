"""LURES — From Russia with Love (1963) PROJECT BOND film package.

Exposes the pure domain core (importable without bond-api) plus the
:func:`~from_russia_with_love.mission.MissionProvider` protocol adapter.
"""

from __future__ import annotations

from from_russia_with_love.entrapment_engine import (
    BaitProfile,
    TrapStage,
    TrapStateMachine,
    bait_bite_probability,
    generate_bait_profile,
    run_bait_campaign,
)
from from_russia_with_love.handoff_protocol import (
    HandoffProtocol,
    HandoffResult,
    HandoffState,
    challenge_confirm_code,
    validate_transition,
)
from from_russia_with_love.sigint import (
    CipherLayer,
    capture_with_noise,
    decide_symbols,
    decipher,
    derive_keystream,
    encipher,
    intercept_channel,
    measure_snr_db,
    symbols_to_bytes,
    traffic_profile,
)

__all__ = [
    "BaitProfile",
    "CipherLayer",
    "HandoffProtocol",
    "HandoffResult",
    "HandoffState",
    "TrapStage",
    "TrapStateMachine",
    "bait_bite_probability",
    "capture_with_noise",
    "challenge_confirm_code",
    "decipher",
    "decide_symbols",
    "derive_keystream",
    "encipher",
    "generate_bait_profile",
    "intercept_channel",
    "measure_snr_db",
    "run_bait_campaign",
    "symbols_to_bytes",
    "traffic_profile",
    "validate_transition",
]
