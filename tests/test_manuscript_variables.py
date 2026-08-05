"""Tests for manuscript {{TOKEN}} hydration + live cross-reference gate."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from from_russia_with_love import scenario
from from_russia_with_love.manuscript_variables import (
    PACKAGE_VERSION,
    _float_field,
    _traffic_field,
    generate_variables,
    load_mission_config,
    validate_mission_config,
)
from from_russia_with_love.sigint import intercept_channel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_FIXED_NOW = "2026-08-04T00:00:00Z"


@pytest.fixture(scope="module")
def variables() -> dict[str, object]:
    return generate_variables(PROJECT_ROOT, allow_draft=True, now=_FIXED_NOW)


def test_config_loaded() -> None:
    config = load_mission_config(PROJECT_ROOT)
    paper = config["paper"]
    assert isinstance(paper, dict)
    assert "title" in paper


def test_config_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_mission_config(tmp_path)


def test_config_non_mapping_raises(tmp_path: Path) -> None:
    (tmp_path / "manuscript").mkdir(parents=True)
    (tmp_path / "manuscript" / "config.yaml").write_text(
        "just a string\n", encoding="utf-8"
    )
    with pytest.raises(TypeError):
        load_mission_config(tmp_path)


def test_variables_identity(variables: dict[str, object]) -> None:
    assert variables["BOND_IDENTITY"] == "LURES"
    assert variables["BOND_CODENAME"] == "LURES"
    assert variables["BOND_VERSION"] == PACKAGE_VERSION
    assert "From Russia with Love" in str(variables["BOND_TITLE"])


def test_variables_live_values(variables: dict[str, object]) -> None:
    # result-derived: never hand-authored
    assert 0.0 < float(variables["LURES_BITE_PROBABILITY"]) < 1.0
    assert variables["LURES_FINAL_STAGE"] in ("sprung", "aborted")
    assert variables["LURES_RECOVERED_EXACT"] == "True"
    assert variables["LURES_HANDOFF_STATE"] == "handoff"
    assert len(str(variables["LURES_CONFIRM_CODE"])) == 6
    assert variables["GENERATION_TIMESTAMP"] == _FIXED_NOW


def test_variables_deterministic() -> None:
    a = generate_variables(PROJECT_ROOT, now=_FIXED_NOW)
    b = generate_variables(PROJECT_ROOT, now=_FIXED_NOW)
    assert a == b


def test_variables_wallclock_fallback() -> None:
    # Omitting `now` exercises the wall-clock fallback branch.
    variables = generate_variables(PROJECT_ROOT)
    assert "GENERATION_TIMESTAMP" in variables
    assert str(variables["GENERATION_TIMESTAMP"]).endswith("Z")


def test_variables_keywords_fallback_branch(tmp_path: Path) -> None:
    # A config whose `keywords` is not a list exercises the empty-list branch.
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        "paper:\n  title: T\n  version: 0.1.0\nkeywords: just-a-string\n",
        encoding="utf-8",
    )
    variables = generate_variables(tmp_path, now=_FIXED_NOW)
    assert variables["CONFIG_KEYWORDS"] == ""  # non-list keywords -> empty join


def test_intercept_field_helpers_read_a_real_intercept() -> None:
    """Happy paths over genuine intercept output, plus both guard branches."""
    channel = intercept_channel(
        scenario.PLAINTEXT, scenario.CIPHERS, snr_db=scenario.SNR_DB, seed=0
    )
    assert _traffic_field(channel, "length") == len(scenario.PLAINTEXT.encode("utf-8"))
    assert _traffic_field(channel, "distinct_symbols") > 0
    with pytest.raises(TypeError, match="must be a mapping"):
        _traffic_field({"traffic": "not-a-mapping"}, "length")

    # A seed-0 capture is exactly lossless, so the empirical SNR is +inf.
    assert _float_field(channel, "empirical_snr_db") == float("inf")
    with pytest.raises(TypeError, match="must be numeric"):
        _float_field({"empirical_snr_db": "not-a-number"}, "empirical_snr_db")


def test_shipped_config_agrees_with_scenario() -> None:
    """The real config must pass the drift guard (it is the shipped state)."""
    validate_mission_config(load_mission_config(PROJECT_ROOT))


def test_config_scenario_drift_is_detected() -> None:
    """Positive control: the guard must actually reject a drifted config.

    Without this, ``validate_mission_config`` could be green by construction.
    """
    drifted = {"mission": {"objectives": len(scenario.OBJECTIVES) + 1}}
    with pytest.raises(ValueError, match="disagrees with scenario.py"):
        validate_mission_config(drifted)

    drifted_seed = {"mission": {"seed": scenario.SEED + 1}}
    with pytest.raises(ValueError, match="seed"):
        validate_mission_config(drifted_seed)


def test_config_without_mission_block_is_allowed() -> None:
    validate_mission_config({"paper": {"title": "T"}})


def test_config_mission_block_must_be_a_mapping() -> None:
    with pytest.raises(TypeError):
        validate_mission_config({"mission": "not-a-mapping"})


def test_generate_variables_rejects_drifted_config(tmp_path: Path) -> None:
    """The drift guard is wired into the manuscript build, not just callable."""
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        "paper:\n  title: T\n  version: 0.1.0\nmission:\n  seed: 999\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="disagrees with scenario.py"):
        generate_variables(tmp_path, now=_FIXED_NOW)


def test_objective_count_token_tracks_the_canonical_tuple(
    variables: dict[str, object],
) -> None:
    """The token is derived from scenario.OBJECTIVES, not a hand-written number."""
    assert variables["LURES_NUM_OBJECTIVES"] == len(scenario.OBJECTIVES)


def test_schedule_tokens_report_the_optimality_gap(
    variables: dict[str, object],
) -> None:
    count = int(str(variables["LURES_SCHEDULE_COUNT"]))
    optimum = int(str(variables["LURES_SCHEDULE_OPTIMUM"]))
    gap = int(str(variables["LURES_SCHEDULE_GAP"]))
    assert optimum >= count
    assert gap == optimum - count
    assert 0 <= optimum <= len(scenario.RENDEZVOUS)


def test_new_scenario_tokens_match_the_source_of_truth(
    variables: dict[str, object],
) -> None:
    assert variables["LURES_ALLOC_TARGETS"] == len(scenario.ALLOC_TARGETS)
    assert variables["LURES_CIPHER_LAYERS"] == len(scenario.CIPHERS)
    assert variables["LURES_SEED"] == scenario.SEED
    assert variables["LURES_MESSAGE_BYTES"] == len(scenario.PLAINTEXT.encode("utf-8"))
    assert int(str(variables["LURES_TRAFFIC_DISTINCT"])) > 0
    assert float(str(variables["LURES_ALLOC_VALUE"])) >= float(
        str(variables["LURES_GREEDY_VALUE"])
    )


def test_all_manuscript_tokens_are_generated(variables: dict[str, object]) -> None:
    """Live gate: every {{TOKEN}} in numbered prose sections must be generated."""
    token_pattern = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")
    referenced: set[str] = set()
    for section in sorted(PROJECT_ROOT.glob("manuscript/[0-9]*.md")):
        text = section.read_text(encoding="utf-8")
        referenced.update(token_pattern.findall(text))
    missing = sorted(tok for tok in referenced if tok not in variables)
    assert not missing, (
        f"manuscript tokens missing from generate_variables(): {missing}"
    )
