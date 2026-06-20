# Final Scientific Decision

Status: `FROZEN`

## Decision

- Artifact route: `foundations_artifact_with_bounded_quantum_illustration`
- Theory decision: `supported`
- Hardware interpretation: `bounded_quantum_illustration`

The decision follows the preregistered rule: objectivity plus coherence pass
allows the IBM run to remain as a bounded quantum illustration, while a
hardware null result cannot invalidate the independently supported theory
package.

## Evidence

| Check | Value |
|---|---:|
| Unsupported claim count | 0 |
| Q-grade claim count | 2 |
| Raw objectivity LCB | 0.8876953125 |
| Raw minimum Z-correlation LCB | 0.9169542107266444 |
| Raw coherence LCB | 0.877685546875 |
| Raw primary pass | True |
| H503 agrees with raw | True |

## Positive Interpretations

- The basis-order-orientation separation is supported by proofs and exact checks.
- Record-capacity and no-go claims are supported independently of QPU data.
- The IBM result supports retaining the four-qubit GHZ illustration in this artifact.

## Negative Interpretations

- Do not claim fixed-partition basis uniqueness as the main novelty.
- Do not claim that the IBM hardware observation proves the theorem package.
- Do not infer temporal orientation from redundant records without an anchor.
- Do not use H503 mitigation to replace or rescue the raw H502 result.

## Reproducibility Archive

- Archive path: `objective-clocks-reproducibility.tar.gz`
- Archive SHA-256: `3b4592c89f7a57c7a6f51334023a6f99a114b0bba43c96be2a1f999241514024`
- Archived file count: `172`
- Clean reproduction command: `/home/emre/quantum-time-experiment/.venv/bin/python scripts/reproduce_all.py`
- Clean reproduction passed: `True`
- Post-reproduction archive refresh: report-only public redaction; full clean reproduction was not rerun for this redaction-only commit. See `results/processed/A603_reproducibility_manifest.json`.

## Scope Boundary

The artifact should be presented as a theory/no-go and reproducibility package
with a bounded IBM illustration. It should not present basis uniqueness as new,
and it should not let the quantum hardware result carry the theorem-level
contribution.
