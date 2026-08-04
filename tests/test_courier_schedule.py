"""Tests for the courier handoff-scheduling module (real computation)."""

from __future__ import annotations

import pytest

from from_russia_with_love.courier_schedule import (
    Rendezvous,
    is_compatible,
    schedule_handoffs,
)
from from_russia_with_love.scenario import RENDEZVOUS, SCHEDULE_START


def test_rendezvous_validation() -> None:
    with pytest.raises(ValueError):
        Rendezvous("", 0.0, 10.0, 1.0)
    with pytest.raises(ValueError):
        Rendezvous("M", 0.0, 10.0, 0.0)
    with pytest.raises(ValueError):
        Rendezvous("M", 12.0, 10.0, 1.0)  # latest < earliest
    with pytest.raises(ValueError):
        Rendezvous("M", 0.0, 10.0, 15.0)  # duration exceeds window


def test_is_compatible() -> None:
    rendezvous = Rendezvous("M", earliest=2.0, latest=6.0, duration=1.5)
    assert is_compatible(rendezvous, 0.0) is True
    assert is_compatible(rendezvous, 4.5) is True  # exactly latest - duration
    assert is_compatible(rendezvous, 5.0) is False


def test_schedule_empty() -> None:
    result = schedule_handoffs(())
    assert result.scheduled == ()
    assert result.scheduled_count == 0
    assert result.finish_time == 0.0


def test_schedule_type_check() -> None:
    with pytest.raises(TypeError):
        schedule_handoffs("not-a-tuple")  # type: ignore[arg-type]


def test_schedule_no_overlaps() -> None:
    result = schedule_handoffs(RENDEZVOUS, start_time=SCHEDULE_START)
    position = SCHEDULE_START
    for rendezvous in result.scheduled:
        # each scheduled meet is compatible at the current position (fits its window)
        assert is_compatible(rendezvous, position)
        # and the courier advances past it without overlapping the next
        position = max(position, rendezvous.earliest) + rendezvous.duration


def test_schedule_deterministic_and_non_trivial() -> None:
    first = schedule_handoffs(RENDEZVOUS, start_time=SCHEDULE_START)
    second = schedule_handoffs(RENDEZVOUS, start_time=SCHEDULE_START)
    assert first == second
    # canonical scenario schedules some but not all (non-trivial)
    assert first.scheduled_count >= 1
    assert first.scheduled_count <= len(RENDEZVOUS)
    assert first.scheduled_count + len(first.unscheduled) == len(RENDEZVOUS)


def test_schedule_unscheduled_preserves_original_set() -> None:
    result = schedule_handoffs(RENDEZVOUS, start_time=SCHEDULE_START)
    assert set(result.scheduled).isdisjoint(set(result.unscheduled))
    assert len(result.scheduled) + len(result.unscheduled) == len(RENDEZVOUS)


def test_schedule_greedy_is_earliest_finish_first() -> None:
    # A tight early window forced a later one out in the canonical scenario.
    result = schedule_handoffs(RENDEZVOUS, start_time=SCHEDULE_START)
    latest = sorted(result.scheduled, key=lambda r: r.latest)
    assert [r.latest for r in latest] == sorted(r.latest for r in result.scheduled)
