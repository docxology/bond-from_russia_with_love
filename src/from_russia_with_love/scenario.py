"""LURES canonical mission scenario — the single source of truth.

Every deterministic number the mission executes, the manuscript tokens, and
the figures consume lives here. ``mission.py``, ``manuscript_variables.py``,
and the figure generators all import from this module, so an outcome value
reported in the manuscript can never disagree with the code that produced it.

The scenario is *fixed and reproducible*: changing a constant here changes
the mission, the tokens, and the figures together.
"""

from __future__ import annotations

from from_russia_with_love.bait_allocation import Target
from from_russia_with_love.courier_schedule import Rendezvous
from from_russia_with_love.direction_finding import Receiver
from from_russia_with_love.sigint import CipherLayer

__all__ = [
    "ALLOC_BUDGET",
    "ALLOC_LURE_STRENGTH",
    "ALLOC_TARGETS",
    "BAIT_PROFILE_IDS",
    "CALL_SIGNS",
    "CHALLENGE",
    "CIPHERS",
    "ENGAGEMENT_THRESHOLD",
    "ENGINES",
    "GREEDY_WITNESS_BUDGET",
    "GREEDY_WITNESS_LURE_STRENGTH",
    "GREEDY_WITNESS_TARGETS",
    "HANDOFF_CALL_SIGN",
    "OBJECTIVES",
    "PLAINTEXT",
    "RENDEZVOUS",
    "SCHEDULE_START",
    "SEED",
    "SNR_DB",
    "TDOA_NOISE_STD",
    "TDOA_RECEIVERS",
    "TDOA_SPEED",
    "TDOA_TRANSMITTER",
    "TDOA_SEED",
]

#: Fixed seed for every seeded draw in the mission (0 disables randomness).
SEED = 11

#: The mission's declared objectives, in execution order. ``mission.py`` puts
#: these verbatim into its :class:`MissionBrief` and ``manuscript_variables``
#: counts them for ``{{LURES_NUM_OBJECTIVES}}``, so the brief and the
#: manuscript can never report a different number of objectives.
OBJECTIVES: tuple[str, ...] = (
    "evaluate a deception lure campaign via the entrapment engine",
    "allocate the lure budget across the analytical target pool",
    "intercept and decipher an encoded SIGINT channel",
    "geolocate the transmitter by TDOA direction finding",
    "schedule defector-handoff rendezvous within time windows",
    "execute the green-pathed defector handoff protocol",
)

#: The analytical engine modules, by module name. This is a *separate* fact
#: from :data:`OBJECTIVES` — an objective is something the mission sets out to
#: do, an engine is a module that computes. They happen to number the same
#: today; nothing forces that, so the manuscript counts them separately
#: (``{{LURES_NUM_ENGINES}}`` vs ``{{LURES_NUM_OBJECTIVES}}``).
#: ``test_scenario_engines_match_the_modules_on_disk`` binds this tuple to the
#: package directory, so adding or deleting an engine module without updating
#: this tuple fails the suite.
ENGINES: tuple[str, ...] = (
    "entrapment_engine",
    "bait_allocation",
    "sigint",
    "direction_finding",
    "courier_schedule",
    "handoff_protocol",
)

# --- SIGINT interception -----------------------------------------------------
PLAINTEXT = "LURES inbound relay: defector green for handoff"
CIPHERS = (CipherLayer(key=b"VALENKA", seed=3), CipherLayer(key=b"GRANT", seed=5))
#: Clean-channel SNR (dB) — lossless byte recovery at and above ~60 dB.
SNR_DB = 80.0

# --- Entrapment / bait allocation -------------------------------------------
BAIT_PROFILE_IDS: tuple[str, ...] = (
    "honey-trap-alpha",
    "relay-decoy-7",
    "cipher-clerk-config-3",
)
ENGAGEMENT_THRESHOLD = 0.5
#: The lure campaign's fixed strength (bait allocation and bite surface).
ALLOC_LURE_STRENGTH = 0.6
#: Lure budget (integer capacity units) for the knapsack allocation.
ALLOC_BUDGET = 5
ALLOC_TARGETS: tuple[Target, ...] = (
    Target("t1", susceptibility=0.3, value=8.0, lure_cost=1),
    Target("t2", susceptibility=0.9, value=5.0, lure_cost=2),
    Target("t3", susceptibility=0.6, value=10.0, lure_cost=1),
    Target("t4", susceptibility=0.2, value=4.0, lure_cost=1),
    Target("t5", susceptibility=0.8, value=7.0, lure_cost=2),
    Target("t6", susceptibility=0.5, value=6.0, lure_cost=1),
)

#: A *witness* target pool on which the profit-density greedy heuristic is
#: strictly worse than the exact knapsack. The canonical pool above does not
#: separate the two solvers — greedy happens to find the optimum there — so the
#: manuscript's separation claim is measured on this instance instead of on a
#: tie. Greedily-picked W2 (value 7, cost 3) blocks W1 (value 10, cost 5);
#: the optimum is W1 alone.
GREEDY_WITNESS_TARGETS: tuple[Target, ...] = (
    Target("W1", susceptibility=1.0, value=10.0, lure_cost=5),
    Target("W2", susceptibility=1.0, value=7.0, lure_cost=3),
    Target("W3", susceptibility=1.0, value=6.0, lure_cost=3),
)
GREEDY_WITNESS_BUDGET = 5
GREEDY_WITNESS_LURE_STRENGTH = 0.5

# --- SIGINT direction finding (TDOA) ----------------------------------------
#: Four fixed intercept sites at the corners of a 20 x 20 grid.
TDOA_RECEIVERS: tuple[Receiver, ...] = (
    Receiver("A", (0.0, 0.0)),
    Receiver("B", (20.0, 0.0)),
    Receiver("C", (20.0, 20.0)),
    Receiver("D", (0.0, 20.0)),
)
#: The true transmitter position the mission tries to recover.
TDOA_TRANSMITTER: tuple[float, float] = (7.0, 9.0)
TDOA_SPEED = 1.0
#: Timing noise (s) added to the TDOA measurements.
TDOA_NOISE_STD = 0.1
TDOA_SEED = 11

# --- Defector handoff -------------------------------------------------------
CALL_SIGNS: tuple[str, ...] = ("ROZA", "KLEBB", "DELILAH")
HANDOFF_CALL_SIGN = "ROZA"
CHALLENGE = "the cow jumped over the moon"
#: Rendezvous windows; M2 cannot fit after M4 (non-trivial -> unscheduled).
RENDEZVOUS: tuple[Rendezvous, ...] = (
    Rendezvous("M1", earliest=0.0, latest=10.0, duration=1.5),
    Rendezvous("M2", earliest=2.0, latest=6.0, duration=1.5),
    Rendezvous("M3", earliest=5.0, latest=12.0, duration=2.0),
    Rendezvous("M4", earliest=3.0, latest=5.0, duration=2.0),
    Rendezvous("M5", earliest=8.0, latest=14.0, duration=1.0),
)
SCHEDULE_START = 0.0
