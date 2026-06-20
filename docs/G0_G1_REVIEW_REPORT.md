# G0/G1 Review Report

Date: 2026-06-20  
Branch: `implementation/g0-g1`

## Completed Task IDs

- R001: Bootstrap repository and environment.
- R002: Implement immutable manifests and hashing.
- R003: Freeze semantic ADR-000.
- T101: Verify chain characterization theorem O1.
- T102: Verify unique scalar timeline criterion.
- T103: Verify binary and multilevel record-capacity bounds.
- T104: Verify noisy redundancy bound.
- T105: Formalize imported basis/objectivity proposition B0.
- T106: Formalize partition and orientation no-go results.

## Verification Results

- `ruff check .`: passed.
- `pytest -q`: 30 passed.
- `mypy src/objective_clocks`: passed.
- `pre-commit run --files <repo files>`: passed.
- `objective-clocks theorem-check --config configs/classical.yaml`: passed.
- `objective-clocks ghz-exact`: passed.
- `objective-clocks ibm-submit`: blocked as expected; no provider job submitted.

## Generated Artifacts

- `results/processed/G0_environment_manifest.json`
- `results/processed/G0_file_manifest.json`
- `results/processed/G1_output_manifest.json`
- `results/processed/T101_chain_verification.json`
- `results/processed/T103_capacity.json`
- `results/processed/T104_noise_bound_grid.json`
- `results/processed/counterexample_catalog.json`
- `figures/fig_03_capacity.pdf`
- `requirements.lock`

## Theorem Counterexamples Found

- Diamond branching poset: two maximal persistent chains, two scheduler linear
  extensions and zero full persistent scalar orders.
- Forced scalar totalization of the diamond requires a record-loss edge between
  incomparable middle snapshots.
- Label permutation no-go: unordered redundant records do not determine temporal
  order.
- Orientation swap no-go: objective Z records do not determine earlier/later
  orientation without blank/present anchoring.
- Unrestricted partition no-go: global refactorization destroys invariant local
  fragment meaning.
- Single-fragment Bell ambiguity: one record is insufficient for preferred-basis
  selection.

## Proposed ADRs

No new ADR is proposed. ADR-000 remains sufficient for G0/G1.

## Scientific Ambiguities Blocking G2

No semantic ambiguity blocks G2. The main implementation constraint for G2 is to
preserve the G1 separation between physical maximal chains, scheduler linear
extensions and automorphism symmetries in all classical experiment outputs.

## Engineering Notes

- The local environment used Python 3.13.11. The package declares
  `requires-python >=3.11`, so this is valid, but the implementation contract
  recommends Python 3.11 or 3.12. A clean reproduction on Python 3.11/3.12 should
  be run before preregistration.
- The repository has not been committed yet; `git_commit` fields are `UNKNOWN`
  until the first commit exists.
