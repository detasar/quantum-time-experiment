# Preregistration Template — IBM Four-Qubit Illustration

**Status:** DRAFT — QPU execution prohibited  
**Project:** Objective Clock Bases from Redundant Records  
**Primary scientific role:** illustration of objective local basis versus global coherence; not a proof of the theory.

## 1. Mandatory identifiers

- Git commit: `TBD`
- Environment archive SHA-256: `TBD`
- Circuit manifest SHA-256: `TBD`
- Qiskit version: `TBD`
- qiskit-ibm-runtime version: `TBD`
- Open Plan instance identifier/name: `TBD_PRIVATE`

## 2. Frozen logical roles

- C = logical qubit 0
- S = logical qubit 1
- R1 = logical qubit 2
- R2 = logical qubit 3

## 3. Science circuits

1. GHZ+ measured in Z
2. GHZ+ measured in X
3. GHZ− measured in Z
4. GHZ− measured in X

Four interleaved blocks, 1024 shots/circuit/block.

## 4. Readout calibration

Eight independent assignment circuits: each selected physical qubit prepared in 0 and 1; 1024 shots each.

## 5. Backend and layout selection

Use the deterministic algorithm in `RESEARCH_SPEC_TR.md`. No manual backend substitution after science results are known.

Selected backend: `TBD`  
Calibration snapshot timestamp: `TBD`  
Selected physical layout: `TBD`  
Selected transpiler seed: `TBD`

## 6. Primary endpoints

\[
\Delta_{obj}=\min(C_{Z,1},C_{Z,2})-\max(|C_{X,1}|,|C_{X,2}|)
\]

\[
\Delta_{coh}=|W_+|-|W_{mix}|,
\qquad W_{mix}=\frac{W_++W_-}{2}.
\]

## 7. Main-text inclusion rule

All must pass on raw results:

- LCB95(delta_obj) > 0.40
- LCB95(min(C_Z1,C_Z2)) > 0.60
- LCB95(delta_coh) > 0.30
- GHZ− global X parity has the expected negative sign
- no single block supplies more than half of the total contrast
- raw and readout-corrected analyses have the same qualitative conclusion

## 8. Statistical method

- Individual Pauli correlations: Clopper–Pearson interval after mapping ±1 products to Bernoulli outcomes.
- Nonlinear contrasts: stratified shot bootstrap, 10,000 replicates, frozen seed 20260621.
- Primary alpha: 0.05.

## 9. Mitigation

- Primary: raw data.
- Secondary: tensor-product readout assignment correction.
- No ZNE, PEC, result-driven postselection, or shot deletion.

## 10. Rerun policy

A rerun is permitted only for provider-declared failed/cancelled jobs, missing provider payload, circuit-hash mismatch, or provider-confirmed service incident. Weak or null scientific results do not permit a rerun.

## 11. Positive and null interpretations

- Objectivity + coherence pass: include main-text quantum illustration.
- Objectivity passes, coherence fails: classical-record illustration only; quantum coherence claim omitted.
- Both fail: hardware null; theory remains evaluated independently.

## 12. Freeze declaration

Mandatory fields contain no `TBD`: `NO`  
Human approval: `NO`  
Status may become `FROZEN` only after all G4 tasks pass.
