import pytest

from pychology.simple_search.a_star import search
from pychology.simple_search.a_star import get_neighbors_and_costs


def constant_zero(a, b):
    return 0.0


def test_basic():
    navgrid = dict(
        start=dict(middle=1),
        middle=dict(start=1, goal=1),
        goal=dict(middle=1),
    )
    path = search(
        get_neighbors_and_costs(navgrid),
        'start',
        'goal',
    )
    assert path == (2, ['start', 'middle', 'goal'])


def test_unconnected():
    navgrid = dict(
        start=dict(middle=1),
        middle=dict(start=1),
        goal=dict(middle=1),
    )
    with pytest.raises(Exception):
        path = search(get_neighbors_and_costs(navgrid), 'start', 'goal')


def test_short_expensive_path():
    navgrid = dict(
        start=dict(goal=5, long_path_1=1),
        long_path_1=dict(start=1, long_path_2=1),
        long_path_2=dict(long_path_1=1, long_path_3=1),
        long_path_3=dict(long_path_2=1, goal=1),
        goal=dict(start=5, long_path_3=1),
    )
    path = search(get_neighbors_and_costs(navgrid), 'start', 'goal')
    assert path == (4, ['start', 'long_path_1', 'long_path_2', 'long_path_3', 'goal'])
