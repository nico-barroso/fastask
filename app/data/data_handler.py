import json
import os


def load_data(file_path: str):
    """
    file_path(String): defines the JSON file path to be read.
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError as e:
        print(f"Error. File not found", e)
    except json.JSONDecodeError as e:
        print(f"There's a fortmar error in the file", e)      


load_tasks = lambda: load_data("data/tasks.json")
