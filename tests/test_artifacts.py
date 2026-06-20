from __future__ import annotations

import json
from pathlib import Path

import pytest

from objective_clocks.artifacts import (
    config_hash,
    file_manifest,
    write_json_atomic,
    write_raw_json_once,
    write_sha256_manifest,
)


def test_config_hash_is_canonical() -> None:
    first = {"seed": 20260620, "grid": {"q": [1, 3], "p": [0.1, 0.2]}}
    second = {"grid": {"p": [0.1, 0.2], "q": [1, 3]}, "seed": 20260620}

    assert config_hash(first) == config_hash(second)


def test_atomic_json_write_replaces_complete_payload(tmp_path: Path) -> None:
    target = tmp_path / "processed" / "result.json"

    write_json_atomic(target, {"status": "first"})
    write_json_atomic(target, {"status": "second", "values": [1, 2, 3]})

    assert json.loads(target.read_text(encoding="utf-8")) == {
        "status": "second",
        "values": [1, 2, 3],
    }
    assert not target.with_suffix(".json.tmp").exists()


def test_raw_json_write_once_rejects_overwrite(tmp_path: Path) -> None:
    raw_root = tmp_path / "results" / "raw"
    target = raw_root / "provider_payload.json"

    write_raw_json_once(target, {"job": "first"}, raw_root=raw_root)

    with pytest.raises(FileExistsError):
        write_raw_json_once(target, {"job": "second"}, raw_root=raw_root)


def test_raw_json_write_once_rejects_paths_outside_raw_root(tmp_path: Path) -> None:
    raw_root = tmp_path / "results" / "raw"

    with pytest.raises(ValueError, match="results/raw"):
        write_raw_json_once(tmp_path / "outside.json", {}, raw_root=raw_root)


def test_file_manifest_records_relative_paths_and_hashes(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    first = root / "a.json"
    second = root / "nested" / "b.txt"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_text('{"a":1}', encoding="utf-8")
    second.write_text("payload", encoding="utf-8")

    manifest = file_manifest([second, first], root=root)

    assert [entry["path"] for entry in manifest] == ["a.json", "nested/b.txt"]
    assert all(len(entry["sha256"]) == 64 for entry in manifest)
    assert [entry["size_bytes"] for entry in manifest] == [7, 7]


def test_write_sha256_manifest(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    payload = root / "result.json"
    payload.parent.mkdir(parents=True)
    payload.write_text("{}", encoding="utf-8")
    target = root / "manifest.json"

    write_sha256_manifest(target, [payload], root=root)

    manifest = json.loads(target.read_text(encoding="utf-8"))
    assert manifest["algorithm"] == "sha256"
    assert manifest["files"][0]["path"] == "result.json"
