"""Image transformations and dominant color extraction."""

from __future__ import annotations

from PIL import Image, ImageOps
import numpy as np
from sklearn.cluster import KMeans


def transform_image(image: Image.Image, transform: str) -> Image.Image:
    """Apply orientation transformations."""
    if transform == "mirror":
        return ImageOps.mirror(image)
    if transform == "flip":
        return ImageOps.flip(image)
    if transform == "rotate_left":
        return image.rotate(90, expand=True)
    if transform == "rotate_right":
        return image.rotate(-90, expand=True)
    return image


def extract_dominant_colors(image: Image.Image, count: int = 8) -> list[str]:
    """Extract dominant colors using KMeans."""
    sample = image.convert("RGB").resize((120, 120))
    pixels = np.array(sample).reshape(-1, 3)
    clusters = KMeans(n_clusters=count, n_init=10, random_state=42).fit(pixels)
    colors = clusters.cluster_centers_.astype(int)
    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in colors]
