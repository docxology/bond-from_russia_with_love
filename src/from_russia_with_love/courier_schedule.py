"""LURES courier schedule — handoff rendezvous planning.

Plans a deterministic sequence of defector-handoff rendezvous within fixed
time windows. Each rendezvous occupies ``duration`` somewhere inside a window
``[earliest, latest]``, and a courier can attend at most one rendezvous at a
time. Maximising the number of completed meets is therefore the single-machine
throughput problem with release times and deadlines, written
``1 | r_j, d_j | sum U_j`` in the standard scheduling taxonomy. That problem is
strongly NP-hard (Garey & Johnson 1979, problem SS1), so this module ships
**two** solvers and reports the gap between them rather than claiming one
number is simultaneously cheap and optimal:

* :func:`schedule_handoffs` — the **earliest-deadline-first greedy heuristic**.
  Windows are ordered by latest feasible start (``latest - duration``) and each
  is taken when it still fits after the courier's current position. Linear
  after the sort, deterministic, and the plan the mission actually executes —
  but *not* optimal in general (see :func:`max_completed_handoffs` and the
  counterexample pinned in ``tests/test_courier_schedule.py``).
* :func:`max_completed_handoffs` — the **exact optimum**, by dynamic
  programming over subsets, recording for each subset the earliest time at
  which exactly that set of meets can all be completed. Exponential in the
  number of rendezvous, so it is bounded to small instances and used as the
  honest reference the heuristic is scored against.

This mirrors the exact-versus-greedy pairing in
:mod:`~from_russia_with_love.bait_allocation`: the manuscript reports both the
heuristic result and the true optimum, so the cost of the heuristic is measured
rather than asserted away.

Concepts
--------
* :class:`Rendezvous` — a frozen meet window with a fixed duration.
* :func:`is_compatible` — can a rendezvous still start at or after a position?
* :func:`schedule_handoffs` — earliest-deadline-first greedy schedule.
* :func:`max_completed_handoffs` — exact maximum number of completed meets.
* :class:`ScheduleResult` — scheduled / unscheduled sets and the final time.

Deterministic: no randomness anywhere; ties break by insertion order.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "MAX_EXACT_RENDEZVOUS",
    "Rendezvous",
    "ScheduleResult",
    "is_compatible",
    "max_completed_handoffs",
    "schedule_handoffs",
]

#: Upper bound on instance size accepted by the exponential exact solver.
MAX_EXACT_RENDEZVOUS = 20


@dataclass(frozen=True)
class Rendezvous:
    """A defector-handoff meet: a window and a fixed duration."""

    name: str
    earliest: float
    latest: float
    duration: float

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if self.duration <= 0.0:
            raise ValueError("duration must be positive")
        if self.latest < self.earliest:
            raise ValueError("latest must be >= earliest")
        if self.duration > self.latest - self.earliest:
            raise ValueError("duration must fit inside the window")


@dataclass(frozen=True)
class ScheduleResult:
    """The outcome of handoff-window scheduling."""

    scheduled: tuple[Rendezvous, ...]
    unscheduled: tuple[Rendezvous, ...]
    finish_time: float
    scheduled_count: int


def is_compatible(rendezvous: Rendezvous, position: float) -> bool:
    """True when ``rendezvous`` can still start at or after ``position``."""
    return position <= rendezvous.latest - rendezvous.duration


def _latest_start(rendezvous: Rendezvous) -> float:
    """The last instant at which ``rendezvous`` can begin and still finish."""
    return rendezvous.latest - rendezvous.duration


def schedule_handoffs(
    rendezvous: tuple[Rendezvous, ...],
    start_time: float = 0.0,
) -> ScheduleResult:
    """Schedule handoffs by the earliest-deadline-first greedy heuristic.

    Windows are considered in order of latest feasible start
    (``latest - duration``, ties by insertion order); the courier takes every
    rendezvous that still fits at the current position and advances its
    position to that rendezvous' finish.

    This is a **heuristic**, not an optimal solver: maximising completed meets
    under release times and deadlines is NP-hard, and this ordering can be
    beaten (a long, slack window sorted first can crowd out two short ones).
    Use :func:`max_completed_handoffs` for the true optimum on small instances.

    Bookkeeping is positional, so value-identical rendezvous records stay
    individually addressable: ``scheduled_count + len(unscheduled)`` always
    equals ``len(rendezvous)``.
    """
    if not isinstance(rendezvous, tuple):
        raise TypeError("rendezvous must be a tuple of Rendezvous records")

    # Sort *indices*, never the records themselves, so that two rendezvous with
    # identical field values are not collapsed by dataclass value-equality.
    order = sorted(
        range(len(rendezvous)), key=lambda i: (_latest_start(rendezvous[i]), i)
    )
    position = float(start_time)
    chosen_indices: list[int] = []
    for index in order:
        item = rendezvous[index]
        if is_compatible(item, position):
            position = max(position, item.earliest) + item.duration
            chosen_indices.append(index)

    chosen = set(chosen_indices)
    return ScheduleResult(
        scheduled=tuple(rendezvous[i] for i in chosen_indices),
        unscheduled=tuple(r for i, r in enumerate(rendezvous) if i not in chosen),
        finish_time=position,
        scheduled_count=len(chosen_indices),
    )


def max_completed_handoffs(
    rendezvous: tuple[Rendezvous, ...],
    start_time: float = 0.0,
) -> int:
    """Exact maximum number of rendezvous completable from ``start_time``.

    Dynamic program over subsets: ``best[mask]`` is the earliest time by which
    every meet in ``mask`` can have been completed, or ``None`` when that
    subset is infeasible. Feasibility of any extension is monotone in the
    current time, so keeping only the earliest completion time per subset is
    lossless and the result is the true optimum rather than a bound.

    Runs in ``O(2^n * n)``; raises ``ValueError`` above
    :data:`MAX_EXACT_RENDEZVOUS` rather than hanging on a large instance.
    """
    if not isinstance(rendezvous, tuple):
        raise TypeError("rendezvous must be a tuple of Rendezvous records")
    count = len(rendezvous)
    if count > MAX_EXACT_RENDEZVOUS:
        raise ValueError(
            f"exact solver is bounded to {MAX_EXACT_RENDEZVOUS} rendezvous, got {count}"
        )
    if count == 0:
        return 0

    best: list[float | None] = [None] * (1 << count)
    best[0] = float(start_time)
    optimum = 0
    for mask in range(1 << count):
        current = best[mask]
        if current is None:
            continue
        optimum = max(optimum, bin(mask).count("1"))
        for index in range(count):
            bit = 1 << index
            if mask & bit:
                continue
            item = rendezvous[index]
            start = max(current, item.earliest)
            if start > _latest_start(item):
                continue
            finish = start + item.duration
            successor = best[mask | bit]
            if successor is None or finish < successor:
                best[mask | bit] = finish
    return optimum
