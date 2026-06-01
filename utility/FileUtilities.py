import os
import json

TEMP_FILE_EXTENSION = ".tmp"

def atomic_write_json(save_path: str, json_data: dict):
    """write JSON data to a file atomically via a temporary file"""
    #create path for temporary file
    temp_path = save_path + TEMP_FILE_EXTENSION

    try:
        #create temporary file
        with open(temp_path, mode="w", encoding="utf-8") as file:
            #write the data as formatted JSON
            json.dump(json_data, file, ensure_ascii=False, indent=2)

        #replace existing file at the save path with temporary file
        os.replace(temp_path, save_path)    #atomic on most systems
    except Exception:
        #attempt to clean up temporary file
        try_remove_file(temp_path)
        raise

def try_remove_file(file_path):
    """remove a file if it exists, ignoring errors"""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
