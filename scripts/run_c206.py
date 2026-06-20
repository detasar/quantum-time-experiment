from __future__ import annotations

from pathlib import Path

from objective_clocks.artifacts import environment_manifest, write_json_atomic
from objective_clocks.classical import c5_ghz_exact_rows


def main() -> None:
    processed = Path("results/processed")
    output = processed / "C5_ghz_exact.json"
    payload = c5_ghz_exact_rows()
    payload["environment"] = environment_manifest()
    payload["visualization_policy"] = (
        "Exact C5 values are binary sanity checks and are reported as JSON/table evidence, "
        "not as a standalone publication figure."
    )
    write_json_atomic(output, payload)
    expectations = payload["expectations"]
    if not isinstance(expectations, dict):
        raise TypeError("expectations must be a dictionary")
    if abs(float(expectations["ZZ_C_R1"]["ghz"]) - 1.0) > 1e-10:
        raise SystemExit("C5 analytic ZZ_C_R1 expectation failed")
    if abs(float(expectations["XXXX"]["dephased"])) > 1e-10:
        raise SystemExit("C5 dephased X parity was not zero")
    print(payload)


if __name__ == "__main__":
    main()
