import os
import json
from PIL import Image, ImageTk

_TEMP_FILE_EXTENSION = ".tmp"

def atomic_write_json(
    save_path: str,
    json_data: dict[str, object]
) -> None:
    """Serialize JSON data and atomically replace the destination file."""
    temp_path = save_path + _TEMP_FILE_EXTENSION

    try:
        with open(temp_path, mode="w", encoding="utf-8") as file:
            json.dump(json_data, file, ensure_ascii=False, indent=2)

        os.replace(temp_path, save_path)    #atomic on most systems
    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise

def load_icon(
    path: str,
    size: tuple[int, int]
) -> ImageTk.PhotoImage | None:
    """Return a resized photo image of the icon at the given path, or None if loading fails."""
    try:
        if path and os.path.exists(path):
            icon = Image.open(path)
            icon = icon.convert("RGBA")
            icon = icon.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(icon)
    except Exception:
        return None
