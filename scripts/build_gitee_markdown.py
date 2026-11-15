#!/usr/bin/env python3
"""Build a Gitee-compatible Markdown copy with locally rendered formulas."""

from __future__ import annotations

import argparse
import html
import re
import struct
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "stix"

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.mathtext import math_to_image
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT / "分析方法" / "多元Logistic回归+机器学习预测.md"
)
DEFAULT_OUTPUT = (
    ROOT / "分析方法" / "多元Logistic回归+机器学习预测.gitee.md"
)
DEFAULT_ASSETS_DIR = ROOT / "分析方法" / "assets" / "logistic-ml"

DISPLAY_MATH_RE = re.compile(r"\\\[\s*(.*?)\s*\\\]", re.DOTALL)
INLINE_MATH_RE = re.compile(r"\\\((.*?)\\\)", re.DOTALL)

FORMULA_REPLACEMENTS = {
    r"\operatorname": r"\mathrm",
    r"\text{阳性事件数}": r"\mathrm{Events}",
    r"\text{模型参数数目}": r"\mathrm{Variables}",
}

EPV_FORMULA_MARKERS = (
    r"\text{阳性事件数}",
    r"\text{模型参数数目}",
)

INLINE_REPLACEMENTS = {
    r"\lambda": "λ",
    r"\alpha": "α",
    r"\phi_j": "φ_j",
    r"\hat p_i": "p̂_i",
}


def normalize_formula(formula: str) -> str:
    normalized = " ".join(formula.split())
    for source, target in FORMULA_REPLACEMENTS.items():
        normalized = normalized.replace(source, target)
    return normalized


def normalize_inline_formula(formula: str) -> str:
    normalized = formula.strip()
    for source, target in INLINE_REPLACEMENTS.items():
        normalized = normalized.replace(source, target)
    return normalized


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a valid PNG file: {path}")
    return struct.unpack(">II", header[16:24])


def add_padding(destination: Path, margin: int = 20) -> None:
    with Image.open(destination) as image:
        formula_image = image.convert("RGBA")
        padded = Image.new(
            "RGBA",
            (
                formula_image.width + margin * 2,
                formula_image.height + margin * 2,
            ),
            (255, 255, 255, 0),
        )
        padded.alpha_composite(formula_image, (margin, margin))
        padded.save(destination, format="PNG", optimize=True)


def find_cjk_font() -> Path:
    for family in (
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans CN",
    ):
        try:
            return Path(
                font_manager.findfont(family, fallback_to_default=False)
            )
        except ValueError:
            continue
    raise RuntimeError("No CJK font is available for the EPV formula.")


def render_epv_formula(destination: Path, dpi: int) -> None:
    label_font = FontProperties(fname=find_cjk_font(), size=13)
    equation_font = FontProperties(size=18)
    figure = plt.figure(figsize=(4.8, 1.35), dpi=dpi)
    figure.patch.set_alpha(0)
    figure.text(
        0.02,
        0.46,
        r"$EPV=$",
        fontproperties=equation_font,
        va="center",
    )
    figure.text(
        0.67,
        0.72,
        "阳性事件数",
        fontproperties=label_font,
        ha="center",
        va="center",
    )
    figure.text(
        0.67,
        0.20,
        "模型参数数目",
        fontproperties=label_font,
        ha="center",
        va="center",
    )
    figure.add_artist(
        Line2D(
            [0.38, 0.96],
            [0.46, 0.46],
            transform=figure.transFigure,
            color="black",
            linewidth=1.5,
        )
    )
    figure.savefig(
        destination,
        dpi=dpi,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.08,
    )
    plt.close(figure)


def render_formula(formula: str, destination: Path, dpi: int) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if all(marker in formula for marker in EPV_FORMULA_MARKERS):
        render_epv_formula(destination, dpi)
    else:
        math_to_image(
            f"${normalize_formula(formula)}$",
            str(destination),
            prop=FontProperties(size=12),
            dpi=dpi,
            format="png",
        )
    add_padding(destination)
    pixel_width, _ = png_dimensions(destination)
    return max(1, round(pixel_width * 96 / dpi))


def build(source: Path, output: Path, assets_dir: Path, dpi: int) -> None:
    markdown = source.read_text(encoding="utf-8")
    formula_number = 0

    def replace_display(match: re.Match[str]) -> str:
        nonlocal formula_number
        formula_number += 1
        filename = f"formula-{formula_number:02d}.png"
        destination = assets_dir / filename
        display_width = render_formula(match.group(1), destination, dpi)
        relative_path = destination.relative_to(output.parent).as_posix()
        alt = html.escape(f"展示公式 {formula_number}", quote=True)
        return (
            f'<p align="center">'
            f'<img src="{relative_path}" alt="{alt}" width="{display_width}">'
            f"</p>"
        )

    def replace_inline(match: re.Match[str]) -> str:
        formula = normalize_inline_formula(match.group(1)).replace("`", r"\`")
        return f"`{formula}`"

    compatible = DISPLAY_MATH_RE.sub(replace_display, markdown)
    compatible = INLINE_MATH_RE.sub(replace_inline, compatible)
    compatible = (
        "<!-- Generated by scripts/build_gitee_markdown.py; do not edit directly. -->\n"
        + compatible
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(compatible, encoding="utf-8", newline="\n")
    print(f"Generated {output}")
    print(f"Rendered {formula_number} display formula(s) in {assets_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the Gitee-compatible Markdown version."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--assets-dir", type=Path, default=DEFAULT_ASSETS_DIR)
    parser.add_argument("--dpi", type=int, default=200)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build(
        source=args.source.resolve(),
        output=args.output.resolve(),
        assets_dir=args.assets_dir.resolve(),
        dpi=args.dpi,
    )
