# Final Scientific Decision

Status: `FROZEN`

## Decision

- Selected path: `full_foundations_paper`
- Theory decision: `supported`
- Hardware interpretation: `main_text_quantum_illustration`

The decision follows the preregistered rule: objectivity plus coherence pass
allows the IBM run to appear as a main-text quantum illustration, while a
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
- The IBM result supports including the four-qubit GHZ illustration in the main text.

## Negative Interpretations

- Do not claim fixed-partition basis uniqueness as the main novelty.
- Do not claim that the IBM hardware observation proves the theorem package.
- Do not infer temporal orientation from redundant records without an anchor.
- Do not use H503 mitigation to replace or rescue the raw H502 result.

## Reproducibility Archive

- Archive path: `objective-clocks-reproducibility.tar.gz`
- Archive SHA-256: `1ad798aea881e7c189d01907d73b9b5eb60366df33af0cfe0e60ab2b56437dea`
- Archived file count: `170`
- Clean reproduction command: `/home/emre/quantum-time-experiment/.venv/bin/python scripts/reproduce_all.py`
- Clean reproduction passed: `True`

## Scope Boundary

The paper should be written as a theory/no-go contribution with a bounded IBM
illustration. It should not present basis uniqueness as new, and it should not
let the quantum hardware result carry the theorem-level contribution.
