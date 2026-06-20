from __future__ import annotations

import json
from pathlib import Path

import yaml

from objective_clocks.hardware import (
    analyze_readout_mitigated_payload,
    latest_h501_payload_path,
    write_processed_analysis,
)


def main() -> None:
    config = yaml.safe_load(Path("configs/quantum_local.yaml").read_text(encoding="utf-8"))
    payload_path = latest_h501_payload_path()
    raw_path = Path("results/processed/Q3_hardware_raw.json")
    if not raw_path.exists():
        raise SystemExit("Run H502 raw analysis before H503 mitigation")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    raw_analysis = json.loads(raw_path.read_text(encoding="utf-8"))
    analysis = analyze_readout_mitigated_payload(
        payload,
        raw_analysis,
        thresholds=config["inclusion_thresholds"],
    )
    output = Path("results/processed/Q3_hardware_mitigated.json")
    write_processed_analysis(
        output,
        analysis,
        [payload_path, raw_path, Path("configs/quantum_local.yaml")],
    )
    print(
        {
            "task": analysis["task"],
            "status": analysis["status"],
            "raw_primary_pass": analysis["raw_primary_pass"],
            "corrected_point_threshold_pass": analysis["corrected_point_threshold_pass"],
            "qualitative_agreement_with_raw": analysis["qualitative_agreement_with_raw"],
        }
    )


if __name__ == "__main__":
    main()
