from __future__ import annotations

import numpy as np

from objective_clocks.classical import (
    C0Config,
    broadcast_basis_score,
    c0_fixture_rows,
    c0_runtime_report,
    c0_theorem_rows,
    c1_qubit_basis_landscape,
    c2_catalog_rows,
    c3_noise_rows,
    c4_assumption_stress_matrix,
    c5_ghz_exact_rows,
)


def test_c201_small_grid_has_zero_theorem_failures() -> None:
    rows = c0_theorem_rows(
        C0Config(
            n_max=3,
            record_max=2,
            random_cases=5,
            seed=20260620,
            exhaustive_state_space_limit=4096,
        )
    )
    fixtures = c0_fixture_rows()
    report = c0_runtime_report(rows, fixtures)

    assert report["failure_count"] == 0
    assert report["grid_cell_count"] == 4


def test_c202_qubit_landscape_recovers_bell_ambiguity_and_ghz_selection() -> None:
    landscape = c1_qubit_basis_landscape(theta_points=3, phi_points=5)

    assert np.allclose(landscape["bell_one_record"], 1.0)
    assert np.isclose(landscape["ghz_two_records"][0, 0], 1.0)
    assert np.isclose(landscape["ghz_two_records"][1, 0], 0.0)
    assert np.isclose(landscape["ghz_two_records"][2, 0], 1.0)


def test_c202_broadcast_identity_and_no_record_controls() -> None:
    identity = np.eye(3, dtype=np.complex128)
    fourier = np.fft.fft(identity) / np.sqrt(3)

    assert np.isclose(broadcast_basis_score(identity, n_records=2), 1.0)
    assert np.isclose(broadcast_basis_score(fourier, n_records=2), 0.0)
    assert np.isclose(broadcast_basis_score(identity, n_records=0), 0.0)


def test_c203_catalog_keeps_linear_extensions_diagnostic_only() -> None:
    rows = c2_catalog_rows()
    by_fixture = {str(row["fixture"]): row for row in rows}

    assert by_fixture["thermometer"]["classification"] == "scalar_time"
    assert by_fixture["diamond"]["classification"] == "branching_or_partial_order"
    assert by_fixture["diamond"]["maximal_persistent_chain_count"] == 2
    assert by_fixture["diamond"]["linear_extension_count_scheduler_only"] == 2
    assert not any(bool(row["linear_extensions_are_physical"]) for row in rows)


def test_c204_noise_rows_are_deterministic_and_bound_checked() -> None:
    config = {
        "n_states": [4],
        "q_values": [1, 3],
        "p_values": [0.0, 0.1],
        "trials_per_cell": 200,
    }
    first = c3_noise_rows(config, seed=20260620)
    second = c3_noise_rows(config, seed=20260620)

    assert first == second
    assert len(first) == 4
    assert not any(row["bound_violation"] for row in first)


def test_c205_assumption_stress_matrix_predicts_failures() -> None:
    matrix = c4_assumption_stress_matrix()

    assert matrix["all_predicted_failures_observed"]
    controls = {control["control"]: control for control in matrix["controls"]}
    assert controls["bell_single_fragment"]["expected_failure"] == "preferred_basis_not_unique"
    assert controls["ghz_two_fragments"]["expected_failure"] == "none"


def test_c206_ghz_exact_rows_match_analytic_expectations() -> None:
    payload = c5_ghz_exact_rows()
    expectations = payload["expectations"]

    assert np.isclose(expectations["ZZ_C_R1"]["ghz"], 1.0)
    assert np.isclose(expectations["ZZ_C_R1"]["dephased"], 1.0)
    assert np.isclose(expectations["XXXX"]["ghz"], 1.0)
    assert np.isclose(expectations["XXXX"]["dephased"], 0.0)
    assert np.isclose(
        payload["objectivity"]["z_basis_ghz"],
        payload["objectivity"]["z_basis_dephased"],
    )
    assert np.isclose(payload["coherence_witness"]["absolute_difference"], 1.0)
