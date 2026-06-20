from __future__ import annotations

from pathlib import Path

from objective_clocks.claims import build_claim_evidence_matrix, validate_claim_evidence_matrix


def test_a601_claim_matrix_has_evidence_and_caveats() -> None:
    rows = build_claim_evidence_matrix(Path("."))
    validate_claim_evidence_matrix(rows)

    by_id = {row.id: row for row in rows}
    assert by_id["O1"].evidence_grade == "P;E"
    assert "mismatch_count=0" in by_id["O1"].evidence_checks
    assert by_id["N1"].evidence_status == "supported_no_go"
    assert by_id["Q1"].evidence_status == "supported_with_hardware"
    assert by_id["Q1"].evidence_grade == "P;E;S;Q"
    assert "raw_delta_obj_lcb=" in by_id["Q1"].evidence_checks
    assert "four-qubit IBM illustration only" in by_id["Q1"].caveat
    assert "theorem-level contribution remains" in by_id["Q1"].caveat
    assert by_id["Q2"].evidence_status == "supported_with_hardware"
    assert by_id["Q2"].evidence_grade == "P;E;S;Q"
    assert "not an independent proof" in by_id["Q2"].caveat
