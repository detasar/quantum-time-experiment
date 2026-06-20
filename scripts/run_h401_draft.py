from __future__ import annotations

from pathlib import Path

from objective_clocks.artifacts import write_json_atomic, write_sha256_manifest
from objective_clocks.preregistration import build_h401_preregistration_draft


def main() -> None:
    draft = build_h401_preregistration_draft()
    draft_path = Path("results/processed/H401_preregistration_draft.md")
    draft_path.write_text(draft.markdown, encoding="utf-8")
    summary_path = Path("results/processed/H401_preregistration_draft_summary.json")
    write_json_atomic(summary_path, draft.summary)
    write_sha256_manifest(
        Path("results/processed/H401_preregistration_draft_manifest.json"),
        [draft_path, summary_path],
    )
    print(draft.summary)


if __name__ == "__main__":
    main()
