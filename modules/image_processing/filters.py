"""Pillow and OpenCV image filters."""

from __future__ import annotations

import random

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def apply_filter(image: Image.Image, filter_name: str, intensity: float = 1.0) -> Image.Image:
    """Apply a named image filter."""
    image = image.convert("RGB")
    if filter_name == "grayscale":
        return ImageOps.grayscale(image).convert("RGB")
    if filter_name == "sepia":
        gray = ImageOps.grayscale(image)
        return ImageOps.colorize(gray, "#21170f", "#ffd9a3")
    if filter_name == "negative":
        return ImageOps.invert(image)
    if filter_name == "blur":
        return image.filter(ImageFilter.BLUR)
    if filter_name == "gaussian_blur":
        return image.filter(ImageFilter.GaussianBlur(radius=2 + intensity * 3))
    if filter_name == "sharpen":
        return image.filter(ImageFilter.SHARPEN)
    if filter_name == "emboss":
        return image.filter(ImageFilter.EMBOSS)
    if filter_name == "edge":
        return image.filter(ImageFilter.FIND_EDGES)
    if filter_name == "cartoon":
        return _cartoon(image)
    if filter_name == "sketch":
        return _sketch(image)
    if filter_name == "watercolor":
        return _watercolor(image)
    if filter_name == "pixelation":
        return _pixelate(image)
    if filter_name == "neon":
        return ImageEnhance.Color(image.filter(ImageFilter.FIND_EDGES)).enhance(2.5)
    if filter_name == "vintage":
        return ImageEnhance.Contrast(apply_filter(image, "sepia")).enhance(0.82)
    if filter_name == "glitch":
        return _glitch(image)
    return image


def adjust_image(
    image: Image.Image,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    hue: int = 0,
) -> Image.Image:
    """Apply global color adjustments."""
    image = ImageEnhance.Brightness(image).enhance(brightness)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Color(image).enhance(saturation)
    if hue:
        hsv = np.array(image.convert("HSV"))
        hsv[..., 0] = (hsv[..., 0].astype(int) + hue) % 255
        image = Image.fromarray(hsv, "HSV").convert("RGB")
    return image


def _cv(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def _pil(array: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(array, cv2.COLOR_BGR2RGB))


def _cartoon(image: Image.Image) -> Image.Image:
    array = _cv(image)
    smooth = cv2.bilateralFilter(array, 9, 120, 120)
    gray = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    cartoon = cv2.bitwise_and(smooth, smooth, mask=edges)
    return _pil(cartoon)


def _sketch(image: Image.Image) -> Image.Image:
    gray = cv2.cvtColor(_cv(image), cv2.COLOR_BGR2GRAY)
    inverted = 255 - gray
    blur = cv2.GaussianBlur(inverted, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return Image.fromarray(sketch).convert("RGB")


def _watercolor(image: Image.Image) -> Image.Image:
    return _pil(cv2.stylization(_cv(image), sigma_s=80, sigma_r=0.45))


def _pixelate(image: Image.Image) -> Image.Image:
    small = image.resize((max(1, image.width // 18), max(1, image.height // 18)), Image.Resampling.BILINEAR)
    return small.resize(image.size, Image.Resampling.NEAREST)


def _glitch(image: Image.Image) -> Image.Image:
    array = np.array(image)
    result = array.copy()
    for _ in range(16):
        y = random.randint(0, max(0, image.height - 8))
        h = random.randint(2, 18)
        shift = random.randint(-36, 36)
        result[y:y + h] = np.roll(result[y:y + h], shift, axis=1)
    result[..., 0] = np.roll(result[..., 0], 5, axis=1)
    result[..., 2] = np.roll(result[..., 2], -5, axis=1)
    return Image.fromarray(result)
