from __future__ import annotations

import argparse
import json
from pathlib import Path

from objective_clocks.artifacts import write_raw_json_once
from objective_clocks.hardware import (
    H501Inputs,
    build_h501_payload,
    h501_raw_paths,
    load_qpy_circuits,
    validate_h501_preconditions,
    write_h501_receipt,
)

H501_APPROVAL_SOURCE = "Codex user message: quantum deneylerini yapalim"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run or dry-run the locked H501 IBM workload")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Validate without Sampler submission")
    mode.add_argument("--execute", action="store_true", help="Submit the frozen SamplerV2 workload")
    return parser


def main() -> None:
    args = _parser().parse_args()
    inputs = H501Inputs()
    if args.dry_run:
        report = validate_h501_preconditions(
            inputs,
            require_execution_env=False,
            require_clean_repo=False,
        )
        print(report)
        if not report["all_checks_passed"]:
            raise SystemExit("H501 dry-run preconditions failed")
        return

    report = validate_h501_preconditions(
        inputs,
        require_execution_env=True,
        require_clean_repo=True,
    )
    if not report["all_checks_passed"]:
        print(report)
        raise SystemExit("H501 execution preconditions failed")

    from qiskit_ibm_runtime import Batch, QiskitRuntimeService, SamplerV2

    circuit_manifest = json.loads(inputs.circuit_manifest.read_text(encoding="utf-8"))
    preregistration_manifest = json.loads(
        inputs.preregistration_manifest.read_text(encoding="utf-8")
    )
    circuits = load_qpy_circuits(inputs.qpy_path)
    backend_name = str(circuit_manifest["backend"])
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    with Batch(backend=backend, max_time="10m") as batch:
        sampler = SamplerV2(mode=batch)
        job = sampler.run(circuits, shots=1024)
        receipt_path, payload_path = h501_raw_paths(job.job_id(), inputs.raw_root)
        write_h501_receipt(
            receipt_path,
            job=job,
            h501_approval_source=H501_APPROVAL_SOURCE,
        )
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
