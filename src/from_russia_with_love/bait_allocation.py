"""LURES bait allocation — lure-budget optimisation for entrapment ops.

Given a fixed pool of analytical targets (each with a susceptibility and an
operational value) and a limited lure budget, decide *which* targets get a
lure. This is a deterministic **0/1 knapsack** over expected engagement
value:

    profit_i = value_i * p(q, s_i)

where ``p(q, s)`` is the logistic bite probability from the entrapment
engine, ``q`` is the lure strength of the campaign, and each target consumes
``lure_cost_i`` units of the (integer) budget.

The module provides:

* :class:`Target` — a frozen analytical target record.
* :class:`AllocationResult` — chosen targets, budget used, expected value.
* :func:`bite_value` — the knapsack profit of one target under a lure.
* :func:`allocate_lures` — exact 0/1 knapsack dynamic program (optimal).
* :func:`greedy_allocate` — the profit/weight greedy heuristic (baseline).

Deterministic: no randomness anywhere; ties break by insertion order so the
same input always yields the same allocation.
"""

from __future__ import annotations

from dataclasses import dataclass

from from_russia_with_love.entrapment_engine import bait_bite_probability

__all__ = [
    "AllocationResult",
    "Target",
    "allocate_lures",
    "bite_value",
    "greedy_allocate",
    "validate_targets",
]


@dataclass(frozen=True)
class Target:
    """An analytical target for a lure campaign."""

    target_id: str
    susceptibility: float  # 0..1 openness of the target
    value: float  # > 0 operational value if engaged
    lure_cost: int = 1  # >= 1 budget units consumed by luring this target

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id must be a non-empty string")
        if not (0.0 <= self.susceptibility <= 1.0):
            raise ValueError("susceptibility must be in [0, 1]")
        if self.value <= 0.0:
            raise ValueError("value must be positive")
        if self.lure_cost < 1:
            raise ValueError("lure_cost must be >= 1")


@dataclass(frozen=True)
class AllocationResult:
    """The outcome of a lure-budget allocation."""

    chosen: tuple[Target, ...]
    budget_used: int
    expected_value: float
    total_targets: int
    total_budget: int


def validate_targets(targets: tuple[Target, ...], budget: int) -> None:
    """Shared argument validation for the allocation solvers."""
    if budget < 0:
        raise ValueError("budget must be >= 0")
    if not isinstance(targets, tuple):
        raise TypeError("targets must be a tuple of Target records")


def bite_value(target: Target, lure_strength: float) -> float:
    """Expected engagement value of luring ``target`` with strength ``q``."""
    if not isinstance(target, Target):
        raise TypeError("target must be a Target record")
    return float(
        target.value * bait_bite_probability(lure_strength, target.susceptibility)
    )


def allocate_lures(
    targets: tuple[Target, ...],
    budget: int,
    lure_strength: float,
) -> AllocationResult:
    """Exact 0/1 knapsack: max expected value under the lure budget.

    Uses the classic dynamic program over items and budget capacity
    (``dp[c]`` = best value with capacity ``c``), back-tracing to recover the
    chosen set. Ties break by insertion order (deterministic). Weights are
    integer lure costs; profits are the float ``bite_value``.
    """
    validate_targets(targets, budget)
    if not (0.0 <= lure_strength <= 1.0):
        raise ValueError("lure_strength must be in [0, 1]")

    profits = [bite_value(t, lure_strength) for t in targets]
    costs = [t.lure_cost for t in targets]

    # dp[c] = (best_value, chosen_mask) for capacity c; masks keep ties stable.
    dp_value: list[float] = [0.0] * (budget + 1)
    dp_choice: list[tuple[int, ...]] = [()] * (budget + 1)
    for index, (profit, cost) in enumerate(zip(profits, costs, strict=True)):
        if cost > budget:
            continue
        for capacity in range(budget, cost - 1, -1):
            candidate = dp_value[capacity - cost] + profit
            if candidate > dp_value[capacity] + 1e-12:
                dp_value[capacity] = candidate
                dp_choice[capacity] = dp_choice[capacity - cost] + (index,)

    chosen_indices = dp_choice[budget]
    chosen = tuple(targets[i] for i in chosen_indices)
    budget_used = sum(targets[i].lure_cost for i in chosen_indices)
    return AllocationResult(
        chosen=chosen,
        budget_used=budget_used,
        expected_value=dp_value[budget],
        total_targets=len(targets),
        total_budget=budget,
    )


def greedy_allocate(
    targets: tuple[Target, ...],
    budget: int,
    lure_strength: float,
) -> AllocationResult:
    """Profit/weight greedy heuristic — the naive baseline for comparison.

    Sorts by ``bite_value / lure_cost`` descending (ties by insertion order)
    and takes each target while budget remains. Never better than the exact
    solver: ``exact.expected_value >= greedy.expected_value`` always holds.
    """
    validate_targets(targets, budget)
    if not (0.0 <= lure_strength <= 1.0):
        raise ValueError("lure_strength must be in [0, 1]")

    ranked = sorted(
        targets,
        key=lambda t: (
            bite_value(t, lure_strength) / float(t.lure_cost),
            -_index(targets, t),
        ),
        reverse=True,
    )
    remaining = budget
    chosen: list[Target] = []
    for target in ranked:
        if target.lure_cost <= remaining:
            chosen.append(target)
            remaining -= target.lure_cost
    return AllocationResult(
        chosen=tuple(chosen),
        budget_used=budget - remaining,
        expected_value=sum(bite_value(t, lure_strength) for t in chosen),
        total_targets=len(targets),
        total_budget=budget,
    )


def _index(targets: tuple[Target, ...], target: Target) -> int:
    """Insertion index of ``target`` (stable tie-break key)."""
    for position, candidate in enumerate(targets):
        if candidate is target:
            return position
    return len(targets)
