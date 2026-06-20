from __future__ import annotations

from pathlib import Path

from objective_clocks.artifacts import environment_manifest, write_json_atomic
from objective_clocks.ibm import list_backend_candidates_without_submission
from objective_clocks.quantum import rank_backend_candidates


def main() -> None:
    source, candidates, metadata = list_backend_candidates_without_submission()
    ranked = rank_backend_candidates(candidates)
    selected = next((row for row in ranked if row["eligible"]), None)
    payload = {
        "experiment_id": "Q303",
        "candidate_source": source,
        "provider_metadata": metadata,
        "ranked_candidates": ranked,
        "selected_backend": selected,
        "selection_uses_hardware_science_results": False,
        "status": "selected" if selected else "no_eligible_backend",
        "environment": environment_manifest(),
    }
    output = Path("results/processed/Q303_backend_candidates.json")
    write_json_atomic(output, payload)
    if selected is None:
        raise SystemExit("Q303 found no eligible backend candidate")
    print(payload)


if __name__ == "__main__":
    main()
