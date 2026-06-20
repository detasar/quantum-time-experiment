# Preregistration Draft Packet - IBM Four-Qubit Illustration

**Status:** DRAFT - QPU execution prohibited
**Generated from:** `scripts/run_h401_draft.py`
**Project:** Objective Clock Bases from Redundant Records
**Primary scientific role:** illustration of objective local basis versus global coherence; not a proof of the theory.

## 1. Mandatory Identifiers

- Git commit: `ff64028ae83dcccfa5ce68970a3b4a1f77061b1f`
- Environment manifest SHA-256: `a74da6121c14507ece144a78059ec3ae6a221b32aeb1e1e6ea9c7e4f13b4b543`
- Environment archive SHA-256: `TBD_BLOCKED`
- Circuit manifest SHA-256: `f7cf02d1a232e882820b85608464ba694eb1f7402d96c4bbaee2bbed87c439de`
- Qiskit version: `2.4.2`
- qiskit-ibm-runtime version: `0.47.0`
- Open Plan instance identifier/name: `open-instance`
- Open Plan: `open` / `free`
- Instance region: `us-east`
- Instance CRN SHA-256: `8958b83a3975312004e6f48292d712fe775bc41402618bf337f46393af4e51b7`

## 2. Frozen Logical Roles

- C = logical qubit 0
- R1 = logical qubit 2
- R2 = logical qubit 3
- S = logical qubit 1

## 3. Science Circuits

1. `ghz_plus_z`: GHZ + measured in Z
2. `ghz_plus_x`: GHZ + measured in X
3. `ghz_minus_z`: GHZ - measured in Z
4. `ghz_minus_x`: GHZ - measured in X

Four interleaved blocks, 1024 shots/circuit/block.

## 4. Readout Calibration

Eight independent assignment circuits: each selected physical qubit prepared in 0 and 1; 1024 shots each.

## 5. Backend and Layout Selection

Use the deterministic algorithm in `docs/RESEARCH_SPEC_TR.md`. No manual backend substitution after science results are known.

- Candidate source: `provider`
- Selected backend: `ibm_kingston`
- Selected physical layout: `[125, 117, 126, 124]`
- Backend twin status: `backend_snapshot_ready`
- Backend twin reason: `backend_derived_aggregate_noise_passed`
- Calibration snapshot timestamp: `2026-06-20T20:55:08+03:00`
- Selected transpiler seed: `TBD_BLOCKED`

## 6. Primary Endpoints

\[
\Delta_{obj}=\min(C_{Z,1},C_{Z,2})-\max(|C_{X,1}|,|C_{X,2}|)
\]

\[
\Delta_{coh}=|W_+|-|W_{mix}|,
\qquad W_{mix}=\frac{W_++W_-}{2}.
\]

## 7. Main-Text Inclusion Rule

All must pass on raw results:

- LCB95(delta_obj) > 0.40
- LCB95(min(C_Z1,C_Z2)) > 0.60
- LCB95(delta_coh) > 0.30
- GHZ- global X parity has the expected negative sign
- no single block supplies more than half of the total contrast
- raw and readout-corrected analyses have the same qualitative conclusion

## 8. Statistical Method

- Individual Pauli correlations: Clopper-Pearson interval after mapping +/-1 products to Bernoulli outcomes.
- Nonlinear contrasts: stratified shot bootstrap, 10,000 replicates, frozen seed 20260621.
- Primary alpha: 0.05.

## 9. Mitigation

- Primary: raw data.
- Secondary: tensor-product readout assignment correction.
- No ZNE, PEC, result-driven postselection, or shot deletion.

## 10. Rerun Policy

A rerun is permitted only for provider-declared failed/cancelled jobs, missing provider payload, circuit-hash mismatch, or provider-confirmed service incident. Weak or null scientific results do not permit a rerun.

## 11. Positive and Null Interpretations

- Objectivity + coherence pass: include main-text quantum illustration.
- Objectivity passes, coherence fails: classical-record illustration only; quantum coherence claim omitted.
- Both fail: hardware null; theory remains evaluated independently.

## 12. Freeze Declaration

Mandatory fields contain no `TBD`: `NO`
Human approval: `NO`
Status may become `FROZEN` only after all G4 tasks pass.

## 13. Current Blockers

- `environment_archive_sha256`: environment archive is not frozen yet
- `selected_transpiler_seed`: ISA transpilation is not frozen yet
- `human_approval`: explicit human approval is not recorded
