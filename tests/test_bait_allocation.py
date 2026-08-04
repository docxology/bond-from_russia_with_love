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
    # Capacity 5; greedily-picked B(7,c3) blocks A(10,c5); optimal is A alone.
    targets = (
        Target("A", susceptibility=1.0, value=10.0, lure_cost=5),
        Target("B", susceptibility=1.0, value=7.0, lure_cost=3),
        Target("C", susceptibility=1.0, value=6.0, lure_cost=3),
    )
    exact = allocate_lures(targets, 5, 0.5)
    greedy = greedy_allocate(targets, 5, 0.5)
    assert greedy.expected_value < exact.expected_value
    assert exact.chosen[0].target_id == "A"
    assert exact.budget_used == 5


def test_greedy_never_beats_exact_canonical() -> None:
    exact = allocate_lures(ALLOC_TARGETS, ALLOC_BUDGET, ALLOC_LURE_STRENGTH)
    greedy = greedy_allocate(ALLOC_TARGETS, ALLOC_BUDGET, ALLOC_LURE_STRENGTH)
    assert exact.expected_value >= greedy.expected_value - 1e-12
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
