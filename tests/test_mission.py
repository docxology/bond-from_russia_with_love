"""Tests for the LURES MissionProvider adapter + gadget registration."""

from __future__ import annotations

from bond_api.protocol import (
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    run_mission,
)
from bond_api.protocol import (
    MissionProvider as ProviderProtocol,
)
from bond_api.registry import GadgetRegistry

from from_russia_with_love import scenario
from from_russia_with_love.mission import GADGETS, MissionProvider, register_gadgets


def test_provider_is_runtime_checkable() -> None:
    provider = MissionProvider()
    assert isinstance(provider, ProviderProtocol)
    assert provider.film == "from_russia_with_love"


def test_brief_shape() -> None:
    provider = MissionProvider()
    brief = provider.brief()
    assert isinstance(brief, MissionBrief)
    assert brief.codename == "LURES"
    # The brief must publish the canonical objectives verbatim, so the count
    # in the manuscript and the count in the brief cannot drift apart.
    assert brief.objectives == scenario.OBJECTIVES
    assert len(brief.objectives) == 6
    assert len(brief.assets) == 3
    assert len(brief.constraints) >= 1


def test_recon_shape() -> None:
    provider = MissionProvider()
    report = provider.recon(ReconRequest(goal="assess LURES posture"))
    assert isinstance(report, ReconReport)
    assert any(find.label == "goal" for find in report.findings)


def test_plan_shape() -> None:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    assert isinstance(plan, MissionPlan)
    assert len(plan.steps) == 8
    assert plan.steps[0].name == "bait"
    assert plan.steps[-1].name == "verify"


def test_execute_deterministic_success() -> None:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    first = provider.execute(plan)
    second = provider.execute(plan)
    assert isinstance(first, MissionOutcome)
    assert first.success is True
    assert first.results["handoff_state"] == "handoff"
    assert first.results["recovered_exact"] is True
    assert first.results["tdoa_error"] < 0.5
    assert first.results["schedule_count"] >= 1
    # The heuristic plan is reported alongside the exact optimum and the gap.
    assert first.results["schedule_optimum"] >= first.results["schedule_count"]
    assert (
        first.results["schedule_gap"]
        == first.results["schedule_optimum"] - first.results["schedule_count"]
    )
    assert isinstance(first.provenance, Provenance)
    assert first.provenance.seed == 11
    # full determinism: identical result dicts
    assert first.results == second.results
    assert first.results["outputs"] == (
        "bait",
        "allocate",
        "intercept",
        "geolocate",
        "schedule",
        "handoff",
        "package",
        "verify",
    )


def test_run_mission_full_flow() -> None:
    provider = MissionProvider()
    debrief = run_mission(provider, ReconRequest(goal="full flow verification"))
    assert debrief.outcome.success is True
    assert len(debrief.lessons) >= 1
    assert all(isinstance(lesson, str) and lesson.strip() for lesson in debrief.lessons)


def test_debrief_lessons() -> None:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    outcome = provider.execute(plan)
    debrief = provider.debrief(outcome)
    assert debrief.outcome is outcome
    assert len(debrief.lessons) == 6


def test_gadgets_registered() -> None:
    registry = GadgetRegistry()
    register_gadgets()
    registry.register(MissionProvider.film, GADGETS)
    assert registry.contains("from_russia_with_love", "bait_profiles")
    assert registry.lookup("from_russia_with_love", "entrapment_engine").endswith(
        "entrapment_engine"
    )
    assert registry.films() == ("from_russia_with_love",)


def test_gadgets_global_shape() -> None:
    assert set(("bait_profiles", "ciphers", "handoff_call_signs", "receivers")) <= set(
        GADGETS
    )
    assert isinstance(GADGETS["bait_profiles"], tuple)


def test_import_without_bond_api_fallback() -> None:
    # The pure core must import with no bond_api dependency (mission.py is
    # the only module that touches it).
    import importlib
    from pathlib import Path

    package_dir = (
        Path(__file__).resolve().parent.parent / "src" / "from_russia_with_love"
    )
    pure_modules = (
        "entrapment_engine",
        "sigint",
        "handoff_protocol",
        "bait_allocation",
        "direction_finding",
        "courier_schedule",
        "scenario",
    )
    for mod in pure_modules:
        assert importlib.import_module(f"from_russia_with_love.{mod}") is not None
        text = (package_dir / f"{mod}.py").read_text(encoding="utf-8")
        assert "bond_api" not in text and "bond-api" not in text, (
            f"{mod} must not import bond_api"
        )


def test_mission_execute_agrees_with_manuscript_variables() -> None:
    """V1: the adapter and the token generator bind to the same engines.

    ``MissionProvider.execute`` and ``generate_variables`` each run the six
    engines through their own call sequence. This test computes both and
    asserts field-by-field equality on every overlapping published quantity, so
    editing one call site alone (e.g. the burst factor in ``mission.py``)
    makes the manuscript token disagree with the executed mission and this test
    goes red.
    """
    from pathlib import Path

    from from_russia_with_love.manuscript_variables import generate_variables

    project_root = Path(__file__).resolve().parent.parent
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    r = outcome.results
    v = generate_variables(project_root)

    assert v["LURES_BITE_PROBABILITY"] == f"{r['bite_probability']:.3f}"
    assert v["LURES_FINAL_STAGE"] == str(r["final_stage"])
    assert v["LURES_ALLOC_VALUE"] == f"{r['allocation_value']:.3f}"
    assert v["LURES_GREEDY_VALUE"] == f"{r['greedy_value']:.3f}"
    assert v["LURES_RECOVERED_EXACT"] == str(bool(r["recovered_exact"]))
    assert v["LURES_EMPIRICAL_SNR_DB"] == f"{r['empirical_snr_db']:.1f}"
    assert v["LURES_BURST_COUNT"] == r["burst_count"]
    assert v["LURES_TDOA_ERROR"] == f"{r['tdoa_error']:.3f}"
    assert v["LURES_TDOA_ITERATIONS"] == r["tdoa_iterations"]
    assert v["LURES_TDOA_CONVERGED"] == str(bool(r["tdoa_converged"]))
    assert v["LURES_SCHEDULE_COUNT"] == r["schedule_count"]
    assert v["LURES_SCHEDULE_OPTIMUM"] == r["schedule_optimum"]
    assert v["LURES_SCHEDULE_GAP"] == r["schedule_gap"]
    assert v["LURES_HANDOFF_STATE"] == str(r["handoff_state"])
    assert v["LURES_RED_PATH_STATE"] == str(r["red_path_state"])
    assert v["LURES_CONFIRM_CODE"] == r["confirm_code"]
