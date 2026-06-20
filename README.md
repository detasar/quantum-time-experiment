# Objective Clock Bases from Redundant Records

Research implementation bundle for the project:

> **Objective Clock Bases from Redundant Records: Why Temporal Order Requires More**

This repository is a theorem-first, falsification-first research program. It separates four questions that must never be conflated:

1. **Clock-basis objectivity:** which projective basis of an internal subsystem is redundantly recorded in independently accessible fragments?
2. **Event-label identification:** which record signature belongs to which clock label?
3. **Temporal order:** which labels can be ordered by persistent record accumulation?
4. **Temporal orientation:** which end of that order is operationally earlier, and what assumptions anchor the arrow?

The main novelty target is not the known fact that redundant records can select an objective observable. The target is the precise boundary between basis objectivity and temporal order/orientation, including exact no-go results and record-capacity bounds.

## Hard research rules

- No claim of retrocausality, cosmological time emergence, or quantum advantage.
- No IBM hardware execution before the preregistration gate passes.
- No LLM output is a primary experimental measurement.
- The four-qubit GHZ experiment is an illustration, not the proof of the theory.
- The exact classical/symbolic results must survive without the quantum experiment.
- Every random computation has a recorded seed.
- Every produced artifact has a SHA-256 manifest.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,quantum]'
pytest -q
python -m objective_clocks.cli theorem-check --config configs/classical.yaml
python -m objective_clocks.cli ghz-exact
```

## Repository map

- `docs/RESEARCH_SPEC_TR.md`: complete theory and experiment specification.
- `docs/CODEX_IMPLEMENTATION.md`: Codex execution contract and task order.
- `docs/PREREGISTRATION.md`: frozen QPU protocol template.
- `docs/PREREGISTRATION_FROZEN.md`: frozen H401 preregistration packet.
- `TASKS.yaml`: machine-readable work breakdown with Definition of Ready and Definition of Done.
- `src/objective_clocks/`: reusable implementation.
- `tests/`: theorem/property/regression tests.
- `configs/`: immutable experiment configurations.
- `results/raw/`: write-once raw outputs.
- `results/processed/`: derived outputs.
- `figures/`: reproducible figures only.

## Project gates

- **G0 — Repository ready:** environment, manifests, semantic ADR and QPU gate baseline.
- **G1 — Theory and exact primitives frozen:** O1--O4, imported B0 and no-go package.
- **G2 — Classical experiments complete:** C0--C5.
- **G3 — Local quantum readiness:** local circuit and noise readiness.
- **G4 — Hardware preregistration frozen:** no QPU submission yet.
- **G5 — One IBM execution and locked analysis:** one preregistered batch only after explicit gate.
- **G6 — Scientific interpretation complete:** evidence-grade claims and reproducibility archive.

## Current G0/G1 artifacts

- `results/processed/T101_chain_verification.json`
- `results/processed/T103_capacity.json`
- `results/processed/T104_noise_bound_grid.json`
- `results/processed/counterexample_catalog.json`
- `figures/fig_03_capacity.pdf`
- `docs/ARCHITECTURE.md`
- `reports/experiment_report.tex`

## Current G2 Batch 1 artifacts

- `results/processed/C0_theorem_verification.parquet`
- `results/processed/C1_basis_landscape.nc`
- `results/processed/C2_order_catalog.parquet`
- `results/processed/C2_graphs/*.graphml`
- `figures/fig_02_basis_landscape.pdf`
- `docs/G2_BATCH1_REVIEW_REPORT.md`

## Current G2 Complete Artifacts

- `results/processed/C3_noise_phase_diagram.parquet`
- `results/processed/C4_assumption_failures.json`
- `results/processed/C5_ghz_exact.json`
- `figures/fig_04_noise_phase.pdf`
- `figures/fig_05_ghz_exact.pdf`
- `docs/G2_REVIEW_REPORT.md`

## Current G3 Artifacts

- `results/processed/Q301_circuit_manifest.json`
- `results/processed/Q301_untranspiled_circuits.qpy`
- `results/processed/Q1_noise_sweep.parquet`
- `results/processed/Q1_noise_sweep_summary.json`
- `figures/fig_q302_noise_readiness.pdf`
- `results/processed/Q303_backend_candidates.json`
- `results/processed/Q2_backend_twin.parquet`
- `results/processed/Q2_backend_twin_summary.json`
- `results/processed/G3_manifest.json`
- `docs/G3_REVIEW_REPORT.md`

G3 completed the local circuit, generic-noise readiness path and provider
metadata preflight without any provider job submission. Q303 currently uses the
saved IBM Open Plan account, selects an Open backend and records only
secret-safe account metadata. Q304 runs a backend-derived local twin from the
selected layout's calibration snapshot; it is not a hardware observation.

## Current G4 Readiness Audit

- `results/processed/G4_readiness_audit.json`
- `results/processed/G4_readiness_manifest.json`
- `results/preregistered/environment_archive.tar.gz`
- `results/preregistered/environment_archive_manifest.json`
- `results/preregistered/circuits.qpy`
- `results/preregistered/circuit_manifest.json`
- `results/preregistered/preregistration_manifest.json`
- `results/preregistered/dry_run_report.json`
- `results/processed/Q305_backend_amendment_diagnostics.json`
- `results/raw/H501_submission_receipt_d8reasegbcrc73f4f4pg.json`
- `results/raw/H501_cancellation_d8reasegbcrc73f4f4pg.json`
- `results/processed/H401_preregistration_draft_summary.json`
- `docs/PREREGISTRATION_DRAFT.md`
- `docs/PREREGISTRATION_FROZEN.md`
- `docs/G4_READINESS_REPORT.md`

Current status is `ready_for_h501`. The audit scans local env-like files, shell
config files and known Qiskit account-file names without recording secret
values. It confirms the saved account is bound to `open-instance` on the Open
plan, freezes the H401 preregistration packet, freezes the H402 ISA circuit
packet and passes the H403 no-submission dry-run. A pre-result backend amendment
cancelled the original queued `ibm_marrakesh` job before any raw result or QPU
usage, compared `ibm_kingston`, `ibm_fez` and `ibm_marrakesh`, and regenerated
Q303/Q304/H402/H401/H403 for `ibm_kingston`. At the frozen G4 boundary, QPU
execution remained disabled unless H501 was invoked with
`ALLOW_QPU_EXECUTION=YES` after the repository was clean and tagged.

## Current G5 Locked Hardware Path

- `scripts/run_h501_execute.py`: gated SamplerV2 dry-run/execute path.
- `scripts/run_h502_raw_analysis.py`: locked raw primary analysis.
- `scripts/run_h503_mitigated_analysis.py`: secondary readout-mitigated analysis.
- `src/objective_clocks/hardware.py`: raw payload extraction, integrity checks,
  raw inclusion decision and independent readout assignment correction.
- `results/raw/H501_submission_receipt_d8rfasuab0ds73drkaig.json`
- `results/raw/H501_provider_payload_d8rfasuab0ds73drkaig.json`
- `results/processed/Q3_hardware_raw.json`
- `results/processed/Q3_hardware_mitigated.json`

The amended H501 target was `ibm_kingston`. The execution path refused to run
without a frozen preregistration manifest, matching circuit-manifest hash, Open
instance metadata, no prior H501 provider payload, a clean repository, tag
`v0.4-qpu-preregistered-kingston` at `HEAD` and `ALLOW_QPU_EXECUTION=YES`.

The amended H501 execution completed on job `d8rfasuab0ds73drkaig`: 24 circuit
instances, 24,576 observed shots and 9 quantum seconds. H502 passed the locked
raw inclusion rule without mitigation
(`passes_main_text_inclusion_without_mitigation=true`), with
`delta_obj_lcb=0.8876953125`, `min_z_correlation_lcb=0.9169542107266444` and
`delta_coh_lcb=0.877685546875` under the preregistered bootstrap seed
`20260621`. H503 readout correction is secondary only; it agrees qualitatively
with the raw result.

## Current A601 Artifacts

- `results/claim_evidence_matrix.csv`
- `results/processed/A601_claim_evidence_summary.json`
- `results/processed/A601_manifest.json`
- `docs/CLAIMS_REGISTER.md`

A601 evidence-grades every planned claim as `P`, `E`, `S`, `Q`, `I` or `N`.
The current matrix has two Q-grade rows, Q1 and Q2, both limited to the
four-qubit IBM illustration. The theorem-level and no-go claims remain
classical/symbolic and do not depend on the hardware observation.
