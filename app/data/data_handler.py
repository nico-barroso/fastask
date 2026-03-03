import json
from functools import partial


def load_json(file_path: str):
    """
    file_path(String):reads the JSON file from the path provided.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError as error:
        print(f"Error. File not found", error)
        return []
    except json.JSONDecodeError as error:
        print(f"There's a format error in the file", error)    
        return []  

def write_json(file_path: str, data: list):
    """
    file_path(String):reads the JSON file from the path provided.
    """
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)
        return data
    except FileNotFoundError as error:
        print(f"Error. File not found", error)
        return []

load_tasks = partial(load_json, "data/tasks.json")
write_tasks = partial(write_json, "data/tasks.json")