# Changelog

All notable changes to this research repository are documented here.

## [0.1.0-g0-g1] - 2026-06-20

### Added
- Bootstrapped the repository from `objective_clocks_codex_bundle_v1.zip`.
- Added G0/G1 verification branch `implementation/g0-g1`.
- Added immutable artifact helpers for canonical config hashing, SHA-256 file manifests, atomic JSON writes and write-once raw JSON writes.
- Added G1 theorem regression tests for O1 chain characterization, scalar-time identifiability, capacity bounds, noisy redundancy and no-go counterexamples.
- Added reproducible G1 artifact generator `scripts/run_g1.py`.
- Generated G0/G1 manifests and outputs under `results/processed/`.
- Generated capacity figure `figures/fig_03_capacity.pdf`.
- Added architecture, data-flow, control-flow, dependency and connectivity diagrams.
- Started the LaTeX experiment report journal in `reports/experiment_report.tex`.

### Changed
- Cleaned lint and type-check baseline without changing scientific semantics.
- Clarified that `scalar_time_identifiable` requires a total quotient poset and nonduplicate signatures.

### Security
- Kept QPU execution disabled by default.
- Kept raw artifacts write-once and outside normal overwrite paths.

## [0.2.0-g2-batch1] - 2026-06-20

### Added
- Added `objective_clocks.classical` for C0-C2 pure experiment primitives.
- Added C201, C202 and C203 reproducible runners.
- Added parquet output support through `pyarrow`.
- Added C0 theorem verification parquet and runtime report.
- Added C1 basis landscape NetCDF, summary and figure.
- Added C2 order catalog parquet and GraphML Hasse diagrams.
- Added G2 batch-1 review report.

### Changed
- Replaced path enumeration for maximal-chain counts with an exact DAG dynamic program.
- Replaced NetworkX VF2 automorphism counting with exact color-class enumeration for small DAGs.
- Vectorized dominance-matrix construction.

### Security
- QPU execution remains disabled; this batch performs classical/exact computation only.

## [0.3.0-g2-complete] - 2026-06-20

### Added
- Added C204 noise sweep runner with parquet, summary and phase-diagram figure.
- Added C205 assumption stress-test matrix.
- Added C206 exact GHZ/dephased analysis with JSON and figure.
- Added G2 batch-2 runner, complete G2 runner and manifests.
- Added complete G2 review report.

### Changed
- Extended `objective_clocks.classical` with C3-C5 pure experiment functions.
- Updated `reproduce_all.py` to run the complete G2 pipeline.

### Security
- QPU execution remains gated; G2 introduces no provider calls.

## [0.4.0-g3-local-quantum] - 2026-06-20

### Added
- Added Q301 circuit manifest and QPY serialization for the science and readout-calibration circuits.
- Added Qiskit bitstring parser and endianness tests.
- Added Q302 generic Aer noise sweep with readiness metrics and figure.
- Added Q303 deterministic backend/layout selection with provider-safe metadata collection.
- Added Q304 backend-twin stop report for missing real backend snapshots.
- Added complete G3 review report.

### Changed
- Extended `reproduce_all.py` to include G3.
- Added Qiskit/Aer/Runtime mypy overrides.

### Security
- No provider job is submitted in G3.
- IBM/Qiskit credential discovery reports only key presence, never secret values.

## [0.5.0-a601-claims] - 2026-06-20

### Added
- Added reproducible A601 claim-evidence matrix generation.
- Added machine checks that every planned claim has evidence artifacts, evidence checks and caveats.
- Added A601 output manifest and summary artifacts.

### Changed
- Updated `reproduce_all.py` and `Makefile` to include A601.
- Updated claims documentation from planned status to evidence-graded status.

### Security
- Hardware claims remain explicitly absent while Q304 is stopped before preregistration.

## [0.6.0-g4-readiness-audit] - 2026-06-20

### Added
- Added secret-safe IBM/Qiskit `.env*` credential discovery that records key names and token-source metadata without secret values.
- Added G4 readiness audit covering provider snapshot, backend twin, preregistration TBD fields, human approval, QPU gate state and repository cleanliness.
- Added G4 readiness manifest and review report.

### Changed
- Extended Q303 backend discovery to use a non-empty IBM/Qiskit token found in process environment or `.env*` files for provider listing only.
- Added `g4-readiness` to the Makefile and reproduction chain.

### Security
- Secret values are never written to artifacts.
- QPU job submission remains unimplemented and gated by `ALLOW_QPU_EXECUTION=YES` plus frozen preregistration hash checks.
