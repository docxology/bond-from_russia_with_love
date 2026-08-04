"""Tests for manuscript {{TOKEN}} hydration + live cross-reference gate."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from from_russia_with_love.manuscript_variables import (
    PACKAGE_VERSION,
    generate_variables,
    load_mission_config,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_FIXED_NOW = "2026-08-04T00:00:00Z"


@pytest.fixture(scope="module")
def variables() -> dict[str, object]:
    return generate_variables(PROJECT_ROOT, allow_draft=True, now=_FIXED_NOW)


def test_config_loaded() -> None:
    config = load_mission_config(PROJECT_ROOT)
    paper = config["paper"]
    assert isinstance(paper, dict)
    assert "title" in paper


def test_config_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_mission_config(tmp_path)


def test_config_non_mapping_raises(tmp_path: Path) -> None:
    (tmp_path / "manuscript").mkdir(parents=True)
    (tmp_path / "manuscript" / "config.yaml").write_text(
        "just a string\n", encoding="utf-8"
    )
    with pytest.raises(TypeError):
        load_mission_config(tmp_path)


def test_variables_identity(variables: dict[str, object]) -> None:
    assert variables["BOND_IDENTITY"] == "LURES"
    assert variables["BOND_CODENAME"] == "LURES"
    assert variables["BOND_VERSION"] == PACKAGE_VERSION
    assert "From Russia with Love" in str(variables["BOND_TITLE"])


def test_variables_live_values(variables: dict[str, object]) -> None:
    # result-derived: never hand-authored
    assert 0.0 < float(variables["LURES_BITE_PROBABILITY"]) < 1.0
    assert variables["LURES_FINAL_STAGE"] in ("sprung", "aborted")
    assert variables["LURES_RECOVERED_EXACT"] == "True"
    assert variables["LURES_HANDOFF_STATE"] == "handoff"
    assert len(str(variables["LURES_CONFIRM_CODE"])) == 6
    assert variables["GENERATION_TIMESTAMP"] == _FIXED_NOW


def test_variables_deterministic() -> None:
    a = generate_variables(PROJECT_ROOT, now=_FIXED_NOW)
    b = generate_variables(PROJECT_ROOT, now=_FIXED_NOW)
    assert a == b


def test_variables_wallclock_fallback() -> None:
    # Omitting `now` exercises the wall-clock fallback branch.
    variables = generate_variables(PROJECT_ROOT)
    assert "GENERATION_TIMESTAMP" in variables
    assert str(variables["GENERATION_TIMESTAMP"]).endswith("Z")


def test_variables_keywords_fallback_branch(tmp_path: Path) -> None:
    # A config whose `keywords` is not a list exercises the empty-list branch.
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        "paper:\n  title: T\n  version: 0.1.0\nkeywords: just-a-string\n",
        encoding="utf-8",
    )
    variables = generate_variables(tmp_path, now=_FIXED_NOW)
    assert variables["CONFIG_KEYWORDS"] == ""  # non-list keywords -> empty join


def test_all_manuscript_tokens_are_generated(variables: dict[str, object]) -> None:
    """Live gate: every {{TOKEN}} in numbered prose sections must be generated."""
    token_pattern = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")
    referenced: set[str] = set()
    for section in sorted(PROJECT_ROOT.glob("manuscript/[0-9]*.md")):
        text = section.read_text(encoding="utf-8")
        referenced.update(token_pattern.findall(text))
    missing = sorted(tok for tok in referenced if tok not in variables)
    assert not missing, (
        f"manuscript tokens missing from generate_variables(): {missing}"
    )
