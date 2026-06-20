from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from .artifacts import sha256_bytes, sha256_file, write_json_atomic

LOGICAL_QUBITS = {"C": 0, "S": 1, "R1": 2, "R2": 3}


def _qiskit() -> Any:
    try:
        from qiskit import QuantumCircuit
    except ImportError as exc:
        raise RuntimeError("Install the quantum extra: pip install -e '.[quantum]'") from exc
    return QuantumCircuit


def ghz_circuit(*, phase: int, basis: str, measure: bool = True) -> Any:
    if phase not in {1, -1}:
        raise ValueError("phase must be +1 or -1")
    if basis not in {"Z", "X"}:
        raise ValueError("basis must be Z or X")
    QuantumCircuit = _qiskit()
    circuit = QuantumCircuit(4, 4, name=f"ghz_{'plus' if phase == 1 else 'minus'}_{basis}")
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(0, 2)
    circuit.cx(0, 3)
    if phase == -1:
        circuit.z(0)
    if basis == "X":
        for qubit in range(4):
            circuit.h(qubit)
    if measure:
        circuit.measure(range(4), range(4))
    return circuit


def science_circuits() -> list[Any]:
    return [
        ghz_circuit(phase=1, basis="Z"),
        ghz_circuit(phase=1, basis="X"),
        ghz_circuit(phase=-1, basis="Z"),
        ghz_circuit(phase=-1, basis="X"),
    ]


def named_science_circuits(*, measure: bool = True) -> dict[str, Any]:
    return {
        "ghz_plus_z": ghz_circuit(phase=1, basis="Z", measure=measure),
        "ghz_plus_x": ghz_circuit(phase=1, basis="X", measure=measure),
        "ghz_minus_z": ghz_circuit(phase=-1, basis="Z", measure=measure),
        "ghz_minus_x": ghz_circuit(phase=-1, basis="X", measure=measure),
    }


def independent_readout_calibration_circuits() -> list[Any]:
    QuantumCircuit = _qiskit()
    circuits: list[Any] = []
    for qubit in range(4):
        for prepared in (0, 1):
            circuit = QuantumCircuit(4, 4, name=f"ro_q{qubit}_{prepared}")
            if prepared:
                circuit.x(qubit)
            circuit.measure(range(4), range(4))
            circuits.append(circuit)
    return circuits


def qpy_payload(circuits: list[Any]) -> bytes:
    try:
        from qiskit import qpy
    except ImportError as exc:
        raise RuntimeError("Install the quantum extra: pip install -e '.[quantum]'") from exc
    buffer = BytesIO()
    qpy.dump(circuits, buffer)
    return buffer.getvalue()


def write_q301_circuit_manifest(manifest_path: Path, qpy_path: Path) -> dict[str, Any]:
    circuits = named_science_circuits(measure=True)
    calibration = independent_readout_calibration_circuits()
    qpy_path.parent.mkdir(parents=True, exist_ok=True)
    qpy_path.write_bytes(qpy_payload([*circuits.values(), *calibration]))
    payload = {
        "experiment_id": "Q301",
        "logical_qubits": LOGICAL_QUBITS,
        "science_circuits": [
            {
                "name": name,
                "basis": "X" if name.endswith("_x") else "Z",
                "phase": -1 if "minus" in name else 1,
                "qubit_count": int(circuit.num_qubits),
                "classical_bit_count": int(circuit.num_clbits),
                "operation_counts": dict(circuit.count_ops()),
            }
            for name, circuit in circuits.items()
        ],
        "readout_calibration_circuits": len(calibration),
        "contains_tomography": False,
        "qpy_path": str(qpy_path),
        "qpy_sha256": sha256_file(qpy_path),
        "unmeasured_circuit_hashes": {
            name: sha256_bytes(qpy_payload([circuit]))
            for name, circuit in named_science_circuits(measure=False).items()
        },
    }
    write_json_atomic(manifest_path, payload)
    return payload
