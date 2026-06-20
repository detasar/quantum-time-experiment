# Claims Register

Authoritative machine-readable output: `results/claim_evidence_matrix.csv`.

Evidence grades:

- `P`: proven analytically.
- `E`: exact exhaustive or deterministic computation.
- `S`: stochastic simulation.
- `Q`: quantum hardware observation.
- `I`: interpretation or inference.
- `N`: negative/no-go result.

Current A601 status: every planned claim has at least one evidence artifact, one
explicit evidence check and one caveat. Q1 and Q2 now have Q-grade evidence from
the completed preregistered H501/H502/H503 IBM observation. The Q-grade rows are
four-qubit illustrations only; the theorem-level contribution remains the
classical/symbolic basis--order--orientation package.

| ID | Evidence grade | Current status | Novelty status | Caveat |
|---|---:|---|---|---|
| B0 | P;E | imported_prior_art_with_local_validation | Imported; not a project novelty claim | Fixed-partition and nondegeneracy assumptions are mandatory. |
| O1 | P;E | supported | Central formalization | The statement is about persistent-record codes, not arbitrary physical dynamics. |
| O2 | P;E | supported | Clock-specific interpretation | Linear extensions are scheduler totalizations, not physical time trajectories. |
| O3 | P;E | supported | Simple exact capacity bound | Capacity bound applies to strict persistent scalar trajectories. |
| O4 | P;E;S | supported | Applied concentration bound | Independent-copy and p<1/2 assumptions are required. |
| N1 | N;E | supported_no_go | Boundary result | External label anchoring can add order information; redundancy alone cannot. |
| N2 | N;E | supported_no_go | Boundary result | The no-go excludes orientation from basis objectivity alone. |
| N3 | N;P;E | supported_no_go | Known-adjacent no-go | This is a boundary condition on admissible physical partitions. |
| Q1 | P;E;S;Q | supported_with_hardware | Illustration only | Q-grade evidence is a four-qubit IBM illustration only; the theorem-level contribution remains the classical/symbolic result. |
| Q2 | P;E;S;Q | supported_with_hardware | Boundary illustration | The hardware contrast uses the preregistered GHZ+ and GHZ- parity mixture construction; it is an illustration, not an independent proof. |
