from __future__ import annotations

from pathlib import Path

from objective_clocks.artifacts import write_environment_archive


def main() -> None:
    manifest = write_environment_archive(
        Path("results/preregistered/environment_archive.tar.gz"),
        Path("results/preregistered/environment_archive_manifest.json"),
    )
    print(
        {
            "task": manifest["task"],
            "archive_sha256": manifest["archive_sha256"],
            "archived_file_count": manifest["archived_file_count"],
            "secret_values_recorded": manifest["secret_values_recorded"],
        }
    )


if __name__ == "__main__":
    main()
