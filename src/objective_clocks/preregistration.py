# ruff: noqa: E501

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .artifacts import freeze_manifest, sha256_file


@dataclass(frozen=True)
class PreregistrationDraft:
    markdown: str
    summary: dict[str, Any]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _required(value: Any, fallback: str = "TBD_BLOCKED") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def build_h401_preregistration_draft(root: Path = Path(".")) -> PreregistrationDraft:
    processed = root / "results" / "processed"
    q301 = _read_json(processed / "Q301_circuit_manifest.json")
    q303 = _read_json(processed / "Q303_backend_candidates.json")
    q304 = _read_json(processed / "Q2_backend_twin_summary.json")
    g4 = _read_json(processed / "G4_readiness_audit.json")
    preregistered = root / "results" / "preregistered"
    archive_manifest = _read_json(preregistered / "environment_archive_manifest.json")
    h402_manifest = _read_json(preregistered / "circuit_manifest.json")

    current_environment = freeze_manifest()
    packages = cast(dict[str, str], current_environment.get("packages", {}))
    selected_backend = cast(dict[str, Any], q303.get("selected_backend") or {})
    provider_metadata = cast(dict[str, Any], q303.get("provider_metadata", {}))
    backend_amendment = cast(dict[str, Any] | None, q303.get("backend_amendment"))
    runtime_account = cast(dict[str, Any], provider_metadata.get("runtime_account", {}))
    provider_source = str(q303.get("candidate_source", "missing"))
    provider_backed = provider_source == "provider"
    calibration_timestamp = selected_backend.get("calibration_timestamp") or q304.get(
        "calibration_timestamp"
    )
    environment_archive_sha = archive_manifest.get("archive_sha256")
    selected_transpiler_seed = h402_manifest.get("selected_transpiler_seed")
    h402_manifest_path = preregistered / "circuit_manifest.json"
    open_instance_confirmed = (
        runtime_account.get("instance_name") == "open-instance"
        and runtime_account.get("plan") == "open"
        and runtime_account.get("pricing_type") == "free"
    )

    unresolved = [
        {
            "field": "environment_archive_sha256",
            "reason": "environment archive is not frozen yet",
            "blocking_tasks": ["H401", "H404"],
        },
        {
            "field": "open_plan_instance_identifier",
            "reason": "Open Plan instance must be confirmed before freeze",
            "blocking_tasks": ["H401", "H403"],
        },
        {
            "field": "selected_backend",
            "reason": f"current backend source is {provider_source}, not provider",
            "blocking_tasks": ["Q303", "H401", "H402"],
        },
        {
            "field": "backend_calibration_snapshot_timestamp",
            "reason": "real provider calibration snapshot is unavailable",
            "blocking_tasks": ["Q303", "Q304", "H401", "H402"],
        },
        {
            "field": "selected_transpiler_seed",
            "reason": "ISA transpilation is not frozen yet",
            "blocking_tasks": ["H402"],
        },
        {
            "field": "human_approval",
            "reason": "explicit human approval is not recorded",
            "blocking_tasks": ["H401"],
        },
    ]
    if provider_backed:
        unresolved = [item for item in unresolved if item["field"] != "selected_backend"]
    if calibration_timestamp:
        unresolved = [
            item for item in unresolved if item["field"] != "backend_calibration_snapshot_timestamp"
        ]
    if open_instance_confirmed:
        unresolved = [
            item for item in unresolved if item["field"] != "open_plan_instance_identifier"
        ]
    if environment_archive_sha:
        unresolved = [item for item in unresolved if item["field"] != "environment_archive_sha256"]
    if selected_transpiler_seed is not None:
        unresolved = [item for item in unresolved if item["field"] != "selected_transpiler_seed"]
    mandatory_fields_complete = not any(item["field"] != "human_approval" for item in unresolved)

    circuit_manifest = root / "results" / "processed" / "Q301_circuit_manifest.json"
    environment_manifest = root / "results" / "processed" / "G0_environment_manifest.json"
    selected_circuit_manifest = (
        h402_manifest_path if h402_manifest_path.exists() else circuit_manifest
    )
    logical_qubits = cast(dict[str, int], q301.get("logical_qubits", {}))
    science_circuits = cast(list[dict[str, Any]], q301.get("science_circuits", []))

    markdown = (
        f"""# Preregistration Draft Packet - IBM Four-Qubit Illustration

**Status:** DRAFT - QPU execution prohibited
**Generated from:** `scripts/run_h401_draft.py`
**Project:** Objective Clock Bases from Redundant Records
**Primary scientific role:** illustration of objective local basis versus global coherence; not a proof of the theory.

## 1. Mandatory Identifiers

- Git commit: `{_required(current_environment.get("git_commit"))}`
- Environment manifest SHA-256: `{sha256_file(environment_manifest) if environment_manifest.exists() else "TBD_BLOCKED"}`
- Environment archive SHA-256: `{environment_archive_sha or "TBD_BLOCKED"}`
- Circuit manifest SHA-256: `{sha256_file(selected_circuit_manifest) if selected_circuit_manifest.exists() else "TBD_BLOCKED"}`
- Qiskit version: `{_required(packages.get("qiskit"))}`
- qiskit-ibm-runtime version: `{_required(packages.get("qiskit-ibm-runtime"))}`
- Open Plan instance identifier/name: `{runtime_account.get("instance_name", "TBD_BLOCKED")}`
- Open Plan: `{runtime_account.get("plan", "TBD_BLOCKED")}` / `{runtime_account.get("pricing_type", "TBD_BLOCKED")}`
- Instance region: `{runtime_account.get("region", "TBD_BLOCKED")}`
- Instance CRN SHA-256: `{runtime_account.get("instance_crn_sha256", "TBD_BLOCKED")}`

## 2. Frozen Logical Roles

"""
        + "\n".join(
            f"- {role} = logical qubit {index}" for role, index in sorted(logical_qubits.items())
        )
        + """

## 3. Science Circuits

"""
        + "\n".join(
            f"{index}. `{circuit['name']}`: GHZ {'+' if circuit['phase'] == 1 else '-'} measured in {circuit['basis']}"
            for index, circuit in enumerate(science_circuits, start=1)
        )
        + f"""

Four interleaved blocks, 1024 shots/circuit/block.

## 4. Readout Calibration

Eight independent assignment circuits: each selected physical qubit prepared in 0 and 1; 1024 shots each.

## 5. Backend and Layout Selection

Use the deterministic algorithm in `docs/RESEARCH_SPEC_TR.md`. No manual backend substitution after science results are known.

- Candidate source: `{provider_source}`
- Selected backend: `{selected_backend.get("name", "TBD_BLOCKED")}`
- Selected physical layout: `{selected_backend.get("selected_layout", "TBD_BLOCKED")}`
- Backend twin status: `{q304.get("status", "missing")}`
- Backend twin reason: `{q304.get("reason", "missing")}`
- Calibration snapshot timestamp: `{calibration_timestamp or "TBD_BLOCKED"}`
- Selected transpiler seed: `{selected_transpiler_seed if selected_transpiler_seed is not None else "TBD_BLOCKED"}`
- ISA circuit QPY SHA-256: `{h402_manifest.get("qpy_sha256", "TBD_BLOCKED")}`
- Exact execution-order seed: `{h402_manifest.get("execution_order_seed", "TBD_BLOCKED")}`
- Exact circuit instances: `{h402_manifest.get("total_circuit_instances", "TBD_BLOCKED")}`

## 5A. Backend Amendment

"""
        + (
            (
                f"- Amendment id: `{backend_amendment.get('amendment_id')}`\n"
                f"- Superseded backend: `{cast(dict[str, Any], backend_amendment.get('supersedes', {})).get('backend')}`\n"
                f"- Superseded job id: `{cast(dict[str, Any], backend_amendment.get('supersedes', {})).get('job_id')}`\n"
                f"- Superseded job final status: `{cast(dict[str, Any], backend_amendment.get('supersedes', {})).get('final_status')}`\n"
                f"- Raw result downloaded before amendment: `{cast(dict[str, Any], backend_amendment.get('supersedes', {})).get('raw_result_downloaded')}`\n"
                f"- Replacement backend: `{cast(dict[str, Any], backend_amendment.get('replacement', {})).get('backend')}`\n"
                "- Dependent Q303/Q304/H402/H401/H403/H404 artifacts must be regenerated before H501.\n"
            )
            if backend_amendment
            else "- No backend amendment is active.\n"
        )
        + f"""

## 6. Primary Endpoints

\\[
\\Delta_{{obj}}=\\min(C_{{Z,1}},C_{{Z,2}})-\\max(|C_{{X,1}}|,|C_{{X,2}}|)
\\]

\\[
\\Delta_{{coh}}=|W_+|-|W_{{mix}}|,
\\qquad W_{{mix}}=\\frac{{W_++W_-}}{{2}}.
\\]

## 7. Main-Text Inclusion Rule

All must pass on raw results:

- LCB95(delta_obj) > 0.40
- LCB95(min(C_Z1,C_Z2)) > 0.60
- LCB95(delta_coh) > 0.30
- GHZ- global X parity has the expected negative sign
- no single block supplies more than half of the total contrast
- raw and readout-corrected analyses have the same qualitative conclusion

## 8. Statistical Method

- Individual Pauli correlations: Clopper-Pearson interval after mapping +/-1 products to Bernoulli outcomes.
- Nonlinear contrasts: stratified shot bootstrap, 10,000 replicates, frozen seed 20260621.
- Primary alpha: 0.05.

## 9. Mitigation

- Primary: raw data.
- Secondary: tensor-product readout assignment correction.
- No ZNE, PEC, result-driven postselection, or shot deletion.

## 10. Rerun Policy

A rerun is permitted only for provider-declared failed/cancelled jobs, missing provider payload, circuit-hash mismatch, or provider-confirmed service incident. Weak or null scientific results do not permit a rerun.

## 11. Positive and Null Interpretations

- Objectivity + coherence pass: include main-text quantum illustration.
- Objectivity passes, coherence fails: classical-record illustration only; quantum coherence claim omitted.
- Both fail: hardware null; theory remains evaluated independently.

## 12. Freeze Declaration

Mandatory fields contain no `TBD`: `{"YES" if mandatory_fields_complete else "NO"}`
Human approval: `NO`
Status may become `FROZEN` only after all G4 tasks pass.

## 13. Current Blockers

"""
        + "\n".join(f"- `{item['field']}`: {item['reason']}" for item in unresolved)
        + "\n"
    )

    summary = {
        "task": "H401_preregistration_draft",
        "status": "draft_blocked",
        "frozen": False,
        "qpu_execution_allowed": False,
        "known_field_count": 12,
        "unresolved_field_count": len(unresolved),
        "unresolved_fields": unresolved,
        "mandatory_fields_complete": mandatory_fields_complete,
        "provider_source": provider_source,
        "backend_amendment_active": backend_amendment is not None,
        "open_instance_confirmed": open_instance_confirmed,
        "backend_twin_status": q304.get("status"),
        "g4_status": g4.get("overall_status"),
        "output": "results/processed/H401_preregistration_draft.md",
    }
    return PreregistrationDraft(markdown=markdown, summary=summary)
