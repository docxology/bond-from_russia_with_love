# Results

All figures and numbers below are produced live by the package's engines and
injected as generated tokens; none are hand-authored. Regenerating the token map
with `scripts/z_generate_manuscript_variables.py` regenerates every quantity
in this section.

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
**{{LURES_GREEDY_VALUE}}** on the same instance, and the exact solution
dominates it: **{{LURES_OPTIMAL_DOMINATES_GREEDY}}**.

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

With **{{LURES_NUM_RECEIVERS}}** intercept sites and seeded timing noise of
standard deviation **{{LURES_TDOA_NOISE_STD}}**, the TDOA Gauss–Newton
estimator converged (**{{LURES_TDOA_CONVERGED}}**) in
**{{LURES_TDOA_ITERATIONS}}** iterations to a transmitter localisation error
of **{{LURES_TDOA_ERROR}}** (units of site spacing).

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

## 3.5 Defector handoff protocol

The green-pathed handoff for the mission call sign completed in state
**{{LURES_HANDOFF_STATE}}**, gated on confirm code
**{{LURES_CONFIRM_CODE}}**. The red-path drill — the identical protocol run
given a deliberately wrong confirm code — ended in
**{{LURES_RED_PATH_STATE}}**, confirming that only the exact code completes a
handoff, and that a failed confirm is an ordinary terminal outcome rather
than an exception.
