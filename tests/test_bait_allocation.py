"""Tests for the bait allocation (0/1 knapsack) module (real computation)."""

from __future__ import annotations

import pytest

from from_russia_with_love.bait_allocation import (
    Target,
    allocate_lures,
    bite_value,
    greedy_allocate,
    validate_targets,
)
from from_russia_with_love.scenario import (
    ALLOC_BUDGET,
    ALLOC_LURE_STRENGTH,
    ALLOC_TARGETS,
    GREEDY_WITNESS_BUDGET,
    GREEDY_WITNESS_LURE_STRENGTH,
    GREEDY_WITNESS_TARGETS,
)


def test_target_validation() -> None:
    with pytest.raises(ValueError):
        Target("", 0.5, 1.0)
    with pytest.raises(ValueError):
        Target("a", 1.5, 1.0)
    with pytest.raises(ValueError):
        Target("a", 0.5, 0.0)
    with pytest.raises(ValueError):
        Target("a", 0.5, 1.0, lure_cost=0)


def test_validate_targets() -> None:
    with pytest.raises(ValueError):
        validate_targets((), -1)
    with pytest.raises(TypeError):
        validate_targets("not-a-tuple", 5)  # type: ignore[arg-type]


def test_bite_value_and_validation() -> None:
    target = Target("t1", susceptibility=0.8, value=10.0)
    value1 = bite_value(target, 0.6)
    strong = bite_value(target, 0.9)
    assert value1 > 0.0
    assert strong > value1  # monotone in lure strength
    with pytest.raises(TypeError):
        bite_value("not-a-target", 0.6)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        bite_value(target, 1.5)


def test_allocate_zero_budget() -> None:
    result = allocate_lures(ALLOC_TARGETS, 0, ALLOC_LURE_STRENGTH)
    assert result.chosen == ()
    assert result.expected_value == 0.0
    assert result.budget_used == 0


def test_allocate_never_exceeds_budget() -> None:
    for budget in (1, 2, 3, ALLOC_BUDGET, 10):
        result = allocate_lures(ALLOC_TARGETS, budget, ALLOC_LURE_STRENGTH)
        assert result.budget_used <= budget
        assert result.total_targets == len(ALLOC_TARGETS)
        assert result.total_budget == budget


def test_allocate_deterministic() -> None:
    first = allocate_lures(ALLOC_TARGETS, ALLOC_BUDGET, ALLOC_LURE_STRENGTH)
    second = allocate_lures(ALLOC_TARGETS, ALLOC_BUDGET, ALLOC_LURE_STRENGTH)
    assert first == second


def test_exact_dominates_greedy_strict_separation() -> None:
    """The shipped witness instance must separate the solvers *strictly*.

    This is the falsifiable half of the allocation claim. ``exact >= greedy``
    is a theorem and cannot fail; a *strictly* positive gap on a fixed
    instance can. If ``allocate_lures`` ever degraded into the greedy pick
    (or the witness pool were edited into a tie), this assertion goes red.
    """
    exact = allocate_lures(
        GREEDY_WITNESS_TARGETS, GREEDY_WITNESS_BUDGET, GREEDY_WITNESS_LURE_STRENGTH
    )
    greedy = greedy_allocate(
        GREEDY_WITNESS_TARGETS, GREEDY_WITNESS_BUDGET, GREEDY_WITNESS_LURE_STRENGTH
    )
    assert greedy.expected_value < exact.expected_value
    assert exact.expected_value - greedy.expected_value > 1e-9
    assert exact.chosen[0].target_id == "W1"
    assert exact.budget_used == GREEDY_WITNESS_BUDGET
    # And the greedy heuristic really does make the blocking pick.
    assert {t.target_id for t in greedy.chosen} == {"W2"}


def test_canonical_pool_does_not_separate_the_solvers() -> None:
    """Pin the honest fact the manuscript now reports: the canonical pool ties.

    Recorded as a measured property so that a scenario edit which *does*
    create a separation cannot silently leave §3.1's "gap is zero" prose
    behind. This assertion is falsifiable in both directions: it fails if the
    canonical gap becomes non-zero, and the sibling witness test fails if the
    exact solver stops beating greedy anywhere.
    """
    exact = allocate_lures(ALLOC_TARGETS, ALLOC_BUDGET, ALLOC_LURE_STRENGTH)
    greedy = greedy_allocate(ALLOC_TARGETS, ALLOC_BUDGET, ALLOC_LURE_STRENGTH)
    assert exact.expected_value == pytest.approx(greedy.expected_value, abs=1e-12)
    assert greedy.budget_used <= ALLOC_BUDGET


def test_allocation_lure_strength_validation() -> None:
    with pytest.raises(ValueError):
        allocate_lures(ALLOC_TARGETS, 5, 1.5)
    with pytest.raises(ValueError):
        greedy_allocate(ALLOC_TARGETS, 5, -0.1)


def test_canonical_allocation_non_trivial() -> None:
    result = allocate_lures(ALLOC_TARGETS, ALLOC_BUDGET, ALLOC_LURE_STRENGTH)
    assert result.chosen  # non-empty: budget is put to work
    assert result.expected_value > 0.0
