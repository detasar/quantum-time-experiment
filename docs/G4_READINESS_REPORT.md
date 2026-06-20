# G4 Readiness Report

Date: 2026-06-20  
Branch: `implementation/g0-g1`

## Completed Audit

- Added `scripts/run_g4_readiness.py`.
- Added secret-safe IBM/Qiskit credential discovery.
- Added H401 environment archive generation.
- Added H402 ISA circuit packet generation.
- Added H401 preregistration freeze generation.
- Added H403 no-submission dry-run.
- Added H501-H503 locked hardware execution and analysis entry points.

## Current Status

Overall status: `ready_for_h501`.
Blocked check count: 0.

Passing checks:

- Q302 generic local readiness: 96 of 100 grid cells pass.
- Q303 provider snapshot: candidate source is `provider`; provider listing was
  read-only and no job was submitted.
- Open Plan instance: active account is `open-instance`, plan `open`, pricing
  type `free`, region `us-east`.
- Q304 backend-derived local twin: `backend_snapshot_ready`, reason
  `backend_derived_aggregate_noise_passed`.
- H401 environment archive: present, hashed and secret-free.
- H402 ISA packet: 24 circuit instances, 24,576 total shots, selected
  transpiler seed 0.
- H401 preregistration packet: frozen with explicit human approval.
- H403 QPU gate: `ALLOW_QPU_EXECUTION` is not `YES`; Sampler was not invoked.
- H404 repository snapshot: remote tracking branch exists. The final tag
  `v0.3-qpu-preregistered` must point to the clean commit immediately before
  H501 execution.

## Credential Audit

- Env-like, shell config and Qiskit account-file candidates are scanned.
- Non-empty IBM/Qiskit token source count: 1.
- Runtime account metadata records only non-secret fields and an instance CRN
  SHA-256 hash.
- Secret values recorded: `false`.

## H501 Boundary

`scripts/run_h501_execute.py --execute` is the only hardware submission entry
point. It refuses to submit unless all of the following hold:

- frozen preregistration manifest exists;
- circuit-manifest SHA-256 matches the frozen preregistration manifest;
- ISA QPY SHA-256 matches the circuit manifest;
- G4 readiness audit is `ready_for_h501`;
- runtime metadata identifies `open-instance` on the Open plan;
- no previous H501 raw provider payload exists;
- repository is clean;
- tag `v0.3-qpu-preregistered` points at `HEAD`;
- `ALLOW_QPU_EXECUTION=YES`.

## Stop Boundary

G4 is complete, but no hardware observation exists yet. H501 may submit exactly
one locked IBM SamplerV2 workload only after the clean preregistration tag is
created and the execution environment gate is explicitly enabled.
