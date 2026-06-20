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

## [0.6.1-post-push-readiness] - 2026-06-20

### Changed
- Refreshed the G4 readiness audit after the initial GitHub push.
- Marked H404 repository cleanliness as passing while keeping provider snapshot, backend twin, preregistration fields and human approval as blockers.

## [0.6.2-credential-discovery] - 2026-06-20

### Changed
- Broadened secret-safe IBM/Qiskit credential discovery to env-like files, shell config files and known Qiskit account-file names.
- Tightened discovery to avoid treating Qiskit documentation examples as real token sources.

## [0.6.3-open-instance-preflight] - 2026-06-20

### Added
- Added Open Plan runtime-account metadata checks for `open-instance`.
- Added native IBM `cz` entangling-gate eligibility in Q303 backend ranking.
- Added backend calibration timestamp/version capture in the Q303 snapshot.
- Added Q304 selected-layout backend-derived aggregate local twin.
- Added H401 preregistration draft generation and manifests.

### Changed
- Updated G4 readiness to pass Q303/Q304 only when provider metadata and the
  local twin are available, while keeping H401/H402/human approval as blockers.
- Updated A601 caveats to preserve zero Q-grade hardware claims after Q304 local
  twin readiness passes.
- Added H401 draft generation to Makefile and the reproduction chain.

### Security
- Saved the IBM API key only in the local Qiskit account store outside the repo.
- Recorded no token values in repository artifacts; runtime CRN is represented
  by a SHA-256 hash in generated metadata.
- QPU job submission remains unimplemented and gated.

## [0.7.0-g4-freeze-h501-path] - 2026-06-20

### Added
- Added deterministic H401 environment archive generation.
- Added H402 ISA circuit packet generation with frozen execution order,
  selected transpiler seed and QPY manifest.
- Added H401 preregistration freeze generation from explicit human approval.
- Added H403 no-submission dry-run report.
- Added H501 SamplerV2 dry-run/execute entry point with frozen hash checks,
  Open instance checks, clean-repo/tag checks and single-payload guard.
- Added H502 locked raw hardware analysis and H503 secondary independent
  readout-assignment correction.
- Added provider-free tests for Sampler result extraction and hardware analysis
  fixtures.

### Changed
- Updated G4 readiness status to `ready_for_h501` after freeze and dry-run pass.
- Updated architecture and reproducibility docs for preregistered and raw
  hardware flows.

### Security
- H501 refuses to run unless `ALLOW_QPU_EXECUTION=YES`, the preregistration
  manifest is frozen, the circuit-manifest hash matches, no previous H501 raw
  payload exists, the repository is clean and the frozen preregistration tag
  points at `HEAD`.
- H501 writes only secret-free receipt/result payloads under `results/raw/`
  using write-once artifact guards.

## [0.7.1-h501a1-kingston-amendment] - 2026-06-20

### Added
- Added `configs/backend_amendment.yaml` for the H501A1 pre-result backend
  amendment.
- Added Q305 backend-amendment diagnostics comparing `ibm_kingston`, `ibm_fez`
  and `ibm_marrakesh` with the same backend-derived local twin gate.
- Added raw cancellation provenance for the original queued `ibm_marrakesh`
  H501 job.
- Added H501 retrieval script for accepted Runtime jobs.
- Added G5 hardware notes for queue, maintenance and layered-error context.

### Changed
- Regenerated Q303/Q304/H402/H401/H403/G4 artifacts for amended backend
  `ibm_kingston`.
- Updated the frozen preregistration manifest to require tag
  `v0.4-qpu-preregistered-kingston`.
- H501 preconditions now block only prior H501 provider payloads; pre-result
  receipts and cancellations remain provenance, not hardware results.

### Security
- The cancelled job reports no running timestamp, no raw result download and
  zero quantum seconds.
- Backend amendment does not record secret values and still requires
  `ALLOW_QPU_EXECUTION=YES` before amended H501 execution.

## [0.8.0-g5-hardware-result] - 2026-06-20

### Added
- Added the completed amended H501 `ibm_kingston` provider payload for job
  `d8rfasuab0ds73drkaig`.
- Added H502 locked raw hardware analysis artifact
  `results/processed/Q3_hardware_raw.json`.
- Added H503 secondary readout-mitigated analysis artifact
  `results/processed/Q3_hardware_mitigated.json`.
- Added post-execution G5 result notes with job timing, usage, raw metrics and
  mitigation agreement.

### Changed
- Updated A601 claim grading so Q1 and Q2 receive Q-grade evidence only when the
  preregistered raw hardware inclusion check passes and H503 qualitatively agrees.
- Updated documentation to distinguish the cancelled pre-result `ibm_marrakesh`
  job from the completed amended `ibm_kingston` observation.

### Security
- Provider payload and derived artifacts record `secret_values_recorded=false`.
- IBM credentials remain only in the local Qiskit account file outside the
  repository.

## [0.9.0-g6-final-interpretation] - 2026-06-20

### Added
- Added A602 final scientific decision generation from the claim matrix and
  H502/H503 hardware analyses.
- Added A603 reproducibility packaging with a clean temporary worktree
  `reproduce_all.py` run.
- Added tests for the final decision tree and archive path exclusions.

### Changed
- Extended the reproduction chain to regenerate A602 after A601.
- Updated architecture diagrams to include the final-decision and archive flow.

### Security
- The reproducibility archive excludes circular final-output files and records
  `secret_values_recorded=false`.
