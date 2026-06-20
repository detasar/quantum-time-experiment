from __future__ import annotations

from typing import Any

import numpy as np

from objective_clocks.hardware import (
    analyze_hardware_raw_payload,
    analyze_readout_mitigated_payload,
    sampler_result_counts,
)


def _key(bits: tuple[int, int, int, int]) -> str:
    return "".join(str(bits[index]) for index in reversed(range(4)))


def _uniform_parity_counts(*, parity: int, shots: int = 1024) -> dict[str, int]:
    states = [
        bits
        for index in range(16)
        if sum(bits := tuple((index >> bit) & 1 for bit in range(4))) % 2 == parity
    ]
    per_state = shots // len(states)
    return {_key(bits): per_state for bits in states}


def _ideal_science_counts(name: str) -> dict[str, int]:
    if name.endswith("_z"):
        return {_key((0, 0, 0, 0)): 512, _key((1, 1, 1, 1)): 512}
    if name == "ghz_plus_x":
        return _uniform_parity_counts(parity=0)
    if name == "ghz_minus_x":
        return _uniform_parity_counts(parity=1)
    raise ValueError(name)


def _fixture_payload() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for qubit in range(4):
        for prepared in (0, 1):
            bits = [0, 0, 0, 0]
            bits[qubit] = prepared
            rows.append(
                {
                    "qpy_index": len(rows),
                    "instance_id": f"ro_q{qubit}_{prepared}",
                    "prototype_name": f"ro_q{qubit}_{prepared}",
                    "role": "readout_calibration",
                    "block": None,
                    "shots": 1024,
                    "count_total": 1024,
                    "counts": {_key(tuple(bits)): 1024},
                }
            )
    for block in range(4):
        for name in ("ghz_plus_z", "ghz_plus_x", "ghz_minus_z", "ghz_minus_x"):
            rows.append(
                {
                    "qpy_index": len(rows),
                    "instance_id": f"{name}__block_{block}",
                    "prototype_name": name,
                    "role": "science",
                    "block": block,
                    "shots": 1024,
                    "count_total": 1024,
                    "counts": _ideal_science_counts(name),
                }
            )
    return {
        "task": "H501_provider_payload",
        "backend": "fixture_backend",
        "job": {"job_id": "fixture-job"},
        "counts": rows,
    }


def test_sampler_result_counts_extracts_single_classical_register() -> None:
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler

    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.measure(range(2), range(2))
    result = StatevectorSampler().run([circuit], shots=8).result()
    rows = sampler_result_counts(
        result,
        [
            {
                "instance_id": "fixture",
                "prototype_name": "fixture",
                "role": "science",
                "block": 0,
                "shots": 8,
            }
        ],
    )

    assert rows[0]["count_total"] == 8
    assert rows[0]["counts"] == {"01": 8}


def test_hardware_raw_and_mitigated_fixture_passes() -> None:
    payload = _fixture_payload()
    thresholds = {
        "delta_obj_lcb": 0.40,
        "min_z_correlation_lcb": 0.60,
        "delta_coh_lcb": 0.30,
    }

    raw = analyze_hardware_raw_payload(
        payload,
        alpha=0.05,
        bootstrap_replicates=200,
        bootstrap_seed=20260621,
        thresholds=thresholds,
    )
    mitigated = analyze_readout_mitigated_payload(payload, raw, thresholds=thresholds)

    assert raw["passes_main_text_inclusion_without_mitigation"] is True
    assert raw["inclusion_checks"]["ghz_minus_xxxx_negative"] is True
    assert raw["block_dominance"]["delta_obj_max_abs_share"] == 0.25
    assert mitigated["corrected_point_threshold_pass"] is True
    assert mitigated["qualitative_agreement_with_raw"] is True
    assert np.isclose(mitigated["metrics"]["w_minus_xxxx"], -1.0)
