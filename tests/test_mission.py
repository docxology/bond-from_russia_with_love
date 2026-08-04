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
    assert len(brief.objectives) == 3
    assert len(brief.assets) == 2
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
    assert len(plan.steps) == 5
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
    assert isinstance(first.provenance, Provenance)
    assert first.provenance.seed == 11
    # full determinism: identical result dicts
    assert first.results == second.results
    assert first.results["outputs"] == (
        "bait",
        "intercept",
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
    assert len(debrief.lessons) == 3


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
    assert set(("bait_profiles", "ciphers", "handoff_call_signs")) <= set(GADGETS)
    assert isinstance(GADGETS["bait_profiles"], tuple)


def test_import_without_bond_api_fallback() -> None:
    # The pure core must import with no bond_api dependency (mission.py is
    # the only module that touches it).
    import importlib
    from pathlib import Path

    package_dir = (
        Path(__file__).resolve().parent.parent / "src" / "from_russia_with_love"
    )
    for mod in ("entrapment_engine", "sigint", "handoff_protocol"):
        assert importlib.import_module(f"from_russia_with_love.{mod}") is not None
        text = (package_dir / f"{mod}.py").read_text(encoding="utf-8")
        assert "bond_api" not in text and "bond-api" not in text, (
            f"{mod} must not import bond_api"
        )
