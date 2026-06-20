from __future__ import annotations

import json
from pathlib import Path

import yaml

from objective_clocks.isa import write_h402_isa_packet


def main() -> None:
    from qiskit_ibm_runtime import QiskitRuntimeService

    q303_path = Path("results/processed/Q303_backend_candidates.json")
    q303 = json.loads(q303_path.read_text(encoding="utf-8"))
    selected_backend = q303["selected_backend"]
    if q303.get("candidate_source") != "provider" or not selected_backend:
        raise SystemExit("H402 requires a selected provider backend from Q303")
    config = yaml.safe_load(Path("configs/quantum_local.yaml").read_text(encoding="utf-8"))
    service = QiskitRuntimeService()
    backend = service.backend(selected_backend["name"])
    manifest = write_h402_isa_packet(
        backend=backend,
        config=config,
        q303_path=q303_path,
        qpy_path=Path("results/preregistered/circuits.qpy"),
        manifest_path=Path("results/preregistered/circuit_manifest.json"),
    )
    print(
        {
            "task": manifest["task"],
            "status": manifest["status"],
            "backend": manifest["backend"],
            "selected_transpiler_seed": manifest["selected_transpiler_seed"],
            "total_circuit_instances": manifest["total_circuit_instances"],
            "total_shots": manifest["total_shots"],
            "qpy_sha256": manifest["qpy_sha256"],
            "hardware_jobs_submitted": manifest["hardware_jobs_submitted"],
        }
    )


if __name__ == "__main__":
    main()
