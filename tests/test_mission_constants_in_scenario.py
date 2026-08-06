"""V3: every mission constant lives in ``scenario.py`` and nowhere else.

A source-reading gate (the same idiom as
``test_import_without_bond_api_fallback``): ``mission.py`` and
``manuscript_variables.py`` must not embed the executable literals that
``scenario.py`` now owns. Reintroducing any of them (the C1 family) fails the
suite, which is the point — the invariant was previously asserted in prose
only and enforced by nothing.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_ADAPTER_FILES = (
    PROJECT_ROOT / "src" / "from_russia_with_love" / "mission.py",
    PROJECT_ROOT / "src" / "from_russia_with_love" / "manuscript_variables.py",
)

#: Literals that must live in scenario.py (as named constants) and nowhere
#: else. They were duplicated across mission.py and manuscript_variables.py
#: before round 2; each now reads the scenario constant instead.
_FORBIDDEN_LITERALS = (
    "honey-trap-alpha",  # -> scenario.PRIMARY_BAIT_PROFILE
    "lures-mission-input",  # -> scenario.INPUT_HASH
    "min_gap=1",  # -> scenario.BURST_MIN_GAP
    "* 0.5",  # -> scenario.BURST_THRESHOLD_FRACTION
    "tdoa_error < 0.5",  # -> scenario.TDOA_SUCCESS_MAX_ERROR
    "scheduled_count >= 1",  # -> scenario.SCHEDULE_SUCCESS_MIN_COUNT
)


def test_mission_constants_are_not_duplicated_outside_scenario() -> None:
    for path in _ADAPTER_FILES:
        assert path.is_file(), f"expected adapter source at {path}"
        text = path.read_text(encoding="utf-8")
        for literal in _FORBIDDEN_LITERALS:
            assert literal not in text, (
                f"{path.name} embeds the mission literal {literal!r}; it must "
                "be sourced from scenario.py (the single source of truth)"
            )


def test_forbidden_literal_scan_is_non_empty() -> None:
    """Guard against a vacuous gate: the scan must assert something real."""
    assert len(_FORBIDDEN_LITERALS) >= 5
    for literal in _FORBIDDEN_LITERALS:
        assert len(literal) > 3
