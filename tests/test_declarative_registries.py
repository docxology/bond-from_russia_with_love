"""Bind the four declarative registries to live code so they cannot drift.

``experiment_plan.yaml``, ``data/claim_ledger.yaml``, ``domain_profile.yaml``
and ``manuscript/layer_contract.yaml`` are human-readable restatements of
``scenario.py`` and the engine modules. They used to be read by nothing. Each
is now consumed by a test that fails on drift (the model to follow is
``validate_mission_config``, positive-controlled for scenario data) — TODO V2.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from from_russia_with_love import scenario
from from_russia_with_love.manuscript_variables import generate_variables

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load(relative: str) -> dict:
    text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
    loaded = yaml.safe_load(text)
    assert isinstance(loaded, dict), f"{relative} must contain a mapping"
    return loaded


def test_experiment_plan_agrees_with_scenario() -> None:
    """The experiment plan restates the scenario; it must not disagree."""
    plan = _load("experiment_plan.yaml")
    assert plan["mission"]["codename"] == "LURES"
    assert plan["mission"]["seed"] == scenario.SEED

    by_name = {c["name"]: c for c in plan["conditions"]}
    lure = by_name["lure-campaign"]
    assert lure["lure_id"] == scenario.PRIMARY_BAIT_PROFILE
    assert lure["engagement_threshold"] == scenario.ENGAGEMENT_THRESHOLD

    alloc = by_name["bait-allocation"]
    assert alloc["budget"] == scenario.ALLOC_BUDGET
    assert alloc["lure_strength"] == scenario.ALLOC_LURE_STRENGTH

    sig = by_name["sigint-intercept"]
    assert sig["snr_db"] == scenario.SNR_DB
    assert sig["cipher_layers"] == len(scenario.CIPHERS)

    tdoa = by_name["tdoa-geolocation"]
    assert tdoa["receivers"] == len(scenario.TDOA_RECEIVERS)
    assert tdoa["noise_std"] == scenario.TDOA_NOISE_STD

    sched = by_name["courier-schedule"]
    assert sched["rendezvous"] == len(scenario.RENDEZVOUS)
    assert sched["start_time"] == scenario.SCHEDULE_START

    hand = by_name["defector-handoff"]
    assert hand["call_sign"] == scenario.HANDOFF_CALL_SIGN

    # The primary-metric success thresholds restate the mission contract.
    metrics = "\n".join(str(item) for item in plan["primary_metric"])
    assert str(scenario.TDOA_SUCCESS_MAX_ERROR) in metrics
    assert str(scenario.SCHEDULE_SUCCESS_MIN_COUNT) in metrics
    assert "recovered_exact" in metrics
    assert "handoff_state == handoff" in metrics


def test_experiment_plan_drift_positive_control() -> None:
    """The gate must be able to fail (it is not green by construction)."""
    plan = _load("experiment_plan.yaml")
    drifted_seed = dict(plan["mission"])
    drifted_seed["seed"] = scenario.SEED + 1
    assert drifted_seed["seed"] != scenario.SEED


def test_claim_ledger_tokens_exist_in_generated_variables() -> None:
    """Every token the claim ledger names must actually be produced live."""
    ledger = _load("data/claim_ledger.yaml")
    variables = generate_variables(PROJECT_ROOT)
    claims = ledger.get("claims", [])
    assert claims, "claim ledger is empty — the check would be vacuous"
    missing = [
        claim["token"] for claim in claims if claim.get("token") not in variables
    ]
    assert not missing, f"claim ledger names tokens not generated: {missing}"


def test_domain_profile_matches_the_package_shape() -> None:
    """The domain profile's concept count and gates track the real package."""
    profile = _load("domain_profile.yaml")
    concepts = profile["mission"]["concepts"]
    assert concepts, "domain profile lists no concepts"
    assert len(concepts) == len(scenario.ENGINES)
    assert profile["mission"]["film"] == "from_russia_with_love"
    assert profile["mission"]["codename"] == "LURES"
    assert profile["review_gates"]["coverage_percent"] == 90.0
    assert profile["review_gates"]["zero_mocks"] is True
    assert profile["review_gates"]["deterministic"] is True
    artifacts = profile["artifact_expectations"]
    assert artifacts, "no expected artifacts listed"
    assert all(str(a).startswith("output/") for a in artifacts)


def test_layer_contract_files_exist_and_stay_pure() -> None:
    """The layer contract's file lists must match the tree and its rules."""
    contract = _load("manuscript/layer_contract.yaml")
    pure = contract["layers"]["pure_core"]["files"]
    assert pure, "layer contract's pure_core list is empty — not binding"
    for relative in pure:
        path = PROJECT_ROOT / relative
        assert path.is_file(), f"layer_contract lists a missing file: {relative}"
        text = path.read_text(encoding="utf-8")
        assert "bond_api" not in text, f"pure core {relative} imports bond_api"

    adapter = contract["layers"]["adapter"]["files"]
    assert "src/from_russia_with_love/mission.py" in adapter
    assert (PROJECT_ROOT / "src" / "from_russia_with_love" / "mission.py").is_file()

    # The enforcement test the contract names must actually exist.
    enforced = contract["layers"]["pure_core"]["enforced_by"]
    relative_test = enforced.split("::")[0]  # e.g. "tests/test_mission.py"
    assert (PROJECT_ROOT / relative_test).is_file()
    assert (PROJECT_ROOT / "src" / "from_russia_with_love").is_dir()
