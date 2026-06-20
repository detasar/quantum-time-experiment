from __future__ import annotations

from pathlib import Path

import yaml

from objective_clocks.artifacts import environment_manifest, write_json_atomic
from objective_clocks.ibm import list_backend_candidates_without_submission
from objective_clocks.quantum import rank_backend_candidates


def _backend_amendment() -> dict[str, object] | None:
    path = Path("configs/backend_amendment.yaml")
    if not path.exists():
        return None
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def main() -> None:
    source, candidates, metadata = list_backend_candidates_without_submission()
    ranked = rank_backend_candidates(candidates)
    amendment = _backend_amendment()
    replacement = amendment.get("replacement", {}) if amendment else {}
    replacement_backend = replacement.get("backend") if isinstance(replacement, dict) else None
    if replacement_backend:
        selected = next(
            (row for row in ranked if row["eligible"] and row["name"] == replacement_backend),
            None,
        )
    else:
        selected = next((row for row in ranked if row["eligible"]), None)
    payload = {
        "experiment_id": "Q303",
        "candidate_source": source,
        "backend_amendment": amendment,
        "backend_amendment_applied": amendment is not None,
        "provider_metadata": metadata,
        "ranked_candidates": ranked,
        "selected_backend": selected,
        "selection_uses_hardware_science_results": False,
        "selection_policy": (
            "pre_result_backend_amendment"
            if amendment is not None
            else "deterministic_lowest_ranked_eligible_backend"
        ),
        "status": "selected" if selected else "no_eligible_backend",
        "environment": environment_manifest(),
    }
    output = Path("results/processed/Q303_backend_candidates.json")
    write_json_atomic(output, payload)
    if selected is None:
        raise SystemExit("Q303 found no eligible backend candidate")
    runtime_account = metadata.get("runtime_account", {})
    print(
        {
            "experiment_id": payload["experiment_id"],
            "candidate_source": source,
            "status": payload["status"],
            "selected_backend": selected["name"],
            "selected_layout": selected["selected_layout"],
            "instance_name": runtime_account.get("instance_name"),
            "plan": runtime_account.get("plan"),
            "pricing_type": runtime_account.get("pricing_type"),
            "secret_values_recorded": runtime_account.get("secret_values_recorded"),
        }
    )


if __name__ == "__main__":
    main()
