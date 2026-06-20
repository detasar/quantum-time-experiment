from __future__ import annotations

from functools import cache
from itertools import permutations, product
from math import factorial, prod

import networkx as nx
import numpy as np
from numpy.typing import NDArray

from .types import OrderInferenceResult, RecordCode

BoolArray = NDArray[np.bool_]


def thermometer_code(n_states: int) -> RecordCode:
    if n_states < 2:
        raise ValueError("n_states must be at least two")
    bits = np.zeros((n_states, n_states - 1), dtype=np.bool_)
    for t in range(n_states):
        bits[t, :t] = True
    return RecordCode(tuple(str(t) for t in range(n_states)), bits)


def dominance_matrix(bits: BoolArray) -> BoolArray:
    values = np.asarray(bits, dtype=np.bool_)
    return np.asarray(np.all((~values[:, None, :]) | values[None, :, :], axis=2), dtype=np.bool_)


def quotient_record_code(code: RecordCode) -> tuple[tuple[tuple[str, ...], ...], BoolArray]:
    groups: dict[tuple[bool, ...], list[str]] = {}
    for label, row in zip(code.labels, code.bits, strict=True):
        groups.setdefault(tuple(bool(x) for x in row), []).append(label)
    sorted_items = sorted(groups.items(), key=lambda item: (sum(item[0]), item[0]))
    labels = tuple(tuple(group) for _, group in sorted_items)
    bits = np.array([signature for signature, _ in sorted_items], dtype=np.bool_)
    return labels, bits


def poset_graph(bits: BoolArray, *, transitive_reduction: bool = True) -> nx.DiGraph:
    relation = dominance_matrix(bits)
    graph = nx.DiGraph()
    graph.add_nodes_from(range(bits.shape[0]))
    for i in range(bits.shape[0]):
        for j in range(bits.shape[0]):
            if i != j and relation[i, j] and not relation[j, i]:
                graph.add_edge(i, j)
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Quotient dominance relation must be acyclic")
    return nx.transitive_reduction(graph) if transitive_reduction else nx.transitive_closure(graph)


def is_persistent_order(code: RecordCode, order: tuple[int, ...]) -> bool:
    if sorted(order) != list(range(code.n_states)):
        raise ValueError("order must be a permutation of state indices")
    ordered = code.bits[np.array(order)]
    return bool(np.all(ordered[:-1].astype(int) <= ordered[1:].astype(int)))


def is_persistent_sequence(code: RecordCode, sequence: tuple[int, ...]) -> bool:
    if len(set(sequence)) != len(sequence):
        raise ValueError("sequence cannot repeat state indices")
    if any(index < 0 or index >= code.n_states for index in sequence):
        raise ValueError("sequence contains an unknown state index")
    if len(sequence) < 2:
        return True
    ordered = code.bits[np.array(sequence)]
    return bool(np.all(ordered[:-1].astype(int) <= ordered[1:].astype(int)))


def is_directed_chain_sequence(code: RecordCode, sequence: tuple[int, ...]) -> bool:
    if len(set(sequence)) != len(sequence):
        raise ValueError("sequence cannot repeat state indices")
    relation = dominance_matrix(code.bits)
    return all(
        bool(relation[before, after]) for before, after in zip(sequence, sequence[1:], strict=False)
    )


def scalar_timeline(code: RecordCode) -> tuple[str, ...] | None:
    result = infer_order(code)
    if not result.scalar_time_identifiable:
        return None
    graph = poset_graph(result.quotient_bits)
    extension = enumerate_linear_extensions(graph, limit=1)[0]
    return tuple(result.quotient_labels[index][0] for index in extension)


def enumerate_linear_extensions(
    graph: nx.DiGraph,
    *,
    limit: int | None = None,
) -> list[tuple[int, ...]]:
    results: list[tuple[int, ...]] = []
    for extension in nx.algorithms.dag.all_topological_sorts(graph):
        results.append(tuple(extension))
        if limit is not None and len(results) >= limit:
            break
    return results


def count_linear_extensions(graph: nx.DiGraph) -> int:
    nodes = tuple(sorted(graph.nodes()))
    n = len(nodes)
    if n > 22:
        raise ValueError("Exact DP is restricted to at most 22 nodes")
    index = {node: i for i, node in enumerate(nodes)}
    predecessor_masks = [0] * n
    for node in nodes:
        mask = 0
        for predecessor in nx.ancestors(graph, node):
            mask |= 1 << index[predecessor]
        predecessor_masks[index[node]] = mask

    @cache
    def dp(mask: int) -> int:
        if mask == (1 << n) - 1:
            return 1
        total = 0
        for i in range(n):
            if mask & (1 << i):
                continue
            if predecessor_masks[i] & ~mask == 0:
                total += dp(mask | (1 << i))
        return total

    return dp(0)


def enumerate_maximal_chains(graph: nx.DiGraph) -> list[tuple[int, ...]]:
    """Enumerate maximal chains in a Hasse DAG.

    A physical persistent-record trajectory is a chain, not an arbitrary linear extension.
    """
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("graph must be a DAG")
    minimal = [node for node in graph.nodes if graph.in_degree(node) == 0]
    maximal = [node for node in graph.nodes if graph.out_degree(node) == 0]
    chains: list[tuple[int, ...]] = []
    if graph.number_of_nodes() == 0:
        return chains
    for source in minimal:
        for target in maximal:
            if source == target:
                chains.append((source,))
            else:
                for path in nx.all_simple_paths(graph, source, target):
                    chains.append(tuple(path))
    # Remove duplicates while preserving deterministic order.
    return sorted(set(chains))


def count_maximal_chains(graph: nx.DiGraph) -> int:
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("graph must be a DAG")
    if graph.number_of_nodes() == 0:
        return 0
    minimal = [node for node in graph.nodes if graph.in_degree(node) == 0]
    path_counts = {node: 0 for node in graph.nodes}
    for node in minimal:
        path_counts[node] = 1
    for node in nx.topological_sort(graph):
        for successor in graph.successors(node):
            path_counts[successor] += path_counts[node]
    maximal = [node for node in graph.nodes if graph.out_degree(node) == 0]
    return int(sum(path_counts[node] for node in maximal))


def count_automorphisms(graph: nx.DiGraph) -> int:
    nodes = tuple(sorted(graph.nodes()))
    n = len(nodes)
    if n <= 1:
        return 1
    if graph.number_of_edges() == 0:
        return factorial(n)
    index = {node: i for i, node in enumerate(nodes)}
    adjacency = np.zeros((n, n), dtype=np.bool_)
    for source, target in graph.edges():
        adjacency[index[source], index[target]] = True
    closure = nx.transitive_closure(graph)
    colors: dict[tuple[int, int, int, int], list[int]] = {}
    for node in nodes:
        color = (
            graph.in_degree(node),
            graph.out_degree(node),
            len(nx.ancestors(closure, node)),
            len(nx.descendants(closure, node)),
        )
        colors.setdefault(color, []).append(index[node])
    groups = tuple(colors[key] for key in sorted(colors))
    if all(len(group) == 1 for group in groups):
        return 1

    group_permutations = [tuple(permutations(group)) for group in groups]
    total = 0
    for choices in product(*group_permutations):
        mapping = list(range(n))
        for group, permuted in zip(groups, choices, strict=True):
            for source, target in zip(group, permuted, strict=True):
                mapping[source] = target
        if np.array_equal(adjacency, adjacency[np.ix_(mapping, mapping)]):
            total += 1
    return total


def infer_order(code: RecordCode) -> OrderInferenceResult:
    quotient_labels, quotient_bits = quotient_record_code(code)
    graph = poset_graph(quotient_bits)
    closure = nx.transitive_closure(graph)
    n = len(quotient_labels)
    comparable_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            if closure.has_edge(i, j) or closure.has_edge(j, i):
                comparable_pairs += 1
    is_total = comparable_pairs == n * (n - 1) // 2
    return OrderInferenceResult(
        quotient_labels=quotient_labels,
        quotient_bits=quotient_bits,
        edges=tuple(sorted(graph.edges())),
        linear_extension_count=count_linear_extensions(graph),
        maximal_chain_count=count_maximal_chains(graph),
        automorphism_count=count_automorphisms(graph),
        is_total=is_total,
        has_duplicates=len(quotient_labels) != code.n_states,
    )


def brute_force_persistent_orders(code: RecordCode) -> list[tuple[int, ...]]:
    if code.n_states > 9:
        raise ValueError("Brute force restricted to n<=9")
    return [
        order for order in permutations(range(code.n_states)) if is_persistent_order(code, order)
    ]


def count_full_persistent_orders(code: RecordCode) -> int:
    result = infer_order(code)
    return count_full_persistent_orders_from_result(result)


def count_full_persistent_orders_from_result(result: OrderInferenceResult) -> int:
    if not result.is_total:
        return 0
    return int(prod(factorial(len(group)) for group in result.quotient_labels))


def binary_chain_capacity(n_records: int) -> int:
    if n_records < 0:
        raise ValueError("n_records must be nonnegative")
    return n_records + 1


def multilevel_chain_capacity(levels: tuple[int, ...]) -> int:
    if any(level < 1 for level in levels):
        raise ValueError("Each coordinate must have at least one level")
    return 1 + sum(level - 1 for level in levels)


def boolean_cube_longest_chain_length(n_records: int) -> int:
    if n_records < 0:
        raise ValueError("n_records must be nonnegative")
    return binary_chain_capacity(n_records)


def normalized_linear_ambiguity(result: OrderInferenceResult) -> float:
    n = len(result.quotient_labels)
    if n <= 1:
        return 0.0
    return float(np.log(result.linear_extension_count) / np.log(factorial(n)))
