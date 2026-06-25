"""Object-oriented shape primitives used by the random art generator."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

from PIL import ImageDraw


@dataclass
class Shape:
    """Base drawable shape."""

    x: float
    y: float
    color: tuple[int, int, int, int]
    rotation: float
    size: float
    stroke: tuple[int, int, int, int]
    stroke_width: int = 2

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        """Draw the shape."""
        raise NotImplementedError

    def move(self, dx: float, dy: float) -> None:
        """Move the shape."""
        self.x += dx
        self.y += dy

    def rotate(self, degrees: float) -> None:
        """Rotate the shape."""
        self.rotation = (self.rotation + degrees) % 360

    def change_color(self, color: tuple[int, int, int, int]) -> None:
        """Change fill color."""
        self.color = color

    def randomize(self, width: int, height: int) -> None:
        """Randomize shape placement and angle."""
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.rotation = random.uniform(0, 360)


class Circle(Shape):
    """Circle primitive."""

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        radius = self.size / 2
        box = [self.x - radius, self.y - radius, self.x + radius, self.y + radius]
        draw.ellipse(box, fill=self.color, outline=self.stroke, width=self.stroke_width)


class Square(Shape):
    """Rotated square primitive."""

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        half = self.size / 2
        points = [(-half, -half), (half, -half), (half, half), (-half, half)]
        draw.polygon(_rotate_points(points, self.rotation, self.x, self.y), fill=self.color, outline=self.stroke)


class Triangle(Shape):
    """Rotated triangle primitive."""

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        radius = self.size / 2
        points = [
            (0, -radius),
            (radius * math.cos(math.radians(30)), radius / 2),
            (-radius * math.cos(math.radians(30)), radius / 2),
        ]
        draw.polygon(_rotate_points(points, self.rotation, self.x, self.y), fill=self.color, outline=self.stroke)


def _rotate_points(points: list[tuple[float, float]], angle: float, cx: float, cy: float) -> list[tuple[float, float]]:
    radians = math.radians(angle)
    cos_a = math.cos(radians)
    sin_a = math.sin(radians)
    return [(cx + px * cos_a - py * sin_a, cy + px * sin_a + py * cos_a) for px, py in points]


def shape_to_dict(shape: Shape, shape_type: str) -> dict[str, Any]:
    """Serialize a shape for the frontend canvas."""
    return {
        "type": shape_type,
        "x": shape.x,
        "y": shape.y,
        "size": shape.size,
        "rotation": shape.rotation,
        "color": f"rgba({shape.color[0]}, {shape.color[1]}, {shape.color[2]}, {shape.color[3] / 255:.3f})",
        "stroke": f"rgba({shape.stroke[0]}, {shape.stroke[1]}, {shape.stroke[2]}, {shape.stroke[3] / 255:.3f})",
    }
