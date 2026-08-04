"""LURES mission CLI — thin orchestrator over the frozen MissionProvider.

Usage::

    uv run python scripts/run_mission.py brief
    uv run python scripts/run_mission.py recon "<goal>"
    uv run python scripts/run_mission.py plan
    uv run python scripts/run_mission.py execute
    uv run python scripts/run_mission.py debrief
    uv run python scripts/run_mission.py run "<goal>"   # full five-stage flow

Exit code is 0 iff the requested phase succeeded (execute succeeds only when
the mission outcome is ``success``).
"""

from __future__ import annotations

import sys
from pathlib import Path

from bond_api.protocol import MissionBrief, MissionOutcome, MissionPlan

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))  # noqa: E402


def _fmt_brief(brief: MissionBrief) -> str:
    lines = [
        f"film      : {brief.film}",
        f"codename  : {brief.codename}",
        "objectives:",
    ]
    lines += [f"  - {o}" for o in brief.objectives]
    lines.append("assets:")
    lines += [f"  - {a.kind} / {a.name}" for a in brief.assets]
    lines.append("constraints:")
    lines += [f"  - [{c.kind}] {c.detail}" for c in brief.constraints]
    return "\n".join(lines)


def _fmt_plan(plan: MissionPlan) -> str:
    lines = ["plan steps:"]
    lines += [
        f"  {i}. {s.name} ({s.action} {s.params})" for i, s in enumerate(plan.steps, 1)
    ]
    return "\n".join(lines)


def _fmt_outcome(outcome: MissionOutcome) -> str:
    lines = [f"success   : {outcome.success}", "results:"]
    for key, value in outcome.results.items():
        lines.append(f"  {key}: {value}")
    lines.append(
        f"provenance: v{outcome.provenance.package_version} "
        f"seed={outcome.provenance.seed} hash={outcome.provenance.input_hash}"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    from bond_api.protocol import ReconRequest, run_mission

    from from_russia_with_love.mission import MissionProvider

    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 2

    provider = MissionProvider()
    command = argv[0]

    if command == "brief":
        print(_fmt_brief(provider.brief()))
        return 0
    if command == "recon":
        goal = " ".join(argv[1:]) or "evaluate the LURES cover posture"
        report = provider.recon(ReconRequest(goal=goal))
        print(f"goal   : {goal}")
        for finding in report.findings:
            print(f"  - [{finding.label}] {finding.detail}")
        return 0
    if command == "plan":
        print(_fmt_plan(provider.plan(provider.brief())))
        return 0
    if command == "execute":
        plan = provider.plan(provider.brief())
        outcome = provider.execute(plan)
        print(_fmt_outcome(outcome))
        return 0 if outcome.success else 1
    if command == "debrief":
        plan = provider.plan(provider.brief())
        outcome = provider.execute(plan)
        debrief = provider.debrief(outcome)
        print(_fmt_outcome(outcome))
        print("lessons:")
        print("\n".join(f"  - {lesson}" for lesson in debrief.lessons))
        return 0 if outcome.success else 1
    if command == "run":
        goal = " ".join(argv[1:]) or "evaluate the LURES cover posture"
        debrief = run_mission(provider, ReconRequest(goal=goal))
        print(_fmt_outcome(debrief.outcome))
        print("lessons:")
        print("\n".join(f"  - {lesson}" for lesson in debrief.lessons))
        return 0 if debrief.outcome.success else 1

    print(f"unknown command: {command!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
