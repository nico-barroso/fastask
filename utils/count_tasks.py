
def count_tasks(list_id: str, tasks: list) -> int:
    return sum(1 for t in tasks if t["list_id"] == list_id and not t["is_deleted"])