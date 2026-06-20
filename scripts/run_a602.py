from __future__ import annotations

from objective_clocks.interpretation import write_final_decision


def main() -> None:
    decision = write_final_decision()
    print(
        {
            "task": decision["task"],
            "status": decision["status"],
            "selected_path": decision["selected_path"],
            "hardware_interpretation": decision["hardware_interpretation"],
        }
    )


if __name__ == "__main__":
    main()
