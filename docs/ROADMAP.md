# Execution Roadmap

## Sprint 0 — Two-day semantic and repository freeze

### Day 1
- Review `RESEARCH_SPEC_TR.md`.
- Accept ADR-000.
- Install environment and run tests.
- Create git tag `v0.1-spec-freeze`.

### Day 2
- Finish manifests and output schemas.
- Confirm no QPU path is executable.
- Review imported-versus-new theorem labels.

**Exit gate:** G0.

## Sprint 1 — Exact theory and counterexamples, days 3–7

- T101 chain characterization.
- T102 scalar-time criterion.
- T103 capacity bounds.
- T104 noisy redundancy.
- T105 imported basis proposition.
- T106 no-go package.

Daily rule: every proof attempt must be paired with one counterexample attempt.

**Exit gate:** G1.

## Sprint 2 — Classical experiments, week 2

- C0 exact verification.
- C1 basis landscapes.
- C2 branching catalog.
- C3 noise phase diagram.
- C4 assumption failures.
- C5 GHZ exact comparison.

**Scientific review at end of week:**

Proceed only if:
- chain/order package is correct and nontrivial;
- basis layer is clearly labeled prior-art-derived;
- partial-order output is operationally meaningful;
- at least one record-capacity or robustness result is useful enough to carry a methods/theory contribution.

**Exit gate:** G2.

## Sprint 3 — Local quantum work, week 3

- Freeze circuits.
- Generic noise sweep.
- Backend/layout selector.
- Digital twin.

No IBM submission.

**Exit gate:** G3 only if local thresholds pass.

## Sprint 4 — Preregistration, week 4

- Fill preregistration.
- Freeze ISA circuits.
- Dry-run gate.
- Reproduce all classical and local quantum outputs from clean environment.
- Tag `v0.3-qpu-preregistered`.

**Exit gate:** G4.

## Sprint 5 — IBM and locked analysis

- Check Open Plan remaining allocation.
- Submit one batch.
- Retrieve and hash raw data.
- Run raw primary analysis.
- Run secondary readout correction.

**Exit gate:** G5.

## Sprint 6 — Interpretation and paper decision

- Evidence-grade claims.
- Apply decision tree.
- Choose:
  - full foundations paper;
  - short theory/no-go note;
  - abandon/pivot.
- Do not begin polished paper writing until this decision is signed.

## Human review checkpoints

1. After G1: theorem correctness and novelty positioning.
2. After G2: whether the classical package is paper-worthy.
3. Before G4: whether IBM adds scientifically interpretable evidence.
4. After G5: interpretation under preregistered rules.

