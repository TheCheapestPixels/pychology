import pytest

from pychology.blackboard import Blackboard


def test_basic():
    bb = Blackboard()
    key = ('foo', )
    assert key not in bb
    bb[key] = 23
    assert key in bb
    v = bb[key]
    assert v == 23
    del bb[key]
    assert key not in bb


def test_with_parent():
    bb_parent = Blackboard()
    bb_child = Blackboard(parent=bb_parent)
    key = ('foo', )

    bb_parent[key] = 23
    assert key in bb_child
    assert bb_child[key] == 23
    with pytest.raises(KeyError):
        del bb_child[key]
