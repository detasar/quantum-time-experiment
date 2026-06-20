# Research Artifact and Reproducibility Package: Objective Clock Bases from Redundant Records

![Objective Clock Bases research status overview](assets/readme/overview.svg)

**Author:** Davut Emre Taşar

This repository is a self-contained research artifact and reproducibility
package. It is formatted as a public-facing artifact, not as an internal
execution log or manuscript submission.

The artifact studies the question:

> When redundant records make a clock basis objective, what extra structure is
> still required to recover event order and temporal orientation?

The completed package supports a narrow answer: redundant records can identify
an objective basis under the fixed-partition assumptions already known in the
literature, but they do not by themselves provide a physical timeline. Persistent
trajectories are chains inside the record-dominance poset; branching linear
extensions are scheduler totalizations, not physical histories. Temporal
orientation needs an anchor beyond redundancy alone.

| Field | Value |
| --- | --- |
| Artifact title | Research Artifact and Reproducibility Package: Objective Clock Bases from Redundant Records |
| Author | Davut Emre Taşar |
| Scientific freeze | `v0.9.0-g6-final-interpretation` |
| Final path | full foundations paper |
| Hardware status | one bounded IBM QPU illustration completed on `ibm_kingston` |
| Archive | `objective-clocks-reproducibility.tar.gz`, SHA-256 `1ad798aea881e7c189d01907d73b9b5eb60366df33af0cfe0e60ab2b56437dea` |

This README is a navigation and presentation layer for the frozen scientific
package. The reproducibility archive records the exact G6 package and source
commit used for the final decision.

The public source tree has been cleaned after the G6 freeze to remove internal
execution-planning notes. The archive remains the immutable scientific freeze
and can contain historical planning files that are intentionally no longer part
of the public-facing repository surface.

## Result At A Glance

| Question | Answer | Primary evidence |
| --- | --- | --- |
| Which basis is objectively recorded? | Fixed-partition redundant records identify a record basis, but this is not claimed as the new contribution. | [B0 proof note](docs/proofs/B0_imported_basis_uniqueness.md), [C1 landscape](results/processed/C1_basis_landscape_summary.json) |
| Do records define a scalar time? | Only when the relevant snapshots form a single chain. | [O1 chain proof](docs/proofs/O1_chain_characterization.md), [T101 checks](results/processed/T101_chain_verification.json) |
| What is the main contribution? | The basis-order-orientation separation, record-capacity results, and partition/orientation no-go package. | [research notes](docs/RESEARCH_SPEC_TR.md), [proofs](docs/proofs), [counterexamples](results/processed/counterexample_catalog.json) |
| Did the QPU run finish? | Yes. `ibm_kingston`, job `d8rfasuab0ds73drkaig`, status `DONE`, 24 circuit instances, 24,576 shots, 9 quantum seconds. | [provider payload](results/raw/H501_provider_payload_d8rfasuab0ds73drkaig.json), [hardware notes](docs/G5_HARDWARE_NOTES.md) |
| What did the QPU result support? | It passed the locked raw inclusion rule and is included only as a four-qubit illustration. | [raw analysis](results/processed/Q3_hardware_raw.json), [final decision](docs/FINAL_DECISION.md) |
| Are unsupported claims left? | No. A601 records 10 claims, 0 unsupported, 2 Q-grade hardware illustration claims. | [claim matrix](results/claim_evidence_matrix.csv), [claims register](docs/CLAIMS_REGISTER.md) |

## What Is In The Repository

| Area | Contents |
| --- | --- |
| Theory and proofs | [docs/RESEARCH_SPEC_TR.md](docs/RESEARCH_SPEC_TR.md), [docs/proofs](docs/proofs) |
| Implementation | [src/objective_clocks](src/objective_clocks), [scripts](scripts), [configs](configs), [tests](tests) |
| Raw hardware records | [results/raw/H501_provider_payload_d8rfasuab0ds73drkaig.json](results/raw/H501_provider_payload_d8rfasuab0ds73drkaig.json), submission receipts, and the cancelled pre-result Marrakesh receipt |
| Processed results | [results/processed](results/processed), including G0-G6 manifests, theorem outputs, classical experiments, quantum local checks, raw QPU analysis, mitigated secondary analysis, and final decision data |
| Figures | Publication PDFs in [figures](figures) and README preview images in [assets/readme](assets/readme) |
| Paper log | [reports/experiment_report.tex](reports/experiment_report.tex) |
| Reproducibility archive | [objective-clocks-reproducibility.tar.gz](objective-clocks-reproducibility.tar.gz) plus [A603 manifest](results/processed/A603_reproducibility_manifest.json) |

Not included: IBM tokens, local `.env` files, virtual environments, cache
directories, or complete terminal session transcripts. The scientific evidence
that matters for reproduction is tracked through raw payloads, processed
artifacts, manifests, reports, SHA-256 records, and the final archive.

## Start Here

| Need | File |
| --- | --- |
| Fast scientific conclusion | [docs/FINAL_DECISION.md](docs/FINAL_DECISION.md) |
| Detailed research notes | [docs/RESEARCH_SPEC_TR.md](docs/RESEARCH_SPEC_TR.md) |
| Architecture and dependency diagrams | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Frozen preregistration | [docs/PREREGISTRATION_FROZEN.md](docs/PREREGISTRATION_FROZEN.md) |
| Hardware execution notes | [docs/G5_HARDWARE_NOTES.md](docs/G5_HARDWARE_NOTES.md) |
| Claim grades | [docs/CLAIMS_REGISTER.md](docs/CLAIMS_REGISTER.md) and [results/claim_evidence_matrix.csv](results/claim_evidence_matrix.csv) |
| Citation metadata | [CITATION.cff](CITATION.cff) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

## Data Flow

```mermaid
flowchart LR
  Spec["Theory specification"] --> G1["G1 proofs and exact primitives"]
  G1 --> G2["G2 classical C0-C5 experiments"]
  G2 --> G3["G3 local quantum readiness"]
  G3 --> G4["G4 frozen preregistration"]
  G4 --> H501["H501 one gated IBM run"]
  H501 --> H502["H502 raw primary analysis"]
  H502 --> H503["H503 secondary readout correction"]
  H502 --> A601["A601 claim evidence matrix"]
  H503 --> A601
  A601 --> A602["A602 final decision"]
  A602 --> A603["A603 reproducibility archive"]
```

The hardware path is deliberately downstream of the theory and classical checks.
The theorem-level and no-go claims survive without the IBM observation.

## Reproduce

### 1. Inspect the frozen result

```bash
git clone <repo-url>
cd quantum-time-experiment
git checkout v0.9.0-g6-final-interpretation
echo "1ad798aea881e7c189d01907d73b9b5eb60366df33af0cfe0e60ab2b56437dea  objective-clocks-reproducibility.tar.gz" | sha256sum -c -
tar -tzf objective-clocks-reproducibility.tar.gz | sed -n '1,30p'
```

This verifies the published archive without contacting IBM.

### 2. Install and run local checks

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,quantum]'
pytest -q
python -m objective_clocks.cli theorem-check --config configs/classical.yaml
python -m objective_clocks.cli ghz-exact
```

Expected local test state at G6: 55 passing tests.

### 3. Re-run the non-submitting pipeline

```bash
make reproduce
```

`make reproduce` replays the scripted non-QPU pipeline and ends with `pytest`.
It never submits a new QPU job. Some provider-metadata stages, such as Q303/Q305,
expect a locally saved IBM Runtime account if you want to refresh current backend
metadata; no token is stored in this repository.

## QPU Safety Boundary

New hardware execution is blocked by design. The execution script refuses to run
unless all of the following are true:

- The preregistration and circuit manifests are frozen and hash-matched.
- The selected Open instance metadata is present.
- There is no prior H501 provider payload for the target run.
- The worktree is clean and at the required preregistration tag.
- The command is explicitly invoked with `ALLOW_QPU_EXECUTION=YES`.

The completed hardware job is already committed as data:

| Field | Value |
| --- | --- |
| Backend | `ibm_kingston` |
| Job id | `d8rfasuab0ds73drkaig` |
| Status | `DONE` |
| Circuit instances | 24 |
| Shots | 24,576 |
| Quantum usage | 9 seconds |
| Raw inclusion rule | Passed without mitigation |

The earlier `ibm_marrakesh` job `d8reasegbcrc73f4f4pg` was cancelled while
queued, before any running timestamp, raw result, or QPU usage. That amendment is
recorded in [configs/backend_amendment.yaml](configs/backend_amendment.yaml) and
[results/raw/H501_cancellation_d8reasegbcrc73f4f4pg.json](results/raw/H501_cancellation_d8reasegbcrc73f4f4pg.json).

## Hardware Result

Raw H502 is the primary analysis; H503 mitigation is secondary only and cannot
rescue or replace the raw result.

| Metric | Raw locked value |
| --- | ---: |
| `passes_main_text_inclusion_without_mitigation` | `true` |
| `delta_obj_lcb` | `0.8876953125` |
| `min_z_correlation_lcb` | `0.9169542107266444` |
| `delta_coh_lcb` | `0.877685546875` |
| `w_plus_xxxx` | `0.8955078125` |
| `w_minus_xxxx` | `-0.87744140625` |
| `w_mix_xxxx` | `0.009033203125` |
| Bootstrap seed | `20260621` |
| Bootstrap replicates | `10000` |

The secondary readout-assignment correction agrees qualitatively with the raw
decision, with assignment condition number `1.1172921620957568`.

## Figure Gallery

These previews are generated from the tracked publication PDFs so the GitHub
front page is inspectable without opening each PDF manually.

<table>
  <tr>
    <td align="center" width="33%">
      <a href="figures/fig_02_basis_landscape.pdf"><img src="assets/readme/fig_02_basis_landscape.png" alt="Basis landscape figure" width="300"></a>
      <br><sub>Basis landscape: ambiguity versus two-record objectivity.</sub>
    </td>
    <td align="center" width="33%">
      <a href="figures/fig_03_capacity.pdf"><img src="assets/readme/fig_03_capacity.png" alt="Record capacity figure" width="300"></a>
      <br><sub>Record-capacity behavior.</sub>
    </td>
    <td align="center" width="33%">
      <a href="figures/fig_04_noise_phase.pdf"><img src="assets/readme/fig_04_noise_phase.png" alt="Noise phase diagram figure" width="300"></a>
      <br><sub>Noise and inclusion phase diagram.</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <a href="figures/fig_05_ghz_exact.pdf"><img src="assets/readme/fig_05_ghz_exact.png" alt="Exact GHZ figure" width="300"></a>
      <br><sub>Exact GHZ sanity check.</sub>
    </td>
    <td align="center" width="33%">
      <a href="figures/fig_q302_noise_readiness.pdf"><img src="assets/readme/fig_q302_noise_readiness.png" alt="Local quantum readiness figure" width="300"></a>
      <br><sub>Local quantum readiness before QPU execution.</sub>
    </td>
    <td align="center" width="33%">
      <a href="docs/ARCHITECTURE.md"><strong>Architecture diagrams</strong></a>
      <br><sub>Data flow, control flow, dependency graph, and connectivity documentation.</sub>
    </td>
  </tr>
</table>

## Artifact Index

| Gate | Status | Key artifacts |
| --- | --- | --- |
| G0 | Repository ready | [G0 environment](results/processed/G0_environment_manifest.json), [file manifest](results/processed/G0_file_manifest.json) |
| G1 | Theory primitives frozen | [T101](results/processed/T101_chain_verification.json), [T103](results/processed/T103_capacity.json), [T104](results/processed/T104_noise_bound_grid.json), [counterexamples](results/processed/counterexample_catalog.json) |
| G2 | Classical experiments complete | [C0](results/processed/C0_theorem_verification.parquet), [C1](results/processed/C1_basis_landscape.nc), [C2](results/processed/C2_order_catalog.parquet), [C3](results/processed/C3_noise_phase_diagram.parquet), [C4](results/processed/C4_assumption_failures.json), [C5](results/processed/C5_ghz_exact.json) |
| G3 | Local quantum readiness complete | [Q301 circuits](results/processed/Q301_circuit_manifest.json), [Q302 sweep](results/processed/Q1_noise_sweep_summary.json), [Q303 candidates](results/processed/Q303_backend_candidates.json), [Q304 twin](results/processed/Q2_backend_twin_summary.json), [Q305 amendment](results/processed/Q305_backend_amendment_diagnostics.json) |
| G4 | Preregistration frozen | [frozen preregistration](docs/PREREGISTRATION_FROZEN.md), [circuits.qpy](results/preregistered/circuits.qpy), [dry run](results/preregistered/dry_run_report.json) |
| G5 | Hardware result recorded | [provider payload](results/raw/H501_provider_payload_d8rfasuab0ds73drkaig.json), [raw analysis](results/processed/Q3_hardware_raw.json), [mitigated analysis](results/processed/Q3_hardware_mitigated.json) |
| G6 | Interpretation complete | [claims](results/claim_evidence_matrix.csv), [final decision](docs/FINAL_DECISION.md), [archive manifest](results/processed/A603_reproducibility_manifest.json) |

## Claim Discipline

Positive claims:

- The basis-order-orientation separation is supported by proofs and exact
  checks.
- Record-capacity and no-go claims are supported independently of QPU data.
- The IBM result supports including the four-qubit GHZ illustration in the main
  text.

Negative claims:

- Do not claim fixed-partition basis uniqueness as the main novelty.
- Do not claim that the IBM hardware observation proves the theorem package.
- Do not infer temporal orientation from redundant records without an anchor.
- Do not use H503 mitigation to replace or rescue the raw H502 result.

## Repository Layout

```text
.
|-- configs/                 # immutable experiment configuration
|-- docs/                    # specification, proofs, reports, architecture
|-- figures/                 # tracked publication figures as PDFs
|-- assets/readme/           # README visual assets and figure previews
|-- reports/                 # LaTeX experiment log for paper development
|-- results/
|   |-- raw/                 # write-once provider receipts and raw payloads
|   |-- processed/           # derived outputs and manifests
|   `-- preregistered/       # frozen QPU preregistration packet
|-- scripts/                 # reproducible task runners
|-- src/objective_clocks/    # typed Python package
|-- tests/                   # theorem, property, regression, and gate tests
|-- CITATION.cff             # citation metadata for the artifact
`-- objective-clocks-reproducibility.tar.gz
```

## Scientific Positioning

The repository intentionally does not rebrand established results as new. It
treats fixed-partition redundant-record basis uniqueness as imported context and
focuses on what remains: ordering, orientation, capacity, and no-go boundaries.
The hardware observation is a preregistered illustration of the four-qubit GHZ
workflow, not the foundation of the theory.

## Use, Citation, And License

Until a preprint is released, cite the repository as a research artifact using
[CITATION.cff](CITATION.cff), the tag
`v0.9.0-g6-final-interpretation` and archive SHA-256
`1ad798aea881e7c189d01907d73b9b5eb60366df33af0cfe0e60ab2b56437dea`.

No standalone license file is currently committed. Treat this as a research
artifact rather than an open-source release until a license is added.

Author and maintainer: Davut Emre Taşar.
