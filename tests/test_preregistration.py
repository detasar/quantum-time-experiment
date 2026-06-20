from __future__ import annotations

from pathlib import Path

from objective_clocks.preregistration import build_h401_preregistration_draft


def test_h401_draft_is_not_frozen_and_preserves_blockers() -> None:
    draft = build_h401_preregistration_draft(Path("."))
    summary = draft.summary

    assert summary["status"] == "draft_blocked"
    assert summary["frozen"] is False
    assert summary["qpu_execution_allowed"] is False
    assert summary["unresolved_field_count"] >= 3
    assert any(item["field"] == "human_approval" for item in summary["unresolved_fields"])
    assert "Status:** FROZEN" not in draft.markdown
    assert "TBD_BLOCKED" in draft.markdown
    assert "Human approval: `NO`" in draft.markdown
