from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy.orm import Query

T = TypeVar("T")


def paginate(items: Sequence[T], page: int = 1, page_size: int = 20) -> dict:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": list(items[start:end]),
        "page": page,
        "page_size": page_size,
        "total": len(items),
    }


def apply_offset(query: Query, page: int = 1, page_size: int = 20) -> Query:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    return query.offset((page - 1) * page_size).limit(page_size)
