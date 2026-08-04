"""Pytest configuration for the LURES package."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Force headless matplotlib in tests.
os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
for _path in (str(SRC), str(ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

PROJECT_ROOT = ROOT
