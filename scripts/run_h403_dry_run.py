from __future__ import annotations

import json
import os
from pathlib import Path

from objective_clocks.artifacts import file_manifest, freeze_manifest, write_json_atomic


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    q303 = _read_json(Path("results/processed/Q303_backend_candidates.json"))
    h402 = _read_json(Path("results/preregistered/circuit_manifest.json"))
    prereg = _read_json(Path("results/preregistered/preregistration_manifest.json"))
    provider_metadata = q303.get("provider_metadata", {})
    runtime_account = (
        provider_metadata.get("runtime_account", {}) if isinstance(provider_metadata, dict) else {}
    )
    qpu_execution_enabled = os.getenv("ALLOW_QPU_EXECUTION") == "YES"
    human_approval = bool(prereg.get("human_approval")) and prereg.get("status") == "FROZEN"
    open_instance = (
        isinstance(runtime_account, dict)
        and runtime_account.get("instance_name") == "open-instance"
        and runtime_account.get("plan") == "open"
        and runtime_account.get("pricing_type") == "free"
    )
    instance_name = (
        runtime_account.get("instance_name") if isinstance(runtime_account, dict) else None
    )
    plan = runtime_account.get("plan") if isinstance(runtime_account, dict) else None
    checks = [
        {
            "id": "qpu_env_disabled",
            "passed": not qpu_execution_enabled,
            "evidence": f"ALLOW_QPU_EXECUTION_is_yes={qpu_execution_enabled}",
        },
        {
            "id": "open_instance",
            "passed": open_instance,
            "evidence": f"instance_name={instance_name}; plan={plan}",
        },
        {
            "id": "isa_packet_present",
            "passed": (
                h402.get("total_circuit_instances") == 24
                and h402.get("total_shots") == 24_576
                and bool(h402.get("qpy_sha256"))
            ),
            "evidence": (
                f"total_circuit_instances={h402.get('total_circuit_instances')}; "
                f"total_shots={h402.get('total_shots')}; "
                f"qpy_sha256_present={bool(h402.get('qpy_sha256'))}"
            ),
        },
        {
            "id": "human_approval_recorded",
            "passed": human_approval,
            "evidence": f"human_approval_recorded={human_approval}",
        },
    ]
    report_path = Path("results/preregistered/dry_run_report.json")
    inputs = [
        Path("results/processed/Q303_backend_candidates.json"),
        Path("results/preregistered/circuit_manifest.json"),
        Path("results/preregistered/preregistration_manifest.json"),
    ]
    qpu_submission_allowed_now = bool(qpu_execution_enabled and human_approval and open_instance)
    all_checks_passed = all(check["passed"] for check in checks)
    report = {
        "task": "H403_qpu_submission_dry_run",
        "status": (
            "passed_no_submission_qpu_env_disabled"
            if all_checks_passed
            else "blocked_no_submission"
        ),
        "checks": checks,
        "all_checks_passed": all_checks_passed,
        "qpu_submission_allowed_now": qpu_submission_allowed_now,
        "hardware_jobs_submitted": 0,
        "sampler_invoked": False,
        "inputs": file_manifest([path for path in inputs if path.exists()]),
        "environment": freeze_manifest(),
    }
    write_json_atomic(report_path, report)
    print(
        {
            "task": report["task"],
            "status": report["status"],
            "all_checks_passed": report["all_checks_passed"],
            "qpu_submission_allowed_now": report["qpu_submission_allowed_now"],
            "hardware_jobs_submitted": report["hardware_jobs_submitted"],
        }
    )


if __name__ == "__main__":
    main()
