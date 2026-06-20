import numpy as np

from objective_clocks.statistics import correlation, spins


def test_spins_and_correlation() -> None:
    bits = np.array([[0, 0], [1, 1], [0, 0], [1, 1]], dtype=int)
    assert spins(bits).tolist() == [[1, 1], [-1, -1], [1, 1], [-1, -1]]
    assert np.isclose(correlation(bits, (0, 1)), 1.0)
