from __future__ import annotations

from objective_clocks.isa import build_execution_order


def _config() -> dict[str, object]:
    return {
        "science": {
            "blocks": 4,
            "shots_per_block": 1024,
            "circuits": ["ghz_plus_z", "ghz_plus_x", "ghz_minus_z", "ghz_minus_x"],
        },
        "readout_calibration": {"shots_per_circuit": 1024},
        "statistics": {"bootstrap_seed": 20260621},
    }


def test_h402_execution_order_is_deterministic_and_complete() -> None:
    first = build_execution_order(_config())
    second = build_execution_order(_config())

    assert first == second
    assert len(first) == 24
    assert sum(item.shots for item in first) == 24_576
    assert sum(item.role == "science" for item in first) == 16
    assert sum(item.role == "readout_calibration" for item in first) == 8
    assert len({item.instance_id for item in first}) == 24
