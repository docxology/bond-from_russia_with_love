"""LURES direction finding — TDOA transmitter geolocation.

A deterministic **time-difference-of-arrival (TDOA)** localisation engine:
several fixed receivers record the arrival time of a single intercepted burst
from an unknown transmitter, and a **Gauss–Newton non-linear least-squares**
solver estimates the transmitter position by minimising

    f(x) = sum_ij ( (|x - r_i| - |x - r_j|) / c - tau_ij )^2

over receiver pairs ``(i, j)`` with measured time differences ``tau_ij``.
Measurement noise is seeded, so the same scenario always yields the same
estimate.

Attribution
-----------
The solver implemented here is the **iterative Taylor-series / Gauss–Newton**
estimator for hyperbolic position location (Foy 1976; Torrieri 1984), i.e. the
standard non-linear least-squares iteration applied to the TDOA residuals.
It is *not* the Chan & Ho (1994) estimator: that method is a **closed-form,
non-iterative** two-stage weighted least-squares solution, published precisely
as an alternative to the iterative scheme used here. Chan & Ho is cited in the
manuscript as related work, not as the source of this implementation.

Units
-----
Receiver and transmitter positions are plain 2-D coordinates in an abstract
scenario coordinate system; ``speed`` converts distance to time in those same
units. :func:`localization_error` therefore returns a distance in **receiver
coordinate units**, not in multiples of the receiver spacing. Use
:func:`min_site_spacing` to convert an error to units of site spacing.

Concepts
--------
* :class:`Receiver` — a fixed intercept site with a 2-D position.
* :func:`tdoa_measurements` — true range-difference TDOAs plus seeded noise.
* :func:`estimate_position` — Gauss–Newton minimisation from a centroid
  initial guess, returning the estimate and a convergence flag.
* :func:`localization_error` — Euclidean error of an estimate, in receiver
  coordinate units (determinism check target: ~0 at zero noise).
* :func:`min_site_spacing` — the smallest distance between two intercept
  sites; the scale a localisation error is meaningfully compared against.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = [
    "Position",
    "Receiver",
    "TdoaEstimate",
    "estimate_position",
    "localization_error",
    "min_site_spacing",
    "tdoa_measurements",
]

Position = tuple[float, float]

_MIN_RECEIVERS = 3  # 2-D TDOA needs at least three sites (>= 2 pairs)


@dataclass(frozen=True)
class Receiver:
    """A fixed intercept receiver site."""

    receiver_id: str
    position: Position

    def __post_init__(self) -> None:
        if not self.receiver_id.strip():
            raise ValueError("receiver_id must be a non-empty string")
        if len(self.position) != 2:
            raise ValueError("receiver position must be a 2-tuple (x, y)")


@dataclass(frozen=True)
class TdoaEstimate:
    """A Gauss–Newton localisation result."""

    position: Position
    converged: bool
    iterations: int
    residual_norm: float


def _pair_tdoa(
    transmitter: Position,
    receivers: tuple[Receiver, ...],
    speed: float,
) -> tuple[tuple[tuple[int, int], ...], tuple[float, ...]]:
    """True TDOA (s) between every ordered receiver pair, no noise."""
    distances = [
        math.hypot(transmitter[0] - r.position[0], transmitter[1] - r.position[1])
        for r in receivers
    ]
    pairs: list[tuple[int, int]] = []
    values: list[float] = []
    for i in range(len(receivers)):
        for j in range(i + 1, len(receivers)):
            pairs.append((i, j))
            values.append((distances[i] - distances[j]) / speed)
    return tuple(pairs), tuple(values)


def _validate_pair_lengths(
    pairs: tuple[tuple[int, int], ...], tdoa: tuple[float, ...]
) -> None:
    """Validate that the pair list and TDOA measurement vector agree."""
    if len(pairs) != len(tdoa):
        raise ValueError("pairs and tdoa must have the same length")


def tdoa_measurements(
    receivers: tuple[Receiver, ...],
    transmitter: Position,
    *,
    speed: float = 1.0,
    noise_std: float = 0.0,
    seed: int = 0,
) -> tuple[tuple[tuple[int, int], ...], tuple[float, ...]]:
    """Measure TDOAs of ``transmitter`` at the receivers, with seeded noise.

    ``seed == 0`` gives noise-free (exact) measurements. ``noise_std`` is the
    standard deviation of the Gaussian timing error in seconds.
    """
    if len(receivers) < _MIN_RECEIVERS:
        raise ValueError(f"at least {_MIN_RECEIVERS} receivers are required")
    if speed <= 0.0:
        raise ValueError("speed must be positive")
    if noise_std < 0.0:
        raise ValueError("noise_std must be >= 0")
    pairs, values = _pair_tdoa(transmitter, receivers, speed)
    if noise_std == 0.0:
        return pairs, values
    folded = (seed * 0x9E3779B1) & 0xFFFFFFFF
    rng = np.random.default_rng(folded)
    noisy = tuple(float(v + rng.normal(0.0, noise_std)) for v in values)
    return pairs, noisy


def estimate_position(
    receivers: tuple[Receiver, ...],
    pairs: tuple[tuple[int, int], ...],
    tdoa: tuple[float, ...],
    *,
    speed: float = 1.0,
    max_iterations: int = 30,
    tolerance: float = 1e-9,
    initial_guess: Position | None = None,
) -> TdoaEstimate:
    """Gauss–Newton least-squares estimate of the transmitter position.

    Iterates ``x <- x - (J^T J)^{-1} J^T r`` where ``r`` is the residual
    vector and ``J`` the analytic Jacobian of the pair TDOA functions.
    Stops on a step smaller than ``tolerance`` or after ``max_iterations``.
    """
    if len(receivers) < _MIN_RECEIVERS:
        raise ValueError(f"at least {_MIN_RECEIVERS} receivers are required")
    _validate_pair_lengths(pairs, tdoa)
    if speed <= 0.0:
        raise ValueError("speed must be positive")
    if initial_guess is None:
        guess = _centroid(receivers)
    else:
        guess = (float(initial_guess[0]), float(initial_guess[1]))

    x = np.array(guess, dtype=np.float64)
    residual = _residual_vector(x, receivers, pairs, tdoa, speed)
    converged = False
    iterations = 0
    for _ in range(max_iterations):
        jacobian = _jacobian(x, receivers, pairs, speed)
        try:
            step = np.linalg.solve(jacobian.T @ jacobian, jacobian.T @ residual)
        except np.linalg.LinAlgError:
            break
        if not np.all(np.isfinite(step)):
            break
        x = x - step
        iterations += 1
        residual = _residual_vector(x, receivers, pairs, tdoa, speed)
        if float(np.linalg.norm(step)) < tolerance:
            converged = True
            break

    return TdoaEstimate(
        position=(float(x[0]), float(x[1])),
        converged=converged,
        iterations=iterations,
        residual_norm=float(np.linalg.norm(residual)),
    )


def localization_error(estimate: Position, truth: Position) -> float:
    """Euclidean distance between an estimate and the true position.

    The result is in **receiver coordinate units** — the same units the
    :class:`Receiver` positions are expressed in. It is *not* normalised by
    the receiver spacing; divide by :func:`min_site_spacing` for that.
    """
    return math.hypot(estimate[0] - truth[0], estimate[1] - truth[1])


def min_site_spacing(receivers: tuple[Receiver, ...]) -> float:
    """Smallest distance between any two intercept sites (coordinate units).

    This is the natural length scale of a receiver array: a localisation error
    is only interpretable relative to how far apart the sites actually are.
    """
    if len(receivers) < 2:
        raise ValueError("at least two receivers are required for a spacing")
    return min(
        math.hypot(
            receivers[i].position[0] - receivers[j].position[0],
            receivers[i].position[1] - receivers[j].position[1],
        )
        for i in range(len(receivers))
        for j in range(i + 1, len(receivers))
    )


def _centroid(receivers: tuple[Receiver, ...]) -> Position:
    """Mean receiver position — a stable initial guess for Gauss–Newton."""
    xs = [r.position[0] for r in receivers]
    ys = [r.position[1] for r in receivers]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _residual_vector(
    x: np.ndarray,
    receivers: tuple[Receiver, ...],
    pairs: tuple[tuple[int, int], ...],
    tdoa: tuple[float, ...],
    speed: float,
) -> np.ndarray:
    """Residuals r_k = h_k(x) - tau_k for every measured pair."""
    distances = [
        math.hypot(float(x[0]) - r.position[0], float(x[1]) - r.position[1])
        for r in receivers
    ]
    residual = np.array(
        [
            (distances[i] - distances[j]) / speed - tdoa[k]
            for k, (i, j) in enumerate(pairs)
        ],
        dtype=np.float64,
    )
    return residual


def _jacobian(
    x: np.ndarray,
    receivers: tuple[Receiver, ...],
    pairs: tuple[tuple[int, int], ...],
    speed: float,
) -> np.ndarray:
    """Analytic Jacobian: d h_k / d x for each measured pair."""
    rows: list[list[float]] = []
    for i, j in pairs:
        di = math.hypot(
            float(x[0]) - receivers[i].position[0],
            float(x[1]) - receivers[i].position[1],
        )
        dj = math.hypot(
            float(x[0]) - receivers[j].position[0],
            float(x[1]) - receivers[j].position[1],
        )
        if di < 1e-12 or dj < 1e-12:
            raise ValueError(
                "receiver and transmitter coincide; TDOA gradient is singular"
            )
        row = [
            float(
                (x[0] - receivers[i].position[0]) / (speed * di)
                - (x[0] - receivers[j].position[0]) / (speed * dj)
            ),
            float(
                (x[1] - receivers[i].position[1]) / (speed * di)
                - (x[1] - receivers[j].position[1]) / (speed * dj)
            ),
        ]
        rows.append(row)
    return np.array(rows, dtype=np.float64)
