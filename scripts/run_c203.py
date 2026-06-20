from __future__ import annotations

import json
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
from objective_clocks.classical import c2_catalog_rows, write_c2_graphs


def main() -> None:
    started = time.perf_counter()
    config_path = Path("configs/classical.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    rows = c2_catalog_rows()
    serializable_rows = [
        {
            **row,
            "maximal_persistent_chains": json.dumps(row["maximal_persistent_chains"]),
        }
        for row in rows
    ]
    processed = Path("results/processed")
    output = processed / "C2_order_catalog.parquet"
    graph_paths = write_c2_graphs(processed / "C2_graphs")
    pd.DataFrame(serializable_rows).to_parquet(output, index=False)
    summary = {
        "experiment_id": "C2",
        "config_hash": config_hash(config),
        "duration_seconds": round(time.perf_counter() - started, 6),
        "row_count": len(rows),
        "classifications": {str(row["fixture"]): str(row["classification"]) for row in rows},
        "linear_extensions_are_physical": False,
        "environment": environment_manifest(),
        "outputs": file_manifest([output, *graph_paths]),
    }
    write_json_atomic(processed / "C2_order_catalog_summary.json", summary)
    if any(row["linear_extensions_are_physical"] for row in rows):
        raise SystemExit("A linear extension was incorrectly marked physical")
    print(summary)


if __name__ == "__main__":
    main()
