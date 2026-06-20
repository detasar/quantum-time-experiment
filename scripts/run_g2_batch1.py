from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from objective_clocks.artifacts import write_sha256_manifest

COMMANDS = [
    [sys.executable, "scripts/run_c201.py"],
    [sys.executable, "scripts/run_c202.py"],
    [sys.executable, "scripts/run_c203.py"],
    [sys.executable, "scripts/run_c2_order_figure.py"],
]


def main() -> None:
    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        subprocess.run(command, check=True)
    processed = Path("results/processed")
    outputs = [
        processed / "C0_theorem_verification.parquet",
        processed / "C0_theorem_fixtures.json",
        processed / "C0_runtime_report.json",
        processed / "C1_basis_landscape.nc",
        processed / "C1_basis_landscape_summary.json",
        Path("figures/fig_02_basis_landscape.pdf"),
        processed / "C2_order_catalog.parquet",
        processed / "C2_order_catalog_summary.json",
        processed / "C2_order_figure_manifest.json",
        Path("figures/fig_01_order_chains.pdf"),
        *sorted((processed / "C2_graphs").glob("*.graphml")),
    ]
    write_sha256_manifest(processed / "G2_C201_C203_manifest.json", outputs)


if __name__ == "__main__":
    main()
