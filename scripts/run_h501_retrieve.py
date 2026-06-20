from __future__ import annotations

import argparse
import json
from pathlib import Path

from objective_clocks.artifacts import write_raw_json_once
from objective_clocks.hardware import H501Inputs, build_h501_payload, h501_raw_paths

H501_APPROVAL_SOURCE = "Codex user message: quantum deneylerini yapalim"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Retrieve an accepted H501 IBM Runtime job")
    parser.add_argument("--job-id", required=True)
    return parser


def main() -> None:
    args = _parser().parse_args()
    inputs = H501Inputs()
    circuit_manifest = json.loads(inputs.circuit_manifest.read_text(encoding="utf-8"))
    preregistration_manifest = json.loads(
        inputs.preregistration_manifest.read_text(encoding="utf-8")
    )
    _, payload_path = h501_raw_paths(args.job_id, inputs.raw_root)
    if Path(payload_path).exists():
        raise SystemExit(f"H501 provider payload already exists: {payload_path}")

    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService()
    job = service.job(args.job_id)
    result = job.result()
    payload = build_h501_payload(
        job=job,
        result=result,
        circuit_manifest=circuit_manifest,
        preregistration_manifest=preregistration_manifest,
        h501_approval_source=H501_APPROVAL_SOURCE,
    )
    write_raw_json_once(payload_path, payload)
    print(
        {
            "task": payload["task"],
            "status": payload["status"],
            "backend": payload["backend"],
            "job_id": payload["job"]["job_id"],
            "payload_path": str(Path(payload_path)),
            "total_circuit_instances": payload["total_circuit_instances"],
            "total_shots_observed": payload["total_shots_observed"],
            "secret_values_recorded": payload["secret_values_recorded"],
        }
    )


if __name__ == "__main__":
    main()
