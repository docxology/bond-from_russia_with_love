"""Tests for TDOA direction-finding geolocation (real computation)."""

from __future__ import annotations

import math

import pytest

from from_russia_with_love.direction_finding import (
    Receiver,
    crlb_error,
    estimate_position,
    localization_error,
    min_site_spacing,
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


def test_min_site_spacing_is_the_smallest_pairwise_distance() -> None:
    """A site spacing is a real distance, computed from the real geometry."""
    receivers = (
        Receiver("A", (0.0, 0.0)),
        Receiver("B", (3.0, 4.0)),  # 5.0 from A
        Receiver("C", (0.0, 2.0)),  # 2.0 from A -> the minimum
    )
    assert min_site_spacing(receivers) == pytest.approx(2.0)


def test_min_site_spacing_requires_two_sites() -> None:
    with pytest.raises(ValueError, match="at least two receivers"):
        min_site_spacing((Receiver("A", (0.0, 0.0)),))


def test_canonical_site_spacing_matches_the_declared_grid() -> None:
    """The scenario's four corners span 20 units, so the spacing is 20.

    Guards the unit claim in §3.3 and §5: the localisation error is reported
    in coordinate units, and this is the divisor that converts it to site
    spacings. If the receiver array is moved, this number moves with it.
    """
    assert min_site_spacing(TDOA_RECEIVERS) == pytest.approx(20.0)


def test_localisation_error_is_not_in_site_spacings() -> None:
    """Positive control for the unit distinction the manuscript now draws.

    The raw error and the error-in-site-spacings are different numbers by a
    factor of the spacing. Asserting the factor makes the §3.3 claim
    falsifiable: if someone re-labels the raw error as "site spacings", this
    test still shows the two quantities differ by 20x.
    """
    pairs, tdoa = tdoa_measurements(
        TDOA_RECEIVERS,
        TDOA_TRANSMITTER,
        speed=TDOA_SPEED,
        noise_std=TDOA_NOISE_STD,
        seed=11,
    )
    estimate = estimate_position(TDOA_RECEIVERS, pairs, tdoa, speed=TDOA_SPEED)
    raw = localization_error(estimate.position, TDOA_TRANSMITTER)
    spacing = min_site_spacing(TDOA_RECEIVERS)
    assert raw > 0.0
    assert raw / spacing == pytest.approx(raw / 20.0)
    assert raw != pytest.approx(raw / spacing)  # the two are not the same number


def test_crlb_finite_and_positive_on_canonical() -> None:
    # The Cramér–Rao bound for the canonical array + timing noise is a finite,
    # strictly positive RMS in coordinate units.
    bound = crlb_error(
        TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=TDOA_SPEED, noise_std=0.1
    )
    assert math.isfinite(bound)
    assert bound > 0.0


def test_crlb_scales_linearly_with_noise() -> None:
    # The bound is noise_std * sqrt(trace((J^T J)^{-1})), so doubling the
    # timing noise doubles the RMS bound exactly. This is a real property of
    # the formula, not a coincidence of one draw.
    lo = crlb_error(TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=TDOA_SPEED, noise_std=0.01)
    hi = crlb_error(TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=TDOA_SPEED, noise_std=0.2)
    assert lo < hi
    assert hi / lo == pytest.approx(20.0, rel=1e-9)


def test_crlb_validation() -> None:
    with pytest.raises(ValueError):
        crlb_error(TDOA_RECEIVERS, TDOA_TRANSMITTER, speed=0.0, noise_std=0.1)
    with pytest.raises(ValueError):
        crlb_error(TDOA_RECEIVERS, TDOA_TRANSMITTER, noise_std=0.0)
    with pytest.raises(ValueError):
        crlb_error(
            (Receiver("A", (0.0, 0.0)), Receiver("B", (1.0, 0.0))),
            (0.5, 0.5),
            noise_std=0.1,
        )


def test_crlb_degenerate_geometry_is_infinite() -> None:
    # Collinear receivers with the transmitter exactly on their line make the
    # Fisher information matrix singular: no finite accuracy is achievable,
    # and the bound must say so (inf) rather than raising or returning a
    # finite "confidence".
    collinear = (
        Receiver("A", (0.0, 0.0)),
        Receiver("B", (1.0, 0.0)),
        Receiver("C", (2.0, 0.0)),
        Receiver("D", (3.0, 0.0)),
    )
    assert math.isinf(crlb_error(collinear, (1.5, 0.0), noise_std=0.1))
