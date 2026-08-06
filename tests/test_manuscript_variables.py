"""Tests for manuscript {{TOKEN}} hydration + live cross-reference gate."""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

from from_russia_with_love import scenario
from from_russia_with_love.direction_finding import min_site_spacing
from from_russia_with_love.manuscript_variables import (
    PACKAGE_VERSION,
    _float_field,
    _traffic_field,
    generate_variables,
    load_mission_config,
    manuscript_date,
    validate_mission_config,
)
from from_russia_with_love.sigint import intercept_channel

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def variables() -> dict[str, object]:
    return generate_variables(PROJECT_ROOT, allow_draft=True)


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


def test_variables_deterministic() -> None:
    """Two live calls, nothing injected — the maps must be equal."""
    a = generate_variables(PROJECT_ROOT)
    b = generate_variables(PROJECT_ROOT)
    assert a == b


def test_manuscript_date_comes_from_the_committed_config() -> None:
    """The date token is a config value, not a clock read."""
    config = load_mission_config(PROJECT_ROOT)
    paper = config["paper"]
    assert isinstance(paper, dict)
    variables = generate_variables(PROJECT_ROOT)
    assert variables["MANUSCRIPT_DATE"] == str(paper["date"])
    assert "GENERATION_TIMESTAMP" not in variables


@pytest.mark.parametrize("bad", [{}, {"date": None}, {"date": "   "}])
def test_manuscript_date_missing_is_rejected(bad: dict[str, object]) -> None:
    """Positive control: the date is required, so it can never silently
    fall back to a clock read."""
    with pytest.raises(ValueError, match="paper.date"):
        manuscript_date(bad)


def test_variables_keywords_fallback_branch(tmp_path: Path) -> None:
    # A config whose `keywords` is not a list exercises the empty-list branch.
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        'paper:\n  title: T\n  version: 0.1.0\n  date: "2026-01-01"\n'
        "keywords: just-a-string\n",
        encoding="utf-8",
    )
    variables = generate_variables(tmp_path)
    assert variables["CONFIG_KEYWORDS"] == ""  # non-list keywords -> empty join


def test_intercept_field_helpers_read_a_real_intercept() -> None:
    """Happy paths over genuine intercept output, plus both guard branches."""
    channel = intercept_channel(
        scenario.PLAINTEXT, scenario.CIPHERS, snr_db=scenario.SNR_DB, seed=0
    )
    assert _traffic_field(channel, "length") == len(scenario.PLAINTEXT.encode("utf-8"))
    assert _traffic_field(channel, "distinct_symbols") > 0
    with pytest.raises(TypeError, match="must be a mapping"):
        _traffic_field({"traffic": "not-a-mapping"}, "length")

    # A seed-0 capture is exactly lossless, so the empirical SNR is +inf.
    assert _float_field(channel, "empirical_snr_db") == float("inf")
    with pytest.raises(TypeError, match="must be numeric"):
        _float_field({"empirical_snr_db": "not-a-number"}, "empirical_snr_db")


def test_shipped_config_agrees_with_scenario() -> None:
    """The real config must pass the drift guard (it is the shipped state)."""
    validate_mission_config(load_mission_config(PROJECT_ROOT))


def test_validate_mission_config_rejects_version_drift(tmp_path: Path) -> None:
    """C2: the config's version copy must equal the single source of truth.

    ``paper.version`` feeds {{BOND_VERSION}} and mission provenance reads the
    same ``__version__``; a drifted config copy must fail the manuscript build
    rather than quietly report a stale version.
    """
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        'paper:\n  title: T\n  version: 9.9.9\n  date: "2026-01-01"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="disagrees with the package version"):
        generate_variables(tmp_path)


def test_config_scenario_drift_is_detected() -> None:
    """Positive control: the guard must actually reject a drifted config.

    Without this, ``validate_mission_config`` could be green by construction.
    """
    drifted = {"mission": {"objectives": len(scenario.OBJECTIVES) + 1}}
    with pytest.raises(ValueError, match="disagrees with scenario.py"):
        validate_mission_config(drifted)

    drifted_seed = {"mission": {"seed": scenario.SEED + 1}}
    with pytest.raises(ValueError, match="seed"):
        validate_mission_config(drifted_seed)


def test_config_without_mission_block_is_allowed() -> None:
    validate_mission_config({"paper": {"title": "T"}})


def test_config_mission_block_must_be_a_mapping() -> None:
    with pytest.raises(TypeError):
        validate_mission_config({"mission": "not-a-mapping"})


def test_generate_variables_rejects_drifted_config(tmp_path: Path) -> None:
    """The drift guard is wired into the manuscript build, not just callable."""
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        "paper:\n  title: T\n  version: 0.1.0\nmission:\n  seed: 999\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="disagrees with scenario.py"):
        generate_variables(tmp_path)


def test_objective_count_token_tracks_the_canonical_tuple(
    variables: dict[str, object],
) -> None:
    """The token is derived from scenario.OBJECTIVES, not a hand-written number."""
    assert variables["LURES_NUM_OBJECTIVES"] == len(scenario.OBJECTIVES)


def test_engine_count_token_tracks_the_engine_tuple(
    variables: dict[str, object],
) -> None:
    assert variables["LURES_NUM_ENGINES"] == len(scenario.ENGINES)


def test_scenario_engines_match_the_modules_on_disk() -> None:
    """Bind the engine count to the package tree, not to the objective count.

    ``{{LURES_NUM_ENGINES}}`` is spent in the abstract, introduction and
    conclusion as a count of *engines*. Previously the prose spent
    ``{{LURES_NUM_OBJECTIVES}}`` there, with nothing forcing the two counts to
    agree. This test is the missing binding: every name in
    ``scenario.ENGINES`` must be a real module file, and every non-supporting
    module in the package must be listed. Adding, renaming, or deleting an
    engine module without updating the tuple fails here.
    """
    package_dir = PROJECT_ROOT / "src" / "from_russia_with_love"
    supporting = {
        "__init__",
        "scenario",
        "mission",
        "manuscript_variables",
    }
    on_disk = {
        path.stem for path in package_dir.glob("*.py") if path.stem not in supporting
    }
    assert on_disk, "no engine modules found — the glob is not binding anything"
    assert set(scenario.ENGINES) == on_disk
    assert len(scenario.ENGINES) == len(set(scenario.ENGINES))
    for name in scenario.ENGINES:
        assert (package_dir / f"{name}.py").is_file()


def test_introduction_engine_list_length_matches_the_engine_count() -> None:
    """The hand-numbered list in §1 must have exactly LURES_NUM_ENGINES items.

    The prose numbers its engines by hand; without this gate the token and the
    list can drift apart silently (which is exactly how the reused
    objective-count token went unnoticed).
    """
    text = (PROJECT_ROOT / "manuscript" / "01_introduction.md").read_text(
        encoding="utf-8"
    )
    numbered = re.findall(r"(?m)^(\d+)\. ", text)
    assert numbered, "no numbered engine list found in the introduction"
    assert len(numbered) == len(scenario.ENGINES)
    assert numbered == [str(i + 1) for i in range(len(scenario.ENGINES))]


def test_allocation_gap_tokens_are_measured_not_tautological(
    variables: dict[str, object],
) -> None:
    """The reported gaps must be the real differences, on both instances.

    The retired ``LURES_OPTIMAL_DOMINATES_GREEDY`` token could only render
    ``False`` on a solver bug — it was green by construction. These tokens are
    scenario properties: the canonical gap is zero (greedy ties) and the
    witness gap is strictly positive, and either can change if a scenario or a
    solver changes.
    """
    assert "LURES_OPTIMAL_DOMINATES_GREEDY" not in variables

    exact = float(str(variables["LURES_ALLOC_VALUE"]))
    greedy = float(str(variables["LURES_GREEDY_VALUE"]))
    gap = float(str(variables["LURES_GREEDY_GAP"]))
    assert gap == pytest.approx(exact - greedy, abs=5e-4)
    assert gap == pytest.approx(0.0, abs=1e-9)  # canonical pool: a genuine tie
    assert variables["LURES_GREEDY_TIES_ON_CANONICAL"] == "True"

    witness_exact = float(str(variables["LURES_WITNESS_EXACT_VALUE"]))
    witness_greedy = float(str(variables["LURES_WITNESS_GREEDY_VALUE"]))
    witness_gap = float(str(variables["LURES_WITNESS_GAP"]))
    assert witness_gap == pytest.approx(witness_exact - witness_greedy, abs=5e-4)
    assert witness_gap > 0.0  # the instance that actually separates them
    assert variables["LURES_WITNESS_TARGETS"] == len(scenario.GREEDY_WITNESS_TARGETS)


def test_tdoa_unit_tokens_distinguish_coordinates_from_site_spacings(
    variables: dict[str, object],
) -> None:
    """The raw error and the site-spacing-normalised error are distinct.

    §3.3 previously labelled the raw Euclidean error "units of site spacing".
    These two tokens now carry the two different quantities, and the spacing
    token is computed from the receiver geometry rather than assumed.
    """
    spacing = float(str(variables["LURES_TDOA_SITE_SPACING"]))
    raw = float(str(variables["LURES_TDOA_ERROR"]))
    normalised = float(str(variables["LURES_TDOA_ERROR_SPACINGS"]))
    assert spacing == pytest.approx(min_site_spacing(scenario.TDOA_RECEIVERS))
    assert spacing > 1.0  # a real array, so the two units genuinely differ
    assert normalised == pytest.approx(raw / spacing, abs=5e-5)
    assert normalised < raw

    # The geometry is actually published, not just used.
    coords = str(variables["LURES_TDOA_RECEIVER_COORDS"])
    for receiver in scenario.TDOA_RECEIVERS:
        assert receiver.receiver_id in coords
    assert str(int(scenario.TDOA_TRANSMITTER[0])) in str(
        variables["LURES_TDOA_TRANSMITTER"]
    )


def test_schedule_tokens_report_the_optimality_gap(
    variables: dict[str, object],
) -> None:
    count = int(str(variables["LURES_SCHEDULE_COUNT"]))
    optimum = int(str(variables["LURES_SCHEDULE_OPTIMUM"]))
    gap = int(str(variables["LURES_SCHEDULE_GAP"]))
    assert optimum >= count
    assert gap == optimum - count
    assert 0 <= optimum <= len(scenario.RENDEZVOUS)


def test_new_scenario_tokens_match_the_source_of_truth(
    variables: dict[str, object],
) -> None:
    assert variables["LURES_ALLOC_TARGETS"] == len(scenario.ALLOC_TARGETS)
    assert variables["LURES_CIPHER_LAYERS"] == len(scenario.CIPHERS)
    assert variables["LURES_SEED"] == scenario.SEED
    assert variables["LURES_MESSAGE_BYTES"] == len(scenario.PLAINTEXT.encode("utf-8"))
    assert int(str(variables["LURES_TRAFFIC_DISTINCT"])) > 0


_ATTRIBUTION_SOURCES = (
    "README.md",
    "manuscript/02_methodology.md",
    "manuscript/07_scope_and_related_work.md",
    "manuscript/99_references.md",
    "src/from_russia_with_love/direction_finding.py",
)

# Phrasings that attribute the *implemented* iterative solver to Chan & Ho.
# Chan & Ho 1994 is a closed-form, non-iterative estimator; this package
# implements the iterative Taylor-series / Gauss-Newton scheme (Foy 1976),
# which Chan & Ho was published as an alternative to.
_MISATTRIBUTION_PATTERNS = (
    r"following the estimator of Chan",
    r"geolocation \(Chan (&|and) Ho",
    r"\(Chan (&|and) Ho 1994 hyperbolic location\)",
    r"hyperbolation \(@chan1994hyperbolic\)",
)


def test_gauss_newton_solver_is_not_attributed_to_chan_and_ho() -> None:
    """Guard the corrected method attribution against regression.

    Positive control for this gate: re-insert any of the retired phrasings
    (e.g. put "geolocation (Chan & Ho 1994)" back in the README row) and this
    test fails, naming the file.
    """
    offenders: list[str] = []
    for relative in _ATTRIBUTION_SOURCES:
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        for pattern in _MISATTRIBUTION_PATTERNS:
            if re.search(pattern, text):
                offenders.append(f"{relative}: {pattern}")
    assert not offenders, (
        "the implemented solver is the iterative Taylor-series/Gauss-Newton "
        "estimator (Foy 1976), not Chan & Ho's closed-form estimator: "
        f"{offenders}"
    )


def test_implemented_solver_cites_the_iterative_estimator() -> None:
    """The corrected citation must actually be present, not merely un-wrong."""
    bib = (PROJECT_ROOT / "manuscript" / "references.bib").read_text(encoding="utf-8")
    assert "foy1976position" in bib
    assert "torrieri1984statistical" in bib
    for relative in ("manuscript/02_methodology.md", "manuscript/99_references.md"):
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "foy1976position" in text, relative
    scope = (PROJECT_ROOT / "manuscript" / "07_scope_and_related_work.md").read_text(
        encoding="utf-8"
    )
    assert "foy1976position" in scope
    assert "does not implement it" in scope


def test_every_cited_bib_key_exists() -> None:
    """Citations in the manuscript must resolve to real bib entries."""
    bib = (PROJECT_ROOT / "manuscript" / "references.bib").read_text(encoding="utf-8")
    defined = set(re.findall(r"@\w+\{([A-Za-z0-9_]+),", bib))
    assert defined, "no bib entries parsed — the check would be vacuous"
    cited: set[str] = set()
    for section in sorted(PROJECT_ROOT.glob("manuscript/[0-9]*.md")):
        cited.update(
            re.findall(
                r"[\[(;]\s*@([A-Za-z][A-Za-z0-9_]*)",
                section.read_text(encoding="utf-8"),
            )
        )
    assert cited, "no citations found — the check would be vacuous"
    assert not (cited - defined), f"undefined bib keys cited: {sorted(cited - defined)}"


def test_schedule_witness_tokens_report_the_separation(
    variables: dict[str, object],
) -> None:
    """E1: the scheduler witness instance separates the solvers (gap > 0).

    The canonical RENDEZVOUS does not — the heuristic reaches the optimum
    there — so the manuscript's scheduling-separation claim is measured on
    this witness instance, mirroring the allocation witness. The token must be
    strict, positive, and consistent with the exact-solver optimum.
    """
    total = int(str(variables["LURES_SCHEDULE_WITNESS_TOTAL"]))
    count = int(str(variables["LURES_SCHEDULE_WITNESS_COUNT"]))
    optimum = int(str(variables["LURES_SCHEDULE_WITNESS_OPTIMUM"]))
    gap = int(str(variables["LURES_SCHEDULE_WITNESS_GAP"]))
    assert total == len(scenario.SCHEDULE_WITNESS)
    assert 0 <= count <= optimum
    assert gap == optimum - count
    assert gap > 0  # the witness instance genuinely separates the solvers


def test_crlb_tokens_are_live_positive_bounds(variables: dict[str, object]) -> None:
    """The uncertainty tokens are computed, finite, and positive on the array."""
    crlb = float(str(variables["LURES_TDOA_CRLB"]))
    assert math.isfinite(crlb)
    assert crlb > 0.0
    assert variables["LURES_TDOA_ERROR_ABOVE_CRLB"] in ("True", "False")
    # The bound is a coordinate-unit RMS; the site-spacing scale is larger.
    assert crlb < float(str(variables["LURES_TDOA_SITE_SPACING"]))


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
