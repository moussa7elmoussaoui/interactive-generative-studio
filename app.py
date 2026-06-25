"""Interactive Generative Studio Flask application."""

from __future__ import annotations

import secrets
import os
from pathlib import Path
from typing import Any

from flask import Flask, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_wtf import FlaskForm
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from wtforms import FileField
from wtforms.validators import DataRequired

from config import Config

os.environ.setdefault("MPLCONFIGDIR", str(Config.GENERATED_FOLDER / ".matplotlib"))

from modules.art.fractal_art import generate_fractal
from modules.art.particle_art import generate_particle_snapshot
from modules.art.random_art import PALETTES, generate_random_art
from modules.image_processing.filters import adjust_image, apply_filter
from modules.image_processing.transformations import extract_dominant_colors, transform_image
from modules.utils.gallery import add_gallery_item, delete_gallery_item, load_gallery
from modules.visualization.data_art import generate_data_art
from modules.visualization.preprocessing import load_and_prepare_dataset


class UploadForm(FlaskForm):
    """Image upload form."""

    image = FileField("Image", validators=[DataRequired()])


def create_app() -> Flask:
    """Create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)
    for folder in [Config.UPLOAD_FOLDER, Config.GENERATED_FOLDER, Config.DOWNLOAD_FOLDER]:
        folder.mkdir(parents=True, exist_ok=True)

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        return {"palettes": PALETTES}

    @app.route("/")
    def index() -> str:
        items = load_gallery(Config.GALLERY_INDEX)
        stats = {
            "artworks": len(items),
            "palettes": len(PALETTES),
            "filters": 22,
            "datasets": len(list(Config.DATASET_FOLDER.glob("*.csv"))),
        }
        return render_template("index.html", stats=stats)

    @app.route("/generative")
    def generative() -> str:
        return render_template("generative.html")

    @app.post("/generative/random")
    def random_art() -> Any:
        filename = _filename("random", "png")
        output = Config.GENERATED_FOLDER / filename
        seed_raw = request.form.get("seed") or None
        seed = int(seed_raw) if seed_raw and seed_raw.isdigit() else None
        _, shapes = generate_random_art(
            output,
            palette_name=request.form.get("palette", "aurora"),
            shape_count=_int_form("shape_count", 90, 8, 260),
            max_size=_int_form("max_size", 120, 20, 260),
            alpha=_float_form("alpha", 0.72, 0.1, 1),
            seed=seed,
        )
        add_gallery_item(Config.GALLERY_INDEX, filename, "Generative Art", "Random Geometry")
        return jsonify({"url": url_for("static", filename=f"generated/{filename}"), "filename": filename, "shapes": shapes})

    @app.post("/generative/particles")
    def particles() -> Any:
        filename = _filename("particles", "png")
        generate_particle_snapshot(
            Config.GENERATED_FOLDER / filename,
            particle_count=_int_form("particle_count", 140, 20, 420),
            palette_name=request.form.get("palette", "cyber"),
        )
        add_gallery_item(Config.GALLERY_INDEX, filename, "Generative Art", "Particle System")
        return jsonify({"url": url_for("static", filename=f"generated/{filename}"), "filename": filename})

    @app.post("/generative/fractal")
    def fractal() -> Any:
        filename = _filename("fractal", "png")
        generate_fractal(
            Config.GENERATED_FOLDER / filename,
            depth=_int_form("depth", 9, 2, 13),
            angle=_float_form("angle", 24, 5, 55),
            length=_float_form("length", 150, 40, 260),
            randomness=_float_form("randomness", 0.18, 0, 0.7),
            thickness=_int_form("thickness", 8, 1, 18),
            palette_name=request.form.get("palette", "aurora"),
            seed=secrets.randbelow(999999),
        )
        add_gallery_item(Config.GALLERY_INDEX, filename, "Generative Art", "Recursive Fractal")
        return jsonify({"url": url_for("static", filename=f"generated/{filename}"), "filename": filename})

    @app.route("/visualization", methods=["GET", "POST"])
    def visualization() -> Any:
        datasets = sorted(path.name for path in Config.DATASET_FOLDER.glob("*.csv"))
        if request.method == "POST":
            dataset = secure_filename(request.form.get("dataset", "stocks.csv"))
            dataset_path = Config.DATASET_FOLDER / dataset
            if not dataset_path.exists():
                flash("Dataset not found.", "error")
                return redirect(url_for("visualization"))
            filename = _filename("visualization", "png")
            frame = load_and_prepare_dataset(dataset_path)
            generate_data_art(
                frame,
                Config.GENERATED_FOLDER / filename,
                style=request.form.get("style", "landscape"),
                palette_name=request.form.get("palette", "aurora"),
                alpha=_float_form("alpha", 0.78, 0.15, 1),
            )
            add_gallery_item(Config.GALLERY_INDEX, filename, "Data Visualization", request.form.get("style", "Landscape"))
            flash("Visualization generated.", "success")
            return render_template("visualization.html", datasets=datasets, generated=filename)
        return render_template("visualization.html", datasets=datasets, generated=None)

    @app.route("/image-tools", methods=["GET", "POST"])
    def image_tools() -> Any:
        form = UploadForm()
        context: dict[str, Any] = {"form": form, "original": None, "processed": None, "colors": []}
        if request.method == "POST":
            uploaded = request.files.get("image")
            if not uploaded or uploaded.filename == "":
                flash("Choose an image before processing.", "error")
                return render_template("image_tools.html", **context)
            try:
                original_name, image = _load_upload(uploaded)
                processed = transform_image(image, request.form.get("transform", "none"))
                processed = apply_filter(processed, request.form.get("filter", "none"), _float_form("intensity", 1, 0.2, 2))
                processed = adjust_image(
                    processed,
                    brightness=_float_form("brightness", 1, 0.2, 2),
                    contrast=_float_form("contrast", 1, 0.2, 2),
                    saturation=_float_form("saturation", 1, 0, 2.5),
                    hue=_int_form("hue", 0, -127, 127),
                )
                processed_name = _filename("processed", "png")
                processed.save(Config.GENERATED_FOLDER / processed_name, "PNG", optimize=True)
                colors = extract_dominant_colors(processed)
                add_gallery_item(Config.GALLERY_INDEX, processed_name, "Image Studio", "Processed Image")
                flash("Image processed successfully.", "success")
                context.update({"original": original_name, "processed": processed_name, "colors": colors})
            except ValueError as exc:
                flash(str(exc), "error")
            except Exception:
                app.logger.exception("Image processing failed")
                flash("The image could not be processed. Try a smaller file or another format.", "error")
        return render_template("image_tools.html", **context)

    @app.route("/upload", methods=["POST"])
    def upload() -> Any:
        uploaded = request.files.get("image")
        if not uploaded:
            return jsonify({"error": "No image uploaded."}), 400
        try:
            filename, image = _load_upload(uploaded)
            return jsonify({"filename": filename, "colors": extract_dominant_colors(image)})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.route("/gallery")
    def gallery() -> str:
        query = request.args.get("q", "").lower()
        module_filter = request.args.get("module", "")
        page = max(int(request.args.get("page", 1)), 1)
        per_page = 9
        items = load_gallery(Config.GALLERY_INDEX)
        if query:
            items = [item for item in items if query in item.get("title", "").lower() or query in item.get("module", "").lower()]
        if module_filter:
            items = [item for item in items if item.get("module") == module_filter]
        total_pages = max(1, (len(items) + per_page - 1) // per_page)
        start = (page - 1) * per_page
        return render_template("gallery.html", items=items[start:start + per_page], page=page, total_pages=total_pages, query=query, module_filter=module_filter)

    @app.post("/gallery/delete/<filename>")
    def delete_gallery(filename: str) -> Any:
        safe = secure_filename(filename)
        delete_gallery_item(Config.GALLERY_INDEX, safe, Config.GENERATED_FOLDER)
        flash("Gallery item deleted.", "success")
        return redirect(url_for("gallery"))

    @app.route("/about")
    def about() -> str:
        return render_template("about.html")

    @app.route("/download/<filename>")
    def download(filename: str) -> Any:
        safe = secure_filename(filename)
        target = Config.GENERATED_FOLDER / safe
        if not target.exists():
            flash("That file is no longer available.", "error")
            return redirect(url_for("gallery"))
        return send_from_directory(Config.GENERATED_FOLDER, safe, as_attachment=True)

    @app.errorhandler(413)
    def too_large(_: Exception) -> tuple[str, int]:
        return render_template("base.html", fatal_error="The upload is too large. Please use an image under 8 MB."), 413

    @app.errorhandler(404)
    def not_found(_: Exception) -> tuple[str, int]:
        return render_template("base.html", fatal_error="The requested page was not found."), 404

    @app.errorhandler(500)
    def server_error(_: Exception) -> tuple[str, int]:
        app.logger.exception("Unhandled exception")
        return render_template("base.html", fatal_error="Something went wrong, but the studio is still intact."), 500

    return app


def _filename(prefix: str, extension: str) -> str:
    return f"{prefix}-{secrets.token_hex(8)}.{extension}"


def _int_form(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(float(request.form.get(name, default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def _float_form(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(request.form.get(name, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def _load_upload(uploaded: FileStorage) -> tuple[str, Image.Image]:
    extension = Path(uploaded.filename or "").suffix.lower().lstrip(".")
    if extension not in Config.ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported image format. Use PNG, JPEG, or WEBP.")
    filename = _filename("upload", "png")
    try:
        image = Image.open(uploaded.stream)
        image.verify()
        uploaded.stream.seek(0)
        image = Image.open(uploaded.stream).convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("The uploaded file is not a valid image.") from exc
    image.thumbnail(Config.IMAGE_MAX_SIZE)
    image.save(Config.UPLOAD_FOLDER / filename, "PNG", optimize=True)
    return filename, image


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
