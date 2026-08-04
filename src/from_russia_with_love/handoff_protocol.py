"""LURES defector handoff protocol — meet / challenge / confirm / abort.

Models the structured, verifiable handoff of a defecting source (mission
theme: From Russia with Love, 1963). The protocol is a deterministic state
machine with a fixed challenge/confirm sequence: the handler and the defector
must exchange a pre-arranged challenge code and, only on the matching confirm
code, may the handoff complete. Any mismatch or abort lands the protocol in a
terminal ``ABORT`` state.

States
------
``DISARM -> MEET -> CHALLENGE -> CONFIRM -> HANDOFF`` (success terminal),
with ``ABORT`` reachable from every active stage.

The confirm code is derived **deterministically** from the challenge and the
call-sign via a stable fingerprunt so no random state or wall-clock time is
involved.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum

__all__ = [
    "HandoffState",
    "HandoffResult",
    "HandoffProtocol",
    "challenge_confirm_code",
    "validate_transition",
]

#: Canonical handoff stage order (for reporting/plotting).
STAGE_ORDER = ("disarm", "meet", "challenge", "confirm", "handoff", "abort")


class HandoffState(str, Enum):
    """Valid states of a defector handoff protocol."""

    DISARM = "disarm"
    MEET = "meet"
    CHALLENGE = "challenge"
    CONFIRM = "confirm"
    HANDOFF = "handoff"
    ABORT = "abort"


_TERMINAL = frozenset({HandoffState.HANDOFF, HandoffState.ABORT})

#: Transition table: (from_state, event) -> to_state.
_TRANSITIONS: dict[tuple[HandoffState, str], HandoffState] = {
    (HandoffState.DISARM, "approach"): HandoffState.MEET,
    (HandoffState.MEET, "challenge"): HandoffState.CHALLENGE,
    (HandoffState.CHALLENGE, "confirm_ok"): HandoffState.CONFIRM,
    (HandoffState.CONFIRM, "complete"): HandoffState.HANDOFF,
    (HandoffState.CHALLENGE, "confirm_fail"): HandoffState.ABORT,
    (HandoffState.MEET, "challenge_fail"): HandoffState.ABORT,
    (HandoffState.DISARM, "abandon"): HandoffState.ABORT,
    (HandoffState.MEET, "abandon"): HandoffState.ABORT,
    (HandoffState.CHALLENGE, "abandon"): HandoffState.ABORT,
    (HandoffState.CONFIRM, "abandon"): HandoffState.ABORT,
}


def validate_transition(state: HandoffState, event: str) -> HandoffState:
    """Return the destination of ``event`` from ``state`` or raise ``ValueError``."""
    if state in _TERMINAL:
        raise ValueError(
            f"handoff is terminal in state {state.value!r}; no further events"
        )
    key = (state, event)
    if key not in _TRANSITIONS:
        raise ValueError(f"invalid event {event!r} from state {state.value!r}")
    return _TRANSITIONS[key]


def challenge_confirm_code(challenge: str, call_sign: str) -> str:
    """Deterministic confirm code for a (challenge, call_sign) pair.

    Both arguments must be non-empty. The confirm code is the first 6 hex
    characters of the SHA-256 of ``call_sign + ':' + challenge`` — stable,
    fast, and independent of any random state.
    """
    if not challenge.strip():
        raise ValueError("challenge must be a non-empty string")
    if not call_sign.strip():
        raise ValueError("call_sign must be a non-empty string")
    digest = hashlib.sha256(f"{call_sign}:{challenge}".encode()).hexdigest()
    return digest[:6]


@dataclass(frozen=True)
class HandoffResult:
    """The outcome of a completed (or aborted) handoff protocol."""

    state: HandoffState
    path: tuple[str, ...]
    confirm_code: str = ""


class HandoffProtocol:
    """Deterministic meet/challenge/confirm/abort handoff state machine."""

    def __init__(self, call_sign: str, challenge: str) -> None:
        if not call_sign.strip():
            raise ValueError("call_sign must be a non-empty string")
        if not challenge.strip():
            raise ValueError("challenge must be a non-empty string")
        self.call_sign = call_sign
        self.challenge_phrase = challenge
        self.confirm_code = challenge_confirm_code(challenge, call_sign)
        self.state = HandoffState.DISARM
        self.path: list[str] = []

    def _go(self, event: str) -> HandoffState:
        self.state = validate_transition(self.state, event)
        self.path.append(f"{self.state.value}:{event}")
        return self.state

    def meet(self) -> HandoffState:
        """Begin contact with the defector."""
        return self._go("approach")

    def challenge(self) -> HandoffState:
        """Issue the challenge; move from MEET to CHALLENGE."""
        return self._go("challenge")

    def confirm(self, code: str) -> HandoffState:
        """Submit a confirm code; only the exact match advances to CONFIRM.

        Any other confirm code raises in CONFIRM → ABORT. Thanks to the
        challenge/confirm derivation, a wrong code cannot complete.
        """
        if self.state != HandoffState.CHALLENGE:
            raise ValueError(
                f"confirm only valid in CHALLENGE, not {self.state.value!r}"
            )
        if code.strip() == self.confirm_code:
            return self._go("confirm_ok")
        return self._go("confirm_fail")

    def complete(self) -> HandoffState:
        """Finish the handoff after a matching confirm."""
        return self._go("complete")

    def abort(self) -> HandoffState:
        """Abort the handoff at any active stage."""
        return self._go("abandon")

    def run_green(self) -> HandoffResult:
        """Run the nominal green path to a clean ``HANDOFF``.

        Deterministic: approach, challenge, matching confirm, complete.
        """
        self.meet()
        self.challenge()
        self.confirm(self.confirm_code)
        self.complete()
        return self.result()

    def result(self) -> HandoffResult:
        """Return the current outcome (state, event path, confirm code)."""
        return HandoffResult(
            state=self.state, path=tuple(self.path), confirm_code=self.confirm_code
        )
