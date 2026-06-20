# Codex Implementation Contract

This document is the execution plan. `RESEARCH_SPEC_TR.md` is the scientific source of truth. If code and theory conflict, stop and open an ADR; do not silently reinterpret the theory.

## 1. Execution philosophy

The implementation must proceed through hard gates. Codex must not skip ahead to the visually interesting quantum stage.

```text
G0 Repository ready
  -> G1 Theory objects + exact property tests
  -> G2 Classical experiments complete
  -> G3 Local quantum simulation passes
  -> G4 Preregistration frozen
  -> G5 One IBM batch
  -> G6 Locked analysis and interpretation
```

## 2. Environment

Target:

- Python 3.11 or 3.12
- Linux preferred
- CPU-first; 12 GB GPU is optional
- Qiskit 2.x
- qiskit-ibm-runtime 0.46.1 or newer compatible release

Recommended setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e '.[dev,quantum]'
pre-commit install
pytest -q
```

## 3. Global constants

```python
MASTER_SEED = 20260620
LOGICAL_QUBITS = {"C": 0, "S": 1, "R1": 2, "R2": 3}
PRIMARY_ALPHA = 0.05
BOOTSTRAP_REPLICATES = 10_000
```

These values may only change through an ADR before preregistration.

## 4. Required implementation modules

### `types.py`

Typed immutable domain objects:

- `ClockBasis`
- `PhysicalPartition`
- `RecordCode`
- `RecordFamily`
- `OrderInferenceResult`
- `ExperimentManifest`
- `QuantumCircuitSpec`

Validation rules:

- basis projectors are Hermitian, idempotent, orthogonal, complete;
- record vectors have consistent dimensions;
- q is odd for majority experiments unless tie policy is explicit;
- clock labels are unique;
- raw paths cannot point outside `results/raw`.

### `information.py`

- von Neumann entropy
- Shannon entropy
- classical mutual information
- partial trace
- Holevo information
- trace distance
- Helstrom binary error

All functions need analytic regression tests.

### `order.py`

- construct dominance preorder
- quotient duplicate signatures
- Hasse diagram
- test persistence of a candidate total order
- enumerate/count maximal persistent chains
- enumerate/count linear extensions only as scheduler diagnostics
- automorphism group enumeration for small graphs
- ambiguity metrics
- thermometer code generator
- multi-level capacity checker

### `states.py`

- Bell state
- GHZ_n state
- dephased GHZ mixture
- generalized broadcast history state
- candidate-basis conditional fragment states
- optional random Haar basis generator

### `basis.py`

- qubit basis parameterization
- PVM distance with Hungarian matching/permutation
- objective score landscape
- fixed-partition basis scan
- maxima clustering

### `noise.py`

- classical bit-flip record noise
- majority decoder
- exact binomial tail
- Hoeffding bound
- Qiskit Aer generic noise models
- backend-derived noise model adapter

### `circuits.py`

- GHZ+ Z/X circuits
- GHZ− Z/X circuits
- readout calibration circuits
- deterministic transpilation and manifest creation
- no provider calls

### `ibm.py`

Provider integration isolated here.

Must enforce:

```python
if os.getenv("ALLOW_QPU_EXECUTION") != "YES":
    raise PermissionError(...)
```

Must verify preregistration hash before submission.

### `statistics.py`

- Pauli correlations from bitstrings
- Clopper–Pearson mapped intervals
- bootstrap contrasts
- block drift diagnostics
- raw vs mitigated reporting

### `artifacts.py`

- config hashing
- SHA-256 manifests
- package/version capture
- git commit capture
- write-once raw artifact guard

### `cli.py`

Required commands:

```text
objective-clocks theorem-check
objective-clocks basis-scan
objective-clocks order-experiment
objective-clocks noise-sweep
objective-clocks ghz-exact
objective-clocks ghz-noise
objective-clocks ibm-prepare
objective-clocks ibm-submit
objective-clocks ibm-analyze
objective-clocks reproduce-all
```

## 5. Test-first order

### Phase 1 — Mathematical primitives

1. Implement entropy and partial trace tests.
2. Implement GHZ analytic correlations.
3. Implement record preorder, maximal chains, and diagnostic linear extensions.
4. Implement capacity-bound property tests.
5. Implement majority bound.

No plot code before these pass.

### Phase 2 — Basis landscape

1. Bell one-fragment ambiguity.
2. GHZ two-fragment preferred basis.
3. Rotated basis scan.
4. Noisy/overlapping record states.

### Phase 3 — Experiments

Implement C0–C5 in order. Each experiment is a pure function from immutable config to an output directory.

### Phase 4 — Quantum

Only after C0–C5 pass.

## 6. Required tests

### Unit tests

- entropy of pure and maximally mixed states;
- GHZ correlations;
- dephased parity zero;
- Qiskit bit endianness fixture;
- thermometer code order;
- diamond has exactly two maximal persistent chains and no full persistent scalar order;
- duplicate signatures quotient correctly;
- maximum Boolean chain bound small exhaustive cases;
- majority exact tail ≤ Hoeffding bound;
- basis distance invariant under permutation/phases.

### Property tests

Use Hypothesis where feasible:

- every persistent trajectory is a chain;
- every chain ordered by dominance satisfies persistence;
- arbitrary linear extensions are never mislabeled as physical trajectories;
- relabeling a record code preserves maximal-chain and linear-extension counts;
- increasing q cannot worsen exact majority error;
- increasing p cannot improve theoretical bit error;
- pure GHZ and GHZ− have identical Z populations.

### Integration tests

- each CLI command creates a manifest;
- rerunning same config produces identical exact outputs;
- stochastic runs reproduce within stored seed;
- no QPU command works without the environment gate;
- preregistration hash mismatch blocks submission.

## 7. Data schemas

### Classical result row

```json
{
  "experiment_id": "C3",
  "config_hash": "...",
  "git_commit": "...",
  "seed": 20260620,
  "N": 8,
  "E": 7,
  "q": 9,
  "p": 0.10,
  "trial_count": 10000,
  "exact_order_recovery": 0.992,
  "hoeffding_lower_success": 0.971,
  "timestamp_utc": "..."
}
```

### Quantum raw metadata

```json
{
  "backend": "...",
  "instance_plan": "open",
  "backend_properties_timestamp": "...",
  "physical_layout": [0, 1, 2, 3],
  "transpiler_seed": 7,
  "optimization_level": 3,
  "circuit_hashes": {},
  "shots_per_block": 1024,
  "blocks": 4,
  "job_id_encrypted_or_private": true,
  "provider_payload_sha256": "..."
}
```

## 8. Experiment runners

Every runner must:

1. load YAML config;
2. validate with Pydantic;
3. calculate config hash;
4. create a run directory named `<experiment>-<hash-prefix>`;
5. refuse overwrite unless exact duplicate and `--resume`;
6. write environment manifest before computation;
7. write result atomically;
8. write completion marker only after validation;
9. generate no claim text automatically.

## 9. Definition of Ready per phase

### G0 DoR

- dependencies resolve;
- tests run;
- repository clean;
- theory spec present.

### G1 DoR

- all definitions encoded;
- no unresolved label semantics;
- analytic fixtures known.

### G2 DoR

- G1 tests pass;
- experiment configs reviewed;
- output schema frozen.

### G3 DoR

- classical results complete;
- Qiskit versions recorded;
- exact GHZ expectations pass.

### G4 DoR

- backend-selection algorithm implemented;
- noise twin results pass thresholds;
- preregistration complete;
- QPU gate tests pass.

### G5 DoR

- Open Plan remaining time verified;
- final circuits hashed;
- repository tagged;
- no uncommitted changes;
- explicit human decision to set `ALLOW_QPU_EXECUTION=YES`.

## 10. Definition of Done per phase

### G1 Done

- theorem property tests pass exhaustively in required finite range;
- counterexamples serialized;
- proof document and code semantics agree.

### G2 Done

- C0–C5 complete;
- no missing grid cells;
- all figures reproducible;
- basis/order/no-go conclusions can be evaluated without hardware.

### G3 Done

- ideal/noisy/twin simulations complete;
- shot design justified;
- expected intervals generated;
- no tomography required.

### G4 Done

- signed preregistration manifest;
- QPY/QASM files frozen;
- QPU submission command dry-run succeeds without provider call.

### G5 Done

- exactly one accepted job or policy-compliant provider retry;
- immutable raw payload;
- primary analysis unchanged;
- outcome classification recorded.

## 11. Stop conditions

Codex must stop and request scientific review if:

- objective-basis score is not invariant under phase/permutation as expected;
- single-record Bell control does not show basis ambiguity;
- chain-characterization property test fails;
- induced poset is treated as total without proof;
- a proposed circuit requires tomography;
- hardware thresholds are changed after seeing hardware data;
- QPU experiment becomes the only remaining contribution.

## 12. Expected deliverables

```text
results/processed/C0_theorem_verification.parquet
results/processed/C1_basis_landscape.nc
results/processed/C2_order_catalog.parquet
results/processed/C3_noise_phase_diagram.parquet
results/processed/C4_assumption_failures.json
results/processed/C5_ghz_exact.json
results/processed/Q1_noise_sweep.parquet
results/processed/Q2_backend_twin.parquet
results/processed/Q3_hardware_summary.json
figures/fig_01_hierarchy.pdf
figures/fig_02_basis_landscape.pdf
figures/fig_03_capacity.pdf
figures/fig_04_noise_phase.pdf
figures/fig_05_ghz.pdf
```

## 13. Final Codex instruction

Optimize for falsification and reproducibility, not for producing a visually positive result. A clean no-go or partial-order result is a successful scientific output.

