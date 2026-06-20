# O1.1 — Unique Scalar Timeline Criterion

## Statement

For distinct persistent-record signatures, all clock labels can be emitted as one
scalar timeline iff the quotient record-poset is total. In implementation terms,
`scalar_time_identifiable` is true only when:

1. every pair of quotient signatures is comparable under coordinate-wise dominance;
2. no original labels were collapsed by duplicate signatures.

## Necessity

If one scalar persistent trajectory visits every label, then every adjacent step
is nondecreasing in every persistent record coordinate. Transitivity gives
coordinate-wise comparability for every pair on that trajectory, so the quotient
poset is total.

Duplicate signatures violate label identifiability: two clock labels have the
same operational record signature. They may be quotient-comparable, but they are
not nondegenerate scalar clock states.

## Sufficiency

If the quotient poset is total and signatures are nonduplicate, the unique
topological order of the Hasse DAG orders every label by nondecreasing persistent
records. That order is the scalar timeline.

## Regression Fixtures

- Thermometer code: emits `("0", "1", "2", "3")`.
- Diamond code: emits no scalar timeline; it has two physical maximal chains.
- Duplicate code: emits no scalar timeline because label identification fails.
- Disconnected/incomparable code: emits no scalar timeline because the quotient
  poset is not total.
