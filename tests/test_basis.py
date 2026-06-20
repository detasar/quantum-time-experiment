import numpy as np

from objective_clocks.basis import basis_distance, minimum_objectivity_score, qubit_basis
from objective_clocks.states import bell_state, ghz_state


def test_basis_distance_permutation_invariant() -> None:
    z = np.eye(2, dtype=np.complex128)
    swapped = z[:, [1, 0]]
    assert np.isclose(basis_distance(z, swapped), 0.0)


def test_ghz_two_records_prefers_z_over_x() -> None:
    ket = ghz_state(3)  # C, R1, R2
    dims = (2, 2, 2)
    z_basis = np.eye(2, dtype=np.complex128)
    x_basis = qubit_basis(np.pi / 2, 0.0)
    z_score = minimum_objectivity_score(ket, dims, z_basis, (1, 2))
    x_score = minimum_objectivity_score(ket, dims, x_basis, (1, 2))
    assert np.isclose(z_score, 1.0, atol=1e-10)
    assert np.isclose(x_score, 0.0, atol=1e-10)


def test_bell_single_record_is_ambiguous_across_basis() -> None:
    ket = bell_state()
    dims = (2, 2)
    for theta, phi in ((0.0, 0.0), (np.pi / 2, 0.0), (np.pi / 3, np.pi / 5)):
        score = minimum_objectivity_score(ket, dims, qubit_basis(theta, phi), (1,))
        assert np.isclose(score, 1.0, atol=1e-10)
