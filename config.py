"""Application configuration for Interactive Generative Studio."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Default Flask configuration."""

    SECRET_KEY = "interactive-generative-studio-dev-key"
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    GENERATED_FOLDER = BASE_DIR / "static" / "generated"
    DOWNLOAD_FOLDER = BASE_DIR / "static" / "downloads"
    DATASET_FOLDER = BASE_DIR / "datasets"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    GALLERY_INDEX = GENERATED_FOLDER / "gallery.json"
    IMAGE_MAX_SIZE = (1400, 1400)
