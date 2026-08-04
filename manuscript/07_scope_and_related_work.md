# Scope and Related Work

## Scope

LURES is an analytical, deterministic mission model — not a real-world
targeting or deception tool. The entrapment engine models lure effectiveness
as a decision surface for defensive countermeasure evaluation; the knapsack
allocation and courier scheduler are combinatorial optimisation on synthetic
records; the SIGINT and TDOA modules simulate channel interception and
geolocation for study; the handoff protocol is a state-machine fragment. It
performs no real signal capture, no real cryptanalysis of live systems, and
no targeting of persons.

## Related Work

- **BOND-API (THE PROTOCOL)** — the frozen `MissionProvider` contract this
  film implements (discovery, lifecycle, provenance).
- **BOND-UTILITIES (Q-BRANCH)** — the Layer-0 foundation (ciphers,
  codenames, provenance persistence, reporting) that downstream packages may
  bind to.
- **Combinatorial optimisation** — exact 0/1 knapsack via dynamic
  programming [@martello1990knapsack]; earliest-finish-first interval
  scheduling [@kleinberg2005algorithm].
- **Localisation** — hyperbolic (TDOA) position estimation by Gauss–Newton
  least squares, following the estimator of Chan & Ho [@chan1994hyperbolic].
- Classical cipher and channel models underpinning the SIGINT module draw on
  the elementary XOR keystream (one-time-pad style) and additive white
  Gaussian noise channel model.
