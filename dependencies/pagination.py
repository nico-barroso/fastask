from fastapi import Query


class Pagination:
    def __init__(
        self,
        page: int | None = Query(default=None, ge=1),
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
    ):
        self.limit = limit
        self.skip = skip if page is None else (page - 1) * limit
