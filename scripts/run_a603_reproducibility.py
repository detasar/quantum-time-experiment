from __future__ import annotations

from objective_clocks.interpretation import write_reproducibility_package


def main() -> None:
    manifest = write_reproducibility_package()
    print(
        {
            "task": manifest["task"],
            "status": manifest["status"],
            "archive_path": manifest["archive_path"],
            "archive_sha256": manifest["archive_sha256"],
            "clean_reproduction_passed": manifest["reproduction"]["passed"],
        }
    )


if __name__ == "__main__":
    main()
