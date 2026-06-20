from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from statistics import fmean
from typing import Any, cast

from .artifacts import sha256_file
from .quantum import SUPPORTED_ENTANGLING_BASIS_GATES, BackendCandidate, fixture_backend_candidates

IBM_TOKEN_KEYS = ("QISKIT_IBM_TOKEN", "IBM_QUANTUM_TOKEN", "QISKIT_TOKEN", "IBM_TOKEN")
IBM_INTERESTING_MARKERS = ("IBM", "QISKIT")
QISKIT_ACCOUNT_FILENAMES = {"qiskit-ibm.json", "qiskitrc", "qiskit.json"}
SHELL_CONFIG_FILENAMES = {".bash_profile", ".bashrc", ".profile", ".zprofile", ".zshrc"}


def assert_qpu_gate(preregistration_manifest: Path, circuit_manifest: Path) -> dict[str, Any]:
    if os.getenv("ALLOW_QPU_EXECUTION") != "YES":
        raise PermissionError("QPU execution is disabled. Set ALLOW_QPU_EXECUTION=YES explicitly.")
    if not preregistration_manifest.exists() or not circuit_manifest.exists():
        raise FileNotFoundError("Preregistration and circuit manifests are mandatory")
    prereg = json.loads(preregistration_manifest.read_text(encoding="utf-8"))
    if prereg.get("status") != "FROZEN":
        raise PermissionError("Preregistration status must be FROZEN")
    expected = prereg.get("circuit_manifest_sha256")
    observed = sha256_file(circuit_manifest)
    if expected != observed:
        raise PermissionError("Circuit manifest hash does not match preregistration")
    return cast(dict[str, Any], prereg)


def submit_sampler_job(*_: Any, **__: Any) -> None:
    """Deliberately unimplemented until preregistration is frozen.

    Codex must implement this only after all qpu_gate tests and the scientific review pass.
    """
    raise NotImplementedError("Hardware submission is intentionally gated")


def discover_ibm_env_keys(paths: list[Path]) -> dict[str, list[str]]:
    discovered: dict[str, list[str]] = {}
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        keys = []
        for key, _ in parse_env_file(path):
            if any(marker in key for marker in IBM_INTERESTING_MARKERS):
                keys.append(key)
        for key_path, _ in parse_json_token_file(path):
            if any(marker in key_path.upper() for marker in (*IBM_INTERESTING_MARKERS, "TOKEN")):
                keys.append(key_path)
        if keys:
            discovered[str(path)] = sorted(set(keys))
    return discovered


def parse_env_file(path: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if not path.exists() or not path.is_file():
        return pairs
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if "=" not in stripped or stripped.startswith("#"):
            continue
        key, value = stripped.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip("'\"")
        if key:
            pairs.append((key, value))
    return pairs


def _json_leaf_items(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    leaves: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_prefix = f"{prefix}.{key}" if prefix else str(key)
            leaves.extend(_json_leaf_items(nested, key_prefix))
    elif isinstance(value, str):
        leaves.append((prefix, value))
    return leaves


def parse_json_token_file(path: Path) -> list[tuple[str, str]]:
    if not path.exists() or not path.is_file() or path.name not in QISKIT_ACCOUNT_FILENAMES:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return []
    pairs = []
    for key_path, value in _json_leaf_items(data):
        if key_path and "TOKEN" in key_path.upper() and value:
            pairs.append((key_path, value))
    return pairs


def discover_ibm_token_sources(paths: list[Path]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for key in IBM_TOKEN_KEYS:
        if os.getenv(key):
            sources.append({"source": "process_environment", "key": key})
    for path in paths:
        for key, value in parse_env_file(path):
            if key in IBM_TOKEN_KEYS and value:
                sources.append({"source": "env_file", "path": str(path), "key": key})
        for key_path, value in parse_json_token_file(path):
            if value:
                sources.append(
                    {"source": "qiskit_account_file", "path": str(path), "key": key_path}
                )
    return sources


def first_ibm_token(paths: list[Path]) -> tuple[str | None, dict[str, Any] | None]:
    for key in IBM_TOKEN_KEYS:
        token = os.getenv(key)
        if token:
            return token, {"source": "process_environment", "key": key}
    for path in paths:
        for key, value in parse_env_file(path):
            if key in IBM_TOKEN_KEYS and value:
                return value, {"source": "env_file", "path": str(path), "key": key}
        for key_path, value in parse_json_token_file(path):
            if value:
                return value, {"source": "qiskit_account_file", "path": str(path), "key": key_path}
    return None, None


def _is_candidate_env_file(path: Path) -> bool:
    name = path.name
    lower_name = name.lower()
    if name in SHELL_CONFIG_FILENAMES or name in QISKIT_ACCOUNT_FILENAMES:
        return True
    return (
        lower_name.startswith(".env")
        or lower_name.endswith(".env")
        or ".env." in lower_name
        or lower_name.endswith(".env.local")
    )


def env_file_candidates(home: Path | None = None, *, limit: int = 1000) -> list[Path]:
    home = Path.home() if home is None else home
    ignored_parts = {
        ".cache",
        ".git",
        ".ipynb_checkpoints",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "miniconda3",
        "node_modules",
    }
    explicit = [home / ".qiskit" / filename for filename in sorted(QISKIT_ACCOUNT_FILENAMES)]
    explicit.extend(home / filename for filename in sorted(SHELL_CONFIG_FILENAMES))
    candidates: set[Path] = set()
    for current_root, dirnames, filenames in os.walk(home):
        root_path = Path(current_root)
        try:
            depth = len(root_path.relative_to(home).parts)
        except ValueError:
            continue
        if depth >= 5:
            dirnames[:] = []
        else:
            dirnames[:] = sorted(dirname for dirname in dirnames if dirname not in ignored_parts)
        for filename in sorted(filenames):
            path = root_path / filename
            if _is_candidate_env_file(path):
                candidates.add(path)
                if len(candidates) >= limit:
                    break
        if len(candidates) >= limit:
            break
    all_candidates = {path for path in candidates}
    all_candidates.update(path for path in explicit if path.exists() and path.is_file())
    return sorted(all_candidates)[:limit]


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _safe_runtime_account_metadata(service: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {"secret_values_recorded": False}
    try:
        active = service.active_account()
    except Exception as exc:
        metadata["active_account_error"] = f"{type(exc).__name__}: {exc}"
        return metadata
    if not isinstance(active, dict):
        return metadata
    instance = str(active.get("instance") or "")
    metadata.update(
        {
            "channel": active.get("channel"),
            "url": active.get("url"),
            "private_endpoint": active.get("private_endpoint"),
            "instance_configured": bool(instance),
            "instance_crn_sha256": _sha256_text(instance) if instance else None,
            "region": instance.split(":")[5] if instance.startswith("crn:") else None,
        }
    )
    try:
        instances = service.instances()
    except Exception as exc:
        metadata["instances_error"] = f"{type(exc).__name__}: {exc}"
        return metadata
    for item in instances:
        if item.get("crn") == instance:
            metadata.update(
                {
                    "instance_name": item.get("name"),
                    "plan": item.get("plan"),
                    "pricing_type": item.get("pricing_type"),
                }
            )
            break
    return metadata


def _mean_or_default(values: list[float], default: float) -> float:
    return float(fmean(values)) if values else default


def _safe_gate_error(properties: Any, gate: str, qubits: tuple[int, ...]) -> float | None:
    candidates: tuple[Any, ...] = (list(qubits), qubits, qubits[0] if len(qubits) == 1 else qubits)
    for candidate in candidates:
        try:
            return float(properties.gate_error(gate, candidate))
        except Exception:
            continue
    return None


def _safe_readout_error(properties: Any, qubit: int) -> float | None:
    try:
        return float(properties.readout_error(qubit))
    except Exception:
        return None


def _safe_datetime_text(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


def _runtime_service_from_token(token: str | None, token_source: dict[str, Any] | None) -> Any:
    from qiskit_ibm_runtime import QiskitRuntimeService

    if token is None or (token_source or {}).get("source") == "qiskit_account_file":
        return QiskitRuntimeService()
    try:
        return QiskitRuntimeService(token=token)
    except TypeError:
        return QiskitRuntimeService()


def _candidate_from_backend(backend: Any) -> BackendCandidate:
    name = str(getattr(backend, "name", "unknown_backend"))
    if callable(getattr(backend, "name", None)):
        name = str(backend.name())
    n_qubits = int(getattr(backend, "num_qubits", getattr(backend, "n_qubits", 0)))
    basis_gates = tuple(str(gate) for gate in getattr(backend, "basis_gates", ()) or ())
    coupling_map = getattr(backend, "coupling_map", None)
    if coupling_map is not None and hasattr(coupling_map, "get_edges"):
        edges = tuple((int(edge[0]), int(edge[1])) for edge in coupling_map.get_edges())
    else:
        edges = ()
    status = backend.status() if callable(getattr(backend, "status", None)) else None
    pending_jobs = int(getattr(status, "pending_jobs", 999) if status is not None else 999)
    operational = bool(getattr(status, "operational", True) if status is not None else True)
    simulator = bool(getattr(backend, "simulator", False))
    properties = backend.properties() if callable(getattr(backend, "properties", None)) else None
    one_qubit_entries: list[tuple[int, float]] = []
    readout_entries: list[tuple[int, float]] = []
    edge_entries: list[tuple[int, int, float]] = []
    if properties is not None:
        for qubit in range(n_qubits):
            one_qubit_values = [
                error
                for gate in ("sx", "x")
                if (error := _safe_gate_error(properties, gate, (qubit,))) is not None
            ]
            if one_qubit_values:
                one_qubit_entries.append((qubit, _mean_or_default(one_qubit_values, 0.001)))
            readout_error = _safe_readout_error(properties, qubit)
            if readout_error is not None:
                readout_entries.append((qubit, readout_error))
        entangling_gates = sorted(
            gate for gate in basis_gates if gate in SUPPORTED_ENTANGLING_BASIS_GATES
        )
        for a, b in edges:
            edge_values = [
                error
                for gate in entangling_gates
                if (error := _safe_gate_error(properties, gate, (a, b))) is not None
            ]
            if edge_values:
                edge_entries.append((a, b, min(edge_values)))
    return BackendCandidate(
        name=name,
        n_qubits=n_qubits,
        operational=operational,
        simulator=simulator,
        pending_jobs=pending_jobs,
        basis_gates=basis_gates or ("cx",),
        coupling_edges=edges,
        one_qubit_error=_mean_or_default([entry[1] for entry in one_qubit_entries], 0.001),
        two_qubit_error=_mean_or_default([entry[2] for entry in edge_entries], 0.01),
        readout_error=_mean_or_default([entry[1] for entry in readout_entries], 0.02),
        one_qubit_gate_errors=tuple(one_qubit_entries),
        two_qubit_edge_errors=tuple(edge_entries),
        readout_errors=tuple(readout_entries),
        calibration_timestamp=_safe_datetime_text(
            getattr(properties, "last_update_date", None) if properties is not None else None
        ),
        backend_version=(
            str(getattr(properties, "backend_version", ""))
            if properties is not None and getattr(properties, "backend_version", None)
            else None
        ),
    )


def list_backend_candidates_without_submission() -> tuple[
    str,
    list[BackendCandidate],
    dict[str, Any],
]:
    env_paths = env_file_candidates()
    token, token_source = first_ibm_token(env_paths)
    metadata: dict[str, Any] = {
        "provider_call_attempted": False,
        "provider_error": None,
        "env_key_presence": discover_ibm_env_keys(env_paths),
        "token_available": token is not None,
        "token_source": token_source,
        "token_sources": discover_ibm_token_sources(env_paths),
    }
    if token or token_source is not None:
        try:
            metadata["provider_call_attempted"] = True
            service = _runtime_service_from_token(token, token_source)
            metadata["runtime_account"] = _safe_runtime_account_metadata(service)
            backends = service.backends()
            return "provider", [_candidate_from_backend(backend) for backend in backends], metadata
        except Exception as exc:
            metadata["provider_error"] = f"{type(exc).__name__}: {exc}"
    elif any(path.name in QISKIT_ACCOUNT_FILENAMES for path in env_paths):
        try:
            metadata["provider_call_attempted"] = True
            metadata["token_source"] = {"source": "qiskit_saved_account_probe"}
            service = _runtime_service_from_token(None, None)
            metadata["runtime_account"] = _safe_runtime_account_metadata(service)
            backends = service.backends()
            return "provider", [_candidate_from_backend(backend) for backend in backends], metadata
        except Exception as exc:
            metadata["provider_error"] = f"{type(exc).__name__}: {exc}"
    candidates = fixture_backend_candidates()
    metadata["fallback_reason"] = "no_runtime_token_or_provider_listing_failed"
    return "deterministic_fixture", candidates, metadata
