import numpy as np

from objective_clocks.noise import (
    exact_majority_error,
    hoeffding_majority_bound,
    majority_decode,
    simulate_redundant_records,
)


def test_majority_decode() -> None:
    values = np.array([[[True, True, False], [False, False, True]]])
    decoded = majority_decode(values)
    assert decoded.tolist() == [[True, False]]


def test_exact_error_below_hoeffding_bound() -> None:
    for q in (1, 3, 5, 7, 9):
        for p in (0.01, 0.05, 0.1, 0.2, 0.3):
            assert exact_majority_error(q, p) <= hoeffding_majority_bound(q, p) + 1e-12


def test_simulation_reproducible() -> None:
    truth = np.array([[False, True, True]], dtype=bool)
    first = simulate_redundant_records(truth, q=5, p=0.1, trials=100, seed=7)
    second = simulate_redundant_records(truth, q=5, p=0.1, trials=100, seed=7)
    assert np.array_equal(first, second)
