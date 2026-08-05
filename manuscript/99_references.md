# References

Suite packages this film binds to:

- [@bond_api]
- [@bond_utilities]

Models implemented by this package:

- [@foy1976position] — iterative Taylor-series / Gauss–Newton TDOA position
  location, the estimator implemented in `direction_finding.py`
- [@torrieri1984statistical] — iterative least-squares passive location
- [@nocedal2006numerical] — Gauss–Newton non-linear least squares
- [@martello1990knapsack] — 0/1 knapsack (`bait_allocation.py`)
- [@bellman1957dynamic] — dynamic programming
- [@kleinberg2005algorithm] — greedy interval scheduling
  (`courier_schedule.py`)
- [@garey1979computers] — NP-hardness of sequencing with release times and
  deadlines, the reason the scheduler ships an exact reference solver
- [@proakis2008digital] — AWGN channel and symbol decision (`sigint.py`)
- [@shannon1949secrecy] — secrecy analysis of keystream ciphers
- [@nist2015fips180] — SHA-256 (`handoff_protocol.py`)
- [@cox1958regression] — logistic binary-response model
  (`entrapment_engine.py`)

Related work *not* implemented by this package:

- [@chan1994hyperbolic] — closed-form two-stage weighted least-squares
  hyperbolic location; an alternative to the iterative estimator used here,
  and not the source of `direction_finding.py`

Source material:

- [@fleming1957russia]
