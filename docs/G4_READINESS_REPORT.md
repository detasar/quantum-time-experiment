# G4 Readiness Report

Date: 2026-06-20  
Branch: `implementation/g0-g1`

## Completed Audit

- Added `scripts/run_g4_readiness.py`.
- Added secret-safe IBM/Qiskit `.env*` discovery.
- Wrote `results/processed/G4_readiness_audit.json`.
- Wrote `results/processed/G4_readiness_manifest.json`.
- Wrote `docs/PREREGISTRATION_DRAFT.md`.
- Wrote `results/processed/H401_preregistration_draft_summary.json`.
- Verified through `scripts/reproduce_all.py`.

## Current Status

Overall status: `blocked_before_g4`.
Blocked check count: 2.

Passing checks:

- Q302 generic local readiness: 96 of 100 grid cells pass.
- Q303 provider snapshot: candidate source is `provider`; provider listing was
  read-only and no job was submitted.
- Open Plan instance: active account is `open-instance`, plan `open`, pricing
  type `free`, region `us-east`.
- Q304 backend-derived local twin: `backend_snapshot_ready`, reason
  `backend_derived_aggregate_noise_passed`.
- Selected backend/layout at this snapshot: `ibm_kingston`,
  `[125, 117, 126, 124]`.
- QPU execution gate: `ALLOW_QPU_EXECUTION` is not `YES`.
- H404 repository snapshot: after the initial GitHub push, the repository has a committed snapshot tracking `origin/implementation/g0-g1`. A final clean-tree check is still required immediately before any preregistration tag.

Blocking checks:

- H401 preregistration fields: `docs/PREREGISTRATION.md` still contains
  mandatory `TBD` fields and is not frozen. The draft packet narrows the
  remaining blockers to environment archive SHA-256, selected transpiler seed
  and human approval.
- H401 human approval: no explicit approval is recorded.

## Credential Audit

- Env-like, shell config and Qiskit account-file candidates scanned: 53.
- Non-empty IBM/Qiskit token sources found: 1.
- Runtime account metadata records only non-secret fields and an instance CRN
  SHA-256 hash.
- Secret values recorded: `false`.

## Verification Results

- `pytest -q`: 49 passed.
- `ruff check .`: passed.
- `mypy src/objective_clocks`: passed.
- `scripts/reproduce_all.py`: passed with G4 readiness in the chain.

## Stop Boundary

G4 must not freeze preregistration or ISA circuits until the H401/H402
remaining blockers are closed and explicit human approval is recorded. H501
remains unreachable because QPU job submission is still intentionally
unimplemented.
