"""Random geometric artwork generator."""

from __future__ import annotations

import random
import math
from pathlib import Path

from PIL import Image, ImageDraw

from modules.art.shapes import Circle, Shape, Square, Triangle, shape_to_dict

PALETTES: dict[str, list[tuple[int, int, int]]] = {
    "aurora": [(124, 58, 237), (37, 99, 235), (236, 72, 153), (251, 146, 60)],
    "cyber": [(14, 165, 233), (217, 70, 239), (34, 197, 94), (250, 204, 21)],
    "sunset": [(244, 63, 94), (249, 115, 22), (168, 85, 247), (59, 130, 246)],
    "mono": [(226, 232, 240), (148, 163, 184), (100, 116, 139), (51, 65, 85)],
}


def generate_random_art(
    output_path: Path,
    palette_name: str = "aurora",
    shape_count: int = 80,
    max_size: int = 120,
    alpha: float = 0.72,
    seed: int | None = None,
    width: int = 1200,
    height: int = 760,
) -> tuple[Path, list[dict[str, object]]]:
    """Generate a PNG and return serialized shapes for Canvas editing."""
    if seed is not None:
        random.seed(seed)
    palette = PALETTES.get(palette_name, PALETTES["aurora"])
    image = Image.new("RGBA", (width, height), (9, 11, 25, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    shapes: list[dict[str, object]] = []

    for _ in range(shape_count):
        shape_type = random.choice(["circle", "square", "triangle", "line"])
        rgb = random.choice(palette)
        stroke_rgb = random.choice(palette)
        fill = (*rgb, int(255 * max(0.08, min(alpha, 1))))
        stroke = (*stroke_rgb, int(255 * 0.9))
        size = random.randint(18, max_size)
        x = random.randint(0, width)
        y = random.randint(0, height)
        rotation = random.uniform(0, 360)
        stroke_width = random.randint(1, 5)

        if shape_type == "line":
            length = size * random.uniform(1.2, 2.6)
            angle = math.radians(rotation)
            x2 = x + length * math.cos(angle)
            y2 = y + length * math.sin(angle)
            draw.line((x, y, x2, y2), fill=stroke, width=stroke_width)
            shapes.append({
                "type": "line",
                "x": x,
                "y": y,
                "x2": x2,
                "y2": y2,
                "size": size,
                "rotation": rotation,
                "color": f"rgba({fill[0]}, {fill[1]}, {fill[2]}, {fill[3] / 255:.3f})",
                "stroke": f"rgba({stroke[0]}, {stroke[1]}, {stroke[2]}, {stroke[3] / 255:.3f})",
            })
            continue

        shape: Shape
        if shape_type == "circle":
            shape = Circle(x, y, fill, rotation, size, stroke, stroke_width)
        elif shape_type == "square":
            shape = Square(x, y, fill, rotation, size, stroke, stroke_width)
        else:
            shape = Triangle(x, y, fill, rotation, size, stroke, stroke_width)
        shape.draw(draw)
        shapes.append(shape_to_dict(shape, shape_type))

    _add_glow_overlay(image, palette)
    image.convert("RGB").save(output_path, "PNG", optimize=True)
    return output_path, shapes


def _add_glow_overlay(image: Image.Image, palette: list[tuple[int, int, int]]) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    width, height = image.size
    for rgb in palette:
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(160, 320)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*rgb, 22))
    image.alpha_composite(overlay)
