from __future__ import annotations

from pathlib import Path

from objective_clocks.interpretation import (
    build_final_decision,
    reproducibility_archive_paths,
    validate_final_decision,
)


def test_a602_final_decision_applies_preregistered_tree() -> None:
    decision = build_final_decision(Path("."))
    validate_final_decision(decision.payload)

    assert (
        decision.payload["artifact_route"]
        == "foundations_artifact_with_bounded_quantum_illustration"
    )
    assert decision.payload["theory_decision"] == "supported"
    assert decision.payload["hardware_interpretation"] == "bounded_quantum_illustration"
    assert "hardware null cannot kill" in decision.payload["preregistered_decision_rule"]
    assert "Do not claim that the IBM hardware observation proves" in decision.markdown


def test_a603_archive_paths_exclude_circular_outputs() -> None:
    paths = {path.as_posix() for path in reproducibility_archive_paths(Path("."))}

    assert "README.md" in paths
    assert "results/processed/Q3_hardware_raw.json" in paths
    assert "results/raw/H501_provider_payload_d8rfasuab0ds73drkaig.json" in paths
    assert "docs/FINAL_DECISION.md" not in paths
    assert "objective-clocks-reproducibility.tar.gz" not in paths
    assert "results/processed/A603_reproducibility_manifest.json" not in paths
