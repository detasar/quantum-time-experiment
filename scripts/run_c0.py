from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import numpy as np

from objective_clocks.order import infer_order
from objective_clocks.types import RecordCode


def main() -> None:
    cases = 0
    failures: list[dict[str, object]] = []
    for n_states in range(2, 6):
        for n_records in range(1, 5):
            # Exhaustive only while the truth-table space is manageable.
            if n_states * n_records > 12:
                continue
            for flat in product((False, True), repeat=n_states * n_records):
                bits = np.array(flat, dtype=bool).reshape(n_states, n_records)
                code = RecordCode(tuple(map(str, range(n_states))), bits)
                result = infer_order(code)
                cases += 1
                # Scalar timeline may be emitted only when quotient poset is total.
                if result.is_total and result.maximal_chain_count != 1:
                    failures.append(
                        {
                            "n_states": n_states,
                            "n_records": n_records,
                            "bits": bits.astype(int).tolist(),
                            "reason": "total poset did not have one maximal chain",
                        }
                    )
    output = {"cases": cases, "failure_count": len(failures), "failures": failures[:100]}
    path = Path("results/processed/C0_theorem_verification.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    if failures:
        raise SystemExit(f"C0 failed with {len(failures)} mismatches")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
