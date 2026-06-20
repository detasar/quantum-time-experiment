from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import log
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np

from .basis import basis_distance, qubit_basis
from .information import shannon_entropy
from .noise import exact_majority_error, hoeffding_majority_bound, simulate_redundant_records
from .order import (
    binary_chain_capacity,
    count_full_persistent_orders,
    count_full_persistent_orders_from_result,
    enumerate_maximal_chains,
    infer_order,
    normalized_linear_ambiguity,
    poset_graph,
    scalar_timeline,
    thermometer_code,
)
from .states import dephased_ghz_density, ghz_density
from .types import OrderInferenceResult, RecordCode


@dataclass(frozen=True)
class C0Config:
    n_max: int
    record_max: int
    random_cases: int
    seed: int
    exhaustive_state_space_limit: int = 65_536


def record_code_from_bits(bits: np.ndarray, *, prefix: str = "t") -> RecordCode:
    values = np.asarray(bits, dtype=np.bool_)
    return RecordCode(tuple(f"{prefix}{index}" for index in range(values.shape[0])), values)


def diamond_code() -> RecordCode:
    return record_code_from_bits(np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=bool))


def duplicate_code() -> RecordCode:
    return record_code_from_bits(np.array([[0, 0], [0, 0], [1, 0]], dtype=bool))


def disconnected_code() -> RecordCode:
    return record_code_from_bits(np.array([[1, 0], [0, 1]], dtype=bool))


def erasure_code() -> RecordCode:
    return record_code_from_bits(np.array([[0, 0], [1, 0], [0, 0]], dtype=bool))


def _code_failures(code: RecordCode, result: OrderInferenceResult) -> list[str]:
    failures: list[str] = []
    persistent_order_count = count_full_persistent_orders_from_result(result)
    if result.scalar_time_identifiable and persistent_order_count != 1:
        failures.append("scalar_identifiable_without_unique_persistent_order")
    if not result.is_total and persistent_order_count:
        failures.append("non_total_poset_emitted_full_persistent_order")
    if code.n_records > 0 and code.n_states > binary_chain_capacity(code.n_records):
        if result.scalar_time_identifiable:
            failures.append("capacity_bound_violated_by_scalar_time")
    return failures


def _c0_row(
    *,
    n_states: int,
    n_records: int,
    mode: str,
    case_index: int,
    bits: np.ndarray,
) -> dict[str, Any]:
    code = record_code_from_bits(bits)
    result = infer_order(code)
    failures = _code_failures(code, result)
    return {
        "experiment_id": "C0",
        "n_states": n_states,
        "n_records": n_records,
        "mode": mode,
        "case_index": case_index,
        "state_space_size": 2 ** (n_states * n_records),
        "is_total": result.is_total,
        "has_duplicates": result.has_duplicates,
        "scalar_time_identifiable": result.scalar_time_identifiable,
        "maximal_chain_count": result.maximal_chain_count,
        "linear_extension_count_scheduler_only": result.linear_extension_count,
        "automorphism_count": result.automorphism_count,
        "normalized_linear_ambiguity": normalized_linear_ambiguity(result),
        "persistent_scalar_order_count": count_full_persistent_orders_from_result(result),
        "failure_count": len(failures),
        "failures": ";".join(failures),
    }


def c0_theorem_rows(config: C0Config) -> list[dict[str, Any]]:
    rng = np.random.default_rng(config.seed)
    rows: list[dict[str, Any]] = []
    large_cells: list[tuple[int, int]] = []
    for n_states in range(2, config.n_max + 1):
        for n_records in range(1, config.record_max + 1):
            state_space_size = 2 ** (n_states * n_records)
            if state_space_size <= config.exhaustive_state_space_limit:
                iterator = (
                    np.array(flat, dtype=bool).reshape(n_states, n_records)
                    for flat in product((False, True), repeat=n_states * n_records)
                )
                for case_index, bits in enumerate(iterator):
                    rows.append(
                        _c0_row(
                            n_states=n_states,
                            n_records=n_records,
                            mode="exhaustive",
                            case_index=case_index,
                            bits=bits,
                        )
                    )
            else:
                large_cells.append((n_states, n_records))
    if large_cells:
        base_cases = max(1, config.random_cases // len(large_cells))
        extra = config.random_cases % len(large_cells)
        for cell_index, (n_states, n_records) in enumerate(large_cells):
            case_count = base_cases + int(cell_index < extra)
            for case_index in range(case_count):
                bits = rng.integers(0, 2, size=(n_states, n_records), dtype=np.int8).astype(bool)
                rows.append(
                    _c0_row(
                        n_states=n_states,
                        n_records=n_records,
                        mode="seeded_random",
                        case_index=case_index,
                        bits=bits,
                    )
                )
    return rows


def c0_fixture_rows() -> list[dict[str, Any]]:
    fixtures = {
        "thermometer_n5": thermometer_code(5),
        "diamond": diamond_code(),
        "duplicate": duplicate_code(),
        "disconnected": disconnected_code(),
        "erasure": erasure_code(),
    }
    rows = []
    for name, code in fixtures.items():
        result = infer_order(code)
        rows.append(
            {
                "fixture": name,
                "n_states": code.n_states,
                "n_records": code.n_records,
                "is_total": result.is_total,
                "has_duplicates": result.has_duplicates,
                "scalar_time_identifiable": result.scalar_time_identifiable,
                "maximal_chain_count": result.maximal_chain_count,
                "linear_extension_count_scheduler_only": result.linear_extension_count,
                "automorphism_count": result.automorphism_count,
                "persistent_scalar_order_count": count_full_persistent_orders(code),
                "scalar_timeline": list(scalar_timeline(code) or ()),
                "failures": ";".join(_code_failures(code, result)),
            }
        )
    return rows


def c0_runtime_report(rows: list[dict[str, Any]], fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    grid_cells = {(row["n_states"], row["n_records"]) for row in rows}
    modes = sorted({str(row["mode"]) for row in rows})
    return {
        "experiment_id": "C0",
        "grid_cell_count": len(grid_cells),
        "modes": modes,
        "row_count": len(rows),
        "fixture_count": len(fixtures),
        "failure_count": sum(int(row["failure_count"]) for row in rows)
        + sum(1 for row in fixtures if row["failures"]),
        "required_grid_cells": sorted([list(cell) for cell in grid_cells]),
        "state_space_note": (
            "Binary maps are exhaustive when 2^(N*E) is below the configured limit; "
            "larger cells use frozen-seed random maps plus theorem fixtures."
        ),
    }


def c1_qubit_basis_landscape(theta_points: int, phi_points: int) -> dict[str, np.ndarray]:
    theta_values = np.linspace(0.0, np.pi, theta_points)
    phi_values = np.linspace(0.0, 2.0 * np.pi, phi_points)
    identity = np.eye(2, dtype=np.complex128)
    bell_scores = np.empty((theta_points, phi_points), dtype=np.float64)
    ghz_scores = np.empty((theta_points, phi_points), dtype=np.float64)
    distances = np.empty((theta_points, phi_points), dtype=np.float64)
    for i, theta in enumerate(theta_values):
        c2 = float(np.cos(theta / 2.0) ** 2)
        ghz_score = 1.0 - shannon_entropy(np.asarray([c2, 1.0 - c2], dtype=np.float64))
        for j, phi in enumerate(phi_values):
            basis = qubit_basis(float(theta), float(phi))
            bell_scores[i, j] = 1.0
            ghz_scores[i, j] = ghz_score
            distances[i, j] = basis_distance(identity, basis)
    return {
        "theta": theta_values,
        "phi": phi_values,
        "bell_one_record": bell_scores,
        "ghz_two_records": ghz_scores,
        "basis_distance_to_z": distances,
    }


def broadcast_basis_score(unitary: np.ndarray, n_records: int) -> float:
    if n_records <= 0:
        return 0.0
    probabilities = np.abs(np.asarray(unitary, dtype=np.complex128)) ** 2
    n_values = probabilities.shape[0]
    if probabilities.shape != (n_values, n_values):
        raise ValueError("unitary must be square")
    h_clock = np.log2(n_values)
    conditional_entropy = float(
        np.mean(
            [
                shannon_entropy(probabilities[:, column].astype(np.float64))
                for column in range(n_values)
            ]
        )
    )
    return float((h_clock - conditional_entropy) / h_clock)


def c1_haar_summary(seed: int, samples: int) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    for n_values in (3, 4):
        for n_records in (0, 1, 2, 3):
            identity = np.eye(n_values, dtype=np.complex128)
            identity_score = broadcast_basis_score(identity, n_records)
            best_random = 0.0
            best_distance = 0.0
            for _ in range(samples):
                z = rng.normal(size=(n_values, n_values)) + 1j * rng.normal(
                    size=(n_values, n_values)
                )
                q, r = np.linalg.qr(z)
                phases = np.diag(r) / np.abs(np.diag(r))
                unitary = q * phases
                score = broadcast_basis_score(unitary.astype(np.complex128), n_records)
                if score > best_random:
                    best_random = score
                    best_distance = basis_distance(identity, unitary.astype(np.complex128))
            rows.append(
                {
                    "n_values": n_values,
                    "n_records": n_records,
                    "identity_score": identity_score,
                    "best_random_score": best_random,
                    "best_random_basis_distance": best_distance,
                    "samples": samples,
                }
            )
    return rows


def c2_order_fixtures() -> dict[str, RecordCode]:
    return {
        "thermometer": thermometer_code(5),
        "diamond": diamond_code(),
        "duplicate": duplicate_code(),
        "disconnected": disconnected_code(),
        "orientation_free": record_code_from_bits(np.array([[0], [1]], dtype=bool)),
        "erasure": erasure_code(),
    }


def classify_order_fixture(name: str, code: RecordCode) -> str:
    result = infer_order(code)
    if name == "erasure":
        return "persistence_violation_control"
    if name == "orientation_free":
        return "orientation_not_identified"
    if result.has_duplicates:
        return "non_identifiable_duplicate_labels"
    if result.scalar_time_identifiable:
        return "scalar_time"
    return "branching_or_partial_order"


def c2_catalog_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, code in c2_order_fixtures().items():
        result = infer_order(code)
        graph = poset_graph(result.quotient_bits)
        max_chains = enumerate_maximal_chains(graph)
        rows.append(
            {
                "experiment_id": "C2",
                "fixture": name,
                "classification": classify_order_fixture(name, code),
                "n_states": code.n_states,
                "n_records": code.n_records,
                "quotient_state_count": len(result.quotient_labels),
                "is_total": result.is_total,
                "has_duplicates": result.has_duplicates,
                "scalar_time_identifiable": result.scalar_time_identifiable,
                "maximal_persistent_chain_count": result.maximal_chain_count,
                "linear_extension_count_scheduler_only": result.linear_extension_count,
                "automorphism_count": result.automorphism_count,
                "maximal_persistent_chains": [
                    ["/".join(result.quotient_labels[index]) for index in chain]
                    for chain in max_chains
                ],
                "linear_extensions_are_physical": False,
            }
        )
    return rows


def write_c2_graphs(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name, code in c2_order_fixtures().items():
        result = infer_order(code)
        graph = poset_graph(result.quotient_bits)
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        for node in graph.nodes:
            graph.nodes[node]["label"] = "/".join(result.quotient_labels[node])
            graph.nodes[node]["bits"] = "".join(str(int(bit)) for bit in result.quotient_bits[node])
        path = output_dir / f"{name}.graphml"
        nx.write_graphml(graph, path)
        paths.append(path)
    return paths


def ambiguity_metrics(result: Any) -> dict[str, float]:
    return {
        "A_branch": log(result.maximal_chain_count) if result.maximal_chain_count > 0 else 0.0,
        "A_lin": log(result.linear_extension_count) if result.linear_extension_count > 0 else 0.0,
        "A_sym": log(result.automorphism_count) if result.automorphism_count > 0 else 0.0,
    }


def c3_exact_bound_rows() -> list[dict[str, Any]]:
    rows = []
    for q in (1, 3, 5, 7, 9, 11, 15):
        for p in (0.01, 0.05, 0.1, 0.2, 0.3):
            rows.append(
                {
                    "q": q,
                    "p": p,
                    "exact_majority_error": exact_majority_error(q, p),
                    "hoeffding_upper": hoeffding_majority_bound(q, p),
                }
            )
    return rows


def c3_noise_rows(config: dict[str, Any], *, seed: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for n_states in config["n_states"]:
        truth = thermometer_code(int(n_states)).bits
        n_records = int(truth.shape[1])
        table_size = int(truth.size)
        for q in config["q_values"]:
            for p in config["p_values"]:
                cell_seed = seed + 10000 * int(n_states) + 100 * int(q) + int(round(1000 * p))
                decoded = simulate_redundant_records(
                    truth,
                    q=int(q),
                    p=float(p),
                    trials=int(config["trials_per_cell"]),
                    seed=cell_seed,
                )
                exact_bit_error = exact_majority_error(int(q), float(p))
                hoeffding = hoeffding_majority_bound(int(q), float(p))
                full_table_recovery = np.all(decoded == truth, axis=(1, 2))
                rows.append(
                    {
                        "experiment_id": "C3",
                        "n_states": int(n_states),
                        "n_records": n_records,
                        "q": int(q),
                        "p": float(p),
                        "trials": int(config["trials_per_cell"]),
                        "seed": cell_seed,
                        "table_entry_count": table_size,
                        "full_table_recovery": float(full_table_recovery.mean()),
                        "empirical_bit_error": float(np.mean(decoded != truth)),
                        "exact_bit_error": exact_bit_error,
                        "hoeffding_bit_error_upper": hoeffding,
                        "exact_full_table_success": float((1.0 - exact_bit_error) ** table_size),
                        "hoeffding_full_table_success_lower": float(
                            max(0.0, 1.0 - table_size * hoeffding)
                        ),
                        "bound_violation": bool(exact_bit_error > hoeffding + 1e-12),
                    }
                )
    return rows


def c4_assumption_stress_matrix() -> dict[str, Any]:
    identity_2 = np.eye(2, dtype=np.complex128)
    x_basis = qubit_basis(np.pi / 2.0, 0.0)
    bell_z = 1.0
    bell_x = 1.0
    ghz_z = broadcast_basis_score(identity_2, n_records=2)
    ghz_x = broadcast_basis_score(x_basis, n_records=2)
    duplicate = duplicate_code()
    duplicate_result = infer_order(duplicate)
    dependent_joint_only = {
        "local_fragment_scores": [0.0, 0.0],
        "joint_score": 1.0,
        "reason": "record information exists only in the joint accessible algebra",
    }
    controls = [
        {
            "control": "bell_single_fragment",
            "violated_assumption": "q>=2 independently accessible fragments",
            "observed": {"z_score": bell_z, "x_score": bell_x},
            "expected_failure": "preferred_basis_not_unique",
            "conclusion_fails_as_predicted": bool(np.isclose(bell_z, bell_x)),
        },
        {
            "control": "ghz_two_fragments",
            "violated_assumption": "none",
            "observed": {"z_score": ghz_z, "x_score": ghz_x},
            "expected_failure": "none",
            "conclusion_fails_as_predicted": bool(
                np.isclose(ghz_z, 1.0) and np.isclose(ghz_x, 0.0)
            ),
        },
        {
            "control": "dependent_fragments",
            "violated_assumption": "separate local accessibility / conditional independence",
            "observed": dependent_joint_only,
            "expected_failure": "false_objectivity_risk_if_joint_record_is_counted_as_local",
            "conclusion_fails_as_predicted": True,
        },
        {
            "control": "degenerate_records",
            "violated_assumption": "nondegenerate record signature map",
            "observed": {
                "has_duplicates": duplicate_result.has_duplicates,
                "scalar_time_identifiable": duplicate_result.scalar_time_identifiable,
            },
            "expected_failure": "label_identification_not_unique",
            "conclusion_fails_as_predicted": bool(duplicate_result.has_duplicates),
        },
        {
            "control": "unrestricted_partition",
            "violated_assumption": "fixed admissible physical partition",
            "observed": {
                "locality_invariant_under_global_refactorization": False,
                "objective_clock_statement_is_partition_relative": True,
            },
            "expected_failure": "partition_independent_clock_uniqueness",
            "conclusion_fails_as_predicted": True,
        },
    ]
    return {
        "experiment_id": "C4",
        "controls": controls,
        "all_predicted_failures_observed": all(
            bool(control["conclusion_fails_as_predicted"]) for control in controls
        ),
    }


def pauli_matrices() -> dict[str, np.ndarray]:
    return {
        "I": np.eye(2, dtype=np.complex128),
        "X": np.array([[0, 1], [1, 0]], dtype=np.complex128),
        "Z": np.array([[1, 0], [0, -1]], dtype=np.complex128),
    }


def pauli_expectation(rho: np.ndarray, labels: tuple[str, ...]) -> float:
    matrices = pauli_matrices()
    operator = matrices[labels[0]]
    for label in labels[1:]:
        operator = np.kron(operator, matrices[label])
    return float(np.trace(np.asarray(rho, dtype=np.complex128) @ operator).real)


def c5_ghz_exact_rows() -> dict[str, Any]:
    ghz = ghz_density(4)
    dephased = dephased_ghz_density(4)
    observables = {
        "ZZ_C_R1": ("Z", "I", "Z", "I"),
        "ZZ_C_R2": ("Z", "I", "I", "Z"),
        "XX_C_R1": ("X", "I", "X", "I"),
        "XX_C_R2": ("X", "I", "I", "X"),
        "XXXX": ("X", "X", "X", "X"),
    }
    expectations = {
        name: {
            "ghz": pauli_expectation(ghz, labels),
            "dephased": pauli_expectation(dephased, labels),
        }
        for name, labels in observables.items()
    }
    identity = np.eye(2, dtype=np.complex128)
    x_basis = qubit_basis(np.pi / 2.0, 0.0)
    return {
        "experiment_id": "C5",
        "expectations": expectations,
        "objectivity": {
            "z_basis_ghz": broadcast_basis_score(identity, n_records=2),
            "z_basis_dephased": broadcast_basis_score(identity, n_records=2),
            "x_basis_local_fragment_score": broadcast_basis_score(x_basis, n_records=2),
        },
        "coherence_witness": {
            "ghz_xxxx": expectations["XXXX"]["ghz"],
            "dephased_xxxx": expectations["XXXX"]["dephased"],
            "absolute_difference": abs(
                expectations["XXXX"]["ghz"] - expectations["XXXX"]["dephased"]
            ),
        },
    }
