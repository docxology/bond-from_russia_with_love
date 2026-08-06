"""LURES entrapment / deception playbook engine.

This module models, in an abstract and purely analytical way, how an analyst
evaluates the effectiveness of *decoy lures* (bait profiles) against
adversarial communications. It is a deterministic decision/state model — it
does not target, track, or harm any real person. The framing is the
From Russia with Love (1963) mission theme: LURES builds and evaluates
deception lures as a defensive, analytical countermeasure.

Concepts
--------
* :class:`BaitProfile` — a declarative description of a lure (cover role,
  target attributes it aims to attract, message content, and lure strength).
* :func:`generate_bait_profile` — deterministic lure generation from a seed.
* :func:`bait_bite_probability` — a bounded logistic model mapping bait
  strength and target susceptibility to the probability that a target "bites"
  the lure (i.e. the lure is effective at drawing attention).
* :class:`TrapStateMachine` — the life-cycle of a single trap/lure campaign:
  ``DISARMED -> ARMED -> BAITED -> ENGAGED -> SPRUNG`` with an ``ABORTED``
  terminal; every transition is validated against a transition table.

Everything is deterministic: any randomness comes from an explicit, seeded
RNG (default seed 0 ⇒ no randomness).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum

__all__ = [
    "BITE_STEEPNESS",
    "BaitProfile",
    "TrapStage",
    "TrapStateMachine",
    "bait_bite_probability",
    "generate_bait_profile",
    "run_bait_campaign",
]

#: Deterministic default seed (0 disables randomness — pure arithmetic).
DEFAULT_SEED = 0

#: Slope of the bounded logistic bite-probability surface. Larger values make
#: the decision boundary sharper (the probability swings from near 0 to near 1
#: over a narrower band of lure strength + susceptibility). It is a modelling
#: choice, not a calibrated parameter — the manuscript says so explicitly —
#: but it is named here so the docstring of :func:`bait_bite_probability` can
#: reference it rather than bury an unexplained ``4.0`` inside an expression.
BITE_STEEPNESS = 4.0

_COVER_ROLES = (
    "wireless_relay_operator",
    "signal_repair_technician",
    "transport_scheduler",
    "cipher_clerk",
    "courier_reserve",
)
_CONTACT_CHANNELS = (
    "shortwave",
    "teleprinter",
    "dispatcher",
    "cover_post",
    "relay_station",
)


@dataclass(frozen=True)
class BaitProfile:
    """A declarative lure: who it pretends to be and what it draws in."""

    lure_id: str
    cover_role: str
    target_susceptibility: float  # 0..1 analytical openness of the target
    message_payload: str
    lure_strength: float  # 0..1 intensity of the lure

    def __post_init__(self) -> None:
        if not self.lure_id.strip():
            raise ValueError("lure_id must be a non-empty string")
        if not self.cover_role.strip():
            raise ValueError("cover_role must be a non-empty string")
        for name, value in (
            ("target_susceptibility", self.target_susceptibility),
            ("lure_strength", self.lure_strength),
        ):
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{name} must be in [0, 1]")


class TrapStage(str, Enum):
    """Life-cycle stages of a single lure campaign."""

    DISARMED = "disarmed"
    ARMED = "armed"
    BAITED = "baited"
    ENGAGED = "engaged"
    SPRUNG = "sprung"
    ABORTED = "aborted"


#: Terminal stages — no further transitions allowed once reached.
_TERMINAL = frozenset({TrapStage.SPRUNG, TrapStage.ABORTED})

#: Allowed transitions: (from_stage, event) -> to_stage.
_TRANSITIONS: dict[tuple[TrapStage, str], TrapStage] = {
    (TrapStage.DISARMED, "deploy"): TrapStage.ARMED,
    (TrapStage.ARMED, "bait"): TrapStage.BAITED,
    (TrapStage.BAITED, "engage"): TrapStage.ENGAGED,
    (TrapStage.ENGAGED, "spring"): TrapStage.SPRUNG,
    (TrapStage.BAITED, "ignore"): TrapStage.ABORTED,
    (TrapStage.ARMED, "stand_down"): TrapStage.ABORTED,
    (TrapStage.DISARMED, "stand_down"): TrapStage.ABORTED,
}


def bait_bite_probability(lure_strength: float, susceptibility: float) -> float:
    """Bounded logistic model of how effective a lure is.

    ``BITE_STEEPNESS * (strength + susceptibility - 1)``. Higher lure strength
    and higher target susceptibility both monotonically raise the bite
    probability, so the model is strictly increasing in each argument — a
    real, differentiable decision surface (no stochastic draws).
    """
    for name, value in (
        ("lure_strength", lure_strength),
        ("susceptibility", susceptibility),
    ):
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{name} must be in [0, 1]")
    z = BITE_STEEPNESS * (lure_strength + susceptibility - 1.0)
    return 1.0 / (1.0 + math.exp(-z))


def _fold_seed(seed: int, salt: str) -> int:
    """Fold an int seed and a string salt into a 32-bit RNG seed.

    A simple, deterministic mix (a multiply-and-shift fold followed by a
    per-character hash fold) — stable across runs and platforms.
    """
    if not isinstance(seed, int):
        raise TypeError("seed must be an int")
    folded = (seed * 0x9E3779B1) & 0xFFFFFFFF
    for char in salt:
        folded = (folded * 31 + ord(char)) & 0xFFFFFFFF
    return folded


def generate_bait_profile(
    lure_id: str,
    *,
    seed: int = DEFAULT_SEED,
    rng: random.Random | None = None,
) -> BaitProfile:
    """Deterministically generate a lure profile from an id and seed.

    ``rng`` may be passed in (a seeded source of draws) for reproducibility;
    otherwise a local RNG is used, seeded by folding ``seed`` and ``lure_id``.
    Elements are drawn from fixed, finite registries, so output is fully
    reproducible for a given id/seed pair.
    """
    if not lure_id.strip():
        raise ValueError("lure_id must be a non-empty string")
    local_rng = rng if rng is not None else random.Random(_fold_seed(seed, lure_id))
    role = _COVER_ROLES[local_rng.randrange(len(_COVER_ROLES))]
    susceptibility = round(local_rng.random(), 3)
    strength = round(0.5 + 0.5 * local_rng.random(), 3)
    channel = _CONTACT_CHANNELS[local_rng.randrange(len(_CONTACT_CHANNELS))]
    message = f"{channel}:{role}:inbound-recon-request"
    return BaitProfile(
        lure_id=lure_id,
        cover_role=role,
        target_susceptibility=susceptibility,
        lure_strength=strength,
        message_payload=message,
    )


class TrapStateMachine:
    """Validated state machine governing a single lure campaign life-cycle."""

    def __init__(self, bait: BaitProfile) -> None:
        if not isinstance(bait, BaitProfile):
            raise TypeError("bait must be a BaitProfile")
        self.bait = bait
        self.stage = TrapStage.DISARMED
        self.history: list[tuple[TrapStage, str, TrapStage]] = []

    def transition(self, event: str) -> TrapStage:
        """Advance the machine on ``event`` or raise ``ValueError``.

        Returns the new stage. Illegal events (not in the table for the
        current stage, or any event on a terminal stage) raise ``ValueError``
        with an actionable message and leave state unchanged.
        """
        key = (self.stage, event)
        if self.stage in _TERMINAL:
            raise ValueError(
                f"trap is terminal in stage {self.stage.value!r}; no further events"
            )
        if key not in _TRANSITIONS:
            raise ValueError(f"invalid event {event!r} from stage {self.stage.value!r}")
        destination = _TRANSITIONS[key]
        previous = self.stage
        self.stage = destination
        self.history.append((previous, event, destination))
        return destination

    def run_campaign(self, *, engage: bool = True) -> TrapStage:
        """Run the full nominal campaign to ``SPRUNG`` or ``ABORTED``.

        Deploys, baits, and (if ``engage``) engages then springs the trap;
        otherwise it stands down after baiting. Deterministic.
        """
        self.transition("deploy")
        self.transition("bait")
        if engage:
            self.transition("engage")
            return self.transition("spring")
        # target did not engage after baiting -> the lure is stood down to ABORT
        return self.transition("ignore")


def run_bait_campaign(
    profile: BaitProfile,
    *,
    engagement_threshold: float = 0.5,
    engage: bool | None = None,
) -> dict[str, object]:
    """Evaluate a lure and run its campaign end-to-end.

    When ``engage`` is ``None`` it is decided deterministically from
    :func:`bait_bite_probability` against ``engagement_threshold`` (bite at
    or above threshold ⇒ engage). Returns a dict with the computed bite
    probability, the chosen decision, and the final trap stage.
    """
    probability = bait_bite_probability(
        profile.lure_strength, profile.target_susceptibility
    )
    decision = engage if engage is not None else probability >= engagement_threshold
    machine = TrapStateMachine(profile)
    final_stage = machine.run_campaign(engage=bool(decision))
    return {
        "lure_id": profile.lure_id,
        "bite_probability": probability,
        "decision": "engage" if decision else "stand_down",
        "final_stage": final_stage.value,
        "history": tuple(entry[0].value for entry in machine.history),
    }
