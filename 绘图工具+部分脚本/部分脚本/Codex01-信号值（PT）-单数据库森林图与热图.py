from __future__ import annotations

import os
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.ticker import NullFormatter


# Fixed public interface: plot(data_path, output_path)
TOP_N = 30
DATABASE_LABEL = "FAERS"
FOREST_XMIN_CAP = 0.5
FOREST_XMAX_CAP = 10.0


def _norm_name(value: object) -> str:
    return "".join(ch for ch in str(value).strip().lower() if ch.isalnum())


def _find_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str:
    lookup = {_norm_name(col): col for col in df.columns}
    for alias in aliases:
        key = _norm_name(alias)
        if key in lookup:
            return lookup[key]
    raise KeyError(f"Missing required column: {aliases[0]}")


def _to_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).astype(bool)

    true_values = {"true", "t", "yes", "y", "1", "是"}
    false_values = {"false", "f", "no", "n", "0", "否", ""}

    def convert(value: object) -> object:
        if pd.isna(value):
            return np.nan
        if isinstance(value, (bool, np.bool_)):
            return bool(value)
        if isinstance(value, (int, float, np.number)):
            return bool(value)
        text = str(value).strip().lower()
        if text in true_values:
            return True
        if text in false_values:
            return False
        return np.nan

    return series.map(convert)


def _metric_column_map(df: pd.DataFrame) -> dict[str, str]:
    return {
        "pt": _find_column(df, ("pt", "preferred term")),
        "a": _find_column(df, ("a",)),
        "b": _find_column(df, ("b",)),
        "ror": _find_column(df, ("ror",)),
        "ror_low": _find_column(df, ("low_95cl_ror", "ror_lcl", "ror_lower")),
        "ror_up": _find_column(df, ("up_95cl_ror", "ror_ucl", "ror_upper")),
        "prr": _find_column(df, ("prr",)),
        "ebgm05": _find_column(df, ("ebgm05",)),
        "ic025": _find_column(df, ("ic025",)),
    }


def _signal_columns(df: pd.DataFrame, last_metric_column: str) -> list[str]:
    start = list(df.columns).index(last_metric_column) + 1
    candidates: list[str] = []
    for column in df.columns[start:]:
        converted = _to_bool(df[column])
        valid_ratio = converted.notna().mean()
        unique_values = set(converted.dropna().unique())
        if valid_ratio >= 0.8 and unique_values.issubset({True, False}):
            candidates.append(column)
    return candidates


def _nice_ceiling(value: float) -> float:
    if not np.isfinite(value) or value <= 0:
        return 10.0
    exponent = np.floor(np.log10(value))
    base = 10.0 ** exponent
    for multiplier in (1.0, 2.0, 5.0, 10.0):
        candidate = multiplier * base
        if candidate >= value:
            return float(candidate)
    return float(10.0 * base)


def _nice_floor(value: float) -> float:
    if not np.isfinite(value) or value <= 0:
        return FOREST_XMIN_CAP
    exponent = np.floor(np.log10(value))
    base = 10.0 ** exponent
    for multiplier in (10.0, 5.0, 2.0, 1.0):
        candidate = multiplier * base
        if candidate <= value:
            return float(candidate)
    return float(base)


def _format_metric(value: float) -> str:
    if not np.isfinite(value):
        return "NA"
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def _format_ror_ci(row: pd.Series) -> str:
    return (
        f"{_format_metric(row['ror'])} "
        f"({_format_metric(row['ror_low'])}-{_format_metric(row['ror_up'])})"
    )


def _draw_header(ax: plt.Axes, n_rows: int) -> None:
    ax.set_xlim(0, 3.0)
    ax.set_ylim(n_rows - 0.5, -1.25)
    ax.axis("off")

    header_y = -0.72
    ax.text(0.02, header_y, "PT", ha="left", va="center", fontsize=8.5, fontweight="bold")
    ax.text(1.72, header_y, "n (%)", ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.text(2.55, header_y, "ROR (95% CI)", ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.plot([0.0, 3.0], [-0.5, -0.5], color="black", linewidth=0.8, clip_on=False)


def _draw_table_rows(ax: plt.Axes, rows: pd.DataFrame, total_records: float) -> None:
    for index, (_, row) in enumerate(rows.iterrows()):
        if index % 2 == 1:
            ax.axhspan(index - 0.5, index + 0.5, color="#f4f4f4", zorder=0)

        pt_text = textwrap.fill(str(row["pt"]).upper(), width=39)
        count_pct = (
            f"{int(row['a']):,} "
            f"({100.0 * float(row['a']) / total_records:.2f}%)"
        )
        ax.text(0.02, index, pt_text, ha="left", va="center", fontsize=6.3)
        ax.text(1.72, index, count_pct, ha="center", va="center", fontsize=6.8)
        ax.text(2.55, index, _format_ror_ci(row), ha="center", va="center", fontsize=6.5)


def _forest_limits(rows: pd.DataFrame) -> tuple[float, float, list[float]]:
    lower_values = rows["ror_low"].replace([np.inf, -np.inf], np.nan).dropna()
    positive_lower = lower_values[lower_values > 0]

    if positive_lower.empty:
        xmin = FOREST_XMIN_CAP
    else:
        lower_floor = _nice_floor(float(positive_lower.min()))
        xmin = min(FOREST_XMIN_CAP, lower_floor)
        xmin = max(xmin, 1e-4)

    finite_upper = rows["ror_up"].replace([np.inf, -np.inf], np.nan).dropna()
    if finite_upper.empty:
        xmax = FOREST_XMAX_CAP
    else:
        upper_target = float(finite_upper.quantile(0.90))
        xmax = min(FOREST_XMAX_CAP, max(2.0, _nice_ceiling(upper_target)))

    tick_candidates = (
        0.0001,
        0.0002,
        0.0005,
        0.001,
        0.002,
        0.005,
        0.01,
        0.02,
        0.05,
        0.1,
        0.2,
        0.5,
        1.0,
        2.0,
        5.0,
        10.0,
        20.0,
        50.0,
        100.0,
    )
    ticks = [tick for tick in tick_candidates if xmin <= tick <= xmax]
    return xmin, xmax, ticks


def _draw_forest(
    ax: plt.Axes,
    rows: pd.DataFrame,
    xmin: float,
    xmax: float,
    ticks: list[float],
) -> None:
    n_rows = len(rows)
    ax.set_xscale("log")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(n_rows - 0.5, -0.5)

    for index in range(n_rows):
        if index % 2 == 1:
            ax.axhspan(index - 0.5, index + 0.5, color="#f4f4f4", zorder=0)

    ax.axvline(1.0, color="black", linestyle="--", linewidth=0.8, zorder=1)
    ax.grid(axis="x", color="#d9d9d9", linestyle=":", linewidth=0.55, zorder=0)

    for index, (_, row) in enumerate(rows.iterrows()):
        point = float(row["ror"])
        lower = float(row["ror_low"])
        upper = float(row["ror_up"])

        lower_plot = min(max(lower, xmin), xmax) if np.isfinite(lower) else xmin
        upper_plot = min(max(upper, xmin), xmax) if np.isfinite(upper) else xmax

        ax.hlines(index, lower_plot, upper_plot, color="black", linewidth=1.0, zorder=3)
        if np.isfinite(point) and xmin <= point <= xmax:
            ax.scatter(
                point,
                index,
                marker="s",
                s=24,
                facecolor="black",
                edgecolor="black",
                linewidth=0.4,
                zorder=4,
                clip_on=True,
            )

        if np.isfinite(upper) and upper > xmax:
            ax.annotate(
                "",
                xy=(xmax, index),
                xytext=(xmax / 1.18, index),
                arrowprops={"arrowstyle": "->", "color": "black", "lw": 0.9},
                annotation_clip=False,
                zorder=5,
            )

    ax.set_yticks([])
    ax.set_xticks(ticks)
    ax.set_xticklabels([_format_metric(tick) for tick in ticks], fontsize=7)
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis="x", width=0.7, length=3, pad=2)
    ax.set_xlabel("ROR", fontsize=8.5, fontweight="bold", labelpad=4)

    for spine in ax.spines.values():
        spine.set_linewidth(0.8)

    ax.set_title("Forest plot", fontsize=8.5, fontweight="bold", pad=8)


def _draw_heatmaps(
    heat_axes: list[plt.Axes],
    colorbar_axes: list[plt.Axes],
    rows: pd.DataFrame,
) -> None:
    specs = (
        ("PRR", "prr", "YlOrRd"),
        ("EBGM05", "ebgm05", "YlGnBu"),
        ("IC025", "ic025", "BuPu"),
    )
    n_rows = len(rows)

    for ax, cbar_ax, (label, column, cmap) in zip(heat_axes, colorbar_axes, specs):
        values = rows[column].to_numpy(dtype=float)
        finite_values = values[np.isfinite(values)]
        if finite_values.size:
            vmin = min(0.0, float(np.nanmin(finite_values)))
            vmax = float(np.nanmax(finite_values))
            if vmax <= vmin:
                vmax = vmin + 1.0
        else:
            vmin, vmax = 0.0, 1.0

        image = ax.imshow(
            values[:, np.newaxis],
            cmap=cmap,
            norm=Normalize(vmin=vmin, vmax=vmax),
            aspect="auto",
            interpolation="nearest",
            origin="upper",
        )
        ax.set_ylim(n_rows - 0.5, -0.5)
        ax.set_yticks([])
        ax.set_xticks([0])
        ax.set_xticklabels([label], fontsize=8.5, fontweight="bold")
        ax.tick_params(axis="x", top=True, labeltop=True, bottom=False, length=0, pad=6)
        for spine in ax.spines.values():
            spine.set_linewidth(0.7)

        for index, value in enumerate(values):
            if not np.isfinite(value):
                text = "NA"
                text_color = "black"
            else:
                text = _format_metric(float(value))
                span = max(vmax - vmin, 1e-12)
                normalized = (value - vmin) / span
                text_color = "white" if normalized > 0.68 else "black"
            ax.text(
                0,
                index,
                text,
                ha="center",
                va="center",
                fontsize=5.3,
                color=text_color,
            )

        colorbar = plt.colorbar(image, cax=cbar_ax, orientation="horizontal")
        colorbar.ax.tick_params(labelsize=5.5, length=2, pad=1)
        colorbar.outline.set_linewidth(0.5)


def plot(data_path, output_path):
    """Create a single-database PT signal forest plot with adjacent heatmaps."""
    data_path = Path(data_path)
    output_path = Path(output_path)

    if data_path.suffix.lower() == ".csv":
        df = pd.read_csv(data_path)
    else:
        df = pd.read_excel(data_path, sheet_name=0)

    if df.empty:
        raise ValueError("The input table is empty.")

    columns = _metric_column_map(df)

    data = pd.DataFrame(
        {
            "pt": df[columns["pt"]].astype(str).str.strip(),
            "a": pd.to_numeric(df[columns["a"]], errors="coerce"),
            "b": pd.to_numeric(df[columns["b"]], errors="coerce"),
            "ror": pd.to_numeric(df[columns["ror"]], errors="coerce"),
            "ror_low": pd.to_numeric(df[columns["ror_low"]], errors="coerce"),
            "ror_up": pd.to_numeric(df[columns["ror_up"]], errors="coerce"),
            "prr": pd.to_numeric(df[columns["prr"]], errors="coerce"),
            "ebgm05": pd.to_numeric(df[columns["ebgm05"]], errors="coerce"),
            "ic025": pd.to_numeric(df[columns["ic025"]], errors="coerce"),
        }
    )

    flag_columns = _signal_columns(df, columns["ic025"])
    if flag_columns:
        signal_mask = pd.concat(
            [_to_bool(df[column]) for column in flag_columns],
            axis=1,
        ).fillna(False).astype(bool).any(axis=1)
    else:
        signal_mask = (
            (data["a"] >= 3)
            & (data["ror_low"] > 1.0)
        )

    data = data.loc[signal_mask].copy()
    if data.empty:
        data = pd.DataFrame(
            {
                "pt": df[columns["pt"]].astype(str).str.strip(),
                "a": pd.to_numeric(df[columns["a"]], errors="coerce"),
                "b": pd.to_numeric(df[columns["b"]], errors="coerce"),
                "ror": pd.to_numeric(df[columns["ror"]], errors="coerce"),
                "ror_low": pd.to_numeric(df[columns["ror_low"]], errors="coerce"),
                "ror_up": pd.to_numeric(df[columns["ror_up"]], errors="coerce"),
                "prr": pd.to_numeric(df[columns["prr"]], errors="coerce"),
                "ebgm05": pd.to_numeric(df[columns["ebgm05"]], errors="coerce"),
                "ic025": pd.to_numeric(df[columns["ic025"]], errors="coerce"),
            }
        ).dropna(subset=["a", "ror", "ror_low", "ror_up"])

    data = data.dropna(subset=["a", "ror", "ror_low", "ror_up"])
    data = data.sort_values(["a", "ror"], ascending=[False, False]).head(TOP_N)
    if data.empty:
        raise ValueError("No plottable PT rows were found.")
    data = data.reset_index(drop=True)

    total_candidates = (data["a"] + data["b"]).replace([np.inf, -np.inf], np.nan).dropna()
    if total_candidates.empty:
        total_records = float(data["a"].max())
    else:
        modes = total_candidates.mode()
        total_records = float(modes.iloc[0] if not modes.empty else total_candidates.median())
    if total_records <= 0:
        total_records = 1.0

    n_rows = len(data)
    figure_height = max(8.5, 4.8 + 0.25 * n_rows)
    fig = plt.figure(figsize=(14.2, figure_height))
    grid = fig.add_gridspec(
        nrows=2,
        ncols=5,
        width_ratios=(3.15, 2.6, 0.48, 0.48, 0.48),
        height_ratios=(1.0, 0.035),
        left=0.045,
        right=0.985,
        top=0.90,
        bottom=0.075,
        wspace=0.035,
        hspace=0.055,
    )

    table_ax = fig.add_subplot(grid[0, 0])
    forest_ax = fig.add_subplot(grid[0, 1])
    heat_axes = [
        fig.add_subplot(grid[0, column])
        for column in (2, 3, 4)
    ]
    colorbar_axes = [
        fig.add_subplot(grid[1, column])
        for column in (2, 3, 4)
    ]

    _draw_header(table_ax, n_rows)
    _draw_table_rows(table_ax, data, total_records)

    xmin, xmax, ticks = _forest_limits(data)
    _draw_forest(forest_ax, data, xmin, xmax, ticks)
    _draw_heatmaps(heat_axes, colorbar_axes, data)

    fig.text(
        0.045,
        0.955,
        "A",
        fontsize=14,
        fontweight="bold",
        ha="left",
        va="center",
    )
    fig.text(
        0.075,
        0.955,
        f"{DATABASE_LABEL}: representative PT-level signals",
        fontsize=10,
        fontweight="bold",
        ha="left",
        va="center",
    )
    fig.text(
        0.985,
        0.935,
        f"Target group records, n = {int(total_records):,}",
        fontsize=7.5,
        ha="right",
        va="center",
    )
    fig.text(
        0.045,
        0.018,
        (
            "Squares: ROR point estimate; horizontal lines: 95% CI; "
            "dashed line: ROR = 1. Arrows indicate an upper CI beyond the plotting range."
        ),
        fontsize=7,
        ha="left",
        va="bottom",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("data_path")
    parser.add_argument("output_path")
    args = parser.parse_args()
    plot(args.data_path, args.output_path)
