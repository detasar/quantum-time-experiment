from __future__ import annotations

from pathlib import Path

from objective_clocks.artifacts import write_json_atomic, write_sha256_manifest
from objective_clocks.claims import (
    build_claim_evidence_matrix,
    validate_claim_evidence_matrix,
    write_claim_evidence_csv,
)


def main() -> None:
    rows = build_claim_evidence_matrix()
    validate_claim_evidence_matrix(rows)
    hardware_observation_claimed = any("Q" in row.evidence_grade.split(";") for row in rows)
    hardware_stage_status = (
        "hardware_observation_complete"
        if hardware_observation_claimed
        else "no_hardware_observation"
    )

    output = Path("results/claim_evidence_matrix.csv")
    write_claim_evidence_csv(output, rows)
    summary = {
        "task": "A601",
        "claim_count": len(rows),
        "claim_ids": [row.id for row in rows],
        "q_grade_claim_count": sum("Q" in row.evidence_grade.split(";") for row in rows),
        "hardware_observation_claimed": hardware_observation_claimed,
        "unsupported_claim_count": sum(row.evidence_status == "unsupported" for row in rows),
        "hardware_stage_status": hardware_stage_status,
    }
    write_json_atomic(Path("results/processed/A601_claim_evidence_summary.json"), summary)
    write_sha256_manifest(
        Path("results/processed/A601_manifest.json"),
        [
            output,
            Path("results/processed/A601_claim_evidence_summary.json"),
        ],
    )
    print(summary)


if __name__ == "__main__":
    main()
