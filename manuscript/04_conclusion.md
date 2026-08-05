# Conclusion

LURES turns the operational fiction of a Cold-War deception mission into a
small, fully deterministic mission-software package. The
{{LURES_NUM_ENGINES}} engines — an entrapment playbook with a validated
trap state machine, an exact knapsack lure-budget allocation, a SIGINT
interception simulation with real cipher, noise and burst-segmentation models,
a TDOA Gauss–Newton transmitter geolocation, an earliest-deadline-first
handoff schedule, and a defector handoff protocol whose confirm code gates
completion — each compute a result rather than assert one. The same fixed
inputs always yield the same lure outcome, allocation, recovered plaintext,
localisation, schedule, and handoff path.

The package's more durable contribution is methodological rather than
narrative. Two of its engines solve problems where a cheap answer is available
and a correct one is expensive, and in both cases the package computes both
and publishes the difference: the knapsack allocator against a profit-density
greedy baseline, and the courier scheduler against an exact subset dynamic
program. Publishing the difference includes publishing it when it is zero — on
the canonical target pool the greedy allocator ties the exact knapsack, so
that instance demonstrates nothing about the exact solver's necessity, and the
separation is measured on an explicit witness instance instead. The scheduling
case is the sharper one, because the obvious greedy
ordering *looks* like the classical optimal interval-scheduling algorithm and
is not — the underlying problem becomes NP-hard once meets carry both release
times and deadlines. Reporting {{LURES_SCHEDULE_COUNT}} completed meets
against an optimum of {{LURES_SCHEDULE_OPTIMUM}} is a weaker-sounding claim
than reporting an optimal schedule, and it is the one the code can actually
support.

Every stage is reproducible, mock-free, and covered by a real-data test suite
above the package's 90% line-and-branch gate. Where a branch is defensive
rather than exercised — a singular Jacobian, a coincident intercept site — it
is documented as such rather than papered over with an artificial test.
