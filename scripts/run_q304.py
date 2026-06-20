from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from objective_clocks.artifacts import file_manifest, write_json_atomic
from objective_clocks.quantum import BackendCandidate, run_backend_derived_twin


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
    q303_path = Path("results/processed/Q303_backend_candidates.json")
    if not q303_path.exists():
        raise SystemExit("Run Q303 before Q304")

    q303 = json.loads(q303_path.read_text(encoding="utf-8"))
    selected = q303.get("selected_backend")
    provider_source = q303.get("candidate_source")
    rows = []
    if provider_source != "provider" or not selected:
        rows.append(
            {
                "experiment_id": "Q304",
                "status": "hardware_stage_stopped",
                "reason": "no_selected_provider_backend_snapshot_available",
                "candidate_source": provider_source,
                "backend": selected["name"] if selected else None,
                "passes_preregistered_local_readiness": False,
            }
        )
    else:
        config = yaml.safe_load(Path("configs/quantum_local.yaml").read_text(encoding="utf-8"))
        row = run_backend_derived_twin(
            _candidate_from_ranked_row(selected),
            tuple(int(qubit) for qubit in selected["selected_layout"]),
            config,
            seed=int(config["master_seed"]) + 304,
        )
        row["status"] = (
            "backend_snapshot_ready"
            if row["passes_preregistered_local_readiness"]
            else "hardware_stage_stopped"
        )
        row["reason"] = (
            "backend_derived_aggregate_noise_passed"
            if row["passes_preregistered_local_readiness"]
            else "backend_derived_aggregate_noise_failed"
        )
        row["model_class"] = "selected_layout_aggregate_depolarizing_proxy"
        rows.append(row)
    output = Path("results/processed/Q2_backend_twin.parquet")
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(output, index=False)
    summary = {
        "experiment_id": "Q304",
        "status": rows[0]["status"],
        "reason": rows[0]["reason"],
        "backend": rows[0].get("backend"),
        "backend_version": rows[0].get("backend_version"),
        "calibration_timestamp": rows[0].get("calibration_timestamp"),
        "candidate_source": rows[0].get("candidate_source"),
        "model_class": rows[0].get("model_class"),
        "passes_preregistered_local_readiness": rows[0]["passes_preregistered_local_readiness"],
        "outputs": file_manifest([output]),
    }
    write_json_atomic(Path("results/processed/Q2_backend_twin_summary.json"), summary)
    print(summary)


if __name__ == "__main__":
    main()
