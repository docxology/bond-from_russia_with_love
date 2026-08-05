# Introduction

Mission codename **LURES** implements the operational concepts behind *From
Russia with Love* (1963) as a small, testable mission-software package. The
film's plot is a deception operation: a fabricated defector and a stolen
cipher machine are used as bait, a radio channel carries the traffic that
gives the operation away, and the whole thing turns on a handoff that only
completes when both sides produce the right recognition signal. Those are the
three things this package computes — luring, listening, and handing over — and
each is expressed as an algorithm rather than as narrative.

The analytical core is {{LURES_NUM_OBJECTIVES}} deterministic engines:

1. an **entrapment playbook** that scores lure effectiveness on a logistic
   decision surface and drives a validated trap state machine over
   {{LURES_NUM_BAIT_PROFILES}} bait profiles;
2. a **lure-budget allocator** that solves the exact 0/1 knapsack over an
   analytical target pool of {{LURES_ALLOC_TARGETS}} targets;
3. a **SIGINT interception** simulation that enciphers, transmits through a
   noisy channel, deciphers, and segments {{LURES_MESSAGE_BYTES}} bytes of
   traffic under {{LURES_CIPHER_LAYERS}} cipher layers;
4. a **TDOA direction finder** that geolocates the transmitter from
   {{LURES_NUM_RECEIVERS}} intercept sites by Gauss–Newton least squares;
5. a **courier scheduler** that fits defector-handoff rendezvous into their
   time windows and is scored against the exact optimum;
6. a **defector handoff protocol** whose confirm code gates the transfer.

The package is built to the shared guardrails of the PROJECT BOND suite: a
pure domain core with no infrastructure imports, a thin adapter to the frozen
BOND-API `MissionProvider` protocol, deterministic computation with no mock
framework, and a coverage floor of 90% line-and-branch on `src/`. Every
scenario constant lives in one module (`scenario.py`), so a number reported
here cannot disagree with the code that produced it.

Two of the six engines pair an exact solver with a cheap heuristic and report
the difference rather than assuming it away: the knapsack allocator against a
profit-density greedy baseline, and the courier scheduler against an exact
subset dynamic program. Section 03 reports both gaps as measured quantities.

## Reader's guide

- Section 02 — the six analytical models and their mathematics.
- Section 03 — live measured results and the two figures.
- Section 04 — what the package demonstrates.
- Section 05 — the experimental setup (parameters + software environment).
- Section 06 — reproducibility, determinism, and the artifact inventory.
- Section 07 — scope boundaries and related work.
