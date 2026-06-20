from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .artifacts import (
    deterministic_tar_gz_bytes,
    file_manifest,
    freeze_manifest,
    git_commit,
    sha256_bytes,
    write_json_atomic,
)


@dataclass(frozen=True)
class FinalDecision:
    payload: dict[str, Any]
    markdown: str


def _read_json(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _read_claim_rows(root: Path) -> list[dict[str, str]]:
    path = root / "results" / "claim_evidence_matrix.csv"
    if not path.exists():
        raise FileNotFoundError(path.as_posix())
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _hardware_interpretation(raw: dict[str, Any], mitigated: dict[str, Any]) -> str:
    raw_pass = raw.get("passes_main_text_inclusion_without_mitigation") is True
    mitigation_agrees = mitigated.get("qualitative_agreement_with_raw") is True
    coherence_pass = (
        cast(dict[str, bool], raw.get("inclusion_checks", {})).get("delta_coh_lcb") is True
    )
    objectivity_pass = (
        cast(dict[str, bool], raw.get("inclusion_checks", {})).get("delta_obj_lcb") is True
        and cast(dict[str, bool], raw.get("inclusion_checks", {})).get("min_z_correlation_lcb")
        is True
    )
    if raw_pass and mitigation_agrees:
        return "bounded_quantum_illustration"
    if objectivity_pass and not coherence_pass:
        return "classical_record_illustration_only"
    if raw_pass and not mitigation_agrees:
        return "raw_positive_mitigation_disagreement_appendix_only"
    return "hardware_null_theory_independent"


def _artifact_route(*, theory_supported: bool, hardware_interpretation: str) -> str:
    if theory_supported and hardware_interpretation == "bounded_quantum_illustration":
        return "foundations_artifact_with_bounded_quantum_illustration"
    if theory_supported:
        return "theory_no_go_artifact_without_hardware_support"
    return "revise_or_pivot"


def build_final_decision(
    root: Path = Path("."),
    *,
    archive_manifest: dict[str, Any] | None = None,
) -> FinalDecision:
    a601 = _read_json(root, "results/processed/A601_claim_evidence_summary.json")
    raw = _read_json(root, "results/processed/Q3_hardware_raw.json")
    mitigated = _read_json(root, "results/processed/Q3_hardware_mitigated.json")
    claims = _read_claim_rows(root)
    unsupported_count = int(a601.get("unsupported_claim_count", -1))
    q_grade_count = int(a601.get("q_grade_claim_count", 0))
    theory_claims = [row for row in claims if not row["id"].startswith("Q")]
    theory_supported = unsupported_count == 0 and all(
        row["evidence_status"] != "unsupported" for row in theory_claims
    )
    hardware_status = _hardware_interpretation(raw, mitigated)
    artifact_route = _artifact_route(
        theory_supported=theory_supported,
        hardware_interpretation=hardware_status,
    )
    raw_metrics = cast(dict[str, float], raw["metrics"])
    raw_bootstrap = cast(dict[str, float], raw["bootstrap"])
    payload: dict[str, Any] = {
        "task": "A602",
        "status": "final_interpretation_frozen",
        "artifact_route": artifact_route,
        "theory_decision": "supported" if theory_supported else "modified_or_falsified",
        "hardware_interpretation": hardware_status,
        "preregistered_decision_rule": (
            "Objectivity plus coherence pass includes the bounded quantum illustration; "
            "hardware null cannot kill a valid theory result."
        ),
        "positive_interpretations": [
            "The basis-order-orientation separation is supported by proofs and exact checks.",
            "Record-capacity and no-go claims are supported independently of QPU data.",
            "The IBM result supports retaining the four-qubit GHZ illustration in this artifact.",
        ],
        "negative_interpretations": [
            "Do not claim fixed-partition basis uniqueness as the main novelty.",
            "Do not claim that the IBM hardware observation proves the theorem package.",
            "Do not infer temporal orientation from redundant records without an anchor.",
            "Do not use H503 mitigation to replace or rescue the raw H502 result.",
        ],
        "key_evidence": {
            "unsupported_claim_count": unsupported_count,
            "q_grade_claim_count": q_grade_count,
            "raw_delta_obj_lcb": raw_bootstrap["delta_obj_lcb"],
            "raw_min_z_correlation_lcb": raw_metrics["min_z_correlation_lcb"],
            "raw_delta_coh_lcb": raw_bootstrap["delta_coh_lcb"],
            "raw_primary_pass": raw["passes_main_text_inclusion_without_mitigation"],
            "mitigation_agrees": mitigated["qualitative_agreement_with_raw"],
        },
        "evidence_artifacts": [
            "results/claim_evidence_matrix.csv",
            "results/processed/A601_claim_evidence_summary.json",
            "results/processed/Q3_hardware_raw.json",
            "results/processed/Q3_hardware_mitigated.json",
            "docs/CLAIMS_REGISTER.md",
            "docs/G5_HARDWARE_NOTES.md",
        ],
        "archive": archive_manifest,
        "environment": freeze_manifest(),
        "secret_values_recorded": False,
    }
    return FinalDecision(payload=payload, markdown=render_final_decision_markdown(payload))


def render_final_decision_markdown(payload: dict[str, Any]) -> str:
    evidence = cast(dict[str, Any], payload["key_evidence"])
    archive = cast(dict[str, Any] | None, payload.get("archive"))
    archive_section = (
        "\n".join(
            [
                "## Reproducibility Archive",
                "",
                f"- Archive path: `{archive['archive_path']}`",
                f"- Archive SHA-256: `{archive['archive_sha256']}`",
                f"- Archived file count: `{archive['archived_file_count']}`",
                f"- Clean reproduction command: `{archive['reproduction']['command']}`",
                f"- Clean reproduction passed: `{archive['reproduction']['passed']}`",
                "",
            ]
        )
        if archive
        else "## Reproducibility Archive\n\nPending A603.\n"
    )
    positives = "\n".join(f"- {item}" for item in payload["positive_interpretations"])
    negatives = "\n".join(f"- {item}" for item in payload["negative_interpretations"])
    return f"""# Final Scientific Decision

Status: `FROZEN`

## Decision

- Artifact route: `{payload["artifact_route"]}`
- Theory decision: `{payload["theory_decision"]}`
- Hardware interpretation: `{payload["hardware_interpretation"]}`

The decision follows the preregistered rule: objectivity plus coherence pass
allows the IBM run to remain as a bounded quantum illustration, while a
hardware null result cannot invalidate the independently supported theory
package.

## Evidence

| Check | Value |
|---|---:|
| Unsupported claim count | {evidence["unsupported_claim_count"]} |
| Q-grade claim count | {evidence["q_grade_claim_count"]} |
| Raw objectivity LCB | {evidence["raw_delta_obj_lcb"]} |
| Raw minimum Z-correlation LCB | {evidence["raw_min_z_correlation_lcb"]} |
| Raw coherence LCB | {evidence["raw_delta_coh_lcb"]} |
| Raw primary pass | {evidence["raw_primary_pass"]} |
| H503 agrees with raw | {evidence["mitigation_agrees"]} |

## Positive Interpretations

{positives}

## Negative Interpretations

{negatives}

{archive_section}
## Scope Boundary

The artifact should be presented as a theory/no-go and reproducibility package
with a bounded IBM illustration. It should not present basis uniqueness as new,
and it should not let the quantum hardware result carry the theorem-level
contribution.
"""


def validate_final_decision(payload: dict[str, Any]) -> None:
    if payload["status"] != "final_interpretation_frozen":
        raise ValueError("Final decision must be frozen")
    if payload["theory_decision"] != "supported":
        raise ValueError("Theory package is not supported")
    if payload["artifact_route"] not in {
        "foundations_artifact_with_bounded_quantum_illustration",
        "theory_no_go_artifact_without_hardware_support",
        "revise_or_pivot",
    }:
        raise ValueError(f"Unexpected artifact route: {payload['artifact_route']}")
    evidence = cast(dict[str, Any], payload["key_evidence"])
    if int(evidence["unsupported_claim_count"]) != 0:
        raise ValueError("Unsupported claims remain")
    if payload["hardware_interpretation"] == "bounded_quantum_illustration":
        if evidence["raw_primary_pass"] is not True or evidence["mitigation_agrees"] is not True:
            raise ValueError("Bounded quantum illustration requires raw pass and H503 agreement")


def compact_archive_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    reproduction = cast(dict[str, Any], manifest["reproduction"])
    return {
        "task": manifest["task"],
        "status": manifest["status"],
        "source_git_commit": manifest["source_git_commit"],
        "archive_path": manifest["archive_path"],
        "archive_sha256": manifest["archive_sha256"],
        "archived_file_count": manifest["archived_file_count"],
        "reproduction": {
            "command": reproduction["command"],
            "passed": reproduction["passed"],
            "return_code": reproduction["return_code"],
        },
        "secret_values_recorded": manifest["secret_values_recorded"],
    }


def write_final_decision(
    *,
    root: Path = Path("."),
    archive_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    decision = build_final_decision(root, archive_manifest=archive_manifest)
    validate_final_decision(decision.payload)
    write_json_atomic(root / "results/processed/A602_final_decision.json", decision.payload)
    (root / "docs/FINAL_DECISION.md").write_text(decision.markdown, encoding="utf-8")
    return decision.payload


def _git_status_clean(root: Path) -> bool:
    output = subprocess.check_output(["git", "status", "--short"], cwd=root, text=True)
    return output.strip() == ""


def _tracked_files(root: Path) -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "-z"],
            cwd=root,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return _source_archive_files(root)
    tracked = [Path(item.decode("utf-8")) for item in output.split(b"\0") if item]
    return tracked if tracked else _source_archive_files(root)


def _source_archive_files(root: Path) -> list[Path]:
    excluded_parts = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
    }
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in excluded_parts for part in relative.parts):
            continue
        if path.suffix == ".pyc":
            continue
        paths.append(relative)
    return sorted(paths, key=lambda item: item.as_posix())


def reproducibility_archive_paths(root: Path = Path(".")) -> list[Path]:
    excluded_prefixes = (
        ".git/",
        ".mypy_cache/",
        ".pytest_cache/",
        ".ruff_cache/",
        ".venv/",
    )
    excluded_paths = {
        "docs/FINAL_DECISION.md",
        "objective-clocks-reproducibility.tar.gz",
        "results/processed/A603_reproducibility_manifest.json",
    }
    paths: list[Path] = []
    for relative in _tracked_files(root):
        text = relative.as_posix()
        if text in excluded_paths or any(text.startswith(prefix) for prefix in excluded_prefixes):
            continue
        if (root / relative).is_file():
            paths.append(relative)
    return sorted(paths, key=lambda item: item.as_posix())


def _run_clean_reproduction(root: Path) -> dict[str, Any]:
    command = [sys.executable, "scripts/reproduce_all.py"]
    branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=root,
        text=True,
    ).strip()
    with tempfile.TemporaryDirectory(prefix="objective-clocks-repro-parent-") as temp:
        temp_path = Path(temp) / "repo"
        subprocess.run(
            [
                "git",
                "clone",
                "--local",
                "--branch",
                branch,
                root.resolve().as_posix(),
                temp_path.as_posix(),
            ],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            env = os.environ.copy()
            env.pop("ALLOW_QPU_EXECUTION", None)
            env["PYTHONPATH"] = (temp_path / "src").as_posix()
            completed = subprocess.run(
                command,
                cwd=temp_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            return {
                "command": " ".join(command),
                "passed": completed.returncode == 0,
                "return_code": completed.returncode,
                "stdout_tail": completed.stdout.splitlines()[-40:],
            }
        finally:
            shutil.rmtree(temp_path, ignore_errors=True)


def write_reproducibility_package(
    *,
    root: Path = Path("."),
    archive_path: Path = Path("objective-clocks-reproducibility.tar.gz"),
    manifest_path: Path = Path("results/processed/A603_reproducibility_manifest.json"),
) -> dict[str, Any]:
    if not _git_status_clean(root):
        raise RuntimeError("A603 requires a clean repository before archive generation")
    reproduction = _run_clean_reproduction(root)
    if reproduction["passed"] is not True:
        raise RuntimeError("Clean reproduction failed")
    paths = reproducibility_archive_paths(root)
    payload = deterministic_tar_gz_bytes(paths, root=root)
    archive = root / archive_path
    archive.write_bytes(payload)
    manifest = {
        "task": "A603",
        "status": "complete",
        "source_git_commit": git_commit(),
        "archive_path": archive_path.as_posix(),
        "archive_sha256": sha256_bytes(payload),
        "archived_file_count": len(paths),
        "archived_files": file_manifest(paths, root=root),
        "excluded_paths": [
            "docs/FINAL_DECISION.md",
            "objective-clocks-reproducibility.tar.gz",
            "results/processed/A603_reproducibility_manifest.json",
        ],
        "reproduction": reproduction,
        "environment": freeze_manifest(),
        "secret_values_recorded": False,
    }
    write_json_atomic(root / manifest_path, manifest)
    write_final_decision(root=root, archive_manifest=compact_archive_manifest(manifest))
    return manifest
