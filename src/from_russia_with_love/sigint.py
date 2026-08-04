"""LURES SIGINT channel interception simulation.

Models the interception of an encoded radio channel in a deterministic,
analytical way (mission theme: From Russia with Love, 1963). The pipeline is
real, revisable math — no magic:

1. **Encode** — a plaintext message is scrambled into a stream of symbol
   magnitudes in ``[0, 256)`` by layering a seeded XOR keystream cipher one
   or more times (:func:`encipher`).
2. **Capture** — the transmitted symbols are observed through additive
   Gaussian noise whose variance follows a requested signal-to-noise ratio
   (:func:`capture_with_noise`).
3. **Decide** — each noisy sample is rounded to the nearest symbol
   magnitude (:func:`decide_symbols`).
4. **Decipher** — the recovered symbols are XOR-decrypted in reverse cipher
   order to recover the original message (:func:`decipher`).
5. **Analyse** — the interceptor measures the empirical SNR and traffic
   profile of the intercepted channel (:func:`measure_snr_db`,
   :func:`traffic_profile`) to support further analysis.

All randomness is seeded and explicit; the same plaintext/key/seed/SNR always
yields the same recovered message, and a zero-seed path makes capture
noise-free for exact round-trips.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import numpy as np

__all__ = [
    "CipherLayer",
    "capture_with_noise",
    "decide_symbols",
    "decipher",
    "encode_symbols",
    "encipher",
    "derive_keystream",
    "intercept_channel",
    "measure_snr_db",
    "segment_bursts",
    "symbols_to_bytes",
    "traffic_profile",
    "bytes_to_symbols",
]

#: Symbol alphabet width — one byte, magnitudes in [0, 256).
_SYMBOL_WIDTH = 256
_DEFAULT_SEED = 0


def bytes_to_symbols(data: bytes) -> np.ndarray:
    """Convert ``bytes`` to an integer symbol array of magnitudes in [0,256)."""
    return np.frombuffer(data, dtype=np.uint8).astype(np.int64)


def symbols_to_bytes(symbols: np.ndarray | list[int]) -> bytes:
    """Convert an integer symbol array back to ``bytes`` (values in [0,256))."""
    arr = np.asarray(symbols, dtype=np.int64)
    if not np.all((arr >= 0) & (arr < _SYMBOL_WIDTH)):
        raise ValueError(f"symbol values must lie in [0, {_SYMBOL_WIDTH})")
    return bytes(int(v) for v in arr.tolist())


def derive_keystream(key: bytes, length: int, seed: int = _DEFAULT_SEED) -> np.ndarray:
    """Derive a deterministic keystream of symbol magnitudes.

    A byte-for-byte XOR stream is produced from a PRNG seeded jointly from
    ``key`` and ``seed``, so the same (key, seed, length) always yields the
    identical keystream.
    """
    if length < 0:
        raise ValueError("length must be >= 0")
    folded = (seed * 0x9E3779B1) & 0xFFFFFFFF
    for char in key:
        folded = (folded * 31 + char) & 0xFFFFFFFF
    rng = random.Random(folded)
    return np.array(
        [rng.randrange(_SYMBOL_WIDTH) for _ in range(length)], dtype=np.int64
    )


def encipher(data: bytes, layers: tuple[CipherLayer, ...]) -> bytes:
    """Layered XOR encryption of ``data`` by applying each layer in order."""
    result = bytes(data)
    for layer in layers:
        if layer.key is None:
            raise ValueError("a cipher layer must declare a key")
        keystream = derive_keystream(layer.key, len(result), layer.seed)
        result = bytes(
            b ^ int(k) % _SYMBOL_WIDTH for b, k in zip(result, keystream, strict=True)
        )
    return result


def decipher(data: bytes, layers: tuple[CipherLayer, ...]) -> bytes:
    """Layered XOR decryption — reverse the layers of :func:`encipher`."""
    result = bytes(data)
    for layer in reversed(layers):
        if layer.key is None:
            raise ValueError("a cipher layer must declare a key")
        keystream = derive_keystream(layer.key, len(result), layer.seed)
        result = bytes(
            b ^ int(k) % _SYMBOL_WIDTH for b, k in zip(result, keystream, strict=True)
        )
    return result


def encode_symbols(
    data: bytes, layers: tuple[CipherLayer, ...] | None = None
) -> np.ndarray:
    """Express a plaintext message as transmitted symbol magnitudes."""
    payload = encipher(data, layers) if layers else data
    return bytes_to_symbols(payload)


def capture_with_noise(
    symbols: np.ndarray,
    *,
    snr_db: float,
    seed: int = _DEFAULT_SEED,
) -> np.ndarray:
    """Observe transmitted ``symbols`` through additive Gaussian noise.

    Noise variance is derived from ``snr_db`` (higher SNR ⇒ less noise).
    With ``seed == 0`` the noise is exactly zero, making capture lossless.
    """
    if snr_db < -40 or snr_db > 120:
        raise ValueError("snr_db must be in [-40, 120]")
    if seed == 0:
        return np.asarray(symbols, dtype=np.float64).copy()
    folded = (seed * 0x9E3779B1) & 0xFFFFFFFF
    rng = np.random.default_rng(folded)
    signal = np.asarray(symbols, dtype=np.float64)
    signal_power = float(np.mean(signal**2)) if signal.size else 0.0
    # noise power = signal power / linear SNR
    linear = 10.0 ** (snr_db / 10.0)
    noise_std = math.sqrt(max(signal_power / linear, 0.0)) if signal_power > 0 else 0.0
    noise = rng.normal(0.0, noise_std, size=signal.shape)
    return signal + noise


def decide_symbols(samples: np.ndarray) -> np.ndarray:
    """Round each noisy sample to the nearest valid symbol magnitude."""
    arr = np.asarray(samples, dtype=np.float64)
    decided = np.clip(np.rint(arr).astype(np.int64), 0, _SYMBOL_WIDTH - 1)
    return decided


def measure_snr_db(samples: np.ndarray, true_symbols: np.ndarray) -> float:
    """Estimate the empirical SNR (dB) of captured samples vs. ground truth.

    Signal power is the mean-square of the true symbols; noise power is the
    mean-square of the residual. A noise-free capture yields ``+inf`` dB.
    """
    samples_a = np.asarray(samples, dtype=np.float64)
    true_a = np.asarray(true_symbols, dtype=np.float64)
    if samples_a.size == 0:
        raise ValueError("cannot measure SNR of an empty capture")
    noise = samples_a - true_a
    signal_power = float(np.mean(true_a**2))
    noise_power = float(np.mean(noise**2))
    if noise_power == 0.0:
        return float("inf")
    return 10.0 * math.log10(max(signal_power / noise_power, 1e-12))


@dataclass(frozen=True)
class CipherLayer:
    """One encryption layer: an XOR key and the seed of its keystream."""

    key: bytes | None = None
    seed: int = _DEFAULT_SEED


def traffic_profile(symbols: np.ndarray) -> dict[str, object]:
    """Summarise the intercepted traffic channel (analysis support).

    Reports channel width (distinct symbol values), total length, and the
    most frequently occurring symbol — a cheap, deterministic traffic
    fingerprint for downstream triage.
    """
    arr = np.asarray(symbols, dtype=np.int64)
    if arr.size == 0:
        raise ValueError("cannot profile empty traffic")
    counts = np.bincount(arr, minlength=_SYMBOL_WIDTH)
    top_index = int(np.argmax(counts))
    return {
        "length": int(arr.size),
        "distinct_symbols": int(np.count_nonzero(counts)),
        "peak_symbol": top_index,
        "peak_frequency": int(counts[top_index]),
    }


def segment_bursts(
    envelope: np.ndarray,
    threshold: float,
    min_gap: int = 0,
) -> tuple[tuple[int, int], ...]:
    """Segment an energy envelope into transmission bursts.

    A sample belongs to a burst when ``envelope > threshold``; bursts are
    emitted as half-open index ranges ``(start, end)``. Two bursts separated
    by at most ``min_gap`` silent samples are merged into one (fading
    tolerance). Deterministic; returns an empty tuple for an all-quiet
    envelope.
    """
    arr = np.asarray(envelope, dtype=np.float64)
    if arr.size == 0:
        raise ValueError("cannot segment an empty envelope")
    active = arr > threshold
    bursts: list[tuple[int, int]] = []
    start: int | None = None
    silence = 0
    for index, is_active in enumerate(active.tolist()):
        if is_active:
            if start is None:
                start = index
            silence = 0
        elif start is not None:
            silence += 1
            if silence > min_gap:
                bursts.append((start, index - min_gap))
                start = None
                silence = 0
    if start is not None:
        bursts.append((start, len(arr)))
    return tuple(bursts)


def intercept_channel(
    plaintext: str,
    layers: tuple[CipherLayer, ...],
    *,
    snr_db: float,
    seed: int = _DEFAULT_SEED,
) -> dict[str, object]:
    """Run the full interception pipeline and report the recovered message.

    Deterministic end-to-end: encodes ``plaintext`` under ``layers``,
    captures it through noise at ``snr_db``, decides the symbols, deciphers,
    and measures the empirical SNR and traffic profile.
    """
    data = plaintext.encode("utf-8")
    transmitted = encode_symbols(data, layers)
    captured = capture_with_noise(transmitted, snr_db=snr_db, seed=seed)
    decided = decide_symbols(captured)
    recovered_bytes = symbols_to_bytes(decided)
    recovered = decipher(recovered_bytes, layers)
    return {
        "transmitted_symbols": transmitted.tolist(),
        "captured_samples": captured.tolist(),
        "decided_symbols": decided.tolist(),
        "recovered_plaintext": recovered.decode("utf-8", errors="replace"),
        "empirical_snr_db": measure_snr_db(captured, transmitted),
        "traffic": traffic_profile(decided),
        "recovered_exact": recovered == data,
    }
