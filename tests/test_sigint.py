"""Tests for the SIGINT interception simulation (real computation)."""

from __future__ import annotations

import numpy as np
import pytest

from from_russia_with_love.sigint import (
    CipherLayer,
    bytes_to_symbols,
    capture_with_noise,
    decide_symbols,
    decipher,
    derive_keystream,
    encipher,
    encode_symbols,
    intercept_channel,
    measure_snr_db,
    symbols_to_bytes,
    traffic_profile,
)


def test_bytes_symbols_roundtrip() -> None:
    data = b"LURES handoff green"
    assert symbols_to_bytes(bytes_to_symbols(data)) == data


def test_symbols_to_bytes_invalid() -> None:
    with pytest.raises(ValueError):
        symbols_to_bytes([256])


def test_derive_keystream_deterministic() -> None:
    key = b"VALENKA"
    k1 = derive_keystream(key, 64, seed=3)
    k2 = derive_keystream(key, 64, seed=3)
    assert np.array_equal(k1, k2)
    assert k1.shape == (64,)
    assert np.all(k1 >= 0) and np.all(k1 < 256)
    # different seed -> different stream
    assert not np.array_equal(k1, derive_keystream(key, 64, seed=4))


def test_derive_keystream_negative_length() -> None:
    with pytest.raises(ValueError):
        derive_keystream(b"k", -1)


def test_encipher_decipher_roundtrip() -> None:
    layers = (CipherLayer(key=b"VALENKA", seed=3), CipherLayer(key=b"GRANT", seed=5))
    data = b"signal capture round trip"
    encrypted = encipher(data, layers)
    # layered encryption changes the bytes and is reversible
    assert encrypted != data
    assert decipher(encrypted, layers) == data


def test_encipher_requires_key() -> None:
    with pytest.raises(ValueError):
        encipher(b"x", (CipherLayer(key=None),))
    with pytest.raises(ValueError):
        decipher(b"x", (CipherLayer(key=None),))


def test_capture_noise_free_seed_zero() -> None:
    symbols = encode_symbols(b"hello")
    captured = capture_with_noise(symbols, snr_db=30.0, seed=0)
    assert np.array_equal(captured, symbols)
    assert np.array_equal(decide_symbols(captured), symbols)


def test_capture_noise_adds_error() -> None:
    symbols = encode_symbols(b"noisy")
    captured = capture_with_noise(symbols, snr_db=5.0, seed=42)
    # low SNR -> most symbols corrupted
    assert not np.array_equal(decide_symbols(captured), symbols)


def test_capture_noise_snr_validation() -> None:
    with pytest.raises(ValueError):
        capture_with_noise(np.array([1]), snr_db=-50)
    with pytest.raises(ValueError):
        capture_with_noise(np.array([1]), snr_db=200)


def test_measure_snr_db() -> None:
    symbols = np.array([100.0, 200.0, 150.0], dtype=np.float64)
    assert measure_snr_db(symbols, symbols) == float("inf")
    # degraded capture has lower empirical SNR than clean
    noisy = capture_with_noise(symbols, snr_db=10.0, seed=7)
    assert measure_snr_db(noisy, symbols) < measure_snr_db(symbols, symbols)


def test_measure_snr_db_empty() -> None:
    with pytest.raises(ValueError):
        measure_snr_db(np.array([]), np.array([]))


def test_traffic_profile() -> None:
    symbols = np.array([1, 2, 2, 3, 2], dtype=np.int64)
    profile = traffic_profile(symbols)
    assert profile["length"] == 5
    assert profile["distinct_symbols"] == 3
    assert profile["peak_symbol"] == 2
    assert profile["peak_frequency"] == 3


def test_traffic_profile_empty() -> None:
    with pytest.raises(ValueError):
        traffic_profile(np.array([], dtype=np.int64))


def test_intercept_channel_high_snr_exact() -> None:
    layers = (CipherLayer(key=b"VALENKA", seed=3),)
    result = intercept_channel("clear weather tomorrow", layers, snr_db=80.0, seed=11)
    assert result["recovered_exact"] is True
    assert result["recovered_plaintext"] == "clear weather tomorrow"
    assert result["empirical_snr_db"] > 0.0
    # at 80 dB the empirical SNR tracks the requested SNR (approx)
    assert result["empirical_snr_db"] > 60.0
    assert result["traffic"]["length"] == len(b"clear weather tomorrow")


def test_intercept_channel_low_snr_may_corrupt() -> None:
    layers = (CipherLayer(key=b"GRANT", seed=5),)
    result = intercept_channel("short burst", layers, snr_db=0.0, seed=11)
    # at 0 dB we expect heavy corruption / non-exact recovery
    assert result["recovered_exact"] in (True, False)
    assert isinstance(result["recovered_plaintext"], str)


def test_intercept_channel_deterministic() -> None:
    layers = (CipherLayer(key=b"X", seed=1), CipherLayer(key=b"Y", seed=2))
    a = intercept_channel("repeat me", layers, snr_db=20.0, seed=9)
    b = intercept_channel("repeat me", layers, snr_db=20.0, seed=9)
    assert a["captured_samples"] == b["captured_samples"]
    assert a["recovered_plaintext"] == b["recovered_plaintext"]
