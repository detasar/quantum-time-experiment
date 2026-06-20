from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

ComplexArray = NDArray[np.complex128]
FloatArray = NDArray[np.float64]


def _normalize_probs(values: FloatArray, *, atol: float = 1e-12) -> FloatArray:
    probs = np.asarray(values, dtype=np.float64)
    if np.any(probs < -atol):
        raise ValueError("Probabilities contain negative values")
    probs = np.clip(probs, 0.0, None)
    total = float(probs.sum())
    if total <= atol:
        raise ValueError("Probability mass is zero")
    return probs / total


def shannon_entropy(probs: FloatArray, *, base: float = 2.0) -> float:
    p = _normalize_probs(probs)
    positive = p[p > 0]
    return float(-np.sum(positive * np.log(positive) / np.log(base)))


def von_neumann_entropy(rho: ComplexArray, *, base: float = 2.0) -> float:
    matrix = np.asarray(rho, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("rho must be square")
    hermitian = (matrix + matrix.conj().T) / 2
    eigenvalues = np.linalg.eigvalsh(hermitian).real
    eigenvalues = np.clip(eigenvalues, 0.0, None)
    if eigenvalues.sum() == 0:
        raise ValueError("rho has zero trace")
    return shannon_entropy(eigenvalues, base=base)


def classical_mutual_information(joint: FloatArray, *, base: float = 2.0) -> float:
    pxy = _normalize_probs(np.asarray(joint, dtype=np.float64).ravel()).reshape(joint.shape)
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    expected = px @ py
    mask = pxy > 0
    return float(np.sum(pxy[mask] * np.log(pxy[mask] / expected[mask]) / np.log(base)))


def partial_trace(rho: ComplexArray, dims: tuple[int, ...], keep: tuple[int, ...]) -> ComplexArray:
    """Trace out all subsystems not listed in keep.

    Subsystem ordering follows dims. The output order follows sorted keep.
    """

    matrix = np.asarray(rho, dtype=np.complex128)
    total = int(np.prod(dims))
    if matrix.shape != (total, total):
        raise ValueError("rho shape does not match dims")
    keep_sorted = tuple(sorted(keep))
    if len(set(keep_sorted)) != len(keep_sorted):
        raise ValueError("keep contains duplicates")
    if any(index < 0 or index >= len(dims) for index in keep_sorted):
        raise ValueError("keep index out of range")

    tensor = matrix.reshape(*dims, *dims)
    trace_out = [index for index in range(len(dims)) if index not in keep_sorted]
    current_dims = list(dims)
    for index in sorted(trace_out, reverse=True):
        tensor = np.trace(tensor, axis1=index, axis2=index + len(current_dims))
        current_dims.pop(index)
    out_dim = int(np.prod([dims[index] for index in keep_sorted]))
    return np.asarray(tensor, dtype=np.complex128).reshape(out_dim, out_dim)


def holevo_information(probs: FloatArray, states: list[ComplexArray]) -> float:
    p = _normalize_probs(probs)
    if len(states) != len(p):
        raise ValueError("states and probabilities must have equal length")
    average = np.zeros_like(states[0], dtype=np.complex128)
    for weight, state in zip(p, states, strict=True):
        average = average + float(weight) * state
    conditional = sum(
        float(weight) * von_neumann_entropy(state) for weight, state in zip(p, states, strict=True)
    )
    return von_neumann_entropy(average) - conditional


def trace_distance(rho: ComplexArray, sigma: ComplexArray) -> float:
    delta = np.asarray(rho, dtype=np.complex128) - np.asarray(sigma, dtype=np.complex128)
    singular_values = np.linalg.svd(delta, compute_uv=False)
    return float(0.5 * singular_values.sum())


def helstrom_binary_error(p0: float, rho0: ComplexArray, p1: float, rho1: ComplexArray) -> float:
    if not np.isclose(p0 + p1, 1.0):
        raise ValueError("p0 and p1 must sum to one")
    delta = p0 * rho0 - p1 * rho1
    singular_values = np.linalg.svd(delta, compute_uv=False)
    return float(0.5 * (1.0 - singular_values.sum()))
