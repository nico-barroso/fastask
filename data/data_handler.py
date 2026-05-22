import json
from functools import partial
from pathlib import Path

from exceptions.exceptions import ApiException

BASE_DIR = Path(__file__).parent


def load_json(file_path: Path):
    """
    Read and parse a JSON file from the given path.
    Returns an empty list if the file is not found or has a format error.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError as error:
        raise ApiException.StorageError.raise_(str(error))

    except json.JSONDecodeError as error:
        raise ApiException.InternalError.raise_(str(error))


def write_json(file_path: Path, data: list):
    """
    Serialize and write a list to a JSON file at the given path.
    Returns an empty list if the file is not found.
    """
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)
        return data
    except FileNotFoundError as error:
        raise ApiException.StorageError.raise_(str(error))


load_tasks = partial(load_json, BASE_DIR / "tasks.json")
write_tasks = partial(write_json, BASE_DIR / "tasks.json")

load_lists = partial(load_json, BASE_DIR / "lists.json")
write_lists = partial(write_json, BASE_DIR / "lists.json")
