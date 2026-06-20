from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from objective_clocks.artifacts import (
    file_manifest,
    freeze_manifest,
    sha256_file,
    write_json_atomic,
)

APPROVAL_SOURCE = "Codex user message: onay veriyorum plana gore gidelim"


def _freeze_markdown(draft: str, *, approval_timestamp: str) -> str:
    frozen = draft.replace("**Status:** DRAFT - QPU execution prohibited", "**Status:** FROZEN")
    frozen = frozen.replace("Human approval: `NO`", "Human approval: `YES`")
    frozen = frozen.replace(
        "Status may become `FROZEN` only after all G4 tasks pass.",
        "Status is `FROZEN`; QPU execution still requires the explicit H501 gate.",
    )
    frozen = frozen.replace(
        "## 13. Current Blockers\n\n- `human_approval`: explicit human approval is not recorded\n",
        (
            "## 13. Human Approval Record\n\n"
            f"- Approval timestamp UTC: `{approval_timestamp}`\n"
            f"- Approval source: `{APPROVAL_SOURCE}`\n"
            "- QPU execution allowed now: `NO`\n"
        ),
    )
    return frozen


def main() -> None:
    draft_path = Path("docs/PREREGISTRATION_DRAFT.md")
    circuit_manifest_path = Path("results/preregistered/circuit_manifest.json")
    qpy_path = Path("results/preregistered/circuits.qpy")
    archive_manifest_path = Path("results/preregistered/environment_archive_manifest.json")
    if not draft_path.exists() or not circuit_manifest_path.exists() or not qpy_path.exists():
        raise SystemExit("Run H401 draft and H402 ISA generation before freezing")
    draft = draft_path.read_text(encoding="utf-8")
    if "TBD_BLOCKED" in draft:
        raise SystemExit("Cannot freeze preregistration while mandatory fields are blocked")
    approval_timestamp = datetime.now(UTC).isoformat()
    frozen_path = Path("docs/PREREGISTRATION_FROZEN.md")
    frozen_path.write_text(
        _freeze_markdown(draft, approval_timestamp=approval_timestamp),
        encoding="utf-8",
    )
    manifest_path = Path("results/preregistered/preregistration_manifest.json")
    manifest = {
        "task": "H401_preregistration_freeze",
        "status": "FROZEN",
        "human_approval": True,
        "approval_timestamp_utc": approval_timestamp,
        "approval_source": APPROVAL_SOURCE,
        "qpu_execution_allowed": False,
        "qpu_execution_allowed_requires": "H501 explicit gate and ALLOW_QPU_EXECUTION=YES",
        "frozen_markdown_path": frozen_path.as_posix(),
        "frozen_markdown_sha256": sha256_file(frozen_path),
        "circuit_manifest_path": circuit_manifest_path.as_posix(),
        "circuit_manifest_sha256": sha256_file(circuit_manifest_path),
        "qpy_path": qpy_path.as_posix(),
        "qpy_sha256": sha256_file(qpy_path),
        "environment_archive_manifest_path": archive_manifest_path.as_posix(),
        "environment_archive_manifest_sha256": (
            sha256_file(archive_manifest_path) if archive_manifest_path.exists() else None
        ),
        "outputs": file_manifest([frozen_path, circuit_manifest_path, qpy_path]),
        "environment": freeze_manifest(),
    }
    write_json_atomic(manifest_path, manifest)
    print(
        {
            "task": manifest["task"],
            "status": manifest["status"],
            "human_approval": manifest["human_approval"],
            "qpu_execution_allowed": manifest["qpu_execution_allowed"],
            "circuit_manifest_sha256": manifest["circuit_manifest_sha256"],
        }
    )


if __name__ == "__main__":
    main()
