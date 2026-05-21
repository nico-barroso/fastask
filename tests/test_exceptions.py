import pytest
from fastapi import HTTPException

from exceptions.exceptions import ApiException


def test_not_found_task():
    with pytest.raises(HTTPException) as exc_info:
        raise ApiException.NotFound.task("12345")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Task "12345" not found'
