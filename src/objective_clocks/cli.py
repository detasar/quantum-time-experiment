from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import numpy as np
import typer

from .order import infer_order, thermometer_code
from .states import dephased_ghz_density, ghz_density

app = typer.Typer(no_args_is_help=True)


def _pauli_expectation(rho: np.ndarray, operators: tuple[np.ndarray, ...]) -> float:
    operator = operators[0]
    for next_operator in operators[1:]:
        operator = np.kron(operator, next_operator)
    return float(np.trace(rho @ operator).real)


@app.command("theorem-check")
def theorem_check(
    config: Annotated[Path, typer.Option()] = Path("configs/classical.yaml"),
) -> None:
    """Run a minimal exact theorem sanity check."""
    code = thermometer_code(5)
    result = infer_order(code)
    payload = {
        "config": str(config),
        "linear_extension_count_scheduler_only": result.linear_extension_count,
        "maximal_persistent_chain_count": result.maximal_chain_count,
        "is_total": result.is_total,
        "automorphism_count": result.automorphism_count,
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("ghz-exact")
def ghz_exact() -> None:
    """Print exact four-qubit GHZ and dephased-control observables."""
    identity = np.eye(2, dtype=np.complex128)
    x = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
    ghz = ghz_density(4)
    mixture = dephased_ghz_density(4)
    observables = {
        "ZZ_C_R1": (z, identity, z, identity),
        "ZZ_C_R2": (z, identity, identity, z),
        "XX_C_R1": (x, identity, x, identity),
        "XX_C_R2": (x, identity, identity, x),
        "XXXX": (x, x, x, x),
    }
    payload = {
        name: {
            "ghz": _pauli_expectation(ghz, ops),
            "mixture": _pauli_expectation(mixture, ops),
        }
        for name, ops in observables.items()
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("ibm-submit")
def ibm_submit() -> None:
    typer.echo("Hardware submission remains intentionally gated; see README.md", err=True)
    raise typer.Exit(1)


if __name__ == "__main__":
    app()
