"""Tests for the LURE-surface figure generator (real matplotlib render)."""

from __future__ import annotations

from pathlib import Path

from from_russia_with_love.figures.lure_surface import plot_lure_surface


def test_plot_lure_surface_writes_png(tmp_path: Path) -> None:
    out = tmp_path / "lure_surface.png"
    returned = plot_lure_surface(out, seed=11)
    assert returned == out
    assert out.exists()
    assert out.stat().st_size > 0
    # PNG magic bytes
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_plot_lure_surface_deterministic(tmp_path: Path) -> None:
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    plot_lure_surface(a, seed=11)
    plot_lure_surface(b, seed=11)
    # byte-identical output => deterministic rendering
    assert a.read_bytes() == b.read_bytes()
