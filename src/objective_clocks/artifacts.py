from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import platform
import subprocess
import tarfile
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def config_hash(config: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(config).encode("utf-8"))


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "UNKNOWN"


def package_versions(packages: tuple[str, ...]) -> dict[str, str]:
    result: dict[str, str] = {}
    for package in packages:
        try:
            result[package] = version(package)
        except PackageNotFoundError:
            result[package] = "NOT_INSTALLED"
    return result


def freeze_manifest() -> dict[str, Any]:
    """Return deterministic package and repository metadata without a timestamp."""

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": git_commit(),
        "packages": package_versions(
            (
                "numpy",
                "scipy",
                "pandas",
                "networkx",
                "qiskit",
                "qiskit-aer",
                "qiskit-ibm-runtime",
            )
        ),
        "qpu_execution_enabled": os.getenv("ALLOW_QPU_EXECUTION") == "YES",
    }


def environment_manifest() -> dict[str, Any]:
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        **freeze_manifest(),
    }


def write_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _ensure_under_directory(path: Path, root: Path) -> tuple[Path, Path]:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Raw artifacts must be written under {root}") from exc
    return resolved_path, resolved_root


def write_raw_json_once(
    path: Path,
    data: Any,
    *,
    raw_root: Path = Path("results/raw"),
) -> None:
    resolved_path, _ = _ensure_under_directory(path, raw_root)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with resolved_path.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
    except FileExistsError as exc:
        raise FileExistsError(
            f"Raw artifact already exists and will not be overwritten: {path}"
        ) from exc


def file_manifest(
    paths: list[Path] | tuple[Path, ...],
    *,
    root: Path = Path("."),
) -> list[dict[str, Any]]:
    resolved_root = root.resolve()
    entries: list[dict[str, Any]] = []
    for path in sorted(paths, key=lambda item: item.resolve().as_posix()):
        resolved_path = path.resolve()
        relative = resolved_path.relative_to(resolved_root).as_posix()
        entries.append(
            {
                "path": relative,
                "sha256": sha256_file(resolved_path),
                "size_bytes": resolved_path.stat().st_size,
            }
        )
    return entries


def write_sha256_manifest(
    path: Path,
    files: list[Path] | tuple[Path, ...],
    *,
    root: Path = Path("."),
) -> None:
    payload = {
        "algorithm": "sha256",
        "created_utc": datetime.now(UTC).isoformat(),
        "files": file_manifest(files, root=root),
    }
    write_json_atomic(path, payload)


def repository_archive_paths(root: Path = Path(".")) -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
    )
    excluded_prefixes = (
        ".git/",
        ".mypy_cache/",
        ".pytest_cache/",
        ".ruff_cache/",
        ".venv/",
        "results/preregistered/",
    )
    excluded_paths = {
        "docs/PREREGISTRATION_FROZEN.md",
        "results/processed/H401_preregistration_draft.md",
        "results/processed/G4_readiness_audit.json",
        "results/processed/G4_readiness_manifest.json",
        "results/processed/H401_preregistration_draft_manifest.json",
        "results/processed/H401_preregistration_draft_summary.json",
    }
    paths: list[Path] = []
    for raw in output.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8")
        path = root / relative
        if any(relative.startswith(prefix) for prefix in excluded_prefixes):
            continue
        if relative in excluded_paths:
            continue
        if path.is_file():
            paths.append(Path(relative))
    return sorted(paths, key=lambda item: item.as_posix())


def deterministic_tar_gz_bytes(paths: list[Path], *, root: Path = Path(".")) -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for relative in paths:
            source = root / relative
            payload = source.read_bytes()
            info = tarfile.TarInfo(relative.as_posix())
            info.size = len(payload)
            info.mode = 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(payload))
    gzip_buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=gzip_buffer, mtime=0) as compressed:
        compressed.write(tar_buffer.getvalue())
    return gzip_buffer.getvalue()


def write_environment_archive(
    archive_path: Path,
    manifest_path: Path,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    paths = repository_archive_paths(root)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    payload = deterministic_tar_gz_bytes(paths, root=root)
    archive_path.write_bytes(payload)
    manifest = {
        "task": "H401_environment_archive",
        "algorithm": "sha256",
        "archive_path": archive_path.as_posix(),
        "archive_sha256": sha256_bytes(payload),
        "archived_file_count": len(paths),
        "excluded_prefixes": [
            ".git/",
            ".mypy_cache/",
            ".pytest_cache/",
            ".ruff_cache/",
            ".venv/",
            "results/preregistered/",
        ],
        "excluded_paths": [
            "docs/PREREGISTRATION_FROZEN.md",
            "results/processed/H401_preregistration_draft.md",
            "results/processed/G4_readiness_audit.json",
            "results/processed/G4_readiness_manifest.json",
            "results/processed/H401_preregistration_draft_manifest.json",
            "results/processed/H401_preregistration_draft_summary.json",
        ],
        "environment": freeze_manifest(),
        "files": [
            {
                "path": relative.as_posix(),
                "sha256": sha256_file(root / relative),
                "size_bytes": (root / relative).stat().st_size,
            }
            for relative in paths
        ],
        "secret_values_recorded": False,
    }
    write_json_atomic(manifest_path, manifest)
    return manifest
