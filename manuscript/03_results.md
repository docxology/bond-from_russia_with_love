# Results

All figures and numbers below are produced live by the package's engines;
none are hand-authored.

## 3.1 Lure effectiveness and allocation

For the fixed lure campaign `honey-trap-alpha`, the computed bite probability
is **{{LURES_BITE_PROBABILITY}}** and the trap resolved to
**{{LURES_FINAL_STAGE}}**. Against a pool of {{LURES_NUM_BAIT_PROFILES}}
profiles at lure strength, the exact knapsack allocation used
**{{LURES_ALLOC_CHOSEN}} of {{LURES_ALLOC_BUDGET}} budget units** for an
expected value of **{{LURES_ALLOC_VALUE}}** (utilization
**{{LURES_ALLOC_UTILIZATION}}%**); the exact allocation dominates the greedy
baseline: **{{LURES_OPTIMAL_DOMINATES_GREEDY}}**.

![LURE surface: bite probability vs. lure strength and target susceptibility.](output/figures/lure_surface.png){#fig:lure_surface}

## 3.2 SIGINT interception

The fixed encoded channel was intercepted at **{{LURES_SNR_DB}} dB**. The
recovered plaintext matched the transmitted message exactly:
**{{LURES_RECOVERED_EXACT}}**, and the capture was segmented into
**{{LURES_BURST_COUNT}} transmission burst(s)**.

## 3.3 Direction finding

With {{LURES_NUM_RECEIVERS}} intercept sites and seeded timing noise, the
TDOA Gauss–Newton estimator converged (**{{LURES_TDOA_CONVERGED}}**) to a
transmitter localisation error of **{{LURES_TDOA_ERROR}}** (units of site
spacing).

![TDOA geometry: intercept sites, true transmitter, and estimate.](output/figures/tdoa_geometry.png){#fig:tdoa_geometry}

## 3.4 Handoff scheduling and protocol

The courier completed **{{LURES_SCHEDULE_COUNT}} of
{{LURES_SCHEDULE_TOTAL}}** handoff rendezvous within their time windows. The
green-pathed handoff for the mission call sign completed in state
**{{LURES_HANDOFF_STATE}}**, gated on confirm code
**{{LURES_CONFIRM_CODE}}**; the red-path drill (a deliberately wrong confirm)
ended in **{{LURES_RED_PATH_STATE}}**, confirming that only the exact code
completes a handoff.
