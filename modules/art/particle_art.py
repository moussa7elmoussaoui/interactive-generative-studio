"""Particle artwork still-frame generator for gallery snapshots."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

from modules.art.random_art import PALETTES


def generate_particle_snapshot(
    output_path: Path,
    particle_count: int = 140,
    palette_name: str = "cyber",
    width: int = 1200,
    height: int = 760,
    seed: int | None = None,
) -> Path:
    """Generate a particle-network PNG for download and gallery use."""
    if seed is not None:
        random.seed(seed)
    palette = PALETTES.get(palette_name, PALETTES["cyber"])
    particles = [
        {
            "x": random.uniform(0, width),
            "y": random.uniform(0, height),
            "vx": random.uniform(-1, 1),
            "vy": random.uniform(-1, 1),
            "color": random.choice(palette),
        }
        for _ in range(particle_count)
    ]
    image = Image.new("RGBA", (width, height), (7, 9, 22, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    for i, first in enumerate(particles):
        for second in particles[i + 1:]:
            distance = math.hypot(first["x"] - second["x"], first["y"] - second["y"])
            if distance < 120:
                alpha = int(130 * (1 - distance / 120))
                draw.line((first["x"], first["y"], second["x"], second["y"]), fill=(120, 170, 255, alpha), width=1)
    for particle in particles:
        rgb = particle["color"]
        r = random.uniform(2.5, 6.5)
        draw.ellipse((particle["x"] - r, particle["y"] - r, particle["x"] + r, particle["y"] + r), fill=(*rgb, 220))
    image.convert("RGB").save(output_path, "PNG", optimize=True)
    return output_path
