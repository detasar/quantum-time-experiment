from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True)
class ClaimEvidence:
    id: str
    planned_claim: str
    evidence_grade: str
    evidence_status: str
    novelty_status: str
    evidence_required: str
    evidence_artifacts: str
    evidence_checks: str
    caveat: str


FIELDNAMES = tuple(ClaimEvidence.__dataclass_fields__)


def _read_json(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _require_file(root: Path, relative: str) -> str:
    path = root / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return relative


def _claim(
    *,
    claim_id: str,
    planned_claim: str,
    evidence_grade: str,
    evidence_status: str,
    novelty_status: str,
    evidence_required: str,
    evidence_artifacts: list[str],
    evidence_checks: list[str],
    caveat: str,
) -> ClaimEvidence:
    return ClaimEvidence(
        id=claim_id,
        planned_claim=planned_claim,
        evidence_grade=evidence_grade,
        evidence_status=evidence_status,
        novelty_status=novelty_status,
        evidence_required=evidence_required,
        evidence_artifacts="; ".join(evidence_artifacts),
        evidence_checks="; ".join(evidence_checks),
        caveat=caveat,
    )


def build_claim_evidence_matrix(root: Path = Path(".")) -> list[ClaimEvidence]:
    t101 = _read_json(root, "results/processed/T101_chain_verification.json")
    t103 = _read_json(root, "results/processed/T103_capacity.json")
    t104 = _read_json(root, "results/processed/T104_noise_bound_grid.json")
    counterexamples = _read_json(root, "results/processed/counterexample_catalog.json")
    c0 = _read_json(root, "results/processed/C0_runtime_report.json")
    c1 = _read_json(root, "results/processed/C1_basis_landscape_summary.json")
    c2 = _read_json(root, "results/processed/C2_order_catalog_summary.json")
    c3 = _read_json(root, "results/processed/C3_noise_phase_summary.json")
    c4 = _read_json(root, "results/processed/C4_assumption_failures.json")
    c5 = _read_json(root, "results/processed/C5_ghz_exact.json")
    q1 = _read_json(root, "results/processed/Q1_noise_sweep_summary.json")
    q2 = _read_json(root, "results/processed/Q2_backend_twin_summary.json")

    proofs = {
        "b0": _require_file(root, "docs/proofs/B0_imported_basis_uniqueness.md"),
        "o1": _require_file(root, "docs/proofs/O1_chain_characterization.md"),
        "o2": _require_file(root, "docs/proofs/O1_unique_scalar_timeline.md"),
        "o3": _require_file(root, "docs/proofs/O2_capacity.md"),
        "o4": _require_file(root, "docs/proofs/O4_noise_bound.md"),
        "n": _require_file(root, "docs/proofs/no_go_package.md"),
    }

    artifact_paths = [
        "results/processed/C0_theorem_verification.parquet",
        "results/processed/C1_basis_landscape.nc",
        "results/processed/C2_order_catalog.parquet",
        "results/processed/C3_noise_phase_diagram.parquet",
        "results/processed/C4_assumption_failures.json",
        "results/processed/C5_ghz_exact.json",
        "results/processed/Q1_noise_sweep.parquet",
        "results/processed/Q2_backend_twin.parquet",
    ]
    for path in artifact_paths:
        _require_file(root, path)

    counterexample_ids = {
        str(item["id"]) for item in cast(list[dict[str, Any]], counterexamples["counterexamples"])
    }
    c5_expectations = cast(dict[str, dict[str, float]], c5["expectations"])
    c5_objectivity = cast(dict[str, float], c5["objectivity"])
    c5_coherence = cast(dict[str, float], c5["coherence_witness"])

    return [
        _claim(
            claim_id="B0",
            planned_claim=(
                "Under a fixed admissible partition, redundant records can select at most "
                "one nondegenerate objective basis."
            ),
            evidence_grade="P;E",
            evidence_status="imported_prior_art_with_local_validation",
            novelty_status="Imported; not a project novelty claim",
            evidence_required="Prior-art theorem plus local Bell/GHZ validation.",
            evidence_artifacts=[proofs["b0"], "results/processed/C1_basis_landscape_summary.json"],
            evidence_checks=[
                f"bell_min={c1['bell_min']}",
                f"bell_max={c1['bell_max']}",
                f"ghz_z_score={c1['ghz_z_score']}",
                f"ghz_x_score={c1['ghz_x_score']}",
            ],
            caveat="Fixed-partition and nondegeneracy assumptions are mandatory.",
        ),
        _claim(
            claim_id="O1",
            planned_claim=(
                "Persistent trajectories are exactly chains in the record-dominance "
                "poset after quotienting duplicate signatures."
            ),
            evidence_grade="P;E",
            evidence_status="supported",
            novelty_status="Central formalization",
            evidence_required="Formal proof plus exhaustive small-code regression.",
            evidence_artifacts=[proofs["o1"], "results/processed/T101_chain_verification.json"],
            evidence_checks=[
                f"codes_checked={t101['codes_checked']}",
                f"sequences_checked={t101['sequences_checked']}",
                f"mismatch_count={t101['mismatch_count']}",
                f"c0_failure_count={c0['failure_count']}",
            ],
            caveat=(
                "The statement is about persistent-record codes, not arbitrary physical dynamics."
            ),
        ),
        _claim(
            claim_id="O2",
            planned_claim=(
                "All labels admit one scalar persistent timeline iff the quotient "
                "record-poset is a chain and labels are nonduplicate."
            ),
            evidence_grade="P;E",
            evidence_status="supported",
            novelty_status="Clock-specific interpretation",
            evidence_required=(
                "Formal iff proof plus branching, duplicate and disconnected fixtures."
            ),
            evidence_artifacts=[
                proofs["o2"],
                "results/processed/C2_order_catalog_summary.json",
                "results/processed/C2_order_catalog.parquet",
            ],
            evidence_checks=[
                f"linear_extensions_are_physical={c2['linear_extensions_are_physical']}",
                f"diamond={cast(dict[str, str], c2['classifications'])['diamond']}",
                f"duplicate={cast(dict[str, str], c2['classifications'])['duplicate']}",
            ],
            caveat="Linear extensions are scheduler totalizations, not physical time trajectories.",
        ),
        _claim(
            claim_id="O3",
            planned_claim=(
                "E binary persistent coordinates encode at most E+1 distinct states on "
                "one strict scalar trajectory."
            ),
            evidence_grade="P;E",
            evidence_status="supported",
            novelty_status="Simple exact capacity bound",
            evidence_required="Rank proof, exhaustive capacity table and thermometer construction.",
            evidence_artifacts=[proofs["o3"], "results/processed/T103_capacity.json"],
            evidence_checks=[
                f"binary_rows={len(cast(list[Any], t103['binary_capacity']))}",
                f"boundary_rows={len(cast(list[Any], t103['boundary_e_equals_n_minus_2']))}",
                "thermometer_n5_present=True",
            ],
            caveat="Capacity bound applies to strict persistent scalar trajectories.",
        ),
        _claim(
            claim_id="O4",
            planned_claim=(
                "q independent noisy copies obey the stated majority-decoding recovery "
                "bound and full-table union bound."
            ),
            evidence_grade="P;E;S",
            evidence_status="supported",
            novelty_status="Applied concentration bound",
            evidence_required="Analytic bound, exact binomial grid and stochastic C3 sweep.",
            evidence_artifacts=[
                proofs["o4"],
                "results/processed/T104_noise_bound_grid.json",
                "results/processed/C3_noise_phase_summary.json",
            ],
            evidence_checks=[
                f"t104_violation_count={t104['violation_count']}",
                f"c3_bound_violation_count={c3['bound_violation_count']}",
                f"c3_grid_cells_complete={c3['grid_cells_complete']}",
            ],
            caveat="Independent-copy and p<1/2 assumptions are required.",
        ),
        _claim(
            claim_id="N1",
            planned_claim="Redundancy alone does not identify the order of labels.",
            evidence_grade="N;E",
            evidence_status="supported_no_go",
            novelty_status="Boundary result",
            evidence_required="Smallest label-permutation counterexample.",
            evidence_artifacts=[proofs["n"], "results/processed/counterexample_catalog.json"],
            evidence_checks=[f"N1_present={'N1' in counterexample_ids}"],
            caveat="External label anchoring can add order information; redundancy alone cannot.",
        ),
        _claim(
            claim_id="N2",
            planned_claim="Temporal orientation needs an anchored write asymmetry.",
            evidence_grade="N;E",
            evidence_status="supported_no_go",
            novelty_status="Boundary result",
            evidence_required="Orientation-swap counterexample.",
            evidence_artifacts=[proofs["n"], "results/processed/counterexample_catalog.json"],
            evidence_checks=[f"N2_present={'N2' in counterexample_ids}"],
            caveat="The no-go excludes orientation from basis objectivity alone.",
        ),
        _claim(
            claim_id="N3",
            planned_claim=(
                "Unrestricted partition freedom destroys partition-independent basis uniqueness."
            ),
            evidence_grade="N;P;E",
            evidence_status="supported_no_go",
            novelty_status="Known-adjacent no-go",
            evidence_required="Formal construction and stress-test control.",
            evidence_artifacts=[
                proofs["n"],
                "results/processed/counterexample_catalog.json",
                "results/processed/C4_assumption_failures.json",
            ],
            evidence_checks=[
                f"N3_present={'N3' in counterexample_ids}",
                f"all_predicted_failures_observed={c4['all_predicted_failures_observed']}",
            ],
            caveat="This is a boundary condition on admissible physical partitions.",
        ),
        _claim(
            claim_id="Q1",
            planned_claim=(
                "In the four-qubit GHZ illustration, Z records are local/objective while "
                "X-basis information is global."
            ),
            evidence_grade="P;E;S",
            evidence_status="supported_without_hardware",
            novelty_status="Illustration only",
            evidence_required="Exact GHZ calculation, C1 landscape and local Q302 simulator sweep.",
            evidence_artifacts=[
                "results/processed/C1_basis_landscape_summary.json",
                "results/processed/C5_ghz_exact.json",
                "results/processed/Q1_noise_sweep_summary.json",
            ],
            evidence_checks=[
                f"ghz_z_score={c1['ghz_z_score']}",
                f"ghz_x_score={c1['ghz_x_score']}",
                f"q302_passing_cells={q1['passing_cells']}/{q1['row_count']}",
            ],
            caveat=(
                "No Q-grade evidence is claimed; Q304 is a backend-derived local twin, "
                "not a hardware observation."
            ),
        ),
        _claim(
            claim_id="Q2",
            planned_claim=(
                "A dephased GHZ mixture preserves Z objectivity but removes the global "
                "X-parity coherence witness."
            ),
            evidence_grade="P;E;S",
            evidence_status="supported_without_hardware",
            novelty_status="Boundary illustration",
            evidence_required="Exact coherent/dephased comparison plus local simulator readiness.",
            evidence_artifacts=[
                "results/processed/C5_ghz_exact.json",
                "results/processed/Q1_noise_sweep_summary.json",
                "results/processed/Q2_backend_twin_summary.json",
            ],
            evidence_checks=[
                f"z_basis_ghz={c5_objectivity['z_basis_ghz']}",
                f"z_basis_dephased={c5_objectivity['z_basis_dephased']}",
                f"ghz_xxxx={c5_expectations['XXXX']['ghz']}",
                f"dephased_xxxx={c5_expectations['XXXX']['dephased']}",
                f"coherence_difference={c5_coherence['absolute_difference']}",
                f"q304_status={q2['status']}",
                f"q304_reason={q2['reason']}",
            ],
            caveat=(
                "No hardware observation is available; the backend-derived twin is "
                "a preregistration readiness simulation only."
            ),
        ),
    ]


def validate_claim_evidence_matrix(rows: list[ClaimEvidence]) -> None:
    expected_ids = {"B0", "O1", "O2", "O3", "O4", "N1", "N2", "N3", "Q1", "Q2"}
    observed_ids = {row.id for row in rows}
    if observed_ids != expected_ids:
        raise ValueError(f"Unexpected claim IDs: {sorted(observed_ids)}")
    for row in rows:
        if not row.evidence_artifacts:
            raise ValueError(f"{row.id} has no evidence artifact")
        if not row.evidence_checks:
            raise ValueError(f"{row.id} has no evidence check")
        if not row.caveat:
            raise ValueError(f"{row.id} has no caveat")
        if row.id.startswith("Q") and "without_hardware" in row.evidence_status:
            if "Q;" in row.evidence_grade or row.evidence_grade == "Q":
                raise ValueError(f"{row.id} cannot have Q-grade evidence without hardware")


def write_claim_evidence_csv(path: Path, rows: list[ClaimEvidence]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
