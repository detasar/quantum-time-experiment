# G2 Batch 1 Review Report

Date: 2026-06-20  
Branch: `implementation/g0-g1`

## Completed Task IDs

- C201: Run C0 exhaustive theorem verification.
- C202: Run C1 basis-objectivity landscapes.
- C203: Run C2 order and branching catalog.

## Verification Results

- `scripts/run_c201.py`: passed.
- `scripts/run_c202.py`: passed.
- `scripts/run_c203.py`: passed.

Current code-level verification after implementation:

- `ruff check .`: passed.
- `pytest -q`: 38 passed.
- `mypy src/objective_clocks`: passed.

## Generated Artifacts

- `results/processed/C0_theorem_verification.parquet`
- `results/processed/C0_theorem_fixtures.json`
- `results/processed/C0_runtime_report.json`
- `results/processed/C1_basis_landscape.nc`
- `results/processed/C1_basis_landscape_summary.json`
- `figures/fig_02_basis_landscape.pdf`
- `results/processed/C2_order_catalog.parquet`
- `results/processed/C2_order_catalog_summary.json`
- `results/processed/C2_graphs/*.graphml`

## C201 Evidence

- Grid cells: 42.
- Rows: 188,692.
- Modes: exhaustive small binary maps and seeded-random large maps.
- Theorem failure count: 0.
- Maximal-chain, linear-extension and automorphism counts are stored as separate columns.

## C202 Evidence

- Bell one-record control: minimum score 1.0 and maximum score 1.0 across the qubit grid.
- GHZ two-record Z score: 1.0.
- GHZ two-record X score: 0.0.
- N>2 generalized broadcast Haar summaries use 2,000 fixed-seed samples per configured case.

## C203 Evidence

- Thermometer fixture classified as scalar time.
- Diamond fixture classified as branching/partial order.
- Duplicate fixture classified as non-identifiable duplicate labels.
- Disconnected fixture classified as branching/partial order.
- Orientation-free fixture classified as orientation not identified.
- Erasure fixture classified as persistence-violation control.
- No linear extension is labeled as a physical trajectory.

## Open Items For Remaining G2

- C204: full C3 noise and redundancy sweep.
- C205: C4 assumption stress-test matrix, dependent on C202 and T106.
- C206: C5 exact GHZ/dephased comparison and figure.
