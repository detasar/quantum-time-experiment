from __future__ import annotations

from pathlib import Path

from objective_clocks.artifacts import file_manifest, write_json_atomic
from objective_clocks.circuits import ghz_circuit, write_q301_circuit_manifest
from objective_clocks.quantum import (
    exact_science_expectations,
    parse_qiskit_bitstring,
    simulate_counts,
)


def main() -> None:
    processed = Path("results/processed")
    manifest_path = processed / "Q301_circuit_manifest.json"
    qpy_path = processed / "Q301_untranspiled_circuits.qpy"
    payload = write_q301_circuit_manifest(manifest_path, qpy_path)
    expectations = exact_science_expectations()
    payload["statevector_expectations"] = expectations
    payload["endianness_fixture"] = {
        "qiskit_key": "0001",
        "logical_order": ["C", "S", "R1", "R2"],
        "parsed": list(parse_qiskit_bitstring("0001")),
    }
    payload["shot_smoke_counts"] = simulate_counts(
        circuit=ghz_circuit(phase=1, basis="Z", measure=True),
        shots=128,
        seed=20260620,
    )
    payload["outputs"] = file_manifest([qpy_path])
    write_json_atomic(manifest_path, payload)
    if payload["contains_tomography"]:
        raise SystemExit("Q301 circuit family must not contain tomography")
    if abs(expectations["ghz_plus_z"]["ZZ_C_R1"] - 1.0) > 1e-10:
        raise SystemExit("Q301 statevector ZZ_C_R1 expectation failed")
    print(payload)


if __name__ == "__main__":
    main()
