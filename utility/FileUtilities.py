import os
import json

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
