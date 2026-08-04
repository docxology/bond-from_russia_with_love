"""Tests for the defector handoff protocol state machine (real computation)."""

from __future__ import annotations

import pytest

from from_russia_with_love.handoff_protocol import (
    STAGE_ORDER,
    HandoffProtocol,
    HandoffResult,
    HandoffState,
    challenge_confirm_code,
    validate_transition,
)


def test_challenge_confirm_code_deterministic() -> None:
    a = challenge_confirm_code("the cow jumped over the moon", "ROZA")
    b = challenge_confirm_code("the cow jumped over the moon", "ROZA")
    assert a == b
    assert len(a) == 6
    # different challenge or call sign -> different code
    assert a != challenge_confirm_code("the cow jumped over the moon", "KLEBB")
    assert a != challenge_confirm_code("a different challenge", "ROZA")


def test_challenge_confirm_code_validation() -> None:
    with pytest.raises(ValueError):
        challenge_confirm_code("", "ROZA")
    with pytest.raises(ValueError):
        challenge_confirm_code("challenge", "  ")


def test_validate_transition() -> None:
    assert validate_transition(HandoffState.DISARM, "approach") == HandoffState.MEET
    assert (
        validate_transition(HandoffState.CHALLENGE, "confirm_fail")
        == HandoffState.ABORT
    )
    with pytest.raises(ValueError):
        validate_transition(HandoffState.DISARM, "confirm_ok")


def test_validate_terminal_blocked() -> None:
    with pytest.raises(ValueError):
        validate_transition(HandoffState.HANDOFF, "approach")
    with pytest.raises(ValueError):
        validate_transition(HandoffState.ABORT, "abandon")


def test_green_handoff_run() -> None:
    protocol = HandoffProtocol(
        call_sign="ROZA", challenge="the cow jumped over the moon"
    )
    result = protocol.run_green()
    assert isinstance(result, HandoffResult)
    assert result.state == HandoffState.HANDOFF
    assert result.path[-1].startswith("handoff:")
    assert protocol.confirm_code == result.confirm_code


def test_wrong_confirm_aborts() -> None:
    protocol = HandoffProtocol(
        call_sign="ROZA", challenge="the cow jumped over the moon"
    )
    protocol.meet()
    protocol.challenge()
    assert protocol.confirm("WRONG") == HandoffState.ABORT
    assert protocol.state == HandoffState.ABORT


def test_correct_confirm_then_complete() -> None:
    protocol = HandoffProtocol(
        call_sign="ROZA", challenge="the cow jumped over the moon"
    )
    protocol.meet()
    protocol.challenge()
    assert protocol.confirm(protocol.confirm_code) == HandoffState.CONFIRM
    assert protocol.complete() == HandoffState.HANDOFF


def test_confirm_only_in_challenge() -> None:
    protocol = HandoffProtocol(
        call_sign="ROZA", challenge="the cow jumped over the moon"
    )
    protocol.meet()
    with pytest.raises(ValueError):
        protocol.confirm("anything")


def test_abort_branches() -> None:
    # abandon from DISARM
    p1 = HandoffProtocol("A", "challenge")
    assert p1.abort() == HandoffState.ABORT
    # abandon from MEET
    p3 = HandoffProtocol("C", "challenge")
    p3.meet()
    assert p3.state == HandoffState.MEET
    assert p3.abort() == HandoffState.ABORT


def test_handoff_constructor_validation() -> None:
    with pytest.raises(ValueError):
        HandoffProtocol("", "challenge")
    with pytest.raises(ValueError):
        HandoffProtocol("ROZA", "  ")


def test_handoff_result_fields() -> None:
    protocol = HandoffProtocol("DELILAH", "some challenge phrase")
    result = protocol.result()
    assert result.state == HandoffState.DISARM
    assert result.path == ()
    assert result.confirm_code == challenge_confirm_code(
        "some challenge phrase", "DELILAH"
    )
    assert protocol.confirm_code == result.confirm_code


def test_stage_order_contains_all_states() -> None:
    assert set(STAGE_ORDER) == {s.value for s in HandoffState}
