from src.utils import paginate

def test_paginate_first_page():
    items = [1, 2, 3, 4, 5]
    paginated_items, pagination = paginate(items, page=1, limit=2)

    assert paginated_items == [1, 2]
    assert pagination["page"] == 1
    assert pagination["limit"] == 2
    assert pagination["total"] == 5
    assert pagination["pages"] == 3
    assert pagination["has_next"] is True
    assert pagination["has_prev"] is False

def test_paginate_second_page():
    items = [1, 2, 3, 4, 5]
    paginated_items, pagination = paginate(items, page=2, limit=2)

    assert paginated_items == [3, 4]
    assert pagination["page"] == 2
    assert pagination["has_next"] is True
    assert pagination["has_prev"] is True

def test_paginate_clamps_page_to_minimum_one():
    items = [1, 2, 3]
    paginated_items, pagination = paginate(items, page=0, limit=2)

    assert paginated_items == [1, 2]
    assert pagination["page"] == 1

def test_paginate_clamps_limit_to_minimum_one():
    items = [1, 2, 3]
    paginated_items, pagination = paginate(items, page=1, limit=0)

    assert paginated_items == [1]
    assert pagination["limit"] == 1

def test_paginate_clamps_limit_to_maximum_hundred():
    items = list(range(200))
    paginated_items, pagination = paginate(items, page=1, limit=1000)

    assert len(paginated_items) == 100
    assert pagination["limit"] == 100
    assert pagination["total"] == 200
    assert pagination["pages"] == 2

def test_paginate_empty_list():
    items = []
    paginated_items, pagination = paginate(items, page=1, limit=10)

    assert paginated_items == []
    assert pagination["total"] == 0
    assert pagination["pages"] == 1
    assert pagination["has_next"] is False
    assert pagination["has_prev"] is False