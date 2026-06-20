from __future__ import annotations

from math import comb, exp

import numpy as np
from numpy.typing import NDArray

BoolArray = NDArray[np.bool_]


def majority_decode(observations: BoolArray) -> BoolArray:
    values = np.asarray(observations, dtype=np.bool_)
    if values.shape[-1] % 2 == 0:
        raise ValueError("Majority decoder requires odd number of copies")
    return np.asarray(values.sum(axis=-1) > values.shape[-1] // 2, dtype=np.bool_)


def exact_majority_error(q: int, p: float) -> float:
    if q <= 0 or q % 2 == 0:
        raise ValueError("q must be positive and odd")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0,1]")
    threshold = q // 2 + 1
    return float(sum(comb(q, k) * p**k * (1 - p) ** (q - k) for k in range(threshold, q + 1)))


def hoeffding_majority_bound(q: int, p: float) -> float:
    if q <= 0:
        raise ValueError("q must be positive")
    if not 0.0 <= p < 0.5:
        raise ValueError("Hoeffding majority bound requires p in [0,0.5)")
    return float(exp(-2.0 * q * (0.5 - p) ** 2))


def simulate_redundant_records(
    truth: BoolArray,
    *,
    q: int,
    p: float,
    trials: int,
    seed: int,
) -> BoolArray:
    if q % 2 == 0:
        raise ValueError("q must be odd")
    rng = np.random.default_rng(seed)
    truth_values = np.asarray(truth, dtype=np.bool_)
    expanded = np.broadcast_to(
        truth_values[None, ..., None],
        (trials, *truth_values.shape, q),
    ).copy()
    flips = rng.random(expanded.shape) < p
    observations = np.logical_xor(expanded, flips)
    return majority_decode(observations)
