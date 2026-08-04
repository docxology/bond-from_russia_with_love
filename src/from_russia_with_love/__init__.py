"""LURES — From Russia with Love (1963) PROJECT BOND film package.

Exposes the pure domain core (importable without bond-api) plus the
:func:`~from_russia_with_love.mission.MissionProvider` protocol adapter.
"""

from __future__ import annotations

from from_russia_with_love.bait_allocation import (
    AllocationResult,
    Target,
    allocate_lures,
    bite_value,
    greedy_allocate,
    validate_targets,
)
from from_russia_with_love.courier_schedule import (
    Rendezvous,
    ScheduleResult,
    is_compatible,
    schedule_handoffs,
)
from from_russia_with_love.direction_finding import (
    Receiver,
    TdoaEstimate,
    estimate_position,
    localization_error,
    tdoa_measurements,
)
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
    segment_bursts,
    symbols_to_bytes,
    traffic_profile,
)

__all__ = [
    "AllocationResult",
    "BaitProfile",
    "CipherLayer",
    "HandoffProtocol",
    "HandoffResult",
    "HandoffState",
    "Receiver",
    "Rendezvous",
    "ScheduleResult",
    "Target",
    "TdoaEstimate",
    "TrapStage",
    "TrapStateMachine",
    "allocate_lures",
    "bait_bite_probability",
    "bite_value",
    "capture_with_noise",
    "challenge_confirm_code",
    "decipher",
    "decide_symbols",
    "derive_keystream",
    "encipher",
    "estimate_position",
    "generate_bait_profile",
    "greedy_allocate",
    "intercept_channel",
    "is_compatible",
    "localization_error",
    "measure_snr_db",
    "run_bait_campaign",
    "schedule_handoffs",
    "segment_bursts",
    "symbols_to_bytes",
    "tdoa_measurements",
    "traffic_profile",
    "validate_targets",
    "validate_transition",
]
