# Methodology

## 2.1 Entrapment / deception playbook engine

The engine models lure effectiveness analytically (a defensive
countermeasure; it does not target any person). A **bait profile**
describes a lure's cover role, intended target susceptibility $s \in [0,1]$,
payload message, and lure strength $q \in [0,1]$. The probability that a
target "bites" the lure is a bounded logistic decision surface:

$$
p(q, s) = \frac{1}{1 + e^{-4(q + s - 1)}} .
$$

$p$ is strictly increasing in both arguments, so stronger lures and more
susceptible targets both raise effectiveness. A **trap state machine** drives
the life-cycle of one lure campaign through the validated transitions

$$
\text{DISARMED} \to \text{ARMED} \to \text{BAITED} \to \text{ENGAGED} \to \text{SPRUNG}
$$

with a single terminal $\text{ABORTED}$ reachable from several stages; any
event not in the transition table raises an error and leaves state unchanged.

## 2.2 SIGINT channel interception simulation

Transmitted symbols are the byte magnitudes of the message, optionally
enciphered by **layered XOR keystream ciphers**. Each layer derives a
deterministic keystream from its key and a seed. The transmitted symbol
vector $x$ is observed through additive Gaussian noise whose variance
follows a requested signal-to-noise ratio:

$$
\text{SNR}_{\text{dB}} = 10 \log_{10} \frac{\mathbb{E}[x^2]}{\sigma^2} .
$$

The interceptor rounds each noisy sample to the nearest symbol, deciphers in
reverse cipher order, and measures the **empirical SNR** of the capture
against ground truth. Traffic profiling (channel width, peak symbol)
supports downstream triage.

## 2.3 Defector handoff protocol

A handoff is a deterministic state machine over

$$
\text{DISARM} \to \text{MEET} \to \text{CHALLENGE} \to \text{CONFIRM} \to \text{HANDOFF},
$$

with a terminal $\text{ABORT}$ reachable from every active stage. The
confirm code is derived from the challenge and call sign via SHA-256:

$$
\text{confirm} = \text{hex}(\text{SHA256}(\text{call\_sign} : \text{challenge}))[0:6].
$$

Only an exact confirm-code match advances to `CONFIRM`; any other confirm
code lands the protocol in `ABORT`.
