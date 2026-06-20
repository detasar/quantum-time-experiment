from __future__ import annotations

from pathlib import Path

import pandas as pd

from objective_clocks.artifacts import file_manifest, write_json_atomic


def main() -> None:
    q303_path = Path("results/processed/Q303_backend_candidates.json")
    if not q303_path.exists():
        raise SystemExit("Run Q303 before Q304")
    import json

    q303 = json.loads(q303_path.read_text(encoding="utf-8"))
    selected = q303.get("selected_backend")
    provider_source = q303.get("candidate_source")
    rows = []
    if provider_source != "provider":
        rows.append(
            {
                "experiment_id": "Q304",
                "status": "hardware_stage_stopped",
                "reason": "no_real_backend_snapshot_available",
                "candidate_source": provider_source,
                "backend": selected["name"] if selected else None,
                "passes_preregistered_local_readiness": False,
            }
        )
    else:
        rows.append(
            {
                "experiment_id": "Q304",
                "status": "backend_snapshot_ready",
                "reason": "provider_backend_snapshot_available",
                "candidate_source": provider_source,
                "backend": selected["name"] if selected else None,
                "passes_preregistered_local_readiness": True,
            }
        )
    output = Path("results/processed/Q2_backend_twin.parquet")
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(output, index=False)
    summary = {
        "experiment_id": "Q304",
        "status": rows[0]["status"],
        "reason": rows[0]["reason"],
        "outputs": file_manifest([output]),
    }
    write_json_atomic(Path("results/processed/Q2_backend_twin_summary.json"), summary)
    print(summary)


if __name__ == "__main__":
    main()
