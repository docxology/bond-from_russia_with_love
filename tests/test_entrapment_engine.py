"""Tests for the entrapment / deception playbook engine (real computation)."""

from __future__ import annotations

import random

import pytest

from from_russia_with_love.entrapment_engine import (
    DEFAULT_SEED,
    BaitProfile,
    TrapStage,
    TrapStateMachine,
    bait_bite_probability,
    generate_bait_profile,
    run_bait_campaign,
)


def test_bait_profile_validation() -> None:
    with pytest.raises(ValueError):
        BaitProfile("", "role", 0.5, "msg", 0.5)
    with pytest.raises(ValueError):
        BaitProfile("id", "", 0.5, "msg", 0.5)
    with pytest.raises(ValueError):
        BaitProfile("id", "role", 1.5, "msg", 0.5)
    with pytest.raises(ValueError):
        BaitProfile("id", "role", 0.5, "msg", -0.1)


def test_bait_profile_ok() -> None:
    profile = BaitProfile("id", "role", 0.0, "msg", 0.0)
    assert profile.lure_id == "id"
    assert profile.cover_role == "role"


def test_bite_probability_bounds_and_monotonic() -> None:
    assert 0.0 < bait_bite_probability(0.0, 0.0) < 1.0
    assert bait_bite_probability(1.0, 1.0) > bait_bite_probability(0.0, 0.0)
    # strictly increasing in strength
    assert bait_bite_probability(0.6, 0.5) > bait_bite_probability(0.4, 0.5)
    # strictly increasing in susceptibility
    assert bait_bite_probability(0.5, 0.7) > bait_bite_probability(0.5, 0.3)
    # symmetry under identical arguments
    assert bait_bite_probability(0.5, 0.5) == bait_bite_probability(0.5, 0.5)


def test_bite_probability_midpoint() -> None:
    # z = 4*(0.5+0.5-1) = 0 -> 0.5 exactly.
    assert bite_approx() == pytest.approx(0.5)


def bite_approx() -> float:
    return bait_bite_probability(0.5, 0.5)


def test_bite_probability_validation() -> None:
    with pytest.raises(ValueError):
        bait_bite_probability(1.1, 0.5)
    with pytest.raises(ValueError):
        bait_bite_probability(0.5, -0.2)


def test_generate_bait_profile_deterministic() -> None:
    first = generate_bait_profile("honey-trap-alpha", seed=11)
    second = generate_bait_profile("honey-trap-alpha", seed=11)
    assert first == second
    assert first.lure_id == "honey-trap-alpha"
    # different seed -> (very likely) different lure
    other = generate_bait_profile("honey-trap-alpha", seed=12)
    assert 0.0 <= other.target_susceptibility <= 1.0
    assert 0.0 <= other.lure_strength <= 1.0


def test_generate_bait_profile_rng_param() -> None:
    rng = random.Random(99)
    profile = generate_bait_profile("decoy-x", rng=rng)
    assert profile.lure_id == "decoy-x"
    # message always follows the channel:role pattern
    assert profile.message_payload.startswith(("shortwave", "teleprinter"))


def test_generate_bait_profile_validation() -> None:
    with pytest.raises(ValueError):
        generate_bait_profile("")


def test_generate_bait_profile_seed_type() -> None:
    from from_russia_with_love.entrapment_engine import _fold_seed

    with pytest.raises(TypeError):
        _fold_seed("not-an-int", "salt")


def test_trap_machine_full_green() -> None:
    profile = generate_bait_profile("honey-trap-alpha", seed=DEFAULT_SEED)
    machine = TrapStateMachine(profile)
    assert machine.stage == TrapStage.DISARMED
    assert machine.transition("deploy") == TrapStage.ARMED
    assert machine.transition("bait") == TrapStage.BAITED
    assert machine.transition("engage") == TrapStage.ENGAGED
    assert machine.transition("spring") == TrapStage.SPRUNG
    assert machine.history[0] == (TrapStage.DISARMED, "deploy", TrapStage.ARMED)
    assert len(machine.history) == 4


def test_trap_machine_abort_branches() -> None:
    # from BAITED -> ABORT on 'ignore'
    m1 = TrapStateMachine(generate_bait_profile("a", seed=1))
    m1.transition("deploy")
    m1.transition("bait")
    assert m1.transition("ignore") == TrapStage.ABORTED
    # from ARMED -> ABORT on 'stand_down'
    m2 = TrapStateMachine(generate_bait_profile("b", seed=2))
    m2.transition("deploy")
    assert m2.transition("stand_down") == TrapStage.ABORTED
    # from DISARMED -> ABORT on 'stand_down'
    m3 = TrapStateMachine(generate_bait_profile("c", seed=3))
    assert m3.transition("stand_down") == TrapStage.ABORTED


def test_trap_machine_illegal_event() -> None:
    machine = TrapStateMachine(generate_bait_profile("a", seed=4))
    with pytest.raises(ValueError):
        machine.transition("engage")  # not valid from DISARMED


def test_trap_machine_terminal_blocked() -> None:
    machine = TrapStateMachine(generate_bait_profile("a", seed=5))
    machine.transition("deploy")
    machine.transition("bait")
    machine.transition("engage")
    machine.transition("spring")
    with pytest.raises(ValueError):
        machine.transition("deploy")


def test_trap_type_check() -> None:
    with pytest.raises(TypeError):
        TrapStateMachine("not-a-bait")


def test_run_campaign_engage_and_stand_down() -> None:
    profile = generate_bait_profile("a", seed=6)
    engaged = TrapStateMachine(profile)
    assert engaged.run_campaign(engage=True) == TrapStage.SPRUNG
    stood_down = TrapStateMachine(profile)
    assert stood_down.run_campaign(engage=False) == TrapStage.ABORTED


def test_run_bait_campaign_deterministic() -> None:
    profile = generate_bait_profile("honey-trap-alpha", seed=11)
    result = run_bait_campaign(profile, engagement_threshold=0.5)
    assert result["lure_id"] == "honey-trap-alpha"
    assert result["final_stage"] in {"sprung", "aborted"}
    assert 0.0 < result["bite_probability"] < 1.0
    assert result["decision"] in {"engage", "stand_down"}
    # forced decisions
    assert run_bait_campaign(profile, engage=True)["final_stage"] == "sprung"
    assert run_bait_campaign(profile, engage=False)["final_stage"] == "aborted"
