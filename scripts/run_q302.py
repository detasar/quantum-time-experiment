from __future__ import annotations

import time
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import yaml
from matplotlib.colors import ListedColormap

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from objective_clocks.artifacts import (
    config_hash,
    environment_manifest,
    file_manifest,
    write_json_atomic,
)
from objective_clocks.quantum import q302_noise_rows


def _write_q302_figure(path: Path, frame: pd.DataFrame, thresholds: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    one_q_values = sorted(float(value) for value in frame["one_qubit_depolarizing"].unique())
    two_q_values = sorted(float(value) for value in frame["two_qubit_depolarizing"].unique())
    readout_values = sorted(float(value) for value in frame["readout_flip"].unique())
    highest_readout = readout_values[-1]
    high_readout = frame[frame["readout_flip"] == highest_readout].copy()
    pass_grid = (
        high_readout.pivot(
            index="two_qubit_depolarizing",
            columns="one_qubit_depolarizing",
            values="passes_inclusion_thresholds",
        )
        .reindex(index=two_q_values, columns=one_q_values)
        .astype(bool)
    )
    margin_columns = []
    for metric, threshold in thresholds.items():
        margin_column = f"{metric}_margin"
        high_readout[margin_column] = high_readout[metric] - float(threshold)
        margin_columns.append(margin_column)
    high_readout["minimum_threshold_margin"] = high_readout[margin_columns].min(axis=1)
    margin = high_readout.pivot(
        index="two_qubit_depolarizing",
        columns="one_qubit_depolarizing",
        values="minimum_threshold_margin",
    ).reindex(index=two_q_values, columns=one_q_values)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), constrained_layout=True)
    pass_cmap = ListedColormap(["#e9ecef", "#2a9d8f"])
    axes[0].imshow(
        pass_grid.astype(int).values,
        origin="lower",
        aspect="auto",
        vmin=0.0,
        vmax=1.0,
        cmap=pass_cmap,
    )
    image1 = axes[1].imshow(
        margin.values,
        origin="lower",
        aspect="auto",
        vmin=-0.04,
        vmax=0.08,
        cmap="RdBu_r",
    )

    for ax in axes:
        ax.set_xticks(range(len(one_q_values)), [f"{value:.4f}" for value in one_q_values])
        ax.set_yticks(range(len(two_q_values)), [f"{value:.3f}" for value in two_q_values])
        ax.set_xlabel("1Q depolarizing")
        ax.set_ylabel("2Q depolarizing")
        ax.set_xticks(np.arange(-0.5, len(one_q_values), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(two_q_values), 1), minor=True)
        ax.grid(which="minor", color="white", alpha=0.30, linewidth=0.8)

    axes[0].set_title(f"Pass/fail at readout={highest_readout:.2f}")
    for row in range(pass_grid.shape[0]):
        for col in range(pass_grid.shape[1]):
            passed = bool(pass_grid.iloc[row, col])
            axes[0].text(
                col,
                row,
                "PASS" if passed else "FAIL",
                ha="center",
                va="center",
                color="white" if passed else "#102a43",
                fontsize=8,
                fontweight="bold",
            )

    axes[1].set_title(f"Minimum inclusion margin at readout={highest_readout:.2f}")
    axes[1].contour(margin.values, levels=[0.0], colors="black", linewidths=1.5)
    for row in range(margin.shape[0]):
        for col in range(margin.shape[1]):
            value = float(margin.iloc[row, col])
            axes[1].text(
                col,
                row,
                f"{value:+.3f}",
                ha="center",
                va="center",
                color="white" if abs(value) > 0.025 else "#102a43",
                fontsize=8,
            )
    fig.colorbar(image1, ax=axes[1], label="margin over preregistered threshold")
    fig.savefig(
        path,
        bbox_inches="tight",
        pad_inches=0.08,
        metadata={"CreationDate": None, "ModDate": None},
    )
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
    _write_q302_figure(figure, frame, config["inclusion_thresholds"])
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
