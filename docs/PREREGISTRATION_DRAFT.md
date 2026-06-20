# Preregistration Draft Packet - IBM Four-Qubit Illustration

**Status:** DRAFT - QPU execution prohibited
**Generated from:** `scripts/run_h401_draft.py`
**Project:** Objective Clock Bases from Redundant Records
**Primary scientific role:** illustration of objective local basis versus global coherence; not a proof of the theory.

## 1. Mandatory Identifiers

- Git commit: `bd8ee36d1fd58ced4e9200543ff36968af38a328`
- Environment manifest SHA-256: `238e5e51b683bd0a8700f40f9c075a5215b543ff6296fb58278fb88df30ad709`
- Environment archive SHA-256: `f62cbe0bc5a1a81effbf832f1ec62de66a6e160e5d0a4a6c7b6a5f17d5aec476`
- Circuit manifest SHA-256: `43c387ed1c3fdc41fdf219e99e17112438e29924a13d3a11688ef6476ac3cb86`
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
- Calibration snapshot timestamp: `2026-06-20T22:25:00+03:00`
- Selected transpiler seed: `0`
- ISA circuit QPY SHA-256: `6cc768cbaf831bbbe5c3f0dffde8f8fb8c32b78a345e5c838f4871e57879cdce`
- Exact execution-order seed: `20260621`
- Exact circuit instances: `24`

## 5A. Backend Amendment

- Amendment id: `H501A1-kingston-pre-result`
- Superseded backend: `ibm_marrakesh`
- Superseded job id: `d8reasegbcrc73f4f4pg`
- Superseded job final status: `CANCELLED`
- Raw result downloaded before amendment: `False`
- Replacement backend: `ibm_kingston`
- Dependent Q303/Q304/H402/H401/H403/H404 artifacts must be regenerated before H501.


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

Mandatory fields contain no `TBD`: `YES`
Human approval: `NO`
Status may become `FROZEN` only after all G4 tasks pass.

## 13. Current Blockers

- `human_approval`: explicit human approval is not recorded
