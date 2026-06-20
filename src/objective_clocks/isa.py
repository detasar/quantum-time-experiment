from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .artifacts import file_manifest, freeze_manifest, sha256_bytes, sha256_file, write_json_atomic
from .circuits import independent_readout_calibration_circuits, named_science_circuits, qpy_payload
from .quantum import SUPPORTED_ENTANGLING_BASIS_GATES


@dataclass(frozen=True)
class ExecutionInstance:
    instance_id: str
    prototype_name: str
    role: str
    block: int | None
    shots: int


def _read_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def build_execution_order(config: dict[str, Any]) -> list[ExecutionInstance]:
    instances: list[ExecutionInstance] = []
    for circuit in independent_readout_calibration_circuits():
        instances.append(
            ExecutionInstance(
                instance_id=circuit.name,
                prototype_name=circuit.name,
                role="readout_calibration",
                block=None,
                shots=int(config["readout_calibration"]["shots_per_circuit"]),
            )
        )
    for block in range(int(config["science"]["blocks"])):
        for name in config["science"]["circuits"]:
            instances.append(
                ExecutionInstance(
                    instance_id=f"{name}__block_{block}",
                    prototype_name=str(name),
                    role="science",
                    block=block,
                    shots=int(config["science"]["shots_per_block"]),
                )
            )
    rng = random.Random(int(config["statistics"]["bootstrap_seed"]))
    rng.shuffle(instances)
    return instances


def _prototype_circuits() -> dict[str, Any]:
    return {
        **named_science_circuits(measure=True),
        **{circuit.name: circuit for circuit in independent_readout_calibration_circuits()},
    }


def _circuits_for_execution_order(order: list[ExecutionInstance]) -> list[Any]:
    prototypes = _prototype_circuits()
    circuits = []
    for instance in order:
        circuit = prototypes[instance.prototype_name].copy()
        circuit.name = instance.instance_id
        circuits.append(circuit)
    return circuits


def _candidate_maps(
    selected_backend: dict[str, Any],
) -> tuple[
    dict[int, float],
    dict[tuple[int, int], float],
    dict[int, float],
]:
    one_q = {
        int(item[0]): float(item[1]) for item in selected_backend.get("one_qubit_gate_errors", [])
    }
    two_q = {
        (int(item[0]), int(item[1])): float(item[2])
        for item in selected_backend.get("two_qubit_edge_errors", [])
    }
    readout = {int(item[0]): float(item[1]) for item in selected_backend.get("readout_errors", [])}
    return one_q, two_q, readout


def _fallback(value_map: dict[Any, float], default: float) -> float:
    return sum(value_map.values()) / len(value_map) if value_map else default


def _circuit_estimated_error(circuit: Any, selected_backend: dict[str, Any]) -> float:
    one_q, two_q, readout = _candidate_maps(selected_backend)
    one_q_default = _fallback(one_q, float(selected_backend["one_qubit_error"]))
    two_q_default = _fallback(two_q, float(selected_backend["two_qubit_error"]))
    readout_default = _fallback(readout, float(selected_backend["readout_error"]))
    total = 0.0
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [circuit.find_bit(qubit).index for qubit in instruction.qubits]
        if name in SUPPORTED_ENTANGLING_BASIS_GATES and len(qubits) == 2:
            total += two_q.get((qubits[0], qubits[1]), two_q_default)
        elif name in {"sx", "x"} and len(qubits) == 1:
            total += one_q.get(qubits[0], one_q_default)
        elif name == "measure" and qubits:
            total += readout.get(qubits[0], readout_default)
    return float(total)


def _circuit_metric(circuit: Any, selected_backend: dict[str, Any]) -> dict[str, Any]:
    counts = dict(circuit.count_ops())
    two_qubit_count = sum(
        int(counts.get(gate, 0)) for gate in sorted(SUPPORTED_ENTANGLING_BASIS_GATES)
    )
    return {
        "name": circuit.name,
        "depth": int(circuit.depth() or 0),
        "two_qubit_count": two_qubit_count,
        "operation_counts": {str(key): int(value) for key, value in sorted(counts.items())},
        "estimated_error": _circuit_estimated_error(circuit, selected_backend),
        "qpy_sha256": sha256_bytes(qpy_payload([circuit])),
    }


def _transpile_ordered_circuits(
    *,
    backend: Any,
    circuits: list[Any],
    layout: list[int],
    seed: int,
) -> list[Any]:
    from qiskit import transpile

    transpiled = transpile(
        circuits,
        backend=backend,
        initial_layout=layout,
        optimization_level=3,
        seed_transpiler=seed,
        num_processes=1,
    )
    return transpiled if isinstance(transpiled, list) else [transpiled]


def _seed_summary(
    *,
    seed: int,
    circuits: list[Any],
    selected_backend: dict[str, Any],
) -> dict[str, Any]:
    circuit_metrics = [_circuit_metric(circuit, selected_backend) for circuit in circuits]
    return {
        "seed": seed,
        "total_two_qubit_count": sum(item["two_qubit_count"] for item in circuit_metrics),
        "total_depth": sum(item["depth"] for item in circuit_metrics),
        "total_estimated_error": sum(item["estimated_error"] for item in circuit_metrics),
        "max_depth": max(item["depth"] for item in circuit_metrics),
    }


def _score_tuple(row: dict[str, Any]) -> tuple[int, int, float, int]:
    return (
        int(row["total_two_qubit_count"]),
        int(row["total_depth"]),
        float(row["total_estimated_error"]),
        int(row["seed"]),
    )


def write_h402_isa_packet(
    *,
    backend: Any,
    config: dict[str, Any],
    q303_path: Path,
    qpy_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    q303 = _read_json(q303_path)
    selected_backend = cast(dict[str, Any], q303["selected_backend"])
    layout = [int(qubit) for qubit in selected_backend["selected_layout"]]
    execution_order = build_execution_order(config)
    ordered_source_circuits = _circuits_for_execution_order(execution_order)

    seed_summaries: list[dict[str, Any]] = []
    transpiled_by_seed: dict[int, list[Any]] = {}
    for seed in range(20):
        transpiled = _transpile_ordered_circuits(
            backend=backend,
            circuits=ordered_source_circuits,
            layout=layout,
            seed=seed,
        )
        transpiled_by_seed[seed] = transpiled
        seed_summaries.append(
            _seed_summary(seed=seed, circuits=transpiled, selected_backend=selected_backend)
        )
    selected_seed = min(seed_summaries, key=_score_tuple)["seed"]
    selected_circuits = transpiled_by_seed[int(selected_seed)]

    qpy_path.parent.mkdir(parents=True, exist_ok=True)
    qpy_path.write_bytes(qpy_payload(selected_circuits))
    execution_rows = [
        {
            "qpy_index": index,
            "instance_id": instance.instance_id,
            "prototype_name": instance.prototype_name,
            "role": instance.role,
            "block": instance.block,
            "shots": instance.shots,
        }
        for index, instance in enumerate(execution_order)
    ]
    circuit_metrics = [_circuit_metric(circuit, selected_backend) for circuit in selected_circuits]
    manifest = {
        "task": "H402_isa_circuit_packet",
        "status": "ready_for_human_preregistration",
        "qpu_execution_allowed": False,
        "backend": selected_backend["name"],
        "backend_version": selected_backend.get("backend_version"),
        "calibration_timestamp": selected_backend.get("calibration_timestamp"),
        "physical_layout": layout,
        "supported_entangling_gates": selected_backend.get("supported_entangling_gates", []),
        "optimization_level": 3,
        "seed_candidates": seed_summaries,
        "seed_selection_rule": (
            "lexicographic_min(total_two_qubit_count,total_depth,total_estimated_error,seed)"
        ),
        "selected_transpiler_seed": selected_seed,
        "execution_order_seed": int(config["statistics"]["bootstrap_seed"]),
        "execution_order": execution_rows,
        "total_circuit_instances": len(execution_rows),
        "total_shots": sum(instance.shots for instance in execution_order),
        "circuit_metrics": circuit_metrics,
        "qpy_path": qpy_path.as_posix(),
        "qpy_sha256": sha256_file(qpy_path),
        "outputs": file_manifest([qpy_path]),
        "environment": freeze_manifest(),
        "selection_uses_hardware_science_results": False,
        "hardware_jobs_submitted": 0,
    }
    write_json_atomic(manifest_path, manifest)
    return manifest
