"""Gallery persistence helpers."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def load_gallery(index_path: Path) -> list[dict[str, Any]]:
    """Load gallery metadata."""
    if not index_path.exists():
        return []
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_gallery(index_path: Path, items: list[dict[str, Any]]) -> None:
    """Save gallery metadata."""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(items, indent=2), encoding="utf-8")


def add_gallery_item(index_path: Path, filename: str, module: str, title: str) -> dict[str, Any]:
    """Add a generated asset to the gallery."""
    items = load_gallery(index_path)
    item = {
        "filename": filename,
        "module": module,
        "title": title,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    items.insert(0, item)
    save_gallery(index_path, items)
    return item


def delete_gallery_item(index_path: Path, filename: str, generated_folder: Path) -> bool:
    """Delete gallery metadata and generated file."""
    items = load_gallery(index_path)
    remaining = [item for item in items if item.get("filename") != filename]
    changed = len(remaining) != len(items)
    if changed:
        save_gallery(index_path, remaining)
    target = generated_folder / filename
    if target.exists() and target.is_file():
        target.unlink()
        changed = True
    return changed
