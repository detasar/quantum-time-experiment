from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, cast

from .artifacts import freeze_manifest
from .ibm import discover_ibm_env_keys, discover_ibm_token_sources, env_file_candidates


def _read_json(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.exists():
        return {}
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _git_status(root: Path) -> list[str]:
    try:
        output = subprocess.check_output(
            ["git", "status", "--short"],
            cwd=root,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return ["git_status_unavailable"]
    return [line for line in output.splitlines() if line.strip()]


def _git_output(root: Path, command: list[str]) -> str:
    try:
        return subprocess.check_output(
            command,
            cwd=root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return ""


def _preregistration_text(root: Path) -> str:
    path = root / "docs/PREREGISTRATION.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _check(
    *,
    check_id: str,
    requirement: str,
    passed: bool,
    evidence: str,
    blocking_tasks: list[str],
    remediation: str,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "requirement": requirement,
        "status": "pass" if passed else "blocked",
        "evidence": evidence,
        "blocking_tasks": blocking_tasks,
        "remediation": remediation,
    }


def build_g4_readiness_audit(root: Path = Path(".")) -> dict[str, Any]:
    q303 = _read_json(root, "results/processed/Q303_backend_candidates.json")
    q304 = _read_json(root, "results/processed/Q2_backend_twin_summary.json")
    q302 = _read_json(root, "results/processed/Q1_noise_sweep_summary.json")
    prereg = _preregistration_text(root)
    env_paths = env_file_candidates()
    token_sources = discover_ibm_token_sources(env_paths)
    git_status = _git_status(root)

    q302_pass = bool(q302.get("grid_cells_complete")) and int(q302.get("passing_cells", 0)) > 0
    q303_provider = q303.get("candidate_source") == "provider"
    q304_ready = q304.get("status") == "backend_snapshot_ready"
    provider_metadata = cast(dict[str, Any], q303.get("provider_metadata", {}))
    runtime_account = cast(dict[str, Any], provider_metadata.get("runtime_account", {}))
    open_instance = (
        runtime_account.get("instance_name") == "open-instance"
        and runtime_account.get("plan") == "open"
        and runtime_account.get("pricing_type") == "free"
    )
    tbd_count = prereg.count("TBD")
    prereg_frozen = "**Status:** FROZEN" in prereg or "Status:** FROZEN" in prereg
    human_approval = "Human approval: `YES`" in prereg
    qpu_disabled = os.getenv("ALLOW_QPU_EXECUTION") != "YES"
    git_commit = _git_output(root, ["git", "rev-parse", "HEAD"])
    upstream = _git_output(
        root,
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
    )
    repo_snapshot_ready = bool(git_commit and upstream)

    checks = [
        _check(
            check_id="G3-Q302",
            requirement="Generic local quantum readiness sweep has at least one passing cell.",
            passed=q302_pass,
            evidence=(
                f"grid_cells_complete={q302.get('grid_cells_complete')}; "
                f"passing_cells={q302.get('passing_cells')}/{q302.get('row_count')}"
            ),
            blocking_tasks=["H401"],
            remediation="Rerun Q302 or revise the local noise thresholds before preregistration.",
        ),
        _check(
            check_id="G3-Q303-PROVIDER",
            requirement="Backend selection uses a real provider calibration snapshot.",
            passed=q303_provider,
            evidence=(
                f"candidate_source={q303.get('candidate_source')}; "
                f"provider_call_attempted={provider_metadata.get('provider_call_attempted')}"
            ),
            blocking_tasks=["H401", "H402"],
            remediation=(
                "Load a valid IBM Runtime token, rerun Q303 and capture a real backend snapshot."
            ),
        ),
        _check(
            check_id="H403-OPEN-INSTANCE",
            requirement="Provider account is bound to the intended IBM Open Plan instance.",
            passed=open_instance,
            evidence=(
                f"instance_name={runtime_account.get('instance_name')}; "
                f"plan={runtime_account.get('plan')}; "
                f"pricing_type={runtime_account.get('pricing_type')}; "
                f"region={runtime_account.get('region')}"
            ),
            blocking_tasks=["H401", "H403"],
            remediation=(
                "Save the Qiskit account with the open-instance CRN before dry-run or QPU gates."
            ),
        ),
        _check(
            check_id="G3-Q304-TWIN",
            requirement=(
                "Backend-derived digital twin passes the preregistered local readiness gate."
            ),
            passed=q304_ready,
            evidence=f"status={q304.get('status')}; reason={q304.get('reason')}",
            blocking_tasks=["H401", "H402"],
            remediation="Rerun Q304 after Q303 obtains a real provider backend snapshot.",
        ),
        _check(
            check_id="H401-PREREG-FIELDS",
            requirement="Preregistration has no mandatory TBD fields and is marked FROZEN.",
            passed=tbd_count == 0 and prereg_frozen,
            evidence=f"tbd_count={tbd_count}; prereg_frozen={prereg_frozen}",
            blocking_tasks=["H401"],
            remediation="Fill all mandatory fields and freeze docs/PREREGISTRATION_FROZEN.md.",
        ),
        _check(
            check_id="H401-HUMAN-APPROVAL",
            requirement="Human review approves the frozen preregistration.",
            passed=human_approval,
            evidence=f"human_approval={human_approval}",
            blocking_tasks=["H401"],
            remediation="Record explicit human approval after preregistration review.",
        ),
        _check(
            check_id="H403-QPU-GATE",
            requirement="QPU execution remains hard-disabled during dry run.",
            passed=qpu_disabled,
            evidence=f"ALLOW_QPU_EXECUTION_is_yes={not qpu_disabled}",
            blocking_tasks=["H403"],
            remediation="Unset ALLOW_QPU_EXECUTION until the explicit H501 human gate.",
        ),
        _check(
            check_id="H404-REPO-SNAPSHOT",
            requirement="Repository has an initial committed snapshot tracking a remote branch.",
            passed=repo_snapshot_ready,
            evidence=(
                f"git_commit={git_commit or 'UNKNOWN'}; upstream={upstream or 'NONE'}; "
                f"working_tree_entries_at_audit_time={len(git_status)}"
            ),
            blocking_tasks=["H404"],
            remediation=(
                "Commit and push the research snapshot before preregistration tagging; "
                "rerun the final H404 clean check immediately before creating the tag."
            ),
        ),
    ]
    blocked = [check for check in checks if check["status"] != "pass"]
    token_key_presence = discover_ibm_env_keys(env_paths)
    return {
        "task": "G4_readiness_audit",
        "overall_status": "ready_for_h401" if not blocked else "blocked_before_g4",
        "blocked_check_count": len(blocked),
        "checks": checks,
        "ibm_credential_audit": {
            "env_files_scanned": len(env_paths),
            "key_presence": token_key_presence,
            "token_source_count": len(token_sources),
            "token_sources": token_sources,
            "secret_values_recorded": False,
        },
        "environment": freeze_manifest(),
        "next_required_actions": [
            check["remediation"] for check in checks if check["status"] != "pass"
        ],
    }
