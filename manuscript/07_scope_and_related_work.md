# Scope and Related Work

## Scope

LURES is an analytical, deterministic mission model — not a real-world
targeting or deception tool. The entrapment engine models lure effectiveness
as a decision surface for defensive countermeasure evaluation; the knapsack
allocation and courier scheduler are combinatorial optimisation over synthetic
records; the SIGINT and TDOA modules simulate channel interception and
geolocation for study; the handoff protocol is a state-machine fragment. The
package performs no real signal capture, no cryptanalysis of live systems, and
no targeting of persons.

The XOR keystream cipher in `sigint.py` is a *pedagogical* construction for
producing a scrambled symbol stream to intercept. It derives its keystream
from a seeded PRNG, which makes it reproducible and completely unsuitable as
cryptography; nothing in this package should be read as a security claim about
the cipher.

Two further boundaries are worth stating plainly. First, the courier scheduler
is a heuristic and is not optimal (§2.5); the exact solver exists to measure
that gap, not to be run at scale, and refuses instances beyond its documented
size bound. Second, the bite-probability surface is a modelling *choice* — a
bounded logistic in strength and susceptibility — not an empirically fitted
model of anything, and its parameters are not calibrated against data.

## Uncertainty and limitations

Beyond the boundaries above, the package reports its uncertainty honestly
rather than implying that a deterministic single number is a confident one:

- **TDOA localisation uncertainty is quantified, not asserted away.** §3.3
  reports both the realised estimate error and the Cramér–Rao lower bound
  (`{{LURES_TDOA_CRLB}}`) for the same geometry and timing noise. The CRLB is a
  bound on achievable *variance*, so a single seeded realisation can land on
  either side of it (the canonical realisation lands below it,
  `{{LURES_TDOA_ERROR_ABOVE_CRLB}}`); a degenerate array has an infinite bound.
  The numbers are generated, not fitted, to a particular noise draw.
- **The seeding fixes the realisation, not the distribution.** Every quantity
  that is stochastic under the model — the SIGINT capture noise, the TDOA
  timing noise, the lure generation — is the outcome of one committed seed
  (`scenario.SEED`). Regeneration is byte-identical by construction, but a
  *different* seed would produce a *different* realisation of the same
  underlying distribution. The manuscript therefore reports what was actually
  computed, never a resample.
- **Both optimality gaps are measured, and may be zero.** The canonical
  allocation pool and the canonical rendezvous set both fail to separate the
  exact solver from its heuristic (gaps `{{LURES_GREEDY_GAP}}` and
  `{{LURES_SCHEDULE_GAP}}`); the separation is only visible on the witness
  instances (`{{LURES_WITNESS_GAP}}` and `{{LURES_SCHEDULE_WITNESS_GAP}}`).
  Reporting the zero as zero prevents the exact solvers from being dressed up
  as necessary where they are not.
- **The decipherability result is a high-SNR, seed-specific outcome.** At
  `{{LURES_SNR_DB}}` dB the recover is exact (`{{LURES_RECOVERED_EXACT}}`) on
  this draw; below some SNR ceiling byte recovery would fail. The package makes
  no claim about performance at low SNR.
- **The XOR keystream cipher is pedagogical.** It is derived from a seeded PRNG
  and is unsuitable as cryptography (§2.3). Nothing here is a security claim.

## Related Work

- **BOND-API (THE PROTOCOL)** — the frozen `MissionProvider` contract this
  film implements (discovery, lifecycle, provenance) [@bond_api].
- **BOND-UTILITIES (Q-BRANCH)** — the Layer-0 foundation (ciphers, codenames,
  provenance persistence, reporting) that downstream packages may bind to
  [@bond_utilities].
- **Combinatorial optimisation** — exact 0/1 knapsack via dynamic programming
  [@martello1990knapsack], on the classical dynamic-programming formulation
  [@bellman1957dynamic]; interval-scheduling greedy algorithms
  [@kleinberg2005algorithm]. The scheduling problem solved here,
  $1 \mid r_j, d_j \mid \sum U_j$, is strongly NP-hard
  [@garey1979computers], which is why the package pairs a heuristic with an
  exact subset dynamic program rather than claiming optimality.
- **Localisation** — hyperbolic (TDOA) position estimation. The solver
  implemented in `direction_finding.py` is the **iterative Taylor-series /
  Gauss–Newton** estimator [@foy1976position; @torrieri1984statistical],
  i.e. the standard non-linear least-squares iteration
  [@nocedal2006numerical] applied to the pair TDOA residuals from a receiver
  centroid start. It is *not* the Chan & Ho estimator
  [@chan1994hyperbolic]: that is a **closed-form, non-iterative** two-stage
  weighted least-squares solution, published as an alternative to exactly the
  iterative scheme used here. Chan & Ho is listed as related work, and this
  package does not implement it.
- **Channel and cipher models** — the additive white Gaussian noise channel
  and symbol-decision model follow standard digital-communications treatment
  [@proakis2008digital]; the keystream construction is an elementary
  one-time-pad-style XOR stream in the sense of Shannon's secrecy analysis
  [@shannon1949secrecy]. The handoff confirm code uses SHA-256 as specified in
  the NIST secure hash standard [@nist2015fips180].
- **Decision surface** — the logistic response model used for bite
  probability is the classical binary-response form [@cox1958regression].
- **Source material** — Ian Fleming's novel [@fleming1957russia], of which the
  1963 film is an adaptation.
