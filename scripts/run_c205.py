from __future__ import annotations

from pathlib import Path

from objective_clocks.artifacts import environment_manifest, write_json_atomic
from objective_clocks.classical import c4_assumption_stress_matrix


def main() -> None:
    processed = Path("results/processed")
    output = processed / "C4_assumption_failures.json"
    payload = c4_assumption_stress_matrix()
    payload["environment"] = environment_manifest()
    write_json_atomic(output, payload)
    if not payload["all_predicted_failures_observed"]:
        raise SystemExit("C4 predicted failure matrix did not pass")
    print(payload)


if __name__ == "__main__":
    main()
