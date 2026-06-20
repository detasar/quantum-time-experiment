from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

ComplexArray = NDArray[np.complex128]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class ClockBasis:
    """Rank-1 projective clock basis, columns are basis vectors."""

    vectors: ComplexArray
    labels: tuple[str, ...]

    def __post_init__(self) -> None:
        vectors = np.asarray(self.vectors, dtype=np.complex128)
        if vectors.ndim != 2 or vectors.shape[0] != vectors.shape[1]:
            raise ValueError("ClockBasis.vectors must be a square matrix")
        if vectors.shape[1] != len(self.labels):
            raise ValueError("Number of labels must match basis dimension")
        gram = vectors.conj().T @ vectors
        if not np.allclose(gram, np.eye(vectors.shape[1]), atol=1e-10):
            raise ValueError("Clock basis vectors must be orthonormal")
        object.__setattr__(self, "vectors", vectors)

    @property
    def dimension(self) -> int:
        return int(self.vectors.shape[0])


@dataclass(frozen=True)
class PhysicalPartition:
    """Physical subsystem dimensions and names, with clock at index zero."""

    names: tuple[str, ...]
    dims: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.names) != len(self.dims):
            raise ValueError("names and dims must have equal length")
        if not self.names or self.names[0] != "C":
            raise ValueError("Clock subsystem C must be first")
        if any(dim < 2 for dim in self.dims):
            raise ValueError("All subsystem dimensions must be >=2")

    @property
    def total_dimension(self) -> int:
        return int(np.prod(self.dims))


@dataclass(frozen=True)
class RecordCode:
    """Binary persistent-record signatures for clock labels."""

    labels: tuple[str, ...]
    bits: BoolArray

    def __post_init__(self) -> None:
        bits = np.asarray(self.bits, dtype=np.bool_)
        if bits.ndim != 2:
            raise ValueError("bits must be a two-dimensional array")
        if bits.shape[0] != len(self.labels):
            raise ValueError("One record vector is required per label")
        if len(set(self.labels)) != len(self.labels):
            raise ValueError("Clock labels must be unique")
        object.__setattr__(self, "bits", bits)

    @property
    def n_states(self) -> int:
        return int(self.bits.shape[0])

    @property
    def n_records(self) -> int:
        return int(self.bits.shape[1])


@dataclass(frozen=True)
class OrderInferenceResult:
    quotient_labels: tuple[tuple[str, ...], ...]
    quotient_bits: BoolArray
    edges: tuple[tuple[int, int], ...]
    linear_extension_count: int
    maximal_chain_count: int
    automorphism_count: int
    is_total: bool
    has_duplicates: bool

    @property
    def scalar_time_identifiable(self) -> bool:
        """Whether distinct labels support one nondegenerate scalar trajectory."""

        return self.is_total and not self.has_duplicates


@dataclass(frozen=True)
class ExperimentManifest:
    experiment_id: str
    config_hash: str
    git_commit: str
    seed: int
    package_versions: dict[str, str]
    timestamp_utc: str
    outputs: tuple[str, ...]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class QuantumCircuitSpec:
    name: str
    basis: str
    phase: int
    shots: int
    logical_to_physical: tuple[int, ...] | None = None
    serialized_path: Path | None = None
