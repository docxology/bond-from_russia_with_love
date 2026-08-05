"""LURES — the From Russia with Love (1963) MissionProvider for BOND-API.

This is the thin adapter between the pure domain core (``entrapment_engine``,
``bait_allocation``, ``sigint``, ``direction_finding``, ``courier_schedule``,
``handoff_protocol``) and the FROZEN ``bond_api`` protocol. The domain
modules are importable without ``bond-api``; only this file touches the
protocol types.

Per the discovery contract, the module exposes a top-level ``MissionProvider``
class (name fixed by the contract) and registers its gadgets with the
``bond_api`` :class:`GadgetRegistry`. The public shape is stable: the five
stages, the ``film`` attribute, and the module-level ``GADGETS`` /
``register_gadgets`` convention are what fleet consumers (coordinator
reconcile, orchestrator, CLI) bind to.
"""

from __future__ import annotations

import numpy as np
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

__all__ = ["MissionProvider", "GADGETS", "register_gadgets", "_PACKAGE_VERSION"]

_PACKAGE_VERSION = "0.1.0"


def register_gadgets() -> None:
    """Register this film's gadgets with the shared BOND gadget registry.

    Gadgets are opaque payloads (the pure engines and their fixed scenario
    data) that other suite packages can ``lookup`` without importing this
    package's internals.
    """
    GADGETS.clear()
    GADGETS.update(
        {
            "bait_profiles": scenario.BAIT_PROFILE_IDS,
            "allocation_targets": len(scenario.ALLOC_TARGETS),
            "ciphers": scenario.CIPHERS,
            "handoff_call_signs": scenario.CALL_SIGNS,
            "receivers": len(scenario.TDOA_RECEIVERS),
            "rendezvous": len(scenario.RENDEZVOUS),
            "entrapment_engine": "from_russia_with_love.entrapment_engine",
            "bait_allocation": "from_russia_with_love.bait_allocation",
            "sigint": "from_russia_with_love.sigint",
            "direction_finding": "from_russia_with_love.direction_finding",
            "courier_schedule": "from_russia_with_love.courier_schedule",
            "handoff_protocol": "from_russia_with_love.handoff_protocol",
        }
    )


#: The film's gadget payloads (dict of name -> opaque payload).
GADGETS: dict[str, object] = {}


class MissionProvider:  # noqa: N801 — class name is fixed by the discovery contract
    """Deterministic LURES mission: deception, SIGINT, defector handoff."""

    film = "from_russia_with_love"

    def brief(self) -> MissionBrief:
        """Declare the LURES mission and its objectives."""
        return MissionBrief(
            film=self.film,
            codename="LURES",
            objectives=scenario.OBJECTIVES,
            assets=(
                Asset(
                    kind="playbook",
                    name="bait_profiles",
                    payload=list(scenario.BAIT_PROFILE_IDS),
                ),
                Asset(
                    kind="sigint",
                    name="cipher_stack",
                    payload={
                        "layers": len(scenario.CIPHERS),
                        "snr_db": scenario.SNR_DB,
                    },
                ),
                Asset(
                    kind="direction_finding",
                    name="receivers",
                    payload={
                        "sites": len(scenario.TDOA_RECEIVERS),
                        "noise_std": scenario.TDOA_NOISE_STD,
                    },
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
        """Survey the mission request against the available engines."""
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(
                    label="engines",
                    detail="entrapment, allocation, sigint, TDOA, courier, handoff",
                ),
                Finding(label="determinism", detail="fixed seed, reproducible outputs"),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the deterministic steps across the six concepts."""
        return MissionPlan(
            steps=(
                Step(
                    name="bait",
                    action="run_bait_campaign",
                    params={"lure_id": "honey-trap-alpha"},
                ),
                Step(
                    name="allocate",
                    action="allocate_lures",
                    params={
                        "budget": scenario.ALLOC_BUDGET,
                        "lure_strength": scenario.ALLOC_LURE_STRENGTH,
                    },
                ),
                Step(
                    name="intercept",
                    action="intercept_channel",
                    params={"snr_db": scenario.SNR_DB},
                ),
                Step(
                    name="geolocate",
                    action="estimate_position",
                    params={"noise_std": scenario.TDOA_NOISE_STD},
                ),
                Step(
                    name="schedule",
                    action="schedule_handoffs",
                    params={"rendezvous": len(scenario.RENDEZVOUS)},
                ),
                Step(
                    name="handoff",
                    action="run_green_handoff",
                    params={"call_sign": scenario.HANDOFF_CALL_SIGN},
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
        """Run the six pure engines deterministically and report results."""
        # 1. Entrapment: a fixed lure evaluated and its campaign run.
        lure = generate_bait_profile("honey-trap-alpha", seed=scenario.SEED)
        campaign = run_bait_campaign(
            lure, engagement_threshold=scenario.ENGAGEMENT_THRESHOLD
        )
        # 2. Bait allocation: exact knapsack + greedy baseline.
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
        # 3. SIGINT: intercept + decipher the fixed channel; segment its burst.
        channel = intercept_channel(
            scenario.PLAINTEXT,
            scenario.CIPHERS,
            snr_db=scenario.SNR_DB,
            seed=scenario.SEED,
        )
        envelope = np.abs(np.asarray(channel["captured_samples"], dtype=np.float64))
        threshold = float(np.mean(envelope)) * 0.5
        bursts = segment_bursts(envelope, threshold=threshold, min_gap=1)
        # 4. Direction finding: TDOA measurements + Gauss-Newton estimate.
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
        tdoa_error = localization_error(estimate.position, scenario.TDOA_TRANSMITTER)
        # 5. Courier schedule: heuristic plan, scored against the exact optimum.
        schedule = schedule_handoffs(
            scenario.RENDEZVOUS, start_time=scenario.SCHEDULE_START
        )
        schedule_optimum = max_completed_handoffs(
            scenario.RENDEZVOUS, start_time=scenario.SCHEDULE_START
        )
        # 6. Handoff: green path plus the red-path abort drill.
        handoff = HandoffProtocol(
            call_sign=scenario.HANDOFF_CALL_SIGN, challenge=scenario.CHALLENGE
        )
        green = handoff.run_green()
        red = HandoffProtocol(
            call_sign=scenario.HANDOFF_CALL_SIGN, challenge=scenario.CHALLENGE
        ).run_red_path()

        results: dict[str, object] = {
            "steps_completed": len(plan.steps),
            "outputs": tuple(step.name for step in plan.steps),
            "bite_probability": campaign["bite_probability"],
            "final_stage": campaign["final_stage"],
            "allocated_targets": allocation.budget_used,
            "allocation_value": allocation.expected_value,
            "greedy_value": greedy.expected_value,
            "recovered_plaintext": channel["recovered_plaintext"],
            "recovered_exact": channel["recovered_exact"],
            "empirical_snr_db": channel["empirical_snr_db"],
            "burst_count": len(bursts),
            "tdoa_error": tdoa_error,
            "tdoa_converged": estimate.converged,
            "tdoa_iterations": estimate.iterations,
            "schedule_count": schedule.scheduled_count,
            "schedule_optimum": schedule_optimum,
            "schedule_gap": schedule_optimum - schedule.scheduled_count,
            "schedule_finish": schedule.finish_time,
            "handoff_state": green.state.value,
            "handoff_path": green.path,
            "red_path_state": red.state.value,
        }
        success = (
            bool(channel["recovered_exact"])
            and green.state.value == "handoff"
            and tdoa_error < 0.5
            and schedule.scheduled_count >= 1
        )
        return MissionOutcome(
            success=success,
            results=results,
            provenance=Provenance(
                package_version=_PACKAGE_VERSION,
                seed=scenario.SEED,
                input_hash="lures-mission-input-v2",
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarise the mission and record the standing lessons."""
        return Debrief(
            outcome=outcome,
            lessons=(
                "deterministic interception round-trips at high SNR",
                "the greedy allocator ties the exact knapsack on the canonical "
                "target pool (gap 0.000); the separation is measured on the "
                "witness pool, not asserted from the exact solver's optimality",
                "TDOA Gauss-Newton recovers the transmitter to within a small "
                "error in receiver coordinate units",
                "the courier heuristic is scored against the exact schedule "
                "optimum rather than assumed optimal",
                "the confirm code gates handoff completion — a wrong code aborts",
                "lure effectiveness is a monotone decision surface",
            ),
        )


register_gadgets()
