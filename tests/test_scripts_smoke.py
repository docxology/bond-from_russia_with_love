"""Subprocess smoke tests for the thin mission-phase CLIs (no mocks)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, str(PROJECT_ROOT / "scripts" / script), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_brief() -> None:
    result = _run("run_mission.py", "brief")
    assert result.returncode == 0, result.stderr
    assert "LURES" in result.stdout
    assert "objectives" in result.stdout


def test_recon() -> None:
    result = _run("run_mission.py", "recon", "assess cover posture")
    assert result.returncode == 0, result.stderr
    assert "assess cover posture" in result.stdout


def test_plan() -> None:
    result = _run("run_mission.py", "plan")
    assert result.returncode == 0, result.stderr
    assert "bait" in result.stdout
    assert "intercept" in result.stdout


def test_execute() -> None:
    result = _run("run_mission.py", "execute")
    assert result.returncode == 0, result.stderr
    assert "success   : True" in result.stdout
    assert "handoff_state" in result.stdout


def test_debrief() -> None:
    result = _run("run_mission.py", "debrief")
    assert result.returncode == 0, result.stderr
    assert "lessons" in result.stdout


def test_run_full_flow() -> None:
    result = _run("run_mission.py", "run", "verify everything")
    assert result.returncode == 0, result.stderr
    assert "lessons" in result.stdout


def test_unknown_command_exit_2() -> None:
    result = _run("run_mission.py", "nonsense")
    assert result.returncode == 2


def test_no_args_usage() -> None:
    result = _run("run_mission.py")
    assert result.returncode == 2


def test_preflight() -> None:
    result = _run("00_preflight.py")
    assert result.returncode == 0, result.stderr
    assert "preflight PASS" in result.stdout


def test_generate_manuscript_variables() -> None:
    result = _run("z_generate_manuscript_variables.py")
    assert result.returncode == 0, result.stderr
    output = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
    figure = PROJECT_ROOT / "output" / "figures" / "lure_surface.png"
    assert output.exists() and output.stat().st_size > 0
    assert figure.exists() and figure.stat().st_size > 0
