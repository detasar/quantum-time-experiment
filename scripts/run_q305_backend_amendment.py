from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from objective_clocks.artifacts import file_manifest, write_json_atomic
from objective_clocks.ibm import _candidate_from_backend
from objective_clocks.quantum import (
    BackendCandidate,
    rank_backend_candidates,
    run_backend_derived_twin,
)


def _candidate_from_ranked_row(row: dict[str, Any]) -> BackendCandidate:
    return BackendCandidate(
        name=str(row["name"]),
        n_qubits=int(row["n_qubits"]),
        operational=bool(row["eligible"]),
        simulator=False,
        pending_jobs=int(row["pending_jobs"]),
        basis_gates=tuple(str(gate) for gate in row["basis_gates"]),
        coupling_edges=tuple((int(edge[0]), int(edge[1])) for edge in row["coupling_edges"]),
        one_qubit_error=float(row["one_qubit_error"]),
        two_qubit_error=float(row["two_qubit_error"]),
        readout_error=float(row["readout_error"]),
        one_qubit_gate_errors=tuple(
            (int(item[0]), float(item[1])) for item in row.get("one_qubit_gate_errors", [])
        ),
        two_qubit_edge_errors=tuple(
            (int(item[0]), int(item[1]), float(item[2]))
            for item in row.get("two_qubit_edge_errors", [])
        ),
        readout_errors=tuple(
            (int(item[0]), float(item[1])) for item in row.get("readout_errors", [])
        ),
        calibration_timestamp=row.get("calibration_timestamp"),
        backend_version=row.get("backend_version"),
    )


def main() -> None:
    from qiskit_ibm_runtime import QiskitRuntimeService

    amendment_path = Path("configs/backend_amendment.yaml")
    if not amendment_path.exists():
        raise SystemExit("Q305 requires configs/backend_amendment.yaml")
    amendment = yaml.safe_load(amendment_path.read_text(encoding="utf-8"))
    config = yaml.safe_load(Path("configs/quantum_local.yaml").read_text(encoding="utf-8"))
    candidate_names = [str(name) for name in amendment["candidate_backends"]]
    service = QiskitRuntimeService()
    candidates = [_candidate_from_backend(service.backend(name)) for name in candidate_names]
    ranked = rank_backend_candidates(candidates)
    rows = []
    for row in ranked:
        candidate = _candidate_from_ranked_row(row)
        twin = run_backend_derived_twin(
            candidate,
            tuple(int(qubit) for qubit in row["selected_layout"]),
            config,
            seed=int(config["master_seed"]) + 304,
        )
        rows.append(
            {
                "backend": row["name"],
                "eligible": row["eligible"],
                "pending_jobs": row["pending_jobs"],
                "layout_score": row["layout_score"],
                "selected_layout": row["selected_layout"],
                "backend_version": row["backend_version"],
                "calibration_timestamp": row["calibration_timestamp"],
                "passes_local_twin": twin["passes_preregistered_local_readiness"],
                "delta_obj_lcb": twin["delta_obj_lcb"],
                "min_z_correlation_lcb": twin["min_z_correlation_lcb"],
                "delta_coh_lcb": twin["delta_coh_lcb"],
                "one_qubit_depolarizing": twin["one_qubit_depolarizing"],
                "two_qubit_depolarizing": twin["two_qubit_depolarizing"],
                "readout_flip": twin["readout_flip"],
            }
        )
    selected_backend = str(amendment["replacement"]["backend"])
    selected = next(row for row in rows if row["backend"] == selected_backend)
    payload = {
        "experiment_id": "Q305",
        "task": "backend_amendment_diagnostics",
        "amendment_id": amendment["amendment_id"],
        "selected_backend": selected_backend,
        "selected_backend_passes_local_twin": selected["passes_local_twin"],
        "selection_uses_hardware_science_results": False,
        "diagnostic_rows": rows,
        "inputs": file_manifest([amendment_path, Path("configs/quantum_local.yaml")]),
        "secret_values_recorded": False,
    }
    output = Path("results/processed/Q305_backend_amendment_diagnostics.json")
    write_json_atomic(output, payload)
    print(
        {
            "experiment_id": payload["experiment_id"],
            "selected_backend": selected_backend,
            "selected_backend_passes_local_twin": selected["passes_local_twin"],
            "candidate_count": len(rows),
        }
    )


if __name__ == "__main__":
    main()
