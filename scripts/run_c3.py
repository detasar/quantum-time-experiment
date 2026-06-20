from __future__ import annotations

import time
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import yaml

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from objective_clocks.artifacts import (
    config_hash,
    environment_manifest,
    file_manifest,
    write_json_atomic,
)
from objective_clocks.classical import c3_noise_rows


def _write_noise_figure(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n_states = int(frame["n_states"].max())
    subset = frame[frame["n_states"] == n_states]
    q_values = sorted(int(value) for value in subset["q"].unique())
    p_values = sorted(float(value) for value in subset["p"].unique())
    matrix = np.empty((len(q_values), len(p_values)), dtype=np.float64)
    for i, q in enumerate(q_values):
        for j, p in enumerate(p_values):
            value = subset[(subset["q"] == q) & (subset["p"] == p)]["full_table_recovery"].iloc[0]
            matrix[i, j] = float(value)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    image = ax.imshow(matrix, origin="lower", aspect="auto", vmin=0.0, vmax=1.0, cmap="viridis")
    ax.set_xticks(range(len(p_values)), [f"{value:.2f}" for value in p_values])
    ax.set_yticks(range(len(q_values)), [str(value) for value in q_values])
    ax.set_xlabel("bit-flip probability p")
    ax.set_ylabel("redundant copies q")
    ax.set_title(f"C3 Noise Sweep: full-table recovery for N={n_states}")
    fig.colorbar(image, ax=ax, label="empirical full-table recovery")
    fig.tight_layout()
    fig.savefig(path, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def main() -> None:
    started = time.perf_counter()
    config_path = Path("configs/classical.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    rows = c3_noise_rows(config["C3"], seed=int(config["master_seed"]))
    frame = pd.DataFrame(rows)
    processed = Path("results/processed")
    figures = Path("figures")
    output = processed / "C3_noise_phase_diagram.parquet"
    figure = figures / "fig_04_noise_phase.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(output, index=False)
    _write_noise_figure(figure, frame)
    summary = {
        "experiment_id": "C3",
        "config_hash": config_hash(config),
        "duration_seconds": round(time.perf_counter() - started, 6),
        "row_count": len(rows),
        "grid_cells_complete": len(rows)
        == (
            len(config["C3"]["n_states"])
            * len(config["C3"]["q_values"])
            * len(config["C3"]["p_values"])
        ),
        "bound_violation_count": int(frame["bound_violation"].sum()),
        "rerun_seed_policy": "seed = master_seed + 10000*N + 100*q + round(1000*p)",
        "environment": environment_manifest(),
        "outputs": file_manifest([output, figure]),
    }
    write_json_atomic(processed / "C3_noise_phase_summary.json", summary)
    if not summary["grid_cells_complete"]:
        raise SystemExit("C3 grid is incomplete")
    if summary["bound_violation_count"]:
        raise SystemExit("C3 exact majority error exceeded Hoeffding bound")
    print(summary)


if __name__ == "__main__":
    main()
