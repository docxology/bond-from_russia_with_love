# Results

All figures and numbers below are produced live by the package's engines and
injected as generated tokens; none are hand-authored. Regenerating the token map
with `scripts/z_generate_manuscript_variables.py` regenerates every quantity
in this section.

## 3.0 At a glance

| Engine | Headline measured quantity | Value |
|---|---|---|
| Entrapment | bite probability | {{LURES_BITE_PROBABILITY}} |
| Allocation (exact) | expected engagement value | {{LURES_ALLOC_VALUE}} |
| Allocation (greedy baseline) | expected value | {{LURES_GREEDY_VALUE}} |
| Allocation | exact-minus-greedy gap (canonical / witness) | {{LURES_GREEDY_GAP}} / {{LURES_WITNESS_GAP}} |
| SIGINT | recovered plaintext exact | {{LURES_RECOVERED_EXACT}} |
| SIGINT | empirical SNR | {{LURES_EMPIRICAL_SNR_DB}} dB |
| SIGINT | transmission bursts segmented | {{LURES_BURST_COUNT}} |
| Direction finding | realised localisation error | {{LURES_TDOA_ERROR}} |
| Direction finding | Cramér–Rao RMS bound | {{LURES_TDOA_CRLB}} |
| Courier (heuristic) | completed meets | {{LURES_SCHEDULE_COUNT}} |
| Courier (exact) | optimum completes | {{LURES_SCHEDULE_OPTIMUM}} |
| Courier | heuristic gap (canonical / witness) | {{LURES_SCHEDULE_GAP}} / {{LURES_SCHEDULE_WITNESS_GAP}} |
| Handoff | green state / red-path state | {{LURES_HANDOFF_STATE}} / {{LURES_RED_PATH_STATE}} |

Every cell is a generated token — a live output of the corresponding engine —
so the table cannot drift from the code that produces it.

## 3.1 Lure effectiveness and allocation

For the fixed lure campaign `honey-trap-alpha`, the computed bite probability
is **{{LURES_BITE_PROBABILITY}}** against an engagement threshold of
**{{LURES_ENGAGEMENT_THRESHOLD}}**, and the trap resolved to
**{{LURES_FINAL_STAGE}}**.

Across the analytical pool of **{{LURES_ALLOC_TARGETS}} targets** at lure
strength **{{LURES_ALLOC_LURE_STRENGTH}}**, the exact knapsack allocation
spent **{{LURES_ALLOC_CHOSEN}} of {{LURES_ALLOC_BUDGET}} budget units**
(utilization **{{LURES_ALLOC_UTILIZATION}}%**) across
**{{LURES_ALLOC_COUNT}} targets**, for an expected engagement value of
**{{LURES_ALLOC_VALUE}}**. The profit-density greedy baseline reached
**{{LURES_GREEDY_VALUE}}** on the same instance — a measured gap of
**{{LURES_GREEDY_GAP}}**.

That gap is zero: on the canonical target pool the cheap heuristic finds the
optimum, and this instance therefore **separates the two solvers not at all**
(greedy ties: **{{LURES_GREEDY_TIES_ON_CANONICAL}}**). We state that plainly
rather than reporting the inequality $\text{exact} \ge \text{greedy}$ as a
finding: that inequality is a theorem about the exact solver, not a property
of this scenario, and it could only come out false if the knapsack
implementation were broken. Reporting it as a result would be green by
construction.

The separation is instead measured where it exists. On the witness pool of
§2.2 — **{{LURES_WITNESS_TARGETS}}** targets under a budget of
**{{LURES_WITNESS_BUDGET}}**, deliberately constructed so that a
profit-density pick blocks the optimal one — the exact allocation reaches
**{{LURES_WITNESS_EXACT_VALUE}}** against the greedy
**{{LURES_WITNESS_GREEDY_VALUE}}**, a strictly positive gap of
**{{LURES_WITNESS_GAP}}**. That is the falsifiable claim: were the exact
solver merely greedy in disguise, this gap would collapse to zero, and the
test suite pins it.

![LURE surface: bite probability vs. lure strength and target susceptibility.](output/figures/lure_surface.png){#fig:lure_surface}

## 3.2 SIGINT interception

A **{{LURES_MESSAGE_BYTES}}-byte** message was enciphered under
**{{LURES_CIPHER_LAYERS}}** keystream layers and intercepted at a requested
**{{LURES_SNR_DB}} dB**; the empirical SNR measured against ground truth was
**{{LURES_EMPIRICAL_SNR_DB}} dB**. The recovered plaintext matched the
transmitted message exactly: **{{LURES_RECOVERED_EXACT}}**. The decided
capture carried **{{LURES_TRAFFIC_DISTINCT}} distinct symbol values** and its
energy envelope segmented into **{{LURES_BURST_COUNT}} transmission
burst(s)**.

## 3.3 Direction finding

With **{{LURES_NUM_RECEIVERS}}** intercept sites at
**{{LURES_TDOA_RECEIVER_COORDS}}**, a true transmitter at
**{{LURES_TDOA_TRANSMITTER}}**, and seeded timing noise of standard deviation
**{{LURES_TDOA_NOISE_STD}}**, the TDOA Gauss–Newton estimator converged
(**{{LURES_TDOA_CONVERGED}}**) in **{{LURES_TDOA_ITERATIONS}}** iterations to a
transmitter localisation error of **{{LURES_TDOA_ERROR}} receiver coordinate
units**.

The units matter. `localization_error()` returns a raw Euclidean distance in
the coordinate system the receivers are declared in — it is not normalised by
the array geometry. The smallest distance between two intercept sites is
**{{LURES_TDOA_SITE_SPACING}}** coordinate units, so the same error expressed
as a fraction of the site spacing is **{{LURES_TDOA_ERROR_SPACINGS}}**. Both
numbers are generated from the same computation; only the second one is "in
units of site spacing".

A useful uncertainty framing is the **Cramér–Rao lower bound** on the position
error — the theoretical best achievable RMS accuracy given the receiver
geometry and the timing noise, computed from the Fisher information matrix at
the true transmitter position (see `direction_finding.py::crlb_error`). For
the canonical array and `{{LURES_TDOA_NOISE_STD}}` s timing noise, that bound
is **{{LURES_TDOA_CRLB}}** coordinate units. The realised Gauss–Newton estimate
achieved an error of **{{LURES_TDOA_ERROR}}**, which is
**{{LURES_TDOA_ERROR_ABOVE_CRLB}}** above that bound. This is honest
uncertainty quantification rather than a single point claim: the CRLB is a
bound on achievable *variance* across draws, so one particular noise
realisation may land on either side of it (as it does here), and a degenerate
array with no finite accuracy has an infinite bound rather than a fabricated
confidence.

![TDOA geometry: intercept sites, true transmitter, and estimate.](output/figures/tdoa_geometry.png){#fig:tdoa_geometry}

## 3.4 Handoff scheduling

Of **{{LURES_SCHEDULE_TOTAL}}** candidate rendezvous, the
earliest-deadline-first heuristic completed **{{LURES_SCHEDULE_COUNT}}**,
finishing at time **{{LURES_SCHEDULE_FINISH}}**. The exact subset dynamic
program of §2.5 puts the true maximum at **{{LURES_SCHEDULE_OPTIMUM}}**, so
the heuristic's cost on this instance is a gap of **{{LURES_SCHEDULE_GAP}}**
meets. The heuristic is not optimal in general — §2.5 describes the family of
instances on which it loses, and the test suite pins a concrete one — so this
gap is a measured property of the canonical scenario, not a guarantee about
the algorithm.

That canonical gap is zero, and we say so plainly: on `scenario.RENDEZVOUS` the
heuristic genuinely reaches the optimum, so this instance separates the two
solvers not at all. Where the scheduler's sub-optimality is *visible* is the
witness instance of §2.5 (`scenario.SCHEDULE_WITNESS`), deliberately built so a
long, slack window sorts first and crowds out two short meets. On that
instance the heuristic can complete **{{LURES_SCHEDULE_WITNESS_COUNT}}** of
**{{LURES_SCHEDULE_WITNESS_TOTAL}}** rendezvous against a true optimum of
**{{LURES_SCHEDULE_WITNESS_OPTIMUM}}** — a strictly positive gap of
**{{LURES_SCHEDULE_WITNESS_GAP}}** meet, pinned by the test suite. Reporting
both instances is the honest version of the claim: the exact solver is
necessary precisely when the problem is hard, and the canonical scenario is
the easy case where the cheap heuristic happens to be optimal.

## 3.5 Defector handoff protocol

The green-pathed handoff for the mission call sign completed in state
**{{LURES_HANDOFF_STATE}}**, gated on confirm code
**{{LURES_CONFIRM_CODE}}**. The red-path drill — the identical protocol run
given a deliberately wrong confirm code — ended in
**{{LURES_RED_PATH_STATE}}**, confirming that only the exact code completes a
handoff, and that a failed confirm is an ordinary terminal outcome rather
than an exception.
