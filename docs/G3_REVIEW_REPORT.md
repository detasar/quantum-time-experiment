# G3 Review Report

Date: 2026-06-20  
Branch: `implementation/g0-g1`

## Completed Task IDs

- Q301: Freeze quantum circuit family and endianness.
- Q302: Run generic quantum noise sweep.
- Q303: Implement deterministic backend and layout selection.
- Q304: Run backend-derived digital twin or stop hardware stage when no real backend snapshot is available.

## Verification Results

- `scripts/run_g3.py`: passed.
- `ruff check .`: passed.
- `pytest -q`: 43 passed.
- `mypy src/objective_clocks`: passed.

## Generated Artifacts

- `results/processed/Q301_circuit_manifest.json`
- `results/processed/Q301_untranspiled_circuits.qpy`
- `results/processed/Q1_noise_sweep.parquet`
- `results/processed/Q1_noise_sweep_summary.json`
- `figures/fig_q302_noise_readiness.pdf`
- `results/processed/Q303_backend_candidates.json`
- `results/processed/Q2_backend_twin.parquet`
- `results/processed/Q2_backend_twin_summary.json`
- `results/processed/G3_manifest.json`

## Q301 Evidence

- Four science circuits are frozen: `ghz_plus_z`, `ghz_plus_x`, `ghz_minus_z`, `ghz_minus_x`.
- Eight independent readout calibration circuits are serialized.
- Circuit family contains no tomography.
- Qiskit bitstring `0001` parses to logical order `[C,S,R1,R2] = [1,0,0,0]`.
- Statevector checks recover exact GHZ Z correlations and X-basis global parity.

## Q302 Evidence

- Generic Aer noise sweep completed 100 grid cells.
- 96 cells pass the configured inclusion thresholds.
- The output records `delta_obj_lcb`, `min_z_correlation_lcb` and `delta_coh_lcb`.

## Q303 Evidence

- No IBM/Qiskit runtime token was found in discovered environment files.
- No provider job was submitted.
- Deterministic fixture backend selection chose `fixture_heavy_hex7` with layout `[1,2,3,4]`.
- Selection is deterministic and does not use hardware science results.

## Q304 Evidence

- Because no real backend snapshot was available, Q304 writes a formal stop row:
  `hardware_stage_stopped`, reason `no_real_backend_snapshot_available`.
- This satisfies the Q304 stop path: hardware preregistration should not proceed until a real backend snapshot is available.

## Stop Boundary

G3 local circuits and generic noise readiness are complete. G4 preregistration is not ready because Q304 did not obtain a real backend-derived digital twin.
