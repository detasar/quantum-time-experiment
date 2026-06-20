from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .information import partial_trace

ComplexArray = NDArray[np.complex128]


def basis_vector(dimension: int, index: int) -> ComplexArray:
    vector = np.zeros(dimension, dtype=np.complex128)
    vector[index] = 1.0
    return vector


def ket_to_density(ket: ComplexArray) -> ComplexArray:
    vector = np.asarray(ket, dtype=np.complex128).reshape(-1)
    norm = float(np.vdot(vector, vector).real)
    if not np.isclose(norm, 1.0):
        vector = vector / np.sqrt(norm)
    return np.outer(vector, vector.conj())


def bell_state() -> ComplexArray:
    zero = basis_vector(2, 0)
    one = basis_vector(2, 1)
    return np.asarray((np.kron(zero, zero) + np.kron(one, one)) / np.sqrt(2), dtype=np.complex128)


def ghz_state(n_qubits: int) -> ComplexArray:
    if n_qubits < 2:
        raise ValueError("GHZ requires at least two qubits")
    zero = basis_vector(2, 0)
    one = basis_vector(2, 1)
    ket0 = zero
    ket1 = one
    for _ in range(n_qubits - 1):
        ket0 = np.asarray(np.kron(ket0, zero), dtype=np.complex128)
        ket1 = np.asarray(np.kron(ket1, one), dtype=np.complex128)
    return np.asarray((ket0 + ket1) / np.sqrt(2), dtype=np.complex128)


def ghz_density(n_qubits: int) -> ComplexArray:
    return ket_to_density(ghz_state(n_qubits))


def dephased_ghz_density(n_qubits: int) -> ComplexArray:
    dimension = 2**n_qubits
    rho = np.zeros((dimension, dimension), dtype=np.complex128)
    rho[0, 0] = 0.5
    rho[-1, -1] = 0.5
    return rho


def generalized_broadcast_state(
    n_values: int,
    n_records: int,
    *,
    include_system: bool = True,
) -> tuple[ComplexArray, tuple[int, ...]]:
    if n_values < 2 or n_records < 0:
        raise ValueError("Invalid dimensions")
    subsystem_count = 1 + int(include_system) + n_records
    dims = tuple(n_values for _ in range(subsystem_count))
    ket = np.zeros(int(np.prod(dims)), dtype=np.complex128)
    for t in range(n_values):
        components = [basis_vector(n_values, t) for _ in range(subsystem_count)]
        term = components[0]
        for component in components[1:]:
            term = np.asarray(np.kron(term, component), dtype=np.complex128)
        ket += term
    ket /= np.sqrt(n_values)
    return ket, dims


def conditional_fragment_states_from_pure(
    ket: ComplexArray,
    dims: tuple[int, ...],
    clock_basis: ComplexArray,
    fragment_indices: tuple[int, ...],
) -> tuple[np.ndarray, dict[int, list[ComplexArray]]]:
    """Return clock outcome probabilities and conditional fragment states.

    Clock is subsystem zero. clock_basis columns are basis vectors.
    """

    vector = np.asarray(ket, dtype=np.complex128).reshape(-1)
    if vector.size != int(np.prod(dims)):
        raise ValueError("ket size does not match dims")
    if clock_basis.shape != (dims[0], dims[0]):
        raise ValueError("clock basis dimension mismatch")
    matrix = vector.reshape(dims[0], -1)
    rest_dims = dims[1:]
    probabilities: list[float] = []
    fragment_states: dict[int, list[ComplexArray]] = {index: [] for index in fragment_indices}
    for outcome in range(dims[0]):
        clock_vector = clock_basis[:, outcome]
        rest_vector = clock_vector.conj() @ matrix
        probability = float(np.vdot(rest_vector, rest_vector).real)
        probabilities.append(probability)
        if probability <= 1e-15:
            normalized = rest_vector
        else:
            normalized = rest_vector / np.sqrt(probability)
        rest_rho = ket_to_density(normalized)
        for global_index in fragment_indices:
            if global_index == 0:
                raise ValueError("fragment index cannot be clock")
            rest_index = global_index - 1
            fragment_states[global_index].append(partial_trace(rest_rho, rest_dims, (rest_index,)))
    return np.asarray(probabilities, dtype=np.float64), fragment_states
