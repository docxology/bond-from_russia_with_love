"""Tests that every copy of the package version agrees with the single source.

The package version lives in ``src/from_russia_with_love/__init__.py`` as
``__version__``; ``mission.py``'s ``_PACKAGE_VERSION`` (provenance payload),
``manuscript_variables.py``'s ``PACKAGE_VERSION``, and the manuscript's
``{{BOND_VERSION}}`` token all read it. The declarative copies
(``pyproject.toml``, ``CITATION.cff``, ``codemeta.json``, ``.zenodo.json``,
``manuscript/config.yaml``) are checked here so bumping one without the others
fails the suite (TODO C2).
"""

from __future__ import annotations

import re
from pathlib import Path

from from_russia_with_love import __version__

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_VERSION_RE = re.compile(
    r'(?<![A-Za-z0-9_-])version"?[ \t]*[:=][ \t]*"?([0-9]+\.[0-9]+\.[0-9]+)'
)


def _read_version(path: Path) -> str:
    """Extract the first dotted version literal from a declarative file."""
    text = path.read_text(encoding="utf-8")
    match = _VERSION_RE.search(text)
    assert match, f"no dotted version literal found in {path.name}"
    return match.group(1)


def test_declarative_version_copies_agree_with_package_version() -> None:
    """Every packaged copy must equal the single source ``__version__``."""
    copies = {
        "pyproject.toml": PROJECT_ROOT / "pyproject.toml",
        "CITATION.cff": PROJECT_ROOT / "CITATION.cff",
        "codemeta.json": PROJECT_ROOT / "codemeta.json",
        ".zenodo.json": PROJECT_ROOT / ".zenodo.json",
        "manuscript/config.yaml": PROJECT_ROOT / "manuscript" / "config.yaml",
    }
    for name, path in copies.items():
        assert path.is_file(), f"declarative version copy missing: {name}"
        assert _read_version(path) == __version__, (
            f"{name} version {_read_version(path)!r} disagrees with the "
            f"single source __version__ {__version__!r}"
        )


def test_mission_and_manuscript_versions_read_the_single_source() -> None:
    from from_russia_with_love.manuscript_variables import PACKAGE_VERSION
    from from_russia_with_love.mission import _PACKAGE_VERSION

    assert PACKAGE_VERSION == __version__ == _PACKAGE_VERSION


def test_version_drift_positive_control(tmp_path: Path) -> None:
    """A drifted declarative copy must be caught (the gate can actually fail)."""
    drifted = tmp_path / "pyproject.toml"
    drifted.write_text('[project]\nversion = "9.9.9"\n', encoding="utf-8")
    assert _read_version(drifted) != __version__
