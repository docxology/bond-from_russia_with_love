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

## 2.2 Lure-budget allocation

Given a pool of analytical targets each carrying an operational value $v_i$,
a susceptibility $s_i$, and a lure cost $c_i$, the mission decides which
targets to lure under a fixed budget $B$. The profit of luring target $i$
with a campaign of strength $q$ is its *expected engagement value*

$$
\text{profit}_i = v_i \cdot p(q, s_i),
$$

and the allocation is the exact **0/1 knapsack**

$$
\max \sum_i \text{profit}_i \cdot x_i \quad \text{s.t.} \quad
\sum_i c_i x_i \le B,\; x_i \in \{0,1\},
$$

solved by dynamic programming (@martello1990knapsack). A
profit-per-unit greedy heuristic is computed as the baseline; the exact
solution always dominates it.

## 2.3 SIGINT channel interception simulation

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
against ground truth. An energy-threshold **burst segmentation** splits the
captured envelope into transmission bursts so the interceptor knows when, and
for how long, the channel was active.

## 2.4 TDOA direction finding

Four fixed intercept sites record the arrival of a single interception burst,
and the mission geolocates the transmitter by **time-difference-of-arrival**
hyperbolation (@chan1994hyperbolic). For receiver pairs $(i,j)$ with measured
TDOAs $\tau_{ij}$,

$$
h_{ij}(x) = \frac{\|x - r_i\| - \|x - r_j\|}{c},
$$

and the transmitter position is the non-linear least-squares minimiser of
$\sum_{ij} (h_{ij}(x) - \tau_{ij})^2$, solved by a deterministic
Gauss–Newton iteration from the receiver centroid. Timing noise is seeded, so
the same scenario always yields the same estimate.

## 2.5 Courier handoff scheduling

A courier must visit defector-handoff rendezvous, each occupying a fixed
duration $d_i$ somewhere inside a time window $[e_i, l_i]$, and can attend
only one meet at a time. Maximising the number of completed meets is the
single-machine throughput problem with release times and deadlines,
$1 \mid r_j, d_j \mid \sum U_j$, which is strongly NP-hard
[@garey1979computers]. The package therefore ships two solvers and reports the
distance between them instead of claiming a cheap algorithm is also optimal.

The **heuristic** — the plan the mission executes — is earliest-deadline-first:
windows are ordered by latest feasible start $l_i - d_i$ and each is taken when
it still fits after the courier's current position, in the spirit of the
classical interval-scheduling greedy [@kleinberg2005algorithm]. It is linear
after the sort, but it is genuinely sub-optimal in general: a long, slack
window sorts first and can crowd out two short meets that together would have
scored higher. A concrete instance exhibiting this is pinned in the test suite.

The **exact optimum** is a dynamic program over subsets. Writing
$T(S)$ for the earliest time by which every meet in $S \subseteq \{1..n\}$ can
have been completed,

$$
T(\emptyset) = t_0, \qquad
T(S \cup \{j\}) = \min_{S} \; \bigl(\max(T(S), e_j) + d_j\bigr)
$$

over those $j \notin S$ with $\max(T(S), e_j) \le l_j - d_j$, and the answer is
the largest $|S|$ with $T(S)$ defined. Because feasibility of any extension is
monotone in the current time, retaining only the earliest completion time per
subset loses no optimal solution, so this is the true maximum rather than a
bound. It runs in $O(2^n n)$ and is bounded to small instances by construction.

Section 03 reports the heuristic count, the exact optimum, and their gap as
three separately computed tokens.

## 2.6 Defector handoff protocol

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
code lands the protocol in `ABORT` (the red-path drill).
