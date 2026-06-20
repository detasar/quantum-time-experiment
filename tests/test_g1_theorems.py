from __future__ import annotations

from itertools import combinations, permutations, product

import numpy as np

from objective_clocks.noise import exact_majority_error, hoeffding_majority_bound
from objective_clocks.order import (
    binary_chain_capacity,
    brute_force_persistent_orders,
    infer_order,
    is_directed_chain_sequence,
    is_persistent_sequence,
    multilevel_chain_capacity,
    scalar_timeline,
    thermometer_code,
)
from objective_clocks.types import RecordCode


def _small_distinct_codes(max_records: int = 3) -> list[RecordCode]:
    codes: list[RecordCode] = []
    for n_records in range(1, max_records + 1):
        signatures = list(product((False, True), repeat=n_records))
        for size in range(1, min(7, len(signatures)) + 1):
            for subset in combinations(signatures, size):
                codes.append(
                    RecordCode(
                        labels=tuple(str(index) for index in range(size)),
                        bits=np.asarray(subset, dtype=bool),
                    )
                )
    return codes


def test_o1_persistent_sequences_are_exactly_directed_chains_small_exhaustive() -> None:
    mismatches: list[tuple[int, tuple[int, ...]]] = []
    for code_index, code in enumerate(_small_distinct_codes()):
        for length in range(1, code.n_states + 1):
            for sequence in permutations(range(code.n_states), length):
                if is_persistent_sequence(code, sequence) != is_directed_chain_sequence(
                    code, sequence
                ):
                    mismatches.append((code_index, sequence))

    assert mismatches == []


def test_t102_scalar_timeline_only_for_total_nondegenerate_codes() -> None:
    total = thermometer_code(4)
    branching = RecordCode(
        labels=("A", "B", "C", "D"),
        bits=np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=bool),
    )
    duplicate = RecordCode(
        labels=("A", "B", "C"),
        bits=np.array([[0, 0], [0, 0], [1, 0]], dtype=bool),
    )
    disconnected = RecordCode(
        labels=("A", "B"),
        bits=np.array([[1, 0], [0, 1]], dtype=bool),
    )

    assert scalar_timeline(total) == ("0", "1", "2", "3")
    assert scalar_timeline(branching) is None
    assert scalar_timeline(duplicate) is None
    assert scalar_timeline(disconnected) is None


def test_t103_boolean_capacity_exhaustive_to_eight_records() -> None:
    for n_records in range(0, 9):
        assert binary_chain_capacity(n_records) == n_records + 1
        if n_records == 0:
            continue
        assert thermometer_code(n_records + 1).n_records == n_records
        tight_code = thermometer_code(n_records + 1)
        assert len(brute_force_persistent_orders(tight_code)) == 1


def test_t103_multilevel_capacity_formula() -> None:
    assert multilevel_chain_capacity((2, 2, 2)) == 4
    assert multilevel_chain_capacity((3, 4)) == 6
    assert multilevel_chain_capacity((1, 5, 2)) == 6


def test_t104_majority_error_monotonicity_grid() -> None:
    for p in (0.01, 0.05, 0.1, 0.2, 0.3):
        errors = [exact_majority_error(q, p) for q in (1, 3, 5, 7, 9)]
        assert errors == sorted(errors, reverse=True)
        for q, error in zip((1, 3, 5, 7, 9), errors, strict=True):
            assert error <= hoeffding_majority_bound(q, p) + 1e-12


def test_t106_failed_assumption_maps_to_failed_conclusion() -> None:
    branching = RecordCode(
        labels=("00", "10", "01", "11"),
        bits=np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=bool),
    )
    result = infer_order(branching)

    assert not result.is_total
    assert result.linear_extension_count == 2
    assert result.maximal_chain_count == 2
    assert not result.scalar_time_identifiable
