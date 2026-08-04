"""LURES courier schedule — handoff rendezvous planning.

Plans a deterministic sequence of defector-handoff rendezvous within fixed
time windows. Each rendezvous occupies ``duration`` inside a window
``[earliest, latest]``; a courier can attend at most one rendezvous at a
time, so the planner solves a **weighted-by-count interval scheduling**
problem: sort the windows by latest start, then greedily take every
rendezvous that fits after the current position (the classic optimal
earliest-finish-first interval scheduling result; Kleinberg & Tardos 2005,
Chapter 4).

Concepts
--------
* :class:`Rendezvous` — a frozen meet window with a fixed duration.
* :func:`schedule_handoffs` — earliest-finish-first greedy schedule.
* :func:`is_compatible` — can a rendezvous follow the current position?
* :class:`ScheduleResult` — scheduled / unscheduled sets and the final time.

Deterministic: no randomness; ties break by insertion order.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Rendezvous",
    "ScheduleResult",
    "is_compatible",
    "schedule_handoffs",
]


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
    """True when ``rendezvous`` can start at or after ``position``."""
    return position <= rendezvous.latest - rendezvous.duration


def schedule_handoffs(
    rendezvous: tuple[Rendezvous, ...],
    start_time: float = 0.0,
) -> ScheduleResult:
    """Maximise completed handoffs by earliest-finish-first scheduling.

    Windows are considered in order of latest *start* (``latest - duration``,
    ties by insertion order); the courier takes every rendezvous that starts
    no earlier than the current position and moves its position to that
    rendezvous' finish. Optimal for maximising the number of completed meets.
    """
    if not isinstance(rendezvous, tuple):
        raise TypeError("rendezvous must be a tuple of Rendezvous records")

    def _latest_start(r: Rendezvous) -> float:
        return r.latest - r.duration

    ordered = sorted(rendezvous, key=_latest_start)
    position = float(start_time)
    scheduled: list[Rendezvous] = []
    for rendezvous_item in ordered:
        if is_compatible(rendezvous_item, position):
            start = max(position, rendezvous_item.earliest)
            position = start + rendezvous_item.duration
            scheduled.append(rendezvous_item)
    scheduled_set = set(scheduled)
    unscheduled = tuple(r for r in rendezvous if r not in scheduled_set)
    return ScheduleResult(
        scheduled=tuple(scheduled),
        unscheduled=unscheduled,
        finish_time=position,
        scheduled_count=len(scheduled),
    )
