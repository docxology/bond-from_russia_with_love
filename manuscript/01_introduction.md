# Introduction

Mission codename **LURES** implements the operational concepts behind *From
Russia with Love* (1963) as a small, testable mission-software package. It
sits alongside {{LURES_NUM_BAIT_PROFILES}} bait profiles, a SIGINT cipher
stack, and a defector handoff challenge — the machinery a field cell needs to
run a deception campaign, read an intercepted channel, and complete a source
handoff.

The package is built to the shared guardrails of the PROJECT BOND suite:
pure domain core (no infrastructure imports), a thin adapter to the frozen
BOND-API `MissionProvider` protocol, deterministic computation with no mock
framework, and >=90% line-and-branch coverage on `src/`. This document's
reader's guide:

- Section 02 — the three analytical models and their mathematics.
- Section 03 — live measured results and the figure.
- Section 05 — the experimental setup (parameters + software).
- Section 06 — reproducibility and the artifact inventory.
