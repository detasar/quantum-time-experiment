from __future__ import annotations

import time
from pathlib import Path

import matplotlib
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
from objective_clocks.quantum import q302_noise_rows


def _write_q302_figure(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subset = frame[frame["readout_flip"] == sorted(frame["readout_flip"].unique())[0]]
    piv = subset.pivot(
        index="two_qubit_depolarizing",
        columns="one_qubit_depolarizing",
        values="delta_obj_lcb",
    )
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    image = ax.imshow(piv.values, origin="lower", aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(piv.columns)), [f"{value:.4f}" for value in piv.columns])
    ax.set_yticks(range(len(piv.index)), [f"{value:.3f}" for value in piv.index])
    ax.set_xlabel("1Q depolarizing")
    ax.set_ylabel("2Q depolarizing")
    ax.set_title("Q302 delta_obj LCB at lowest readout error")
    fig.colorbar(image, ax=ax, label="delta_obj_lcb")
    fig.tight_layout()
    fig.savefig(path, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def main() -> None:
    started = time.perf_counter()
    config_path = Path("configs/quantum_local.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    rows = q302_noise_rows(config, seed=int(config["master_seed"]))
    frame = pd.DataFrame(rows)
    processed = Path("results/processed")
    figures = Path("figures")
    output = processed / "Q1_noise_sweep.parquet"
    figure = figures / "fig_q302_noise_readiness.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(output, index=False)
    _write_q302_figure(figure, frame)
    summary = {
        "experiment_id": "Q302",
        "config_hash": config_hash(config),
        "duration_seconds": round(time.perf_counter() - started, 6),
        "row_count": len(rows),
        "grid_cells_complete": len(rows)
        == len(config["noise_sweep"]["one_qubit_depolarizing"])
        * len(config["noise_sweep"]["two_qubit_depolarizing"])
        * len(config["noise_sweep"]["readout_flip"]),
        "passing_cells": int(frame["passes_inclusion_thresholds"].sum()),
        "thresholds": config["inclusion_thresholds"],
        "environment": environment_manifest(),
        "outputs": file_manifest([output, figure]),
    }
    write_json_atomic(processed / "Q1_noise_sweep_summary.json", summary)
    if not summary["grid_cells_complete"]:
        raise SystemExit("Q302 grid incomplete")
    print(summary)


if __name__ == "__main__":
    main()
