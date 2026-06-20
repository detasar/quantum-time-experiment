from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from objective_clocks.artifacts import write_sha256_manifest

COMMANDS = [
    [sys.executable, "scripts/run_c3.py"],
    [sys.executable, "scripts/run_c205.py"],
    [sys.executable, "scripts/run_c206.py"],
]


def main() -> None:
    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        subprocess.run(command, check=True)
    processed = Path("results/processed")
    outputs = [
        processed / "C3_noise_phase_diagram.parquet",
        processed / "C3_noise_phase_summary.json",
        Path("figures/fig_04_noise_phase.pdf"),
        processed / "C4_assumption_failures.json",
        processed / "C5_ghz_exact.json",
        Path("figures/fig_05_ghz_exact.pdf"),
    ]
    write_sha256_manifest(processed / "G2_C204_C206_manifest.json", outputs)


if __name__ == "__main__":
    main()
