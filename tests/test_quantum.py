from __future__ import annotations

import numpy as np

from objective_clocks.circuits import named_science_circuits
from objective_clocks.quantum import (
    BackendCandidate,
    backend_derived_noise_parameters,
    best_layout_for_candidate,
    exact_science_expectations,
    fixture_backend_candidates,
    parse_qiskit_bitstring,
    q302_noise_rows,
    rank_backend_candidates,
    simulate_counts,
)


def test_qiskit_bitstring_parser_uses_logical_order() -> None:
    assert parse_qiskit_bitstring("0001") == (1, 0, 0, 0)
    assert parse_qiskit_bitstring("1000") == (0, 0, 0, 1)


def test_q301_statevector_expectations_are_exact() -> None:
    expectations = exact_science_expectations()

    assert np.isclose(expectations["ghz_plus_z"]["ZZ_C_R1"], 1.0)
    assert np.isclose(expectations["ghz_plus_z"]["ZZ_C_R2"], 1.0)
    assert np.isclose(expectations["ghz_plus_x"]["XXXX"], 1.0)
    assert np.isclose(expectations["ghz_minus_x"]["XXXX"], -1.0)


def test_q301_shot_smoke_counts_are_ghz_z_only() -> None:
    counts = simulate_counts(
        named_science_circuits(measure=True)["ghz_plus_z"],
        shots=128,
        seed=7,
    )

    assert set(counts).issubset({"0000", "1111"})
    assert sum(counts.values()) == 128


def test_q302_noise_rows_complete_small_grid() -> None:
    config = {
        "noise_sweep": {
            "one_qubit_depolarizing": [0.0],
            "two_qubit_depolarizing": [0.0],
            "readout_flip": [0.0],
            "shots_per_point": 512,
        },
        "statistics": {"alpha": 0.05},
        "inclusion_thresholds": {
            "delta_obj_lcb": 0.1,
            "min_z_correlation_lcb": 0.1,
            "delta_coh_lcb": 0.1,
        },
    }

    rows = q302_noise_rows(config, seed=20260620)

    assert len(rows) == 1
    assert rows[0]["passes_inclusion_thresholds"]
    assert rows[0]["delta_obj"] > 0.8
    assert rows[0]["delta_coh"] > 0.8


def test_q303_backend_selection_is_deterministic() -> None:
    first = rank_backend_candidates(fixture_backend_candidates())
    second = rank_backend_candidates(fixture_backend_candidates())

    assert first == second
    assert first[0]["eligible"]
    assert first[0]["name"] == "fixture_heavy_hex7"
    layout, score = best_layout_for_candidate(fixture_backend_candidates()[1])
    assert len(layout) == 4
    assert score >= 0.0


def test_q303_accepts_native_cz_backend_candidates() -> None:
    candidate = BackendCandidate(
        name="native_cz_backend",
        n_qubits=5,
        operational=True,
        simulator=False,
        pending_jobs=0,
        basis_gates=("rz", "sx", "x", "cz", "measure"),
        coupling_edges=((0, 1), (1, 2), (2, 3), (3, 4)),
        one_qubit_error=0.001,
        two_qubit_error=0.012,
        readout_error=0.02,
        two_qubit_edge_errors=((0, 1, 0.01), (1, 2, 0.012), (2, 3, 0.014)),
        readout_errors=((0, 0.01), (1, 0.02), (2, 0.015), (3, 0.017)),
    )

    ranked = rank_backend_candidates([candidate])
    noise = backend_derived_noise_parameters(candidate, tuple(ranked[0]["selected_layout"]))

    assert ranked[0]["eligible"]
    assert ranked[0]["supported_entangling_gates"] == ["cz"]
    assert len(ranked[0]["selected_layout"]) == 4
    assert noise["path_edge_error_count"] > 0
