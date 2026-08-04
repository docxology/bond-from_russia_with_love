# Results

All figures and numbers below are produced live by the package's engines;
none are hand-authored.

## 3.1 Lure effectiveness

For the fixed lure campaign `honey-trap-alpha` evaluated at
threshold = 0.5, the computed bite probability is **{{LURES_BITE_PROBABILITY}}**
and the trap resolved to **{{LURES_FINAL_STAGE}}**.

![LURE surface: bite probability vs. lure strength and target susceptibility.](output/figures/lure_surface.png){#fig:lure_surface}

As @fig:lure_surface shows, the bite probability rises monotonically with
lure strength and target susceptibility.

## 3.2 SIGINT interception

The fixed encoded channel was intercepted at **{{LURES_SNR_DB}} dB**. The
recovered plaintext matched the transmitted message exactly:
**{{LURES_RECOVERED_EXACT}}**.

## 3.3 Defector handoff

The green-path handoff for the mission call sign completed in state
**{{LURES_HANDOFF_STATE}}**, gated on confirm code **{{LURES_CONFIRM_CODE}}**.
