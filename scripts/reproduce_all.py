from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    [sys.executable, "-m", "pytest", "-q"],
    [sys.executable, "scripts/run_g1.py"],
    [sys.executable, "scripts/run_g2_all.py"],
    [sys.executable, "scripts/run_g3.py"],
    [sys.executable, "scripts/run_g4_readiness.py"],
    [sys.executable, "scripts/run_h401_draft.py"],
    [sys.executable, "scripts/run_a601.py"],
    [sys.executable, "-m", "objective_clocks.cli", "ghz-exact"],
]


def main() -> None:
    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
