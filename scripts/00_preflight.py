"""LURES preflight — verify the package can run its gates.

Checks that bond-api (the FROZEN protocol) is importable, the provider
passes the runtime protocol check, and the pure domain modules import with
no ``bond_api`` dependency. Exits 0 iff all pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    del argv
    failures: list[str] = []

    # 1. Pure core importable without bond_api.
    try:
        import from_russia_with_love.entrapment_engine  # noqa: F401
        import from_russia_with_love.handoff_protocol  # noqa: F401
        import from_russia_with_love.sigint  # noqa: F401

        print("[ok] pure domain core imports (no bond_api)")
    except Exception as exc:  # pragma: no cover - preflight failure path
        failures.append(f"pure core import failed: {exc!r}")

    # 2. bond-api wired and provider passes the runtime protocol check.
    try:
        from bond_api.protocol import MissionProvider, ReconRequest, run_mission

        from from_russia_with_love.mission import MissionProvider as LuresProvider

        provider = LuresProvider()
        if not isinstance(provider, MissionProvider):
            failures.append("provider failed the runtime MissionProvider check")
        else:
            debrief = run_mission(provider, ReconRequest(goal="preflight verification"))
            status = "success" if debrief.outcome.success else "failed"
            print(f"[ok] bond-api wired; mission run -> {status}")
    except Exception as exc:  # pragma: no cover - preflight failure path
        failures.append(f"bond-api integration failed: {exc!r}")

    for failure in failures:
        print(f"[FAIL] {failure}")
    if failures:
        return 1
    print("preflight PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
