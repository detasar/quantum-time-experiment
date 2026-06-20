from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from objective_clocks.artifacts import environment_manifest, sha256_file, write_json_atomic
from objective_clocks.classical import c5_ghz_exact_rows


def _write_ghz_figure(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    expectations = payload["expectations"]
    if not isinstance(expectations, dict):
        raise TypeError("expectations must be a dictionary")
    labels = list(expectations)
    ghz = [float(expectations[label]["ghz"]) for label in labels]
    dephased = [float(expectations[label]["dephased"]) for label in labels]
    positions = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.bar(positions - width / 2, ghz, width, label="GHZ")
    ax.bar(positions + width / 2, dephased, width, label="dephased")
    ax.set_xticks(positions, labels, rotation=25, ha="right")
    ax.set_ylabel("expectation")
    ax.set_ylim(-0.1, 1.1)
    ax.set_title("C5 exact GHZ vs dephased-control observables")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def main() -> None:
    processed = Path("results/processed")
    figures = Path("figures")
    output = processed / "C5_ghz_exact.json"
    figure = figures / "fig_05_ghz_exact.pdf"
    payload = c5_ghz_exact_rows()
    _write_ghz_figure(figure, payload)
    payload["environment"] = environment_manifest()
    payload["figure"] = {"path": str(figure), "sha256": sha256_file(figure)}
    write_json_atomic(output, payload)
    expectations = payload["expectations"]
    if not isinstance(expectations, dict):
        raise TypeError("expectations must be a dictionary")
    if abs(float(expectations["ZZ_C_R1"]["ghz"]) - 1.0) > 1e-10:
        raise SystemExit("C5 analytic ZZ_C_R1 expectation failed")
    if abs(float(expectations["XXXX"]["dephased"])) > 1e-10:
        raise SystemExit("C5 dephased X parity was not zero")
    print(payload)


if __name__ == "__main__":
    main()
