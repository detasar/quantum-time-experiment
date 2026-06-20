from __future__ import annotations

from itertools import combinations, permutations, product
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from objective_clocks.artifacts import (
    environment_manifest,
    file_manifest,
    write_json_atomic,
    write_sha256_manifest,
)
from objective_clocks.noise import exact_majority_error, hoeffding_majority_bound
from objective_clocks.order import (
    binary_chain_capacity,
    brute_force_persistent_orders,
    enumerate_linear_extensions,
    infer_order,
    is_directed_chain_sequence,
    is_persistent_sequence,
    multilevel_chain_capacity,
    poset_graph,
    thermometer_code,
)
from objective_clocks.types import RecordCode


def _small_distinct_codes(max_records: int = 3) -> list[RecordCode]:
    codes: list[RecordCode] = []
    for n_records in range(1, max_records + 1):
        signatures = list(product((False, True), repeat=n_records))
        for size in range(1, min(7, len(signatures)) + 1):
            for subset in combinations(signatures, size):
                codes.append(
                    RecordCode(
                        labels=tuple(str(index) for index in range(size)),
                        bits=np.asarray(subset, dtype=bool),
                    )
                )
    return codes


def _diamond_code() -> RecordCode:
    return RecordCode(
        labels=("00", "10", "01", "11"),
        bits=np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=bool),
    )


def verify_t101() -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    sequence_count = 0
    codes = _small_distinct_codes()
    for code_index, code in enumerate(codes):
        for length in range(1, code.n_states + 1):
            for sequence in permutations(range(code.n_states), length):
                sequence_count += 1
                persistent = is_persistent_sequence(code, sequence)
                chain = is_directed_chain_sequence(code, sequence)
                if persistent != chain:
                    mismatches.append(
                        {
                            "code_index": code_index,
                            "sequence": sequence,
                            "persistent": persistent,
                            "directed_chain": chain,
                        }
                    )

    diamond = _diamond_code()
    diamond_result = infer_order(diamond)
    graph = poset_graph(diamond.bits)
    forced_scalar_counterexamples = []
    for extension in enumerate_linear_extensions(graph):
        loss_edges = []
        for before, after in zip(extension, extension[1:], strict=False):
            before_bits = diamond.bits[before].astype(int).tolist()
            after_bits = diamond.bits[after].astype(int).tolist()
            if not np.all(diamond.bits[before].astype(int) <= diamond.bits[after].astype(int)):
                loss_edges.append(
                    {
                        "before": diamond.labels[before],
                        "after": diamond.labels[after],
                        "before_bits": before_bits,
                        "after_bits": after_bits,
                    }
                )
        if loss_edges:
            forced_scalar_counterexamples.append(
                {
                    "linear_extension": [diamond.labels[index] for index in extension],
                    "record_loss_edges": loss_edges,
                }
            )

    return {
        "task": "T101",
        "codes_checked": len(codes),
        "sequences_checked": sequence_count,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "diamond": {
            "maximal_persistent_chain_count": diamond_result.maximal_chain_count,
            "linear_extension_count_scheduler_only": diamond_result.linear_extension_count,
            "full_persistent_scalar_order_count": len(brute_force_persistent_orders(diamond)),
            "scalar_time_identifiable": diamond_result.scalar_time_identifiable,
            "forced_scalar_counterexamples": forced_scalar_counterexamples,
        },
    }


def verify_t103() -> dict[str, Any]:
    binary = [
        {
            "record_coordinates": n_records,
            "max_chain_length": binary_chain_capacity(n_records),
            "tight_for_n_states": n_records + 1,
        }
        for n_records in range(0, 9)
    ]
    boundary = [
        {
            "n_states": n_states,
            "records_available": n_states - 2,
            "capacity": binary_chain_capacity(n_states - 2),
            "can_encode": binary_chain_capacity(n_states - 2) >= n_states,
        }
        for n_states in range(2, 10)
    ]
    return {
        "task": "T103",
        "binary_capacity": binary,
        "boundary_e_equals_n_minus_2": boundary,
        "multilevel_examples": [
            {"levels": [2, 2, 2], "capacity": multilevel_chain_capacity((2, 2, 2))},
            {"levels": [3, 4], "capacity": multilevel_chain_capacity((3, 4))},
            {"levels": [1, 5, 2], "capacity": multilevel_chain_capacity((1, 5, 2))},
        ],
        "thermometer_n5": thermometer_code(5).bits.astype(int).tolist(),
    }


def verify_t104() -> dict[str, Any]:
    rows = []
    violations = []
    for q in (1, 3, 5, 7, 9, 11, 15):
        for p in (0.01, 0.05, 0.1, 0.2, 0.3, 0.45):
            exact = exact_majority_error(q, p)
            bound = hoeffding_majority_bound(q, p)
            row = {"q": q, "p": p, "exact_error": exact, "hoeffding_upper": bound}
            rows.append(row)
            if exact > bound + 1e-12:
                violations.append(row)
    return {"task": "T104", "grid": rows, "violation_count": len(violations)}


def counterexample_catalog() -> dict[str, Any]:
    diamond = _diamond_code()
    return {
        "task": "T106",
        "counterexamples": [
            {
                "id": "N1",
                "name": "label_permutation",
                "smallest_example": {"labels": ["0", "1"], "permutation": ["1", "0"]},
                "failed_assumption": "ordered labels are externally anchored",
                "failed_conclusion": "redundant objectivity alone fixes temporal order",
            },
            {
                "id": "N2",
                "name": "orientation_swap",
                "smallest_example": {"state": "GHZ2 records |000>+|111>", "swap": "0<->1"},
                "failed_assumption": "blank/present write asymmetry is physically anchored",
                "failed_conclusion": "basis objectivity fixes earlier/later orientation",
            },
            {
                "id": "N3",
                "name": "unrestricted_partition",
                "smallest_example": {
                    "operation": "global Hilbert-space refactorization",
                    "effect": "clock factor and local fragments are not invariant",
                },
                "failed_assumption": "fixed admissible physical partition",
                "failed_conclusion": "partition-independent unique clock basis",
            },
            {
                "id": "N4",
                "name": "single_fragment_bell_ambiguity",
                "smallest_example": {"state": "Bell pair |00>+|11>", "fragments": 1},
                "failed_assumption": "at least two independently accessible fragments",
                "failed_conclusion": "one record selects a preferred basis",
            },
            {
                "id": "O1.2",
                "name": "diamond_branching_no_scalar_time",
                "smallest_example": {
                    "labels": list(diamond.labels),
                    "bits": diamond.bits.astype(int).tolist(),
                },
                "failed_assumption": "all signatures form a chain",
                "failed_conclusion": "one scalar trajectory visits every snapshot",
            },
        ],
    }


def write_capacity_figure(path: Path) -> None:
    records = np.arange(0, 9)
    capacity = np.asarray([binary_chain_capacity(int(value)) for value in records])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    ax.plot(records, capacity, marker="o", color="#1f77b4", label="binary capacity")
    ax.plot(records, records + 1, linestyle="--", color="#555555", label="E + 1")
    ax.set_xlabel("binary persistent record coordinates E")
    ax.set_ylabel("maximum strict-chain clock states N")
    ax.set_title("Persistent Record Capacity")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def main() -> None:
    processed = Path("results/processed")
    figures = Path("figures")
    write_json_atomic(processed / "G0_environment_manifest.json", environment_manifest())
    write_json_atomic(processed / "T101_chain_verification.json", verify_t101())
    write_json_atomic(processed / "T103_capacity.json", verify_t103())
    write_json_atomic(processed / "T104_noise_bound_grid.json", verify_t104())
    write_json_atomic(processed / "counterexample_catalog.json", counterexample_catalog())
    write_capacity_figure(figures / "fig_03_capacity.pdf")

    files = [
        *Path("src").rglob("*.py"),
        *Path("tests").rglob("*.py"),
        *Path("scripts").rglob("*.py"),
        *Path("docs").rglob("*.md"),
        *Path("reports").rglob("*.tex"),
        Path(".gitignore"),
        Path(".pre-commit-config.yaml"),
        Path("pyproject.toml"),
        Path("requirements.lock"),
        Path("README.md"),
        Path("CHANGELOG.md"),
        Path("TASKS.yaml"),
    ]
    write_json_atomic(
        processed / "G0_file_manifest.json",
        {"algorithm": "sha256", "files": file_manifest(files)},
    )
    write_sha256_manifest(
        processed / "G1_output_manifest.json",
        [
            processed / "T101_chain_verification.json",
            processed / "T103_capacity.json",
            processed / "T104_noise_bound_grid.json",
            processed / "counterexample_catalog.json",
            figures / "fig_03_capacity.pdf",
            Path("docs/proofs/O1_unique_scalar_timeline.md"),
            Path("docs/proofs/B0_imported_basis_uniqueness.md"),
            Path("docs/ARCHITECTURE.md"),
            Path("reports/experiment_report.tex"),
        ],
    )
    print("Wrote G0/G1 manifests and theorem artifacts.")


if __name__ == "__main__":
    main()
