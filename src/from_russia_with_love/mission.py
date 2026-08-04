"""LURES — the From Russia with Love (1963) MissionProvider for BOND-API.

This is the thin adapter between the pure domain core (``entrapment_engine``,
``sigint``, ``handoff_protocol``) and the FROZEN ``bond_api`` protocol. The
domain modules are importable without ``bond-api``; only this file touches
the protocol types.

Per the discovery contract, the module exposes a top-level ``MissionProvider``
class (name fixed by the contract) and registers its gadgets with the
``bond_api`` :class:`GadgetRegistry`.
"""

from __future__ import annotations

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)

from from_russia_with_love.entrapment_engine import (
    generate_bait_profile,
    run_bait_campaign,
)
from from_russia_with_love.handoff_protocol import HandoffProtocol
from from_russia_with_love.sigint import CipherLayer, intercept_channel

__all__ = ["MissionProvider", "GADGETS", "register_gadgets", "_PACKAGE_VERSION"]

_PACKAGE_VERSION = "0.1.0"
_SEED = 11

#: Fixed, reproducible interception scenario used by ``execute``.
_PLAINTEXT = "LURES inbound relay: defector green for handoff"
_CIPHERS = (CipherLayer(key=b"VALENKA", seed=3), CipherLayer(key=b"GRANT", seed=5))
#: Clean-channel SNR (dB) — lossless byte recovery at and above ~60 dB.
_SNR_DB = 80.0

#: Fixed, typed scenario data surfaced both as gadgets and in the brief.
_BAIT_PROFILE_IDS: tuple[str, ...] = (
    "honey-trap-alpha",
    "relay-decoy-7",
    "cipher-clerk-config-3",
)
_CALL_SIGNS: tuple[str, ...] = ("ROZA", "KLEBB", "DELILAH")


def register_gadgets() -> None:
    """Register this film's gadgets with the shared BOND gadget registry.

    Gadgets are opaque payloads (the pure engines and their fixed scenario
    data) that other suite packages can ``lookup`` without importing this
    package's internals.
    """
    GADGETS.clear()
    GADGETS.update(
        {
            "bait_profiles": _BAIT_PROFILE_IDS,
            "ciphers": _CIPHERS,
            "handoff_call_signs": _CALL_SIGNS,
            "entrapment_engine": "from_russia_with_love.entrapment_engine",
            "sigint": "from_russia_with_love.sigint",
            "handoff_protocol": "from_russia_with_love.handoff_protocol",
        }
    )


#: The film's gadget payloads (dict of name -> opaque payload).
GADGETS: dict[str, object] = {}


class MissionProvider:  # noqa: N801 — class name is fixed by the discovery contract
    """Deterministic LURES mission: deception, SIGINT, defector handoff."""

    film = "from_russia_with_love"

    def brief(self) -> MissionBrief:
        """Declare the LURES mission and its three objectives."""
        return MissionBrief(
            film=self.film,
            codename="LURES",
            objectives=(
                "evaluate a deception lure campaign via the entrapment engine",
                "intercept and decipher an encoded SIGINT channel",
                "execute a green-pathed defector handoff protocol",
            ),
            assets=(
                Asset(
                    kind="playbook",
                    name="bait_profiles",
                    payload=list(_BAIT_PROFILE_IDS),
                ),
                Asset(
                    kind="sigint",
                    name="cipher_stack",
                    payload={"layers": len(_CIPHERS), "snr_db": _SNR_DB},
                ),
            ),
            constraints=(
                Constraint(
                    kind="determinism",
                    detail="fixed seed; no random draws, no wall-clock",
                ),
                Constraint(
                    kind="ethics",
                    detail="analytical deception model; no targeting of persons",
                ),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the mission request against the three available engines."""
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(
                    label="engines", detail="entrapment, sigint, handoff available"
                ),
                Finding(label="determinism", detail="fixed seed, reproducible outputs"),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the five deterministic steps across the three concepts."""
        return MissionPlan(
            steps=(
                Step(
                    name="bait",
                    action="run_bait_campaign",
                    params={"lure_id": "honey-trap-alpha"},
                ),
                Step(
                    name="intercept",
                    action="intercept_channel",
                    params={"snr_db": _SNR_DB},
                ),
                Step(
                    name="handoff",
                    action="run_green_handoff",
                    params={"call_sign": "ROZA"},
                ),
                Step(
                    name="package",
                    action="assemble_outcome",
                    params={"objectives": len(brief.objectives)},
                ),
                Step(name="verify", action="check_outcome", params={"success": True}),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the three pure engines deterministically and report results."""
        # 1. Entrapment: a fixed lure evaluated and campaigns run.
        lure = generate_bait_profile("honey-trap-alpha", seed=_SEED)
        campaign = run_bait_campaign(lure, engagement_threshold=0.5)
        # 2. SIGINT: intercept and decipher a fixed encoded channel at 80 dB.
        channel = intercept_channel(_PLAINTEXT, _CIPHERS, snr_db=_SNR_DB, seed=_SEED)
        # 3. Handoff: run the green path for a fixed call sign/challenge.
        handoff = HandoffProtocol(
            call_sign="ROZA", challenge="the cow jumped over the moon"
        )
        green = handoff.run_green()

        results: dict[str, object] = {
            "steps_completed": len(plan.steps),
            "outputs": tuple(step.name for step in plan.steps),
            "bite_probability": campaign["bite_probability"],
            "final_stage": campaign["final_stage"],
            "recovered_plaintext": channel["recovered_plaintext"],
            "recovered_exact": channel["recovered_exact"],
            "empirical_snr_db": channel["empirical_snr_db"],
            "handoff_state": green.state.value,
            "handoff_path": green.path,
        }
        return MissionOutcome(
            success=bool(channel["recovered_exact"]) and green.state.value == "handoff",
            results=results,
            provenance=Provenance(
                package_version=_PACKAGE_VERSION,
                seed=_SEED,
                input_hash="lures-mission-input-v1",
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarise the mission and record the standing lessons."""
        return Debrief(
            outcome=outcome,
            lessons=(
                "deterministic interception round-trips at high SNR",
                "the confirm code gates handoff completion — a wrong code aborts",
                "lure effectiveness is a monotone decision surface",
            ),
        )


register_gadgets()
