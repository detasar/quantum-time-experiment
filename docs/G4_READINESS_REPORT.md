# G4 Readiness Report

Date: 2026-06-20  
Branch: `implementation/g0-g1`

## Completed Audit

- Added `scripts/run_g4_readiness.py`.
- Added secret-safe IBM/Qiskit `.env*` discovery.
- Wrote `results/processed/G4_readiness_audit.json`.
- Wrote `results/processed/G4_readiness_manifest.json`.
- Verified through `scripts/reproduce_all.py`.

## Current Status

Overall status: `blocked_before_g4`.
Blocked check count: 4.

Passing checks:

- Q302 generic local readiness: 96 of 100 grid cells pass.
- QPU execution gate: `ALLOW_QPU_EXECUTION` is not `YES`.
- H404 repository snapshot: after the initial GitHub push, the repository has a committed snapshot tracking `origin/implementation/g0-g1`. A final clean-tree check is still required immediately before any preregistration tag.

Blocking checks:

- Q303 provider snapshot: current candidate source is `deterministic_fixture`; no provider call was attempted.
- Q304 backend twin: `hardware_stage_stopped`, reason `no_real_backend_snapshot_available`.
- H401 preregistration fields: `docs/PREREGISTRATION.md` still contains mandatory `TBD` fields and is not frozen.
- H401 human approval: no explicit approval is recorded.

## Credential Audit

- Env-like, shell config and Qiskit account-file candidates scanned: 52.
- Non-empty IBM/Qiskit token sources found: 0.
- Secret values recorded: `false`.

## Verification Results

- `pytest -q`: 46 passed.
- `ruff check .`: passed.
- `mypy src/objective_clocks`: passed.
- `scripts/reproduce_all.py`: passed with G4 readiness in the chain.

## Stop Boundary

G4 must not freeze preregistration or ISA circuits until Q303 obtains a real provider backend snapshot and Q304 produces a backend-derived digital twin. H501 remains unreachable because QPU job submission is still intentionally unimplemented.
