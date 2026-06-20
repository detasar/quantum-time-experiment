# G5 Hardware Notes

Date: 2026-06-20  
Scope: post-submit operator dashboard context for H501.

## Original Submitted Job

- Job id: `d8reasegbcrc73f4f4pg`
- Original backend frozen in H401/H402: `ibm_marrakesh`
- Original physical layout frozen in H402: `[111, 98, 112, 110]`
- Circuit instances: 24
- Total planned shots: 24,576
- Submission receipt: `results/raw/H501_submission_receipt_d8reasegbcrc73f4f4pg.json`
- Cancellation record: `results/raw/H501_cancellation_d8reasegbcrc73f4f4pg.json`

The original job was cancelled while still queued, before any `running`
timestamp, raw result download or QPU usage. The cancellation is treated as a
pre-result protocol amendment, not as a hardware result.

## Backend Amendment H501A1

- Amendment id: `H501A1-kingston-pre-result`
- Replacement backend: `ibm_kingston`
- Replacement physical layout: `[125, 117, 126, 124]`
- Replacement preregistration tag: `v0.4-qpu-preregistered-kingston`
- Q305 diagnostic artifact:
  `results/processed/Q305_backend_amendment_diagnostics.json`

Q305 compared `ibm_kingston`, `ibm_fez` and `ibm_marrakesh` before any
replacement H501 result was available. All candidates passed the backend-derived
local twin gate; `ibm_kingston` was frozen as the replacement backend and all
dependent Q303/Q304/H402/H401/H403/H404 artifacts were regenerated.

## Amended H501 Execution

- Job id: `d8rfasuab0ds73drkaig`
- Backend: `ibm_kingston`
- Physical layout: `[125, 117, 126, 124]`
- Preregistration tag at execution: `v0.4-qpu-preregistered-kingston`
- Submission receipt: `results/raw/H501_submission_receipt_d8rfasuab0ds73drkaig.json`
- Downloaded provider payload: `results/raw/H501_provider_payload_d8rfasuab0ds73drkaig.json`
- Status after result retrieval: `DONE`
- Created: `2026-06-20T20:17:55.809388Z`
- Running: `2026-06-20T20:17:57.209474Z`
- Finished: `2026-06-20T20:18:10.354081Z`
- Quantum usage: 9 seconds
- Circuit instances: 24
- Observed shots: 24,576
- Secret values recorded: `false`

The amended execution is the only completed QPU observation in the repository.
It uses the H501A1-regenerated H401/H402 packet and the Open instance
`open-instance`.

## H502 Locked Raw Analysis

- Artifact: `results/processed/Q3_hardware_raw.json`
- Primary inclusion result:
  `passes_main_text_inclusion_without_mitigation=true`
- Interpretation: `hardware_positive_pending_mitigation_check`
- Bootstrap seed: `20260621`
- Bootstrap replicates: 10,000
- `delta_obj_lcb`: 0.8876953125
- `min_z_correlation_lcb`: 0.9169542107266444
- `delta_coh_lcb`: 0.877685546875
- `w_plus_xxxx`: 0.8955078125
- `w_minus_xxxx`: -0.87744140625
- `w_mix_xxxx`: 0.009033203125
- No-single-block-dominance check: `true`

The primary result remains the raw, unmitigated H502 decision. This is the value
used for bounded artifact-inclusion decisions.

## H503 Secondary Readout Mitigation

- Artifact: `results/processed/Q3_hardware_mitigated.json`
- Raw primary pass carried forward: `true`
- Corrected point-threshold pass: `true`
- Qualitative agreement with raw: `true`
- Tensor assignment condition number: 1.1172921620957568
- Corrected `delta_obj`: 0.9850328718815358
- Corrected `delta_coh`: 0.9687926905262139

H503 is a secondary robustness analysis. It cannot replace or rescue H502; it
only records whether an independent tensor-product readout correction agrees
with the raw conclusion.

## Maintenance Context

Operator dashboard note supplied on 2026-06-20:

- `ibm_marrakesh` is online.
- Scheduled maintenance window shown for `ibm_marrakesh`: 2026-07-15 15:00 to
  2026-07-15 19:00.
- This maintenance window is after the H501 submission date and does not affect
  the current queue decision.

## Queue Context

Read-only API status check during H501 queue wait on 2026-06-20:

| Backend | Operational | Pending jobs | Status message |
|---|---:|---:|---|
| `ibm_marrakesh` | true | 2 | active |
| `ibm_kingston` | true | 0 | active |
| `ibm_fez` | true | 0 | active |

This observation alone was not used to move the experiment. The backend change
was applied only after explicit user approval and after documenting a
pre-result protocol amendment with regenerated dependent artifacts.

## Layered Two-Qubit Error Context

Dashboard table supplied on 2026-06-20 for `ibm_marrakesh`. Values are dashboard
aggregate layered two-qubit errors by number of qubits used; they are context
metadata, not a replacement for the Q303/Q304 calibration snapshot or the H402
selected-layout manifest.

| Number of qubits used | Two-qubit error layered |
|---:|---:|
| 4 | 2.14e-3 |
| 5 | 2.10e-3 |
| 6 | 2.02e-3 |
| 7 | 2.01e-3 |
| 8 | 2.07e-3 |
| 9 | 2.20e-3 |
| 10 | 2.28e-3 |
| 11 | 2.29e-3 |
| 12 | 2.34e-3 |
| 13 | 2.42e-3 |
| 14 | 2.52e-3 |
| 15 | 2.60e-3 |
| 16 | 2.71e-3 |
| 17 | 2.73e-3 |
| 18 | 2.77e-3 |
| 19 | 2.80e-3 |
| 20 | 2.80e-3 |
| 21 | 2.81e-3 |
| 22 | 2.86e-3 |
| 23 | 2.91e-3 |
| 24 | 2.88e-3 |
| 25 | 2.85e-3 |
| 26 | 2.82e-3 |
| 27 | 2.84e-3 |
| 28 | 2.86e-3 |
| 29 | 2.86e-3 |
| 30 | 2.86e-3 |
| 31 | 2.88e-3 |
| 32 | 2.91e-3 |
| 33 | 2.92e-3 |
| 34 | 2.93e-3 |
| 35 | 2.96e-3 |
| 36 | 3.01e-3 |
| 37 | 3.06e-3 |
| 38 | 3.09e-3 |
| 39 | 3.11e-3 |
| 40 | 3.14e-3 |
| 41 | 3.19e-3 |
| 42 | 3.21e-3 |
| 43 | 3.19e-3 |
| 44 | 3.15e-3 |
| 45 | 3.13e-3 |
| 46 | 3.13e-3 |
| 47 | 3.14e-3 |
| 48 | 3.13e-3 |
| 49 | 3.13e-3 |
| 50 | 3.19e-3 |
| 51 | 3.25e-3 |
| 52 | 3.28e-3 |
| 53 | 3.34e-3 |
| 54 | 3.39e-3 |
| 55 | 3.41e-3 |
| 56 | 3.40e-3 |
| 57 | 3.39e-3 |
| 58 | 3.38e-3 |
| 59 | 3.38e-3 |
| 60 | 3.36e-3 |
| 61 | 3.35e-3 |
| 62 | 3.35e-3 |
| 63 | 3.39e-3 |
| 64 | 3.43e-3 |
| 65 | 3.44e-3 |
| 66 | 3.45e-3 |
| 67 | 3.45e-3 |
| 68 | 3.47e-3 |
| 69 | 3.51e-3 |
| 70 | 3.65e-3 |
| 71 | 3.83e-3 |
| 72 | 3.83e-3 |
| 73 | 3.85e-3 |
| 74 | 3.83e-3 |
| 75 | 3.82e-3 |
| 76 | 3.83e-3 |
| 77 | 3.83e-3 |
| 78 | 3.85e-3 |
| 79 | 3.87e-3 |
| 80 | 3.89e-3 |
| 81 | 3.90e-3 |
| 82 | 3.89e-3 |
| 83 | 3.89e-3 |
| 84 | 3.90e-3 |
| 85 | 3.90e-3 |
| 86 | 3.92e-3 |
| 87 | 3.92e-3 |
| 88 | 3.92e-3 |
| 89 | 3.92e-3 |
| 90 | 4.01e-3 |
| 91 | 4.14e-3 |
| 92 | 4.14e-3 |
| 93 | 4.16e-3 |
| 94 | 4.17e-3 |
| 95 | 4.17e-3 |
| 96 | 4.18e-3 |
| 97 | 4.19e-3 |
| 98 | 4.17e-3 |
| 99 | 4.16e-3 |
| 100 | 4.16e-3 |

For the frozen four-qubit workload, the relevant dashboard aggregate row is
4 qubits, layered two-qubit error `2.14e-3`.
