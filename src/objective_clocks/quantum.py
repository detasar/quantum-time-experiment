from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .circuits import named_science_circuits
from .statistics import clopper_pearson_expectation_interval

IntArray = NDArray[np.int_]


def parse_qiskit_bitstring(bitstring: str, *, width: int = 4) -> tuple[int, ...]:
    compact = bitstring.replace(" ", "")
    if len(compact) != width or any(bit not in {"0", "1"} for bit in compact):
        raise ValueError(f"Expected a {width}-bit computational-basis string")
    return tuple(int(bit) for bit in compact[::-1])


def counts_to_bit_array(counts: dict[str, int], *, width: int = 4) -> IntArray:
    rows: list[tuple[int, ...]] = []
    for bitstring, count in sorted(counts.items()):
        rows.extend([parse_qiskit_bitstring(bitstring, width=width)] * int(count))
    return np.asarray(rows, dtype=np.int_)


def product_values_from_counts(
    counts: dict[str, int],
    columns: tuple[int, ...],
    *,
    width: int = 4,
) -> NDArray[np.int_]:
    bits = counts_to_bit_array(counts, width=width)
    spins = 1 - 2 * bits[:, columns]
    return np.asarray(np.prod(spins, axis=1), dtype=np.int_)


def expectation_from_counts(
    counts: dict[str, int],
    columns: tuple[int, ...],
    *,
    width: int = 4,
) -> float:
    products = product_values_from_counts(counts, columns, width=width)
    return float(products.mean())


def interval_from_counts(
    counts: dict[str, int],
    columns: tuple[int, ...],
    *,
    alpha: float,
    width: int = 4,
) -> Any:
    return clopper_pearson_expectation_interval(
        product_values_from_counts(counts, columns, width=width),
        alpha=alpha,
    )


def statevector_probabilities(circuit: Any) -> dict[str, float]:
    from qiskit.quantum_info import Statevector

    state = Statevector.from_instruction(circuit)
    probabilities = state.probabilities_dict()
    return {str(key): float(value) for key, value in sorted(probabilities.items())}


def exact_expectation_from_probabilities(
    probabilities: dict[str, float],
    columns: tuple[int, ...],
    *,
    width: int = 4,
) -> float:
    total = 0.0
    for bitstring, probability in probabilities.items():
        bits = parse_qiskit_bitstring(bitstring, width=width)
        value = 1
        for column in columns:
            value *= 1 - 2 * bits[column]
        total += float(probability) * value
    return float(total)


def exact_science_expectations() -> dict[str, dict[str, float]]:
    circuits = named_science_circuits(measure=False)
    observables = {
        "ZZ_C_R1": (0, 2),
        "ZZ_C_R2": (0, 3),
        "XX_C_R1": (0, 2),
        "XX_C_R2": (0, 3),
        "XXXX": (0, 1, 2, 3),
    }
    return {
        name: {
            observable: exact_expectation_from_probabilities(
                statevector_probabilities(circuit),
                columns,
            )
            for observable, columns in observables.items()
        }
        for name, circuit in circuits.items()
    }


def build_generic_noise_model(*, one_qubit: float, two_qubit: float, readout: float) -> Any:
    from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

    noise_model = NoiseModel()
    if one_qubit > 0.0:
        noise_model.add_all_qubit_quantum_error(
            depolarizing_error(one_qubit, 1),
            ["h", "x", "z"],
        )
    if two_qubit > 0.0:
        noise_model.add_all_qubit_quantum_error(depolarizing_error(two_qubit, 2), ["cx"])
    if readout > 0.0:
        noise_model.add_all_qubit_readout_error(
            ReadoutError([[1.0 - readout, readout], [readout, 1.0 - readout]])
        )
    return noise_model


def simulate_counts(
    circuit: Any,
    *,
    shots: int,
    seed: int,
    noise_model: Any | None = None,
) -> dict[str, int]:
    from qiskit_aer import AerSimulator

    simulator = AerSimulator(noise_model=noise_model, seed_simulator=seed)
    result = simulator.run(circuit, shots=shots).result()
    return {str(key): int(value) for key, value in result.get_counts().items()}


def _abs_interval_upper(interval: Any) -> float:
    return float(max(abs(interval.lower), abs(interval.upper)))


def _abs_interval_lower(interval: Any) -> float:
    lower = float(interval.lower)
    upper = float(interval.upper)
    if lower <= 0.0 <= upper:
        return 0.0
    return float(min(abs(lower), abs(upper)))


def quantum_metrics_from_counts(
    counts: dict[str, dict[str, int]],
    *,
    alpha: float,
) -> dict[str, float]:
    z_counts = counts["ghz_plus_z"]
    x_counts = counts["ghz_plus_x"]
    minus_x_counts = counts["ghz_minus_x"]
    z1 = interval_from_counts(z_counts, (0, 2), alpha=alpha)
    z2 = interval_from_counts(z_counts, (0, 3), alpha=alpha)
    x1 = interval_from_counts(x_counts, (0, 2), alpha=alpha)
    x2 = interval_from_counts(x_counts, (0, 3), alpha=alpha)
    w_plus = interval_from_counts(x_counts, (0, 1, 2, 3), alpha=alpha)
    w_minus = interval_from_counts(minus_x_counts, (0, 1, 2, 3), alpha=alpha)
    min_z_lcb = min(float(z1.lower), float(z2.lower))
    max_local_x_abs_ucb = max(_abs_interval_upper(x1), _abs_interval_upper(x2))
    w_mix = 0.5 * (float(w_plus.estimate) + float(w_minus.estimate))
    w_mix_abs_ucb = max(
        abs(0.5 * (plus_endpoint + minus_endpoint))
        for plus_endpoint in (float(w_plus.lower), float(w_plus.upper))
        for minus_endpoint in (float(w_minus.lower), float(w_minus.upper))
    )
    return {
        "z_c_r1": float(z1.estimate),
        "z_c_r2": float(z2.estimate),
        "x_c_r1": float(x1.estimate),
        "x_c_r2": float(x2.estimate),
        "w_plus_xxxx": float(w_plus.estimate),
        "w_minus_xxxx": float(w_minus.estimate),
        "w_mix_xxxx": w_mix,
        "delta_obj": min(float(z1.estimate), float(z2.estimate))
        - max(abs(float(x1.estimate)), abs(float(x2.estimate))),
        "delta_obj_lcb": min_z_lcb - max_local_x_abs_ucb,
        "min_z_correlation_lcb": min_z_lcb,
        "delta_coh": abs(float(w_plus.estimate)) - abs(w_mix),
        "delta_coh_lcb": _abs_interval_lower(w_plus) - w_mix_abs_ucb,
    }


def run_generic_noise_cell(
    *,
    one_qubit: float,
    two_qubit: float,
    readout: float,
    shots: int,
    seed: int,
    alpha: float,
) -> dict[str, float]:
    circuits = named_science_circuits(measure=True)
    noise_model = build_generic_noise_model(
        one_qubit=one_qubit,
        two_qubit=two_qubit,
        readout=readout,
    )
    counts = {
        name: simulate_counts(
            circuit,
            shots=shots,
            seed=seed + index,
            noise_model=noise_model,
        )
        for index, (name, circuit) in enumerate(circuits.items())
    }
    return quantum_metrics_from_counts(counts, alpha=alpha)


def q302_noise_rows(config: dict[str, Any], *, seed: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    thresholds = config["inclusion_thresholds"]
    sweep = config["noise_sweep"]
    for one_q in sweep["one_qubit_depolarizing"]:
        for two_q in sweep["two_qubit_depolarizing"]:
            for readout in sweep["readout_flip"]:
                cell_seed = (
                    seed
                    + int(round(1_000_000 * one_q))
                    + 10 * int(round(1_000_000 * two_q))
                    + 100 * int(round(1_000_000 * readout))
                )
                metrics = run_generic_noise_cell(
                    one_qubit=float(one_q),
                    two_qubit=float(two_q),
                    readout=float(readout),
                    shots=int(sweep["shots_per_point"]),
                    seed=cell_seed,
                    alpha=float(config["statistics"]["alpha"]),
                )
                rows.append(
                    {
                        "experiment_id": "Q302",
                        "one_qubit_depolarizing": float(one_q),
                        "two_qubit_depolarizing": float(two_q),
                        "readout_flip": float(readout),
                        "shots_per_circuit": int(sweep["shots_per_point"]),
                        "seed": cell_seed,
                        **metrics,
                        "passes_inclusion_thresholds": bool(
                            metrics["delta_obj_lcb"] >= thresholds["delta_obj_lcb"]
                            and metrics["min_z_correlation_lcb"]
                            >= thresholds["min_z_correlation_lcb"]
                            and metrics["delta_coh_lcb"] >= thresholds["delta_coh_lcb"]
                        ),
                    }
                )
    return rows


@dataclass(frozen=True)
class BackendCandidate:
    name: str
    n_qubits: int
    operational: bool
    simulator: bool
    pending_jobs: int
    basis_gates: tuple[str, ...]
    coupling_edges: tuple[tuple[int, int], ...]
    one_qubit_error: float
    two_qubit_error: float
    readout_error: float


def fixture_backend_candidates() -> list[BackendCandidate]:
    return [
        BackendCandidate(
            name="fixture_falcon_line4",
            n_qubits=5,
            operational=True,
            simulator=False,
            pending_jobs=3,
            basis_gates=("rz", "sx", "x", "cx", "measure"),
            coupling_edges=((0, 1), (1, 2), (2, 3), (3, 4)),
            one_qubit_error=0.001,
            two_qubit_error=0.010,
            readout_error=0.020,
        ),
        BackendCandidate(
            name="fixture_heavy_hex7",
            n_qubits=7,
            operational=True,
            simulator=False,
            pending_jobs=1,
            basis_gates=("rz", "sx", "x", "cx", "measure"),
            coupling_edges=((0, 1), (1, 2), (1, 3), (3, 4), (3, 5), (5, 6)),
            one_qubit_error=0.0008,
            two_qubit_error=0.008,
            readout_error=0.018,
        ),
        BackendCandidate(
            name="fixture_busy_backend",
            n_qubits=5,
            operational=True,
            simulator=False,
            pending_jobs=80,
            basis_gates=("rz", "sx", "x", "cx", "measure"),
            coupling_edges=((0, 1), (1, 2), (2, 3), (3, 4)),
            one_qubit_error=0.001,
            two_qubit_error=0.012,
            readout_error=0.030,
        ),
    ]


def _undirected_distances(candidate: BackendCandidate) -> dict[tuple[int, int], int]:
    nodes = range(candidate.n_qubits)
    distances: dict[tuple[int, int], int] = {}
    adjacency: dict[int, set[int]] = {node: set() for node in nodes}
    for a, b in candidate.coupling_edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    for source in nodes:
        frontier = [(source, 0)]
        seen = {source}
        for node, distance in frontier:
            distances[(source, node)] = distance
            for nxt in adjacency[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append((nxt, distance + 1))
    return distances


def best_layout_for_candidate(
    candidate: BackendCandidate,
) -> tuple[tuple[int, int, int, int], float]:
    distances = _undirected_distances(candidate)
    best_layout: tuple[int, int, int, int] | None = None
    best_score = float("inf")
    for layout in combinations(range(candidate.n_qubits), 4):
        c, s, r1, r2 = layout
        star_distance = sum(distances.get((c, target), 99) for target in (s, r1, r2))
        score = (
            star_distance
            + candidate.pending_jobs / 100.0
            + 100.0 * candidate.two_qubit_error
            + 10.0 * candidate.readout_error
        )
        if score < best_score:
            best_score = score
            best_layout = layout
    if best_layout is None:
        raise ValueError("candidate has fewer than four qubits")
    return best_layout, float(best_score)


def rank_backend_candidates(candidates: list[BackendCandidate]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        eligible = (
            candidate.operational
            and not candidate.simulator
            and candidate.n_qubits >= 4
            and "cx" in candidate.basis_gates
        )
        layout: tuple[int, ...]
        if eligible:
            layout, score = best_layout_for_candidate(candidate)
        else:
            layout = ()
            score = float("inf")
        rows.append(
            {
                "name": candidate.name,
                "eligible": eligible,
                "n_qubits": candidate.n_qubits,
                "pending_jobs": candidate.pending_jobs,
                "basis_gates": list(candidate.basis_gates),
                "coupling_edges": [list(edge) for edge in candidate.coupling_edges],
                "one_qubit_error": candidate.one_qubit_error,
                "two_qubit_error": candidate.two_qubit_error,
                "readout_error": candidate.readout_error,
                "selected_layout": list(layout),
                "layout_score": score,
            }
        )
    return sorted(rows, key=lambda row: (not row["eligible"], row["layout_score"], row["name"]))
