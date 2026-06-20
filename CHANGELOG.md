# Changelog

This changelog records the scientific evolution of the artifact. It intentionally
omits operational details that do not help a reader understand the research
process, evidence chain, or claim boundaries.

## 2026-06-21 - Public Research Artifact Narrative

### Changed
- Reframed the repository as a quantum systems experiment and reproducibility
  package rather than an internal execution log.
- Clarified that `clock` means a candidate quantum subsystem whose basis labels
  are interpreted as possible time labels, not a literal timing device.
- Rewrote the README entry path around motivation, basic concepts, experimental
  system, result boundaries, figure interpretation, and reproducibility.
- Replaced weak or misleading visual summaries with claim-carrying figures:
  order chains, basis ambiguity diagnostics, capacity bounds, noise recovery,
  local readiness, and raw IBM hardware evidence.
- Added a full narrative LaTeX report for the artifact with literature
  positioning, concept definitions, figures, tables, claim boundaries, and
  reproducibility metadata.

### Scientific Rationale
- Public readers should understand why quantum Darwinism, redundant records,
  objective-past work, and fixed-partition uniqueness results motivate the
  basis-order-orientation question before seeing implementation details.
- Figures are retained only when they explain a claim; binary exact sanity checks
  are reported as tables/data rather than low-information plots.

## 2026-06-20 - Final Scientific Interpretation and Reproducibility Freeze

### Added
- Final claim-evidence matrix: 10 claims, 0 unsupported claims, 2 bounded
  hardware-illustration claims.
- Final decision artifact stating that the theory/no-go package is supported
  independently of the IBM observation.
- Reproducibility archive
  `objective-clocks-reproducibility.tar.gz`, SHA-256
  `1ad798aea881e7c189d01907d73b9b5eb60366df33af0cfe0e60ab2b56437dea`.

### Scientific Rationale
- The accepted artifact route is a foundations artifact with a bounded quantum
  illustration.
- The IBM result may illustrate the four-qubit protocol, but it does not carry
  the theorem-level contribution.

## 2026-06-20 - IBM Quantum Hardware Observation

### Added
- One completed amended IBM Quantum observation on `ibm_kingston`, job
  `d8rfasuab0ds73drkaig`.
- Locked raw H502 analysis and secondary H503 readout-assignment correction.
- Hardware notes documenting queue context, backend amendment provenance, job
  timing, usage, and raw/mitigated interpretation.

### Evidence
- 24 circuit instances, 24,576 observed shots, 9 quantum seconds.
- Raw primary inclusion passed without mitigation.
- Raw lower confidence bounds:
  `delta_obj_lcb=0.8876953125`,
  `min_z_correlation_lcb=0.9169542107266444`,
  `delta_coh_lcb=0.877685546875`.
- H503 qualitatively agreed with the raw H502 decision and did not replace it.

### Scientific Rationale
- The original `ibm_marrakesh` job was cancelled while still queued and is
  retained only as pre-result provenance.
- The completed `ibm_kingston` run is interpreted as a bounded GHZ/dephased
  workflow illustration.

## 2026-06-20 - Preregistration and Quantum Readiness

### Added
- Frozen preregistration packet for the one-shot QPU workflow.
- ISA circuit packet, execution order, backend-derived local twin, dry-run
  report, and backend-amendment diagnostics.
- Local quantum noise-readiness sweep before hardware execution.

### Scientific Rationale
- Hardware execution was downstream of theory, classical checks, local
  simulation, preregistration, and explicit human approval.
- The preregistered rule separated raw inclusion from secondary mitigation.

## 2026-06-20 - Classical Experiment Backbone

### Added
- C0 exhaustive/seeded theorem verification.
- C1 basis ambiguity and two-record diagnostic.
- C2 order catalog with thermometer, diamond, duplicate, disconnected,
  orientation-free, and erasure fixtures.
- C3 noise-recovery phase diagram.
- C4 assumption stress tests.
- C5 exact GHZ/dephased-control sanity table.

### Scientific Rationale
- The core contribution is not fixed-partition basis uniqueness itself.
- The artifact tests what remains after basis objectivity: order, orientation,
  record capacity, and no-go boundaries.
- C5 exact values are table evidence; they are not used as a standalone
  publication figure because a 0/1 exact sanity check is visually
  low-information.

## 2026-06-20 - Theory and Claim Boundary

### Added
- Formal proof notes for imported basis uniqueness, chain characterization,
  scalar-time identifiability, capacity bounds, noisy redundancy, and no-go
  examples.
- Counterexample catalog for label permutation, orientation swap, unrestricted
  partition, single-fragment Bell ambiguity, and diamond branching.

### Scientific Rationale
- Persistent physical trajectories are chains in the record-dominance poset.
- Branching linear extensions are scheduler totalizations, not physical
  histories.
- Temporal orientation requires an anchor beyond redundant records alone.
