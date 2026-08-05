"""Regeneration determinism: the byte-for-byte claim in §6, bound to a test.

The manuscript claims that regenerating the artifacts reproduces them
byte-for-byte. This module is the gate that makes that claim falsifiable.

Why it is written this way. The previous determinism test compared two calls to
``generate_variables(..., now=FIXED)`` — it injected a fixed clock, so it was
green while the real generator stamped ``datetime.now()`` into
``manuscript_variables.json`` and into the manuscript's own date row. Every
regeneration produced different bytes and no test noticed. So this module
injects nothing: it runs the real entry point,
``scripts/z_generate_manuscript_variables.py``, twice as a subprocess, and
compares the SHA-256 of every persisted artifact.

Proven able to fail: re-introducing a wall-clock value into
``generate_variables`` (e.g. ``"STAMP": datetime.now(timezone.utc).isoformat()``)
turns ``test_regeneration_is_byte_identical`` red, and re-introducing the
``datetime.now`` call itself also turns ``test_no_wall_clock_read_under_src``
red.
"""

from __future__ import annotations

import ast
import hashlib
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = PROJECT_ROOT / "scripts" / "z_generate_manuscript_variables.py"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Calls that would make a persisted artifact depend on when it was produced.
_CLOCK_CALLS = {
    ("datetime", "now"),
    ("datetime", "utcnow"),
    ("date", "today"),
    ("time", "time"),
    ("time", "time_ns"),
    ("time", "monotonic"),
}


def _run_generator() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def _artifact_digests() -> dict[str, str]:
    """SHA-256 of every persisted artifact, keyed by path relative to output/."""
    digests = {
        str(path.relative_to(OUTPUT_DIR)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUTPUT_DIR.rglob("*"))
        if path.is_file()
    }
    assert digests, "no artifacts found — the comparison would be vacuous"
    return digests


def test_regeneration_is_byte_identical() -> None:
    """Run the real generator twice; every persisted byte must match.

    This is the manuscript's §6 reproducibility claim, executed. No clock is
    injected and no value is stubbed — if any artifact depends on the wall
    clock, on iteration order, or on any other unpinned input, the digests
    diverge and this fails.
    """
    _run_generator()
    first = _artifact_digests()
    _run_generator()
    second = _artifact_digests()

    assert sorted(first) == sorted(second), "the artifact set itself changed"
    differing = sorted(name for name in first if first[name] != second[name])
    assert not differing, (
        "regeneration is not byte-identical; these artifacts changed between "
        f"two runs of {GENERATOR.name}: {differing}. The manuscript claims "
        "byte-for-byte reproducibility, so either the non-determinism or the "
        "claim has to go."
    )


def test_the_generated_token_map_is_covered_by_the_comparison() -> None:
    """Guard against the comparison quietly stopping at the figures.

    ``manuscript_variables.json`` is the artifact the manuscript prose is
    hydrated from, so it is the one that must be in scope. Without this the
    byte-comparison could pass over an empty or figure-only artifact set.
    """
    _run_generator()
    digests = _artifact_digests()
    assert "data/manuscript_variables.json" in digests
    assert any(name.endswith(".png") for name in digests)


def test_no_wall_clock_read_under_src() -> None:
    """Positive control: no module under ``src/`` may read the clock.

    Parsed with ``ast`` rather than grepped, so a mention inside a docstring or
    a comment (this file's own prose, for instance) is not a false positive.
    """
    offenders: list[str] = []
    modules = sorted((PROJECT_ROOT / "src").rglob("*.py"))
    assert modules, "no source modules found — the scan would be vacuous"
    for module in modules:
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not isinstance(func, ast.Attribute):
                continue
            owner = func.value
            owner_name = owner.attr if isinstance(owner, ast.Attribute) else None
            if isinstance(owner, ast.Name):
                owner_name = owner.id
            if (owner_name, func.attr) in _CLOCK_CALLS:
                relative = module.relative_to(PROJECT_ROOT)
                offenders.append(f"{relative}:{node.lineno} {owner_name}.{func.attr}()")
    assert not offenders, (
        "wall-clock reads found in the package; persisted artifacts would stop "
        f"being byte-reproducible: {offenders}"
    )
