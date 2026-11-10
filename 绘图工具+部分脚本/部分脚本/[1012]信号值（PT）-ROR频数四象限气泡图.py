import sys
import textwrap
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import patheffects

try:
    from adjustText import adjust_text
except ImportError:
    adjust_text = None


PT_COLUMN = "pt"
COUNT_COLUMN = "a"
ROR_COLUMN = "low_95cl_ror"
ROR_LOG2_THRESHOLD = 0
COUNT_LOG2_THRESHOLD = 4
TOP_LABELS_PER_QUADRANT = 7

QUADRANT_INFO = {
    "Q1": {
        "condition": "High signal / High count",
        "color": "#C43D3D",
    },
    "Q2": {
        "condition": "Low signal / High count",
        "color": "#2A6FBB",
    },
    "Q3": {
        "condition": "Low signal / Low count",
        "color": "#8A8A8A",
    },
    "Q4": {
        "condition": "High signal / Low count",
        "color": "#D98B2B",
    },
}


def _prepare_data(data_path):
    df = pd.read_excel(data_path)
    required_columns = [PT_COLUMN, COUNT_COLUMN, ROR_COLUMN]
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    plot_df = df[required_columns].copy()
    for column in [COUNT_COLUMN, ROR_COLUMN]:
        plot_df[column] = pd.to_numeric(plot_df[column], errors="coerce")

    valid_mask = (
        plot_df[PT_COLUMN].notna()
        & plot_df[COUNT_COLUMN].gt(0)
        & plot_df[ROR_COLUMN].gt(0)
        & np.isfinite(plot_df[COUNT_COLUMN])
        & np.isfinite(plot_df[ROR_COLUMN])
    )
    invalid_count = int((~valid_mask).sum())
    plot_df = plot_df.loc[valid_mask].copy()
    if plot_df.empty:
        raise ValueError("No valid PT, report count, or lower ROR records found.")

    plot_df["log2_ror"] = np.log2(plot_df[ROR_COLUMN])
    plot_df["log2_count"] = np.log2(plot_df[COUNT_COLUMN])

    x_values = plot_df["log2_ror"]
    y_values = plot_df["log2_count"]
    plot_df["quadrant"] = np.select(
        [
            (x_values >= ROR_LOG2_THRESHOLD)
            & (y_values >= COUNT_LOG2_THRESHOLD),
            (x_values < ROR_LOG2_THRESHOLD)
            & (y_values >= COUNT_LOG2_THRESHOLD),
            (x_values < ROR_LOG2_THRESHOLD)
            & (y_values < COUNT_LOG2_THRESHOLD),
            (x_values >= ROR_LOG2_THRESHOLD)
            & (y_values < COUNT_LOG2_THRESHOLD),
        ],
        ["Q1", "Q2", "Q3", "Q4"],
    )

    # Composite prominence balances signal strength and reporting frequency.
    plot_df["prominence"] = (
        plot_df[ROR_COLUMN] * plot_df[COUNT_COLUMN]
    )
    return plot_df, invalid_count


def _wrap_label(label, width=34):
    return "\n".join(textwrap.wrap(str(label), width=width))


def _add_quadrant_backgrounds(ax, x_min, x_max, y_min, y_max):
    x_split = ROR_LOG2_THRESHOLD
    y_split = COUNT_LOG2_THRESHOLD
    quadrants = [
        ("Q2", x_min, x_split, y_split, y_max),
        ("Q1", x_split, x_max, y_split, y_max),
        ("Q3", x_min, x_split, y_min, y_split),
        ("Q4", x_split, x_max, y_min, y_split),
    ]
    for quadrant, x0, x1, y0, y1 in quadrants:
        ax.add_patch(
            plt.Rectangle(
                (x0, y0),
                x1 - x0,
                y1 - y0,
                facecolor=QUADRANT_INFO[quadrant]["color"],
                edgecolor="none",
                alpha=0.035,
                zorder=0,
            )
        )


def plot(data_path, output_path):
    plot_df, invalid_count = _prepare_data(data_path)
    print(f"[QuadrantBubble] Data loaded: {len(plot_df)} valid PT records")
    if invalid_count:
        print(
            "[QuadrantBubble] Excluded invalid or non-positive records: "
            f"{invalid_count}"
        )
    print(
        "[QuadrantBubble] Thresholds: "
        f"log2(ROR lower 95% CI) = {ROR_LOG2_THRESHOLD}, "
        f"log2(N) = {COUNT_LOG2_THRESHOLD}"
    )

    plt.rcParams.update(
        {
            "font.size": 9,
            "font.family": "Arial",
            "axes.linewidth": 0.9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "figure.dpi": 150,
            "savefig.dpi": 600,
        }
    )

    fig, ax = plt.subplots(figsize=(9.2, 7.2), facecolor="white")
    ax.set_facecolor("white")

    x_values = plot_df["log2_ror"].to_numpy()
    y_values = plot_df["log2_count"].to_numpy()
    x_range = x_values.max() - x_values.min()
    y_range = y_values.max() - y_values.min()
    x_padding = max(0.45, x_range * 0.035)
    y_padding = max(0.45, y_range * 0.045)
    x_min = min(x_values.min() - x_padding, ROR_LOG2_THRESHOLD - 0.5)
    x_max = max(x_values.max() + x_padding, ROR_LOG2_THRESHOLD + 0.5)
    y_min = min(y_values.min() - y_padding, COUNT_LOG2_THRESHOLD - 0.5)
    y_max = max(y_values.max() + y_padding, COUNT_LOG2_THRESHOLD + 0.5)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    _add_quadrant_backgrounds(ax, x_min, x_max, y_min, y_max)

    max_count = plot_df[COUNT_COLUMN].max()
    bubble_areas = pd.Series(
        700.0 * plot_df[COUNT_COLUMN].to_numpy() / max_count,
        index=plot_df.index,
    )
    quadrant_legend_handles = []

    for quadrant in ["Q1", "Q2", "Q3", "Q4"]:
        quadrant_df = plot_df.loc[plot_df["quadrant"] == quadrant]
        color = QUADRANT_INFO[quadrant]["color"]
        ax.scatter(
            quadrant_df["log2_ror"],
            quadrant_df["log2_count"],
            s=bubble_areas.loc[quadrant_df.index],
            c=color,
            alpha=0.62,
            edgecolors="white",
            linewidths=0.35,
            zorder=3,
            rasterized=True,
        )
        quadrant_legend_handles.append(
            plt.Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                markerfacecolor=color,
                markeredgecolor="white",
                markeredgewidth=0.5,
                markersize=7,
                label=(
                    f"{quadrant}: {QUADRANT_INFO[quadrant]['condition']} "
                    f"(n={len(quadrant_df)})"
                ),
            )
        )

    ax.axvline(
        ROR_LOG2_THRESHOLD,
        color="#303030",
        linestyle=(0, (5, 4)),
        linewidth=1.15,
        zorder=4,
    )
    ax.axhline(
        COUNT_LOG2_THRESHOLD,
        color="#303030",
        linestyle=(0, (5, 4)),
        linewidth=1.15,
        zorder=4,
    )

    ax.grid(
        True,
        which="major",
        axis="both",
        color="#D7D7D7",
        linewidth=0.45,
        linestyle="-",
        alpha=0.48,
        zorder=0,
    )
    ax.set_axisbelow(True)
    ax.set_xlabel("log2(ROR lower 95% CI)", fontsize=11, fontweight="bold")
    ax.set_ylabel("log2(Report Count, N)", fontsize=11, fontweight="bold")
    ax.set_title(
        "Quadrant Bubble Plot of Adverse Event Signals",
        fontsize=13,
        fontweight="bold",
        pad=34,
    )
    ax.tick_params(axis="both", labelsize=8.5, colors="#252525")

    label_rows = []
    for quadrant in ["Q1", "Q2", "Q3", "Q4"]:
        quadrant_df = plot_df.loc[plot_df["quadrant"] == quadrant]
        top_rows = quadrant_df.nlargest(
            TOP_LABELS_PER_QUADRANT, "prominence"
        ).sort_values("prominence", ascending=False)
        label_rows.append(top_rows)
        displayed_names = "; ".join(top_rows[PT_COLUMN].astype(str))
        print(
            f"[QuadrantBubble] {quadrant} ({len(quadrant_df)} PTs) "
            f"top labels: {displayed_names}"
        )

    label_df = pd.concat(label_rows, ignore_index=True)
    adjusted_label_df = label_df.loc[label_df["quadrant"] != "Q3"].copy()
    texts = []
    for row in adjusted_label_df.itertuples(index=False):
        color = QUADRANT_INFO[row.quadrant]["color"]
        text_artist = ax.text(
            row.log2_ror,
            row.log2_count,
            _wrap_label(row.pt),
            fontsize=6.3,
            fontweight="semibold",
            color="#171717",
            ha="center",
            va="center",
            zorder=6,
            path_effects=None,
        )
        texts.append(text_artist)

    if adjust_text is not None and texts:
        with redirect_stdout(StringIO()):
            adjust_text(
                texts,
                ax=ax,
                x=adjusted_label_df["log2_ror"].to_numpy(),
                y=adjusted_label_df["log2_count"].to_numpy(),
                expand=(1.08, 1.18),
                force_text=(0.28, 0.42),
                force_static=(0.20, 0.35),
                force_explode=(0.04, 0.05),
                max_move=(400, 400),
                ensure_inside_axes=True,
                expand_axes=False,
                time_lim=10,
                arrowprops=dict(
                    arrowstyle="-",
                    color="#4A4A4A",
                    linewidth=0.45,
                    shrinkA=2,
                    shrinkB=2,
                ),
            )
    else:
        offsets = [(8, 8), (-8, 8), (8, -8), (-8, -8), (10, 0), (-10, 0)]
        for text_artist, (x_pos, y_pos), offset in zip(
            texts,
            zip(
                adjusted_label_df["log2_ror"],
                adjusted_label_df["log2_count"],
            ),
            [offsets[i % len(offsets)] for i in range(len(texts))],
        ):
            text_artist.remove()
            ax.annotate(
                text_artist.get_text(),
                xy=(x_pos, y_pos),
                xytext=offset,
                textcoords="offset points",
                fontsize=6.3,
                fontweight="semibold",
                color="#171717",
                ha="center",
                va="center",
                zorder=6,
                arrowprops=dict(
                    arrowstyle="-",
                    color="#4A4A4A",
                    linewidth=0.45,
                    shrinkA=2,
                    shrinkB=2,
                ),
            )

    q3_label_df = label_df.loc[label_df["quadrant"] == "Q3"].copy()
    q3_anchor_x = x_min + max(
        x_padding * 0.65,
        0.025 * (x_max - x_min),
    )
    q3_anchor_y_values = np.linspace(
        COUNT_LOG2_THRESHOLD - 0.36,
        y_min + max(
            y_padding * 1.15,
            0.04 * (y_max - y_min),
        ),
        len(q3_label_df),
    )
    for row, anchor_y in zip(
        q3_label_df.itertuples(index=False), q3_anchor_y_values
    ):
        ax.annotate(
            _wrap_label(row.pt, width=27),
            xy=(row.log2_ror, row.log2_count),
            xytext=(q3_anchor_x, anchor_y),
            textcoords="data",
            fontsize=6.3,
            fontweight="semibold",
            color="#171717",
            ha="left",
            va="center",
            zorder=6,
            arrowprops=dict(
                arrowstyle="-",
                color="#777777",
                linewidth=0.35,
                alpha=0.68,
                shrinkA=2,
                shrinkB=2,
                connectionstyle="arc3,rad=0.03",
            ),
        )

    for text_artist in ax.texts:
        if text_artist.get_transform() is ax.transData:
            text_artist.set_path_effects(
                [
                    patheffects.withStroke(
                        linewidth=2.2, foreground="white", alpha=0.9
                    )
                ]
            )

    quadrant_legend = ax.legend(
        handles=[
            quadrant_legend_handles[0],
            quadrant_legend_handles[2],
            quadrant_legend_handles[1],
            quadrant_legend_handles[3],
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 1.005),
        ncol=2,
        frameon=False,
        fontsize=7.3,
        handletextpad=0.35,
        columnspacing=1.0,
        borderaxespad=0.0,
    )
    ax.add_artist(quadrant_legend)

    fig.subplots_adjust(left=0.09, right=0.91, top=0.83, bottom=0.10)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=600, bbox_inches="tight", facecolor="white")
    print(f"[QuadrantBubble] Figure saved: {output_path}")
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python quadrant_bubble_plot.py "
            "<data_path.xlsx> <output_path.png>"
        )
    else:
        plot(sys.argv[1], sys.argv[2])
