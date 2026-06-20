from __future__ import annotations

import json
from pathlib import Path

import pytest

from objective_clocks.ibm import (
    discover_ibm_env_keys,
    discover_ibm_token_sources,
    env_file_candidates,
    first_ibm_token,
    parse_json_token_file,
)
from objective_clocks.readiness import build_g4_readiness_audit


def test_ibm_env_discovery_records_keys_without_secret_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in ("QISKIT_IBM_TOKEN", "IBM_QUANTUM_TOKEN", "QISKIT_TOKEN", "IBM_TOKEN"):
        monkeypatch.delenv(key, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "QISKIT_IBM_TOKEN=placeholder\nOTHER=value\n",
        encoding="utf-8",
    )

    assert discover_ibm_env_keys([env_file]) == {str(env_file): ["QISKIT_IBM_TOKEN"]}
    token_sources = discover_ibm_token_sources([env_file])
    token, token_source = first_ibm_token([env_file])

    assert token == "placeholder"
    assert token_source == {"source": "env_file", "path": str(env_file), "key": "QISKIT_IBM_TOKEN"}
    serialized = json.dumps(token_sources)
    assert "QISKIT_IBM_TOKEN" in serialized
    assert "placeholder" not in serialized


def test_ibm_env_candidates_include_shell_run_env_and_qiskit_json(tmp_path: Path) -> None:
    (tmp_path / ".bashrc").write_text("export QISKIT_IBM_TOKEN=shell-placeholder\n")
    project = tmp_path / "project"
    project.mkdir()
    (project / "run.env").write_text("IBM_QUANTUM_TOKEN=run-placeholder\n")
    ignored = tmp_path / "node_modules"
    ignored.mkdir()
    (ignored / ".env").write_text("QISKIT_IBM_TOKEN=ignored-placeholder\n")
    qiskit_dir = tmp_path / ".qiskit"
    qiskit_dir.mkdir()
    account_file = qiskit_dir / "qiskit-ibm.json"
    account_file.write_text('{"default": {"token": "json-placeholder"}}\n')

    candidates = {path.relative_to(tmp_path).as_posix() for path in env_file_candidates(tmp_path)}
    token_sources = discover_ibm_token_sources(env_file_candidates(tmp_path))
    serialized = json.dumps(token_sources)

    assert ".bashrc" in candidates
    assert "project/run.env" in candidates
    assert ".qiskit/qiskit-ibm.json" in candidates
    assert "node_modules/.env" not in candidates
    assert parse_json_token_file(account_file) == [("default.token", "json-placeholder")]
    assert "json-placeholder" not in serialized
    assert "qiskit_account_file" in serialized


def test_g4_readiness_audit_blocks_without_provider_snapshot() -> None:
    report = build_g4_readiness_audit(Path("."))
    checks = {check["id"]: check for check in report["checks"]}

    assert report["overall_status"] == "blocked_before_g4"
    assert checks["G3-Q302"]["status"] == "pass"
    assert checks["G3-Q304-TWIN"]["status"] == "blocked"
    assert checks["H403-QPU-GATE"]["status"] == "pass"
    assert not report["ibm_credential_audit"]["secret_values_recorded"]
