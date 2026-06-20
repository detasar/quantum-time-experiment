from __future__ import annotations

import glob
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np

from .artifacts import file_manifest, freeze_manifest, sha256_file, write_json_atomic
from .ibm import assert_qpu_gate
from .quantum import counts_to_bit_array, parse_qiskit_bitstring, quantum_metrics_from_counts
from .statistics import bootstrap_contrasts


@dataclass(frozen=True)
class H501Inputs:
    preregistration_manifest: Path = Path("results/preregistered/preregistration_manifest.json")
    circuit_manifest: Path = Path("results/preregistered/circuit_manifest.json")
    qpy_path: Path = Path("results/preregistered/circuits.qpy")
    g4_readiness_audit: Path = Path("results/processed/G4_readiness_audit.json")
    q303_snapshot: Path = Path("results/processed/Q303_backend_candidates.json")
    raw_root: Path = Path("results/raw")


def _read_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _safe_identifier(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return cleaned[:96] or "unknown_job"


def _jsonable(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {str(key): _jsonable(nested) for key, nested in value.items()}
        if isinstance(value, (list, tuple)):
            return [_jsonable(item) for item in value]
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)


def _git_clean(root: Path = Path(".")) -> bool:
    import subprocess

    output = subprocess.check_output(["git", "status", "--short"], cwd=root, text=True)
    return output.strip() == ""


def _tag_points_at_head(tag: str, root: Path = Path(".")) -> bool:
    import subprocess

    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        tag_commit = subprocess.check_output(
            ["git", "rev-list", "-n", "1", tag],
            cwd=root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return False
    return bool(head and head == tag_commit)


def _existing_h501_raw_files(raw_root: Path) -> list[Path]:
    return [Path(path) for path in sorted(glob.glob(str(raw_root / "H501_*")))]


def validate_h501_preconditions(
    inputs: H501Inputs | None = None,
    *,
    require_execution_env: bool,
    require_clean_repo: bool = True,
) -> dict[str, Any]:
    inputs = H501Inputs() if inputs is None else inputs
    if require_execution_env:
        prereg = assert_qpu_gate(inputs.preregistration_manifest, inputs.circuit_manifest)
    else:
        prereg = _read_json(inputs.preregistration_manifest)
        if not inputs.circuit_manifest.exists():
            raise FileNotFoundError("Circuit manifest is mandatory")
    circuit_manifest = _read_json(inputs.circuit_manifest)
    g4 = _read_json(inputs.g4_readiness_audit)
    q303 = _read_json(inputs.q303_snapshot)
    provider_metadata = cast(dict[str, Any], q303.get("provider_metadata", {}))
    runtime_account = cast(dict[str, Any], provider_metadata.get("runtime_account", {}))
    existing_raw = _existing_h501_raw_files(inputs.raw_root)
    open_instance = (
        runtime_account.get("instance_name") == "open-instance"
        and runtime_account.get("plan") == "open"
        and runtime_account.get("pricing_type") == "free"
    )
    qpy_hash_matches = inputs.qpy_path.exists() and (
        sha256_file(inputs.qpy_path) == circuit_manifest.get("qpy_sha256")
    )
    g4_ready = g4.get("overall_status") == "ready_for_h501" and g4.get("blocked_check_count") == 0
    clean_repo = _git_clean() if require_clean_repo else True
    tag_ready = _tag_points_at_head("v0.3-qpu-preregistered")
    all_shots = {int(item["shots"]) for item in circuit_manifest.get("execution_order", [])}
    env_enabled = os.getenv("ALLOW_QPU_EXECUTION") == "YES"
    checks = [
        {
            "id": "env_gate",
            "passed": env_enabled if require_execution_env else not env_enabled,
            "evidence": f"ALLOW_QPU_EXECUTION_is_yes={env_enabled}",
        },
        {
            "id": "frozen_preregistration",
            "passed": prereg.get("status") == "FROZEN",
            "evidence": f"status={prereg.get('status')}",
        },
        {
            "id": "circuit_manifest_hash",
            "passed": prereg.get("circuit_manifest_sha256") == sha256_file(inputs.circuit_manifest),
            "evidence": "manifest_hash_matches_preregistration",
        },
        {
            "id": "qpy_hash",
            "passed": qpy_hash_matches,
            "evidence": f"qpy_hash_present={bool(circuit_manifest.get('qpy_sha256'))}",
        },
        {
            "id": "g4_ready",
            "passed": g4_ready,
            "evidence": (
                f"overall_status={g4.get('overall_status')}; "
                f"blocked_check_count={g4.get('blocked_check_count')}"
            ),
        },
        {
            "id": "open_instance",
            "passed": open_instance,
            "evidence": (
                f"instance_name={runtime_account.get('instance_name')}; "
                f"plan={runtime_account.get('plan')}; "
                f"pricing_type={runtime_account.get('pricing_type')}"
            ),
        },
        {
            "id": "single_shot_count",
            "passed": all_shots == {1024},
            "evidence": f"unique_shot_counts={sorted(all_shots)}",
        },
        {
            "id": "no_prior_h501_raw_payload",
            "passed": len(existing_raw) == 0,
            "evidence": f"existing_h501_raw_files={len(existing_raw)}",
        },
        {
            "id": "repo_clean",
            "passed": clean_repo,
            "evidence": f"require_clean_repo={require_clean_repo}; clean={clean_repo}",
        },
        {
            "id": "preregistration_tag",
            "passed": tag_ready,
            "evidence": "tag=v0.3-qpu-preregistered",
        },
    ]
    return {
        "task": "H501_preconditions",
        "all_checks_passed": all(check["passed"] for check in checks),
        "checks": checks,
        "backend": circuit_manifest.get("backend"),
        "qpy_path": inputs.qpy_path.as_posix(),
        "total_circuit_instances": circuit_manifest.get("total_circuit_instances"),
        "total_shots": circuit_manifest.get("total_shots"),
        "secret_values_recorded": False,
    }


def load_qpy_circuits(path: Path) -> list[Any]:
    from qiskit import qpy

    with path.open("rb") as handle:
        return list(qpy.load(handle))


def sampler_result_counts(
    result: Any,
    execution_order: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if len(result) != len(execution_order):
        raise ValueError(
            f"Sampler result length {len(result)} does not match execution order "
            f"{len(execution_order)}"
        )
    for index, (pub_result, execution) in enumerate(zip(result, execution_order, strict=True)):
        data_items = list(pub_result.data.items())
        bit_arrays = [value for _, value in data_items if hasattr(value, "get_counts")]
        if len(bit_arrays) != 1:
            raise ValueError(f"Expected one classical bit array for qpy_index={index}")
        counts = {str(key): int(value) for key, value in bit_arrays[0].get_counts().items()}
        count_total = sum(counts.values())
        rows.append(
            {
                "qpy_index": index,
                "instance_id": execution["instance_id"],
                "prototype_name": execution["prototype_name"],
                "role": execution["role"],
                "block": execution["block"],
                "shots": int(execution["shots"]),
                "count_total": count_total,
                "counts": dict(sorted(counts.items())),
            }
        )
    return rows


def _job_status_text(job: Any) -> str:
    try:
        status = job.status()
    except Exception as exc:
        return f"status_error:{type(exc).__name__}"
    return str(getattr(status, "name", status))


def _job_metadata(job: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "job_id": job.job_id() if callable(getattr(job, "job_id", None)) else None,
        "status": _job_status_text(job),
    }
    for name in ("creation_date",):
        try:
            value = getattr(job, name)
            metadata[name] = value.isoformat() if hasattr(value, "isoformat") else str(value)
        except Exception:
            metadata[name] = None
    for method in ("usage", "metrics"):
        try:
            value = getattr(job, method)()
            metadata[method] = _jsonable(value)
        except Exception as exc:
            metadata[f"{method}_error"] = f"{type(exc).__name__}: {exc}"
    return metadata


def h501_raw_paths(job_id: str, raw_root: Path = Path("results/raw")) -> tuple[Path, Path]:
    safe_job_id = _safe_identifier(job_id)
    return (
        raw_root / f"H501_submission_receipt_{safe_job_id}.json",
        raw_root / f"H501_provider_payload_{safe_job_id}.json",
    )


def build_h501_payload(
    *,
    job: Any,
    result: Any,
    circuit_manifest: dict[str, Any],
    preregistration_manifest: dict[str, Any],
    h501_approval_source: str,
) -> dict[str, Any]:
    execution_order = cast(list[dict[str, Any]], circuit_manifest["execution_order"])
    counts = sampler_result_counts(result, execution_order)
    return {
        "task": "H501_provider_payload",
        "status": "result_downloaded",
        "h501_approval_source": h501_approval_source,
        "backend": circuit_manifest["backend"],
        "job": _job_metadata(job),
        "circuit_manifest_sha256": sha256_file(Path("results/preregistered/circuit_manifest.json")),
        "preregistration_manifest_sha256": sha256_file(
            Path("results/preregistered/preregistration_manifest.json")
        ),
        "preregistration_status": preregistration_manifest.get("status"),
        "shots_per_pub": 1024,
        "total_circuit_instances": len(counts),
        "total_shots_observed": sum(item["count_total"] for item in counts),
        "counts": counts,
        "result_metadata": _jsonable(getattr(result, "metadata", {})),
        "environment": freeze_manifest(),
        "secret_values_recorded": False,
    }


def write_h501_receipt(path: Path, *, job: Any, h501_approval_source: str) -> None:
    from .artifacts import write_raw_json_once

    payload = {
        "task": "H501_submission_receipt",
        "status": "job_accepted",
        "h501_approval_source": h501_approval_source,
        "job": _job_metadata(job),
        "environment": freeze_manifest(),
        "secret_values_recorded": False,
    }
    write_raw_json_once(path, payload)


def _science_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in payload["counts"] if row["role"] == "science"]


def science_counts_by_prototype(payload: dict[str, Any]) -> dict[str, dict[str, int]]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in _science_rows(payload):
        counters[str(row["prototype_name"])].update(
            {str(bitstring): int(count) for bitstring, count in row["counts"].items()}
        )
    return {name: dict(counter) for name, counter in sorted(counters.items())}


def science_block_arrays(payload: dict[str, Any], prototype_name: str) -> list[np.ndarray]:
    rows = [
        row
        for row in _science_rows(payload)
        if row["prototype_name"] == prototype_name and row["block"] is not None
    ]
    return [
        counts_to_bit_array(
            {str(bitstring): int(count) for bitstring, count in row["counts"].items()}
        )
        for row in sorted(rows, key=lambda item: int(item["block"]))
    ]


def _lower_quantile(values: np.ndarray, alpha: float) -> float:
    return float(np.quantile(values, alpha, method="linear"))


def _block_metric_shares(payload: dict[str, Any], *, alpha: float) -> dict[str, Any]:
    del alpha
    obj_values: list[float] = []
    coh_values: list[float] = []
    for block in sorted({int(row["block"]) for row in _science_rows(payload)}):
        counts: dict[str, dict[str, int]] = {}
        for row in _science_rows(payload):
            if int(row["block"]) == block:
                counts[str(row["prototype_name"])] = {
                    str(bitstring): int(count) for bitstring, count in row["counts"].items()
                }
        metrics = quantum_metrics_from_counts(counts, alpha=0.05)
        obj_values.append(float(metrics["delta_obj"]))
        coh_values.append(float(metrics["delta_coh"]))

    def share(values: list[float]) -> float:
        total = sum(abs(value) for value in values)
        return 0.0 if total == 0.0 else float(max(abs(value) for value in values) / total)

    return {
        "delta_obj_block_values": obj_values,
        "delta_coh_block_values": coh_values,
        "delta_obj_max_abs_share": share(obj_values),
        "delta_coh_max_abs_share": share(coh_values),
    }


def analyze_hardware_raw_payload(
    payload: dict[str, Any],
    *,
    alpha: float,
    bootstrap_replicates: int,
    bootstrap_seed: int,
    thresholds: dict[str, float],
) -> dict[str, Any]:
    counts = science_counts_by_prototype(payload)
    metrics = quantum_metrics_from_counts(counts, alpha=alpha)
    bootstrap = bootstrap_contrasts(
        science_block_arrays(payload, "ghz_plus_z"),
        science_block_arrays(payload, "ghz_plus_x"),
        science_block_arrays(payload, "ghz_plus_x"),
        science_block_arrays(payload, "ghz_minus_x"),
        replicates=bootstrap_replicates,
        seed=bootstrap_seed,
    )
    block_shares = _block_metric_shares(payload, alpha=alpha)
    delta_obj_lcb = _lower_quantile(bootstrap["delta_obj"], alpha)
    delta_coh_lcb = _lower_quantile(bootstrap["delta_coh"], alpha)
    ghz_minus_sign_correct = bool(metrics["w_minus_xxxx"] < 0.0)
    block_dominance_pass = bool(
        block_shares["delta_obj_max_abs_share"] <= 0.5
        and block_shares["delta_coh_max_abs_share"] <= 0.5
    )
    inclusion_pass = bool(
        delta_obj_lcb > thresholds["delta_obj_lcb"]
        and metrics["min_z_correlation_lcb"] > thresholds["min_z_correlation_lcb"]
        and delta_coh_lcb > thresholds["delta_coh_lcb"]
        and ghz_minus_sign_correct
        and block_dominance_pass
    )
    return {
        "task": "H502_locked_raw_analysis",
        "status": "complete",
        "backend": payload["backend"],
        "job_id": payload["job"]["job_id"],
        "primary": "raw",
        "metrics": metrics,
        "bootstrap": {
            "replicates": bootstrap_replicates,
            "seed": bootstrap_seed,
            "alpha": alpha,
            "delta_obj_lcb": delta_obj_lcb,
            "delta_coh_lcb": delta_coh_lcb,
        },
        "block_dominance": block_shares,
        "inclusion_checks": {
            "delta_obj_lcb": delta_obj_lcb > thresholds["delta_obj_lcb"],
            "min_z_correlation_lcb": (
                metrics["min_z_correlation_lcb"] > thresholds["min_z_correlation_lcb"]
            ),
            "delta_coh_lcb": delta_coh_lcb > thresholds["delta_coh_lcb"],
            "ghz_minus_xxxx_negative": ghz_minus_sign_correct,
            "no_single_block_dominates": block_dominance_pass,
        },
        "passes_main_text_inclusion_without_mitigation": inclusion_pass,
        "result_interpretation": (
            "hardware_positive_pending_mitigation_check"
            if inclusion_pass
            else "hardware_null_or_partial_pending_mitigation_check"
        ),
        "secret_values_recorded": False,
    }


def _bits_to_index(bits: tuple[int, ...]) -> int:
    return sum(bit << index for index, bit in enumerate(bits))


def _counts_vector(counts: dict[str, int]) -> np.ndarray:
    vector = np.zeros(16, dtype=np.float64)
    total = sum(counts.values())
    if total <= 0:
        raise ValueError("counts must contain at least one shot")
    for bitstring, count in counts.items():
        vector[_bits_to_index(parse_qiskit_bitstring(bitstring))] += int(count)
    return vector / total


def _tensor_assignment_matrix(assignments: list[np.ndarray]) -> np.ndarray:
    matrix = np.zeros((16, 16), dtype=np.float64)
    for true_index in range(16):
        true_bits = tuple((true_index >> bit) & 1 for bit in range(4))
        for observed_index in range(16):
            observed_bits = tuple((observed_index >> bit) & 1 for bit in range(4))
            probability = 1.0
            for qubit in range(4):
                probability *= assignments[qubit][observed_bits[qubit], true_bits[qubit]]
            matrix[observed_index, true_index] = probability
    return matrix


def _calibration_assignment_matrices(payload: dict[str, Any]) -> list[np.ndarray]:
    rows = {
        row["prototype_name"]: row
        for row in payload["counts"]
        if row["role"] == "readout_calibration"
    }
    matrices = []
    for qubit in range(4):
        matrix = np.zeros((2, 2), dtype=np.float64)
        for prepared in (0, 1):
            row = rows[f"ro_q{qubit}_{prepared}"]
            counts = {str(bitstring): int(count) for bitstring, count in row["counts"].items()}
            total = sum(counts.values())
            for bitstring, count in counts.items():
                measured = parse_qiskit_bitstring(bitstring)[qubit]
                matrix[measured, prepared] += int(count) / total
        matrices.append(matrix)
    return matrices


def _expectation_from_distribution(probabilities: np.ndarray, columns: tuple[int, ...]) -> float:
    total = 0.0
    for index, probability in enumerate(probabilities):
        bits = tuple((index >> bit) & 1 for bit in range(4))
        value = 1
        for column in columns:
            value *= 1 - 2 * bits[column]
        total += float(probability) * value
    return float(total)


def _mitigated_metrics(distributions: dict[str, np.ndarray]) -> dict[str, float]:
    z = distributions["ghz_plus_z"]
    x = distributions["ghz_plus_x"]
    minus_x = distributions["ghz_minus_x"]
    z1 = _expectation_from_distribution(z, (0, 2))
    z2 = _expectation_from_distribution(z, (0, 3))
    x1 = _expectation_from_distribution(x, (0, 2))
    x2 = _expectation_from_distribution(x, (0, 3))
    w_plus = _expectation_from_distribution(x, (0, 1, 2, 3))
    w_minus = _expectation_from_distribution(minus_x, (0, 1, 2, 3))
    w_mix = 0.5 * (w_plus + w_minus)
    return {
        "z_c_r1": z1,
        "z_c_r2": z2,
        "x_c_r1": x1,
        "x_c_r2": x2,
        "w_plus_xxxx": w_plus,
        "w_minus_xxxx": w_minus,
        "w_mix_xxxx": w_mix,
        "delta_obj": min(z1, z2) - max(abs(x1), abs(x2)),
        "delta_coh": abs(w_plus) - abs(w_mix),
    }


def analyze_readout_mitigated_payload(
    payload: dict[str, Any],
    raw_analysis: dict[str, Any],
    *,
    thresholds: dict[str, float],
) -> dict[str, Any]:
    assignments = _calibration_assignment_matrices(payload)
    tensor_matrix = _tensor_assignment_matrix(assignments)
    inverse = np.linalg.pinv(tensor_matrix)
    raw_counts = science_counts_by_prototype(payload)
    corrected: dict[str, np.ndarray] = {}
    negativity: dict[str, float] = {}
    for name, counts in raw_counts.items():
        corrected_distribution = inverse @ _counts_vector(counts)
        corrected[name] = corrected_distribution
        negative_entries = corrected_distribution[corrected_distribution < 0.0]
        negativity[name] = float(np.sum(np.abs(negative_entries)))
    metrics = _mitigated_metrics(corrected)
    point_pass = bool(
        metrics["delta_obj"] > thresholds["delta_obj_lcb"]
        and min(metrics["z_c_r1"], metrics["z_c_r2"]) > thresholds["min_z_correlation_lcb"]
        and metrics["delta_coh"] > thresholds["delta_coh_lcb"]
        and metrics["w_minus_xxxx"] < 0.0
    )
    raw_pass = bool(raw_analysis["passes_main_text_inclusion_without_mitigation"])
    return {
        "task": "H503_readout_mitigated_analysis",
        "status": "complete",
        "primary_result_remains": "raw",
        "metrics": metrics,
        "assignment_matrices": [matrix.tolist() for matrix in assignments],
        "tensor_assignment_condition_number": float(np.linalg.cond(tensor_matrix)),
        "negative_quasiprobability_l1": negativity,
        "corrected_point_threshold_pass": point_pass,
        "raw_primary_pass": raw_pass,
        "qualitative_agreement_with_raw": point_pass == raw_pass,
        "secret_values_recorded": False,
    }


def latest_h501_payload_path(raw_root: Path = Path("results/raw")) -> Path:
    matches = sorted(raw_root.glob("H501_provider_payload_*.json"))
    if not matches:
        raise FileNotFoundError("No H501 provider payload found")
    return matches[-1]


def write_processed_analysis(path: Path, payload: dict[str, Any], inputs: list[Path]) -> None:
    output = {
        **payload,
        "inputs": file_manifest(inputs),
        "environment": freeze_manifest(),
    }
    write_json_atomic(path, output)
