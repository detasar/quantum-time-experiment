from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from objective_clocks.artifacts import write_sha256_manifest

COMMANDS = [
    [sys.executable, "scripts/run_g2_batch1.py"],
    [sys.executable, "scripts/run_g2_batch2.py"],
]


def main() -> None:
    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        subprocess.run(command, check=True)
    processed = Path("results/processed")
    outputs = [
        processed / "C0_theorem_verification.parquet",
        processed / "C1_basis_landscape.nc",
        processed / "C2_order_catalog.parquet",
        processed / "C2_order_figure_manifest.json",
        processed / "C3_noise_phase_diagram.parquet",
        processed / "C4_assumption_failures.json",
        processed / "C5_ghz_exact.json",
        Path("figures/fig_01_order_chains.pdf"),
        Path("figures/fig_02_basis_landscape.pdf"),
        Path("figures/fig_04_noise_phase.pdf"),
    ]
    write_sha256_manifest(processed / "G2_complete_manifest.json", outputs)


if __name__ == "__main__":
    main()
