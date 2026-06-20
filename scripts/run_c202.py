from __future__ import annotations

import time
from pathlib import Path

import matplotlib
import numpy as np
import yaml
from scipy.io import netcdf_file

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from objective_clocks.artifacts import (
    config_hash,
    environment_manifest,
    file_manifest,
    write_json_atomic,
)
from objective_clocks.classical import c1_haar_summary, c1_qubit_basis_landscape


def _write_netcdf(
    path: Path,
    landscape: dict[str, np.ndarray],
    haar_rows: list[dict[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    haar_matrix = np.array(
        [
            [
                row["n_values"],
                row["n_records"],
                row["identity_score"],
                row["best_random_score"],
                row["best_random_basis_distance"],
                row["samples"],
            ]
            for row in haar_rows
        ],
        dtype=np.float64,
    )
    with netcdf_file(path, "w") as handle:
        handle.createDimension("theta", landscape["theta"].size)
        handle.createDimension("phi", landscape["phi"].size)
        handle.createDimension("haar_case", haar_matrix.shape[0])
        handle.createDimension("haar_metric", haar_matrix.shape[1])
        theta = handle.createVariable("theta", "f8", ("theta",))
        phi = handle.createVariable("phi", "f8", ("phi",))
        bell = handle.createVariable("bell_one_record", "f8", ("theta", "phi"))
        ghz = handle.createVariable("ghz_two_records", "f8", ("theta", "phi"))
        distance = handle.createVariable("basis_distance_to_z", "f8", ("theta", "phi"))
        haar = handle.createVariable("haar_summary", "f8", ("haar_case", "haar_metric"))
        theta[:] = landscape["theta"]
        phi[:] = landscape["phi"]
        bell[:, :] = landscape["bell_one_record"]
        ghz[:, :] = landscape["ghz_two_records"]
        distance[:, :] = landscape["basis_distance_to_z"]
        haar[:, :] = haar_matrix
        handle.title = b"C1 basis objectivity landscape"
        handle.haar_metric_order = (
            b"n_values,n_records,identity_score,best_random_score,"
            b"best_random_basis_distance,samples"
        )


def _write_figure(path: Path, landscape: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    theta = landscape["theta"]
    phi = landscape["phi"]
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6), sharex=True, sharey=True)
    for ax, key, title in (
        (axes[0], "bell_one_record", "Bell one-record ambiguity"),
        (axes[1], "ghz_two_records", "GHZ two-record objectivity"),
    ):
        image = ax.imshow(
            landscape[key],
            origin="lower",
            aspect="auto",
            extent=[float(phi[0]), float(phi[-1]), float(theta[0]), float(theta[-1])],
            vmin=0.0,
            vmax=1.0,
            cmap="viridis",
        )
        ax.set_title(title)
        ax.set_xlabel("phi")
        ax.set_ylabel("theta")
    fig.colorbar(image, ax=axes.ravel().tolist(), label="O_min")
    fig.savefig(
        path,
        bbox_inches="tight",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def main() -> None:
    started = time.perf_counter()
    config_path = Path("configs/classical.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    c1 = config["C1"]
    landscape = c1_qubit_basis_landscape(
        theta_points=int(c1["qubit_theta_points"]),
        phi_points=int(c1["qubit_phi_points"]),
    )
    haar_rows = c1_haar_summary(
        seed=int(config["master_seed"]) + 1,
        samples=int(c1["haar_samples"]),
    )
    processed = Path("results/processed")
    figures = Path("figures")
    nc_output = processed / "C1_basis_landscape.nc"
    figure_output = figures / "fig_02_basis_landscape.pdf"
    _write_netcdf(nc_output, landscape, haar_rows)
    _write_figure(figure_output, landscape)

    z_index = 0
    x_index = int(np.argmin(np.abs(landscape["theta"] - np.pi / 2.0)))
    summary = {
        "experiment_id": "C1",
        "config_hash": config_hash(config),
        "duration_seconds": round(time.perf_counter() - started, 6),
        "bell_min": float(np.min(landscape["bell_one_record"])),
        "bell_max": float(np.max(landscape["bell_one_record"])),
        "ghz_z_score": float(landscape["ghz_two_records"][z_index, 0]),
        "ghz_x_score": float(landscape["ghz_two_records"][x_index, 0]),
        "haar_summary": haar_rows,
        "environment": environment_manifest(),
        "outputs": file_manifest([nc_output, figure_output]),
    }
    write_json_atomic(processed / "C1_basis_landscape_summary.json", summary)
    if not np.isclose(summary["bell_min"], 1.0, atol=1e-10):
        raise SystemExit("Bell one-record control did not remain basis-ambiguous")
    if not np.isclose(summary["ghz_z_score"], 1.0, atol=1e-10):
        raise SystemExit("GHZ Z-basis objectivity score is not one")
    if not np.isclose(summary["ghz_x_score"], 0.0, atol=1e-10):
        raise SystemExit("GHZ X-basis local objectivity score is not zero")
    print(summary)


if __name__ == "__main__":
    main()
