import numpy as np

from objective_clocks.information import (
    classical_mutual_information,
    partial_trace,
    shannon_entropy,
    von_neumann_entropy,
)
from objective_clocks.states import bell_state, ket_to_density


def test_entropy_basics() -> None:
    assert np.isclose(shannon_entropy(np.array([0.5, 0.5])), 1.0)
    pure = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=np.complex128)
    mixed = np.eye(2, dtype=np.complex128) / 2
    assert np.isclose(von_neumann_entropy(pure), 0.0)
    assert np.isclose(von_neumann_entropy(mixed), 1.0)


def test_classical_mutual_information_perfect_bit() -> None:
    joint = np.array([[0.5, 0.0], [0.0, 0.5]])
    assert np.isclose(classical_mutual_information(joint), 1.0)


def test_partial_trace_bell_is_maximally_mixed() -> None:
    rho = ket_to_density(bell_state())
    reduced = partial_trace(rho, (2, 2), (0,))
    assert np.allclose(reduced, np.eye(2) / 2)
