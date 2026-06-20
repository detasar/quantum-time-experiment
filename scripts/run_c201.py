from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import yaml

from objective_clocks.artifacts import (
    config_hash,
    environment_manifest,
    file_manifest,
    write_json_atomic,
)
from objective_clocks.classical import C0Config, c0_fixture_rows, c0_runtime_report, c0_theorem_rows


def main() -> None:
    started = time.perf_counter()
    config_path = Path("configs/classical.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    c0 = config["C0"]
    c0_config = C0Config(
        n_max=int(c0["exhaustive_n_max"]),
        record_max=int(c0["exhaustive_record_max"]),
        random_cases=int(c0["random_cases"]),
        seed=int(config["master_seed"]),
    )
    rows = c0_theorem_rows(c0_config)
    fixtures = c0_fixture_rows()
    frame = pd.DataFrame(rows)
    processed = Path("results/processed")
    output = processed / "C0_theorem_verification.parquet"
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(output, index=False)

    fixture_output = processed / "C0_theorem_fixtures.json"
    write_json_atomic(fixture_output, {"fixtures": fixtures})
    report = c0_runtime_report(rows, fixtures)
    report.update(
        {
            "config_hash": config_hash(config),
            "duration_seconds": round(time.perf_counter() - started, 6),
            "environment": environment_manifest(),
            "outputs": file_manifest([output, fixture_output]),
        }
    )
    write_json_atomic(processed / "C0_runtime_report.json", report)
    if report["failure_count"]:
        raise SystemExit(f"C0 failed with {report['failure_count']} theorem failures")
    print(report)


if __name__ == "__main__":
    main()
