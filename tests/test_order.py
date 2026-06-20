from itertools import permutations

import numpy as np

from objective_clocks.order import (
    binary_chain_capacity,
    brute_force_persistent_orders,
    count_automorphisms,
    count_maximal_chains,
    enumerate_maximal_chains,
    infer_order,
    is_persistent_order,
    poset_graph,
    thermometer_code,
)
from objective_clocks.types import RecordCode


def test_thermometer_unique_order() -> None:
    code = thermometer_code(5)
    result = infer_order(code)
    assert result.is_total
    assert result.linear_extension_count == 1
    assert result.automorphism_count == 1
    assert is_persistent_order(code, tuple(range(5)))


def test_diamond_has_two_linear_extensions() -> None:
    # 00 < 10, 01 < 11 with 10 and 01 incomparable.
    code = RecordCode(
        labels=("A", "B", "C", "D"),
        bits=np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=bool),
    )
    result = infer_order(code)
    assert not result.is_total
    assert result.linear_extension_count == 2  # arbitrary scheduler totalizations
    assert result.maximal_chain_count == 2  # physically persistent branches
    assert result.automorphism_count == 2
    persistent = brute_force_persistent_orders(code)
    assert len(persistent) == 0  # no scalar timeline can visit both incomparable snapshots
    graph = poset_graph(result.quotient_bits)
    assert count_maximal_chains(graph) == len(enumerate_maximal_chains(graph))


def test_antichain_automorphism_count_is_factorial() -> None:
    code = RecordCode(
        labels=("A", "B", "C"),
        bits=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=bool),
    )
    graph = poset_graph(code.bits)
    assert count_automorphisms(graph) == 6


def test_duplicate_signatures_are_quotiented() -> None:
    code = RecordCode(
        labels=("A", "B", "C"),
        bits=np.array([[0, 0], [0, 0], [1, 0]], dtype=bool),
    )
    result = infer_order(code)
    assert result.has_duplicates
    assert len(result.quotient_labels) == 2


def test_binary_capacity_small() -> None:
    assert binary_chain_capacity(0) == 1
    assert binary_chain_capacity(1) == 2
    assert binary_chain_capacity(4) == 5


def test_persistent_orders_equal_expected_for_thermometer() -> None:
    code = thermometer_code(4)
    candidates = [p for p in permutations(range(4)) if is_persistent_order(code, p)]
    assert candidates == [(0, 1, 2, 3)]
