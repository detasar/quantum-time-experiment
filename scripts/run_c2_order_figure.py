from __future__ import annotations

from pathlib import Path

import matplotlib
import networkx as nx

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from objective_clocks.artifacts import sha256_file, write_json_atomic
from objective_clocks.classical import diamond_code
from objective_clocks.order import poset_graph, thermometer_code


def _draw_hasse(
    ax: plt.Axes,
    graph: nx.DiGraph,
    positions: dict[int, tuple[float, float]],
    labels: dict[int, str],
    *,
    title: str,
    highlight_edges: list[tuple[int, int]] | None = None,
) -> None:
    highlight_edges = highlight_edges or []
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=16,
        width=2.1,
        edge_color="#52616f",
        connectionstyle="arc3,rad=0.0",
    )
    if highlight_edges:
        nx.draw_networkx_edges(
            graph,
            positions,
            edgelist=highlight_edges,
            ax=ax,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=18,
            width=3.4,
            edge_color="#2a9d8f",
        )
    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=ax,
        node_color="#ffffff",
        edgecolors="#102a43",
        linewidths=1.8,
        node_size=1250,
    )
    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        ax=ax,
        font_size=10,
        font_weight="bold",
        font_color="#102a43",
    )
    ax.set_title(title)
    ax.set_axis_off()


def write_order_figure(path: Path, manifest_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    thermometer = thermometer_code(5)
    thermometer_graph = poset_graph(thermometer.bits)
    thermometer_positions = {index: (index, 0.0) for index in range(5)}
    thermometer_labels = {
        index: "".join(map(str, row.astype(int))) for index, row in enumerate(thermometer.bits)
    }

    diamond = diamond_code()
    diamond_graph = poset_graph(diamond.bits)
    diamond_positions = {
        0: (0.0, 0.0),
        1: (-0.9, 1.0),
        2: (0.9, 1.0),
        3: (0.0, 2.0),
    }
    diamond_labels = {
        index: "".join(map(str, row.astype(int))) for index, row in enumerate(diamond.bits)
    }

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.4))
    _draw_hasse(
        axes[0],
        thermometer_graph,
        thermometer_positions,
        thermometer_labels,
        title="Accumulating records: one persistent chain",
        highlight_edges=list(thermometer_graph.edges()),
    )
    axes[0].text(
        2.0,
        -0.55,
        "arrows mean: records can accumulate without being erased",
        ha="center",
        va="center",
        color="#2f855a",
        fontsize=10,
    )

    _draw_hasse(
        axes[1],
        diamond_graph,
        diamond_positions,
        diamond_labels,
        title="Branching records: no single timeline",
        highlight_edges=[(0, 1), (1, 3)],
    )
    jump_style = {
        "arrowstyle": "-|>",
        "color": "#c44569",
        "linewidth": 2.3,
        "linestyle": "--",
        "shrinkA": 0,
        "shrinkB": 0,
    }
    axes[1].annotate(
        "",
        xy=(0.68, 0.82),
        xytext=(0.18, 0.16),
        arrowprops={**jump_style, "connectionstyle": "arc3,rad=-0.18"},
    )
    axes[1].annotate(
        "",
        xy=(0.18, 1.84),
        xytext=(0.68, 1.18),
        arrowprops={**jump_style, "connectionstyle": "arc3,rad=-0.18"},
    )
    axes[1].text(
        0.05,
        -0.35,
        "two valid chains; forcing one total list jumps branches",
        ha="center",
        va="center",
        color="#7f1d1d",
        fontsize=10,
    )

    fig.suptitle("Order evidence: a physical trajectory must stay on one chain", fontweight="bold")
    fig.subplots_adjust(left=0.04, right=0.98, top=0.84, bottom=0.18, wspace=0.16)
    fig.savefig(path, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)

    write_json_atomic(
        manifest_path,
        {
            "task": "C2_order_figure",
            "status": "complete",
            "figure": {"path": path.as_posix(), "sha256": sha256_file(path)},
            "secret_values_recorded": False,
        },
    )


def main() -> None:
    write_order_figure(
        Path("figures/fig_01_order_chains.pdf"),
        Path("results/processed/C2_order_figure_manifest.json"),
    )


if __name__ == "__main__":
    main()
