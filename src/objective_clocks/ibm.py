from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, cast

from .artifacts import sha256_file
from .quantum import BackendCandidate, fixture_backend_candidates

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


def _runtime_service_from_token(token: str | None) -> Any:
    from qiskit_ibm_runtime import QiskitRuntimeService

    if token is None:
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
    return BackendCandidate(
        name=name,
        n_qubits=n_qubits,
        operational=operational,
        simulator=simulator,
        pending_jobs=pending_jobs,
        basis_gates=basis_gates or ("cx",),
        coupling_edges=edges,
        one_qubit_error=0.001,
        two_qubit_error=0.01,
        readout_error=0.02,
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
            service = _runtime_service_from_token(token)
            backends = service.backends()
            return "provider", [_candidate_from_backend(backend) for backend in backends], metadata
        except Exception as exc:
            metadata["provider_error"] = f"{type(exc).__name__}: {exc}"
    elif any(path.name in QISKIT_ACCOUNT_FILENAMES for path in env_paths):
        try:
            metadata["provider_call_attempted"] = True
            metadata["token_source"] = {"source": "qiskit_saved_account_probe"}
            service = _runtime_service_from_token(None)
            backends = service.backends()
            return "provider", [_candidate_from_backend(backend) for backend in backends], metadata
        except Exception as exc:
            metadata["provider_error"] = f"{type(exc).__name__}: {exc}"
    candidates = fixture_backend_candidates()
    metadata["fallback_reason"] = "no_runtime_token_or_provider_listing_failed"
    return "deterministic_fixture", candidates, metadata
