from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import matplotlib
import numpy as np
import yaml

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from objective_clocks.artifacts import sha256_file, write_json_atomic


def _read_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def write_hardware_summary_figure(
    *,
    raw_path: Path,
    config_path: Path,
    figure_path: Path,
    manifest_path: Path,
) -> None:
    raw = _read_json(raw_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    thresholds = cast(dict[str, float], config["inclusion_thresholds"])
    metrics = cast(dict[str, float], raw["metrics"])
    bootstrap = cast(dict[str, float], raw["bootstrap"])

    lcb_labels = [
        r"$\Delta_{obj}$ LCB",
        r"min $Z$ corr. LCB",
        r"$\Delta_{coh}$ LCB",
    ]
    lcb_values = np.asarray(
        [
            float(bootstrap["delta_obj_lcb"]),
            float(metrics["min_z_correlation_lcb"]),
            float(bootstrap["delta_coh_lcb"]),
        ]
    )
    threshold_values = np.asarray(
        [
            float(thresholds["delta_obj_lcb"]),
            float(thresholds["min_z_correlation_lcb"]),
            float(thresholds["delta_coh_lcb"]),
        ]
    )
    witness_labels = [
        "GHZ +",
        "GHZ -",
        "mixture",
    ]
    witness_values = np.asarray(
        [
            float(metrics["w_plus_xxxx"]),
            float(metrics["w_minus_xxxx"]),
            float(metrics["w_mix_xxxx"]),
        ]
    )

    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax_lcb, ax_witness) = plt.subplots(
        1,
        2,
        figsize=(10.8, 4.3),
        gridspec_kw={"width_ratios": [1.0, 1.0]},
        constrained_layout=True,
    )

    y = np.arange(len(lcb_labels))
    ax_lcb.barh(y, lcb_values, color="#2a9d8f", height=0.56)
    ax_lcb.scatter(threshold_values, y, marker="|", s=520, color="#c44569", linewidths=2.2)
    for index, (value, threshold) in enumerate(zip(lcb_values, threshold_values, strict=True)):
        ax_lcb.text(
            min(value + 0.025, 0.98),
            index,
            f"{value:.3f}",
            va="center",
            ha="left" if value < 0.94 else "right",
            color="#102a43",
            fontweight="bold",
        )
        ax_lcb.text(
            threshold,
            index + 0.34,
            f"threshold {threshold:.2f}",
            va="center",
            ha="center",
            color="#7f1d1d",
            fontsize=8,
        )
    ax_lcb.set_yticks(y, lcb_labels)
    ax_lcb.set_xlim(0.0, 1.02)
    ax_lcb.set_xlabel("lower confidence bound")
    ax_lcb.set_title("Raw QPU inclusion margins")
    ax_lcb.grid(axis="x", alpha=0.25)
    ax_lcb.invert_yaxis()

    colors = ["#1f77b4", "#d95f02", "#7a8fa3"]
    y2 = np.arange(len(witness_labels))
    ax_witness.axvline(0.0, color="#102a43", linewidth=1.0)
    ax_witness.barh(y2, witness_values, color=colors, height=0.56)
    for index, value in enumerate(witness_values):
        if abs(value) > 0.15:
            x = value / 2.0
            ha = "center"
            color = "white"
        else:
            x = value + 0.05
            ha = "left"
            color = "#102a43"
        ax_witness.text(
            x,
            index,
            f"{value:+.3f}",
            va="center",
            ha=ha,
            color=color,
            fontweight="bold",
        )
    ax_witness.set_yticks(y2, witness_labels)
    ax_witness.set_xlim(-1.12, 1.12)
    ax_witness.set_xlabel(r"raw $\langle XXXX\rangle$ expectation")
    ax_witness.set_title("Global coherence witness")
    ax_witness.grid(axis="x", alpha=0.25)
    ax_witness.invert_yaxis()

    fig.suptitle(
        "H502 locked raw hardware result on ibm_kingston",
        fontsize=13,
        fontweight="bold",
    )
    fig.savefig(
        figure_path,
        bbox_inches="tight",
        pad_inches=0.08,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)

    write_json_atomic(
        manifest_path,
        {
            "task": "Q3_hardware_summary_figure",
            "status": "complete",
            "inputs": [raw_path.as_posix(), config_path.as_posix()],
            "figure": {
                "path": figure_path.as_posix(),
                "sha256": sha256_file(figure_path),
            },
            "secret_values_recorded": False,
        },
    )


def main() -> None:
    write_hardware_summary_figure(
        raw_path=Path("results/processed/Q3_hardware_raw.json"),
        config_path=Path("configs/quantum_local.yaml"),
        figure_path=Path("figures/fig_q3_hardware_summary.pdf"),
        manifest_path=Path("results/processed/Q3_hardware_summary_figure.json"),
    )


if __name__ == "__main__":
    main()
