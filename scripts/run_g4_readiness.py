from __future__ import annotations

from pathlib import Path

from objective_clocks.artifacts import write_json_atomic, write_sha256_manifest
from objective_clocks.readiness import build_g4_readiness_audit


def main() -> None:
    output = Path("results/processed/G4_readiness_audit.json")
    manifest = Path("results/processed/G4_readiness_manifest.json")
    payload = build_g4_readiness_audit()
    write_json_atomic(output, payload)
    write_sha256_manifest(manifest, [output])
    print(
        {
            "task": payload["task"],
            "overall_status": payload["overall_status"],
            "blocked_check_count": payload["blocked_check_count"],
            "token_source_count": payload["ibm_credential_audit"]["token_source_count"],
            "secret_values_recorded": payload["ibm_credential_audit"]["secret_values_recorded"],
        }
    )


if __name__ == "__main__":
    main()
