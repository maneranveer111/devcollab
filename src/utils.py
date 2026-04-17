import math

def paginate(items: list, page: int, limit: int):
    """
    Paginate a plain Python list.
    Returns (paginated_items, pagination_metadata)
    """
    page = max(1, page)
    limit = max(1, min(100, limit))

    total = len(items)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start = (page - 1) * limit
    end = start + limit

    paginated_items = items[start:end]

    pagination = {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

    return paginated_items, pagination