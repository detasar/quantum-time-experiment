# Codex / Agent Operating Contract

## Mission

Implement and validate the research specification without changing the scientific question to make results easier to obtain.

## Non-negotiable constraints

1. Never submit a QPU job unless all of the following are true:
   - environment variable `ALLOW_QPU_EXECUTION=YES`;
   - `docs/PREREGISTRATION.md` contains no `TBD` in mandatory fields;
   - `results/preregistration_manifest.json` exists;
   - the SHA-256 of the executable circuit manifest matches the preregistered hash;
   - all tests tagged `qpu_gate` pass.
2. Never store IBM tokens, API keys, or provider credentials in the repository.
3. Never alter a theorem definition silently. Any semantic change requires an ADR in `docs/adr/`.
4. Never report an empirical fit as a proof.
5. Never call the X-basis decomposition a full alternative clock unless the relational-admissibility test in the specification is explicitly passed.
6. Never use an LLM judgment as ground truth for an experimental endpoint.
7. Never delete raw data. Corrected data must be written as a new version with lineage metadata.
8. All plots must be generated from scripts; no manual spreadsheet editing.

## Development method

- Write or update tests before implementation.
- Prefer pure, typed functions.
- Every CLI command must emit:
  - config hash,
  - git commit,
  - seed,
  - package versions,
  - timestamp in UTC,
  - output manifest.
- Use deterministic algorithms where possible.
- For numerical optimization, use at least three fixed initialization seeds and report all outcomes.
- Treat theorem counterexamples as first-class outputs.

## Completion standard

A task is not done because code runs once. It is done only when its task-level Definition of Done in `TASKS.yaml` is satisfied and the relevant regression tests pass.

