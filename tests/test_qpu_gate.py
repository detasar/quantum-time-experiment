import json
from pathlib import Path

import pytest

from objective_clocks.artifacts import sha256_file
from objective_clocks.ibm import assert_qpu_gate


@pytest.mark.qpu_gate
def test_qpu_gate_disabled_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALLOW_QPU_EXECUTION", raising=False)
    circuit_manifest = tmp_path / "circuits.json"
    circuit_manifest.write_text("{}", encoding="utf-8")
    prereg = tmp_path / "prereg.json"
    prereg.write_text(
        json.dumps(
            {
                "status": "FROZEN",
                "circuit_manifest_sha256": sha256_file(circuit_manifest),
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(PermissionError):
        assert_qpu_gate(prereg, circuit_manifest)
