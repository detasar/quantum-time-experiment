# ADR-000: Semantic Freeze

## Status
Accepted for implementation v1.0.

## Decisions

1. `stationary history` means one global static encoding, not hardware thermodynamic stationarity.
2. `candidate clock basis` is a PVM on subsystem C; it is not automatically a complete physical clock.
3. `objective` means redundantly and separately locally accessible under a fixed admissible partition.
4. `persistent record` requires a physically anchored blank/present semantics and no allowed silent erasure.
5. A persistent trajectory is a **chain** in the record-poset.
6. A linear extension of a branching record-poset is a scheduler totalization, not generally a physical trajectory.
7. Scalar time is emitted only when all relevant clock states form a chain.
8. IBM GHZ data are illustrative and cannot prove the analytical theorems.

## Consequences

Any change to these meanings requires a new ADR and invalidates downstream preregistration hashes.

## G0/G1 Implementation Check

The implementation exposes this freeze through `scalar_time_identifiable` and
`scalar_timeline`: scalar time is unavailable for branching, duplicate or
incomparable record signatures. Linear-extension counts are retained only as
scheduler/gauge diagnostics.
