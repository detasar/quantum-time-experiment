from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from objective_clocks.artifacts import write_sha256_manifest

COMMANDS = [
    [sys.executable, "scripts/run_q301.py"],
    [sys.executable, "scripts/run_q302.py"],
    [sys.executable, "scripts/run_q305_backend_amendment.py"],
    [sys.executable, "scripts/run_q303.py"],
    [sys.executable, "scripts/run_q304.py"],
]


def main() -> None:
    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        subprocess.run(command, check=True)
    processed = Path("results/processed")
    outputs = [
        processed / "Q301_circuit_manifest.json",
        processed / "Q301_untranspiled_circuits.qpy",
        processed / "Q1_noise_sweep.parquet",
        processed / "Q1_noise_sweep_summary.json",
        Path("figures/fig_q302_noise_readiness.pdf"),
        processed / "Q305_backend_amendment_diagnostics.json",
        processed / "Q303_backend_candidates.json",
        processed / "Q2_backend_twin.parquet",
        processed / "Q2_backend_twin_summary.json",
    ]
    write_sha256_manifest(processed / "G3_manifest.json", outputs)


if __name__ == "__main__":
    main()
