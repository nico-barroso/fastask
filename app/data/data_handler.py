import json
import os
from functools import partial


def load_data(file_path: str):
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


load_tasks = partial(load_data, "data/tasks.json")
