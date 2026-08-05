"""Tests for the courier handoff-scheduling module (real computation)."""

from __future__ import annotations

import itertools

import pytest

from from_russia_with_love.courier_schedule import (
    MAX_EXACT_RENDEZVOUS,
    Rendezvous,
    is_compatible,
    max_completed_handoffs,
    schedule_handoffs,
)
from from_russia_with_love.scenario import RENDEZVOUS, SCHEDULE_START


def _brute_force_max(rendezvous: tuple[Rendezvous, ...], start: float = 0.0) -> int:
    """Independent oracle: try every ordering of every subset, take the best.

    Deliberately written a different way from the production DP so that a
    shared bug cannot make both agree.
    """
    for size in range(len(rendezvous), 0, -1):
        for candidate in itertools.permutations(rendezvous, size):
            position = start
            feasible = True
            for item in candidate:
                begin = max(position, item.earliest)
                if begin > item.latest - item.duration:
                    feasible = False
                    break
                position = begin + item.duration
            if feasible:
                return size
    return 0


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


def test_schedule_takes_windows_in_deadline_order() -> None:
    """The heuristic must emit meets ordered by latest feasible start."""
    result = schedule_handoffs(RENDEZVOUS, start_time=SCHEDULE_START)
    deadlines = [r.latest - r.duration for r in result.scheduled]
    assert deadlines == sorted(deadlines)
    # Non-trivial: the canonical scenario really does leave a meet behind, so
    # this is not vacuously true over an empty or complete schedule.
    assert 0 < result.scheduled_count < len(RENDEZVOUS)


def test_duplicate_rendezvous_are_counted_individually() -> None:
    """Value-identical meets must not collapse in the scheduled/unscheduled split.

    Regression guard: ``Rendezvous`` is a frozen dataclass, so a set-based
    membership test silently merged duplicates and dropped a meet from the
    ledger entirely.
    """
    duplicated = (
        Rendezvous("M1", earliest=0.0, latest=3.0, duration=2.0),
        Rendezvous("M1", earliest=0.0, latest=3.0, duration=2.0),
    )
    result = schedule_handoffs(duplicated)
    assert result.scheduled_count == 1
    assert len(result.unscheduled) == 1
    assert result.scheduled_count + len(result.unscheduled) == len(duplicated)


def test_greedy_is_not_optimal_pinned_counterexample() -> None:
    """The heuristic is honestly sub-optimal — this pins a concrete instance.

    A long, slack window sorts first by latest feasible start and crowds out
    two short meets that together would have scored higher. If someone later
    claims this scheduler is optimal, this test fails.
    """
    instance = (
        Rendezvous("long", earliest=0.0, latest=10.0, duration=10.0),
        Rendezvous("short-a", earliest=0.0, latest=2.0, duration=1.0),
        Rendezvous("short-b", earliest=2.0, latest=4.0, duration=1.0),
    )
    heuristic = schedule_handoffs(instance)
    optimum = max_completed_handoffs(instance)
    assert heuristic.scheduled_count == 1
    assert optimum == 2
    assert optimum > heuristic.scheduled_count


def test_exact_solver_matches_independent_brute_force() -> None:
    """The subset DP must agree with an exhaustive permutation search."""
    instances = (
        RENDEZVOUS,
        (
            Rendezvous("long", earliest=0.0, latest=10.0, duration=10.0),
            Rendezvous("short-a", earliest=0.0, latest=2.0, duration=1.0),
            Rendezvous("short-b", earliest=2.0, latest=4.0, duration=1.0),
        ),
        (
            Rendezvous("solo", earliest=1.0, latest=4.0, duration=3.0),
            Rendezvous("clash", earliest=1.0, latest=4.0, duration=3.0),
        ),
        (Rendezvous("only", earliest=0.0, latest=5.0, duration=5.0),),
    )
    for instance in instances:
        assert max_completed_handoffs(instance) == _brute_force_max(instance), (
            f"exact DP disagreed with brute force on {instance}"
        )


def test_exact_solver_never_below_the_heuristic() -> None:
    result = schedule_handoffs(RENDEZVOUS, start_time=SCHEDULE_START)
    optimum = max_completed_handoffs(RENDEZVOUS, start_time=SCHEDULE_START)
    assert optimum >= result.scheduled_count


def test_exact_solver_respects_start_time() -> None:
    instance = (Rendezvous("late", earliest=0.0, latest=4.0, duration=2.0),)
    assert max_completed_handoffs(instance, start_time=0.0) == 1
    # Starting after the last feasible start makes the meet unreachable.
    assert max_completed_handoffs(instance, start_time=3.0) == 0


def test_exact_solver_edge_cases() -> None:
    assert max_completed_handoffs(()) == 0
    with pytest.raises(TypeError):
        max_completed_handoffs("not-a-tuple")  # type: ignore[arg-type]
    oversized = tuple(
        Rendezvous(f"M{i}", earliest=0.0, latest=2.0, duration=1.0)
        for i in range(MAX_EXACT_RENDEZVOUS + 1)
    )
    with pytest.raises(ValueError, match="bounded to"):
        max_completed_handoffs(oversized)
