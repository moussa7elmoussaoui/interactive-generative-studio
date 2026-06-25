"""Artistic matplotlib visualizations generated from CSV datasets."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from modules.art.random_art import PALETTES


def generate_data_art(
    frame: pd.DataFrame,
    output_path: Path,
    style: str = "landscape",
    palette_name: str = "aurora",
    alpha: float = 0.75,
) -> Path:
    """Render a selected artistic chart style."""
    palette = np.array(PALETTES.get(palette_name, PALETTES["aurora"])) / 255
    numeric = frame.select_dtypes(include=[np.number])
    values = numeric.iloc[:, 0].to_numpy() if not numeric.empty else np.arange(20)
    values = _normalize(values)
    labels = frame.iloc[:, 0].astype(str).head(len(values)).to_numpy()

    fig, ax = plt.subplots(figsize=(12, 7.6), dpi=120)
    fig.patch.set_facecolor("#070916")
    ax.set_facecolor("#070916")
    getattr(_Styles, style, _Styles.landscape)(ax, values, labels, palette, alpha)
    ax.tick_params(colors="#dbeafe")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(style.replace("_", " ").title(), color="#f8fafc", fontsize=22, pad=18)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return output_path


class _Styles:
    @staticmethod
    def landscape(ax: plt.Axes, values: np.ndarray, labels: np.ndarray, palette: np.ndarray, alpha: float) -> None:
        x = np.linspace(0, 1, len(values))
        for i, scale in enumerate([1.0, 0.76, 0.52]):
            y = np.clip(values * scale + i * 0.12, 0, 1.25)
            ax.fill_between(x, 0, y, color=palette[i % len(palette)], alpha=alpha * (0.36 + i * 0.16))
            ax.plot(x, y, color=palette[(i + 1) % len(palette)], linewidth=2)
        ax.set_xticks([])
        ax.set_yticks([])

    @staticmethod
    def circular_bars(ax: plt.Axes, values: np.ndarray, labels: np.ndarray, palette: np.ndarray, alpha: float) -> None:
        ax.remove()
        polar = plt.gcf().add_subplot(111, projection="polar")
        theta = np.linspace(0, 2 * np.pi, len(values), endpoint=False)
        width = 2 * np.pi / max(len(values), 1) * 0.78
        colors = [palette[i % len(palette)] for i in range(len(values))]
        polar.bar(theta, values + 0.15, width=width, color=colors, alpha=alpha)
        polar.set_facecolor("#070916")
        polar.set_xticks([])
        polar.set_yticks([])
        polar.spines["polar"].set_visible(False)

    @staticmethod
    def heatmap(ax: plt.Axes, values: np.ndarray, labels: np.ndarray, palette: np.ndarray, alpha: float) -> None:
        grid = np.outer(values, values[::-1])
        ax.imshow(grid, cmap="magma", alpha=alpha, interpolation="bicubic")
        ax.set_xticks([])
        ax.set_yticks([])

    @staticmethod
    def bubbles(ax: plt.Axes, values: np.ndarray, labels: np.ndarray, palette: np.ndarray, alpha: float) -> None:
        rng = np.random.default_rng(42)
        x = rng.random(len(values))
        y = rng.random(len(values))
        sizes = 2500 * values + 80
        colors = [palette[i % len(palette)] for i in range(len(values))]
        ax.scatter(x, y, s=sizes, c=colors, alpha=alpha, edgecolors="#f8fafc", linewidths=0.7)
        ax.set_xticks([])
        ax.set_yticks([])

    @staticmethod
    def ribbons(ax: plt.Axes, values: np.ndarray, labels: np.ndarray, palette: np.ndarray, alpha: float) -> None:
        x = np.linspace(0, 1, len(values))
        for i in range(6):
            phase = i * 0.55
            y = 0.5 + 0.22 * np.sin(8 * x + phase) + values * (0.12 + i * 0.015)
            ax.plot(x, y, color=palette[i % len(palette)], linewidth=8 - i, alpha=alpha * 0.62)
        ax.set_xticks([])
        ax.set_yticks([])


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.nan_to_num(values.astype(float))
    minimum = values.min()
    maximum = values.max()
    if maximum == minimum:
        return np.full_like(values, 0.5)
    return (values - minimum) / (maximum - minimum)
