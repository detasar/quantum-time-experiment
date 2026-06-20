import numpy as np

from objective_clocks.states import dephased_ghz_density, ghz_density

IDENTITY = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)


def kron(*ops: np.ndarray) -> np.ndarray:
    result = ops[0]
    for op in ops[1:]:
        result = np.kron(result, op)
    return result


def expectation(rho: np.ndarray, *ops: np.ndarray) -> float:
    return float(np.trace(rho @ kron(*ops)).real)


def test_ghz_exact_correlations() -> None:
    rho = ghz_density(4)
    assert np.isclose(expectation(rho, Z, IDENTITY, Z, IDENTITY), 1.0)
    assert np.isclose(expectation(rho, Z, IDENTITY, IDENTITY, Z), 1.0)
    assert np.isclose(expectation(rho, X, IDENTITY, X, IDENTITY), 0.0)
    assert np.isclose(expectation(rho, X, IDENTITY, IDENTITY, X), 0.0)
    assert np.isclose(expectation(rho, X, X, X, X), 1.0)


def test_dephased_control_preserves_z_and_loses_x_parity() -> None:
    rho = dephased_ghz_density(4)
    assert np.isclose(expectation(rho, Z, IDENTITY, Z, IDENTITY), 1.0)
    assert np.isclose(expectation(rho, Z, IDENTITY, IDENTITY, Z), 1.0)
    assert np.isclose(expectation(rho, X, X, X, X), 0.0)
