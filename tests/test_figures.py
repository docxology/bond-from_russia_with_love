"""Tests for the LURE-surface and TDOA-geometry figure generators."""

from __future__ import annotations

from pathlib import Path

from from_russia_with_love.figures.lure_surface import plot_lure_surface
from from_russia_with_love.figures.tdoa_geometry import plot_tdoa_geometry


def test_plot_lure_surface_writes_png(tmp_path: Path) -> None:
    out = tmp_path / "lure_surface.png"
    returned = plot_lure_surface(out, seed=11)
    assert returned == out
    assert out.exists()
    assert out.stat().st_size > 0
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_plot_lure_surface_deterministic(tmp_path: Path) -> None:
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    plot_lure_surface(a, seed=11)
    plot_lure_surface(b, seed=11)
    assert a.read_bytes() == b.read_bytes()


def test_plot_tdoa_geometry_writes_png(tmp_path: Path) -> None:
    out = tmp_path / "tdoa_geometry.png"
    returned = plot_tdoa_geometry(out)
    assert returned == out
    assert out.exists()
    assert out.stat().st_size > 0
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_plot_tdoa_geometry_deterministic(tmp_path: Path) -> None:
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    plot_tdoa_geometry(a)
    plot_tdoa_geometry(b)
    assert a.read_bytes() == b.read_bytes()
