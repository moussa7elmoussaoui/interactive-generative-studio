"""Recursive fractal artwork generator."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from modules.art.random_art import PALETTES


def generate_fractal(
    output_path: Path,
    depth: int = 9,
    angle: float = 24,
    length: float = 150,
    randomness: float = 0.18,
    thickness: int = 8,
    palette_name: str = "aurora",
    seed: int | None = None,
    width: int = 1200,
    height: int = 760,
) -> Path:
    """Generate a recursive tree fractal."""
    if seed is not None:
        random.seed(seed)
    palette = PALETTES.get(palette_name, PALETTES["aurora"])
    image = Image.new("RGBA", (width, height), (8, 10, 24, 255))
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    glow_draw = ImageDraw.Draw(glow, "RGBA")

    def branch(x: float, y: float, branch_length: float, branch_angle: float, level: int, line_width: int) -> None:
        if level <= 0 or branch_length < 3:
            return
        end_x = x + branch_length * math.cos(math.radians(branch_angle))
        end_y = y - branch_length * math.sin(math.radians(branch_angle))
        color = palette[level % len(palette)]
        alpha = int(90 + 165 * (level / max(depth, 1)))
        draw.line((x, y, end_x, end_y), fill=(*color, alpha), width=max(1, line_width))
        glow_draw.line((x, y, end_x, end_y), fill=(*color, 85), width=max(2, line_width * 2))
        jitter = random.uniform(-angle * randomness, angle * randomness)
        next_length = branch_length * random.uniform(0.68, 0.78)
        branch(end_x, end_y, next_length, branch_angle + angle + jitter, level - 1, line_width - 1)
        branch(end_x, end_y, next_length, branch_angle - angle + jitter, level - 1, line_width - 1)
        if level % 3 == 0:
            branch(end_x, end_y, next_length * 0.72, branch_angle + random.uniform(-12, 12), level - 2, line_width - 2)

    branch(width / 2, height - 54, length, 90, depth, thickness)
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    image.alpha_composite(glow)
    image.convert("RGB").save(output_path, "PNG", optimize=True)
    return output_path
