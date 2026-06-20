# Codex Start Prompt

You are implementing the research repository **Objective Clock Bases from Redundant Records**.

Read these files in this exact order:

1. `AGENTS.md`
2. `docs/RESEARCH_SPEC_TR.md`
3. `docs/CODEX_IMPLEMENTATION.md`
4. `TASKS.yaml`
5. `docs/adr/000-semantic-freeze.md`

Then execute only Gate G0 and Gate G1 tasks. Do not start quantum hardware work. Do not submit any provider job. Do not change the scientific semantics without creating a new ADR.

Critical scientific correction that must be preserved:

- persistent trajectories are **chains** in the record-dominance poset;
- arbitrary linear extensions are scheduler totalizations and are not generally physical trajectories;
- scalar time may be emitted only when all relevant record signatures form a chain.

Working procedure:

- create a git branch `implementation/g0-g1`;
- install the environment;
- run the existing 18 tests;
- implement tasks in dependency order;
- add tests before changing implementation;
- create the artifacts required by each task’s Definition of Done;
- stop at the end of G1 and produce a review report listing:
  - completed task IDs,
  - test results,
  - theorem counterexamples found,
  - any proposed ADR,
  - any scientific ambiguity that blocks G2.

The goal is falsification and reproducibility, not a positive-looking result.
