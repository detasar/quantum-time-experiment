from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.stats import beta

BitArray = NDArray[np.int8]


@dataclass(frozen=True)
class Interval:
    estimate: float
    lower: float
    upper: float


def spins(bits: NDArray[np.integer]) -> NDArray[np.int8]:
    values = np.asarray(bits, dtype=np.int8)
    if np.any((values != 0) & (values != 1)):
        raise ValueError("bits must be binary")
    return (1 - 2 * values).astype(np.int8)


def correlation(bits: NDArray[np.integer], columns: tuple[int, ...]) -> float:
    values = spins(bits[:, columns])
    products = np.prod(values, axis=1)
    return float(products.mean())


def clopper_pearson_expectation_interval(
    products: NDArray[np.integer], *, alpha: float = 0.05
) -> Interval:
    values = np.asarray(products, dtype=np.int8)
    if np.any((values != -1) & (values != 1)):
        raise ValueError("products must be +/-1")
    successes = int(np.sum(values == 1))
    n = int(values.size)
    p_hat = successes / n
    lower_p = 0.0 if successes == 0 else float(beta.ppf(alpha / 2, successes, n - successes + 1))
    upper_p = (
        1.0 if successes == n else float(beta.ppf(1 - alpha / 2, successes + 1, n - successes))
    )
    return Interval(estimate=2 * p_hat - 1, lower=2 * lower_p - 1, upper=2 * upper_p - 1)


def bootstrap_contrasts(
    z_counts: list[NDArray[np.integer]],
    x_counts: list[NDArray[np.integer]],
    plus_x_counts: list[NDArray[np.integer]],
    minus_x_counts: list[NDArray[np.integer]],
    *,
    replicates: int,
    seed: int,
) -> dict[str, NDArray[np.float64]]:
    rng = np.random.default_rng(seed)
    obj = np.empty(replicates, dtype=np.float64)
    coh = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        z = np.concatenate([block[rng.integers(0, len(block), len(block))] for block in z_counts])
        x = np.concatenate([block[rng.integers(0, len(block), len(block))] for block in x_counts])
        plus = np.concatenate(
            [block[rng.integers(0, len(block), len(block))] for block in plus_x_counts]
        )
        minus = np.concatenate(
            [block[rng.integers(0, len(block), len(block))] for block in minus_x_counts]
        )
        cz1 = correlation(z, (0, 2))
        cz2 = correlation(z, (0, 3))
        cx1 = correlation(x, (0, 2))
        cx2 = correlation(x, (0, 3))
        obj[replicate] = min(cz1, cz2) - max(abs(cx1), abs(cx2))
        w_plus = correlation(plus, (0, 1, 2, 3))
        w_minus = correlation(minus, (0, 1, 2, 3))
        w_mix = 0.5 * (w_plus + w_minus)
        coh[replicate] = abs(w_plus) - abs(w_mix)
    return {"delta_obj": obj, "delta_coh": coh}
