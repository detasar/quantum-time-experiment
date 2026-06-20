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
- `pytest -q`: 53 passed.
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

- No provider job was submitted.
- The saved Qiskit account is bound to `open-instance` on the IBM Open plan.
- Deterministic provider-backed selection currently chooses `ibm_marrakesh`
  with layout `[111, 98, 112, 110]`.
- The selected backend supports native `cz` entangling gates, which the ranking
  code treats as valid for the GHZ workload.
- Selection is deterministic and does not use hardware science results.
- Secret values are not written to the Q303 artifact.

## Q304 Evidence

- Q304 runs a local backend-derived aggregate noise twin from the selected
  layout's calibration snapshot.
- Current status: `backend_snapshot_ready`, reason
  `backend_derived_aggregate_noise_passed`.
- Backend version: `1.0.21`; calibration timestamp:
  `2026-06-20T20:46:56+03:00`.
- This is still a local simulation proxy, not a QPU hardware observation.

## Stop Boundary

G3 local circuits, generic noise readiness, provider backend selection and the
backend-derived local twin are complete. G4 has since frozen preregistration and
the H501 path remains the only allowed QPU execution entry point.
