# Preregistration Draft Packet - IBM Four-Qubit Illustration

**Status:** FROZEN
**Generated from:** `scripts/run_h401_draft.py`
**Project:** Objective Clock Bases from Redundant Records
**Primary scientific role:** illustration of objective local basis versus global coherence; not a proof of the theory.

## 1. Mandatory Identifiers

- Git commit: `54877212485df4ab57b723b5b3706a6c75dbd52f`
- Environment manifest SHA-256: `796c7f5150c81015837d7808f1ec2cb19188ded12c51d96c04072b82508e26f2`
- Environment archive SHA-256: `c74d263331cbb85e0f1216b0393b795ec291433ee852ef391963d53eb482933b`
- Circuit manifest SHA-256: `a85b10ffe83a40d7656875fe3f3227ac10af280661eb82c97dfc97973770f893`
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
- Selected physical layout: `[105, 117, 104, 106]`
- Backend twin status: `backend_snapshot_ready`
- Backend twin reason: `backend_derived_aggregate_noise_passed`
- Calibration snapshot timestamp: `2026-06-21T01:15:10+03:00`
- Selected transpiler seed: `0`
- ISA circuit QPY SHA-256: `2e9af2eb37bb555e2c7ec0c85dd1a8729307a37dd93839bc80595067f6188768`
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

- Objectivity + coherence pass: include the bounded quantum illustration.
- Objectivity passes, coherence fails: classical-record illustration only; quantum coherence claim omitted.
- Both fail: hardware null; theory remains evaluated independently.

## 12. Freeze Declaration

Mandatory fields contain no `TBD`: `YES`
Human approval: `YES`
Status is `FROZEN`; QPU execution still requires the explicit H501 gate.

## 13. Human Approval Record

- Approval timestamp UTC: `2026-06-20T23:22:44.509796+00:00`
- Approval source: `explicit human approval recorded during the execution session`
- QPU execution allowed now: `NO`
