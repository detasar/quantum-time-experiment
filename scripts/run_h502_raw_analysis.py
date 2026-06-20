from __future__ import annotations

import json
from pathlib import Path

import yaml

from objective_clocks.hardware import (
    analyze_hardware_raw_payload,
    latest_h501_payload_path,
    write_processed_analysis,
)


def main() -> None:
    config = yaml.safe_load(Path("configs/quantum_local.yaml").read_text(encoding="utf-8"))
    payload_path = latest_h501_payload_path()
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    analysis = analyze_hardware_raw_payload(
        payload,
        alpha=float(config["statistics"]["alpha"]),
        bootstrap_replicates=int(config["statistics"]["bootstrap_replicates"]),
        bootstrap_seed=int(config["statistics"]["bootstrap_seed"]),
        thresholds=config["inclusion_thresholds"],
    )
    output = Path("results/processed/Q3_hardware_raw.json")
    write_processed_analysis(output, analysis, [payload_path, Path("configs/quantum_local.yaml")])
    print(
        {
            "task": analysis["task"],
            "status": analysis["status"],
            "job_id": analysis["job_id"],
            "passes_main_text_inclusion_without_mitigation": analysis[
                "passes_main_text_inclusion_without_mitigation"
            ],
            "result_interpretation": analysis["result_interpretation"],
        }
    )


if __name__ == "__main__":
    main()
