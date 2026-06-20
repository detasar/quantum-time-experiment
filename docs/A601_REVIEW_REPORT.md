# A601 Review Report

Date: 2026-06-20  
Branch: `implementation/g0-g1`

## Completed Task IDs

- A601: Evidence-grade all claims.

## Verification Results

- `scripts/run_a601.py`: passed after H501/H502/H503 artifacts were added.
- `pytest tests/test_claims.py -q`: 1 passed after H501/H502/H503 artifacts
  were added.
- `scripts/reproduce_all.py`: passed in the pre-hardware A601 integration run;
  the hardware job itself is intentionally excluded from full automatic
  reproduction.
- `pytest -q`: 53 passed after H501/H502/H503 artifacts were added.

## Generated Artifacts

- `results/claim_evidence_matrix.csv`
- `results/processed/A601_claim_evidence_summary.json`
- `results/processed/A601_manifest.json`

## Evidence Boundary

- Ten planned claims are evidence-graded: B0, O1, O2, O3, O4, N1, N2, N3, Q1 and Q2.
- Unsupported claim count is zero.
- Q-grade claim count is two: Q1 and Q2.
- Q1 and Q2 are supported with the preregistered H501/H502/H503 IBM observation
  as four-qubit illustrations.
- No theorem-level or no-go claim depends on the IBM hardware observation.

## Stop Boundary

A601 does not promote the hardware illustration into a proof. The primary
theory and no-go claims remain evaluated by proofs, exact checks and classical
experiments; H501/H502/H503 only update the Q1/Q2 illustration rows.
