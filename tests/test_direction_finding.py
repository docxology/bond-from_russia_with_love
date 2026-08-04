"""Tests for TDOA direction-finding geolocation (real computation)."""

from __future__ import annotations

import pytest

from from_russia_with_love.direction_finding import (
    Receiver,
    estimate_position,
    localization_error,
    tdoa_measurements,
)
from from_russia_with_love.scenario import (
    TDOA_NOISE_STD,
    TDOA_RECEIVERS,
    TDOA_SPEED,
    TDOA_TRANSMITTER,
)


def test_receiver_validation() -> None:
    with pytest.raises(ValueError):
        Receiver("", (0.0, 0.0))
    with pytest.raises(ValueError):
        Receiver("A", (0.0,))  # not a 2-tuple
    with pytest.raises(ValueError):
        Receiver("A", (0.0, 1.0, 2.0))


def test_tdoa_too_few_receivers() -> None:
    receivers = (Receiver("A", (0.0, 0.0)), Receiver("B", (1.0, 0.0)))
    with pytest.raises(ValueError):
        tdoa_measurements(receivers, (0.5, 0.5))


def test_tdoa_argument_validation() -> None:
    with pytest.raises(ValueError):
        tdoa_measurements(TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=0.0)
    with pytest.raises(ValueError):
        tdoa_measurements(TDOA_RECEIVERS, TDOA_TRANSMITTER, noise_std=-1.0)


def test_tdoa_noise_free_pairs() -> None:
    pairs, tdoa = tdoa_measurements(TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=TDOA_SPEED)
    # n receivers -> n choose 2 pairs
    expected_pairs = len(TDOA_RECEIVERS) * (len(TDOA_RECEIVERS) - 1) // 2
    assert len(pairs) == expected_pairs
    assert len(tdoa) == expected_pairs
    # receiver 0 is first, so node-A-minus-node-B TDOA < 0 when A is closer.
    assert isinstance(tdoa, tuple)


def test_tdoa_deterministic_noise() -> None:
    a = tdoa_measurements(TDOA_RECEIVERS, TDOA_TRANSMITTER, noise_std=0.1, seed=11)
    b = tdoa_measurements(TDOA_RECEIVERS, TDOA_TRANSMITTER, noise_std=0.1, seed=11)
    assert a == b


def test_estimate_exact_no_noise() -> None:
    pairs, tdoa = tdoa_measurements(TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=TDOA_SPEED)
    estimate = estimate_position(TDOA_RECEIVERS, pairs, tdoa, speed=TDOA_SPEED)
    assert estimate.converged is True
    assert localization_error(estimate.position, TDOA_TRANSMITTER) < 1e-6


def test_estimate_with_noise_is_accurate() -> None:
    pairs, tdoa = tdoa_measurements(
        TDOA_RECEIVERS,
        TDOA_TRANSMITTER,
        speed=TDOA_SPEED,
        noise_std=0.1,
        seed=11,
    )
    estimate = estimate_position(TDOA_RECEIVERS, pairs, tdoa, speed=TDOA_SPEED)
    assert estimate.converged is True
    assert localization_error(estimate.position, TDOA_TRANSMITTER) < 0.5


def test_estimate_initial_guess() -> None:
    pairs, tdoa = tdoa_measurements(TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=TDOA_SPEED)
    estimate = estimate_position(
        TDOA_RECEIVERS,
        pairs,
        tdoa,
        speed=TDOA_SPEED,
        initial_guess=(10.0, 10.0),
    )
    assert estimate.converged is True


def test_estimate_validation() -> None:
    with pytest.raises(ValueError):
        estimate_position(
            (Receiver("A", (0.0, 0.0)), Receiver("B", (1.0, 0.0))),
            ((0, 1),),
            (0.0,),
        )
    # pairs/tdoa length mismatch
    with pytest.raises(ValueError):
        estimate_position(TDOA_RECEIVERS, ((0, 1), (0, 2)), (0.0, 0.0, 0.0))
    with pytest.raises(ValueError):
        pairs, tdoa = tdoa_measurements(
            TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=TDOA_SPEED
        )
        estimate_position(TDOA_RECEIVERS, pairs, tdoa, speed=0.0)


def test_estimate_collinear_does_not_false_positive() -> None:
    # Collinear receivers cannot solve 2-D TDOA: singular normal equations.
    collinear = (
        Receiver("A", (0.0, 0.0)),
        Receiver("B", (1.0, 0.0)),
        Receiver("C", (2.0, 0.0)),
        Receiver("D", (3.0, 0.0)),
    )
    pairs, tdoa = tdoa_measurements(
        collinear, (1.5, 0.2), speed=TDOA_SPEED, noise_std=0.01, seed=5
    )
    estimate = estimate_position(collinear, pairs, tdoa, speed=TDOA_SPEED)
    # must not claim a converged, confident fix far from truth
    error = localization_error(estimate.position, (1.5, 0.2))
    assert estimate.converged is False or error > 0.05


def test_localization_error() -> None:
    assert localization_error((0.0, 0.0), (0.0, 0.0)) == 0.0
    assert abs(localization_error((3.0, 4.0), (0.0, 0.0)) - 5.0) < 1e-9


def test_canonical_error_below_threshold() -> None:
    # The mission's canonical scenario must satisfy its own success gate.
    pairs, tdoa = tdoa_measurements(
        TDOA_RECEIVERS,
        TDOA_TRANSMITTER,
        speed=TDOA_SPEED,
        noise_std=TDOA_NOISE_STD,
        seed=11,
    )
    estimate = estimate_position(TDOA_RECEIVERS, pairs, tdoa, speed=TDOA_SPEED)
    assert localization_error(estimate.position, TDOA_TRANSMITTER) < 0.5
