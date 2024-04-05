import pytest

from pychology.blackboard import Blackboard


def test_basic():
    bb = Blackboard()
    assert 'foo' not in bb
    bb['foo'] = 23
    assert 'foo' in bb
    v = bb['foo']
    assert v == 23
    del bb['foo']
    assert 'foo' not in bb


def test_with_parent():
    bb_parent = Blackboard()
    bb_child = Blackboard(parent=bb_parent)

    bb_parent['foo'] = 23
    assert 'foo' in bb_child
    assert bb_child['foo'] == 23
    with pytest.raises(KeyError):
        del bb_child['foo']
