from __future__ import annotations

from itertools import permutations

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linear_sum_assignment

from .information import holevo_information, shannon_entropy
from .states import conditional_fragment_states_from_pure

ComplexArray = NDArray[np.complex128]


def qubit_basis(theta: float, phi: float) -> ComplexArray:
    return np.array(
        [
            [np.cos(theta / 2), -np.exp(-1j * phi) * np.sin(theta / 2)],
            [np.exp(1j * phi) * np.sin(theta / 2), np.cos(theta / 2)],
        ],
        dtype=np.complex128,
    )


def basis_distance(first: ComplexArray, second: ComplexArray) -> float:
    first = np.asarray(first, dtype=np.complex128)
    second = np.asarray(second, dtype=np.complex128)
    if first.shape != second.shape or first.ndim != 2 or first.shape[0] != first.shape[1]:
        raise ValueError("Both bases must have equal square shape")
    overlaps = np.abs(first.conj().T @ second) ** 2
    rows, cols = linear_sum_assignment(-overlaps)
    return float(1.0 - overlaps[rows, cols].mean())


def objective_scores_pure(
    ket: ComplexArray,
    dims: tuple[int, ...],
    clock_basis: ComplexArray,
    fragment_indices: tuple[int, ...],
) -> dict[int, float]:
    probs, fragment_states = conditional_fragment_states_from_pure(
        ket, dims, clock_basis, fragment_indices
    )
    h_clock = shannon_entropy(probs)
    if h_clock <= 1e-15:
        return {index: 0.0 for index in fragment_indices}
    return {
        index: float(holevo_information(probs, states) / h_clock)
        for index, states in fragment_states.items()
    }


def minimum_objectivity_score(
    ket: ComplexArray,
    dims: tuple[int, ...],
    clock_basis: ComplexArray,
    fragment_indices: tuple[int, ...],
) -> float:
    scores = objective_scores_pure(ket, dims, clock_basis, fragment_indices)
    return min(scores.values()) if scores else 0.0


def permutation_orbit_bases(dimension: int) -> list[ComplexArray]:
    identity = np.eye(dimension, dtype=np.complex128)
    return [identity[:, permutation] for permutation in permutations(range(dimension))]
