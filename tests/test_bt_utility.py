from pychology.behavior_trees import NodeState
from pychology.behavior_trees import Action

from pychology.bt_utility import BTReasoner
from pychology.bt_utility import BTOption
from pychology.bt_utility import BTConsideration
from pychology.bt_utility import RankDownOnSuccess


def set_result(value):
    def inner(env):
        env['result'] = value
        return NodeState.DONE
    return inner


def append_result(value):
    def inner(env):
        env.append(value)
        return NodeState.DONE
    return inner


class InstrumentedConsideration(BTConsideration):
    def select(self, environment):
        environment.append('_'.join([self.name, 'select']))

    def done(self, environment):
        environment.append('_'.join([self.name, 'done']))

    def active(self, environment):
        environment.append('_'.join([self.name, 'active']))

    def failed(self, environment):
        environment.append('_'.join([self.name, 'failed']))


def test_consideration_invocations():
    ai = BTReasoner(
        BTOption(
            Action(append_result("1_processing")),
            InstrumentedConsideration(
                lambda env: (0, 1.0, 1.0),
                name="1",
            ),
        ),
    )
    env = list()
    ai(env)
    assert env == ["1_select", "1_processing", "1_done"]


def test_selection_change():
    ai = BTReasoner(
        BTOption(
            Action(append_result("1_processing")),
            InstrumentedConsideration(
                lambda env: (-1000, 1.0, 1.0),
                name="1",
            ),
            RankDownOnSuccess(rank=2, decay=2)
        ),
        BTOption(
            Action(append_result("2_processing")),
            InstrumentedConsideration(
                lambda env: (1, 1.0, 1.0),
                name="2",
            ),
        ),
    )
    env = list()
    ai(env)
    assert env == ["1_select", "1_processing", "1_done"]
    ai(env)
    assert env == [
        "1_select", "1_processing", "1_done",
        "2_select", "2_processing", "2_done",
    ]


def test_bt_utility_integration():
    ai = BTReasoner(
        BTOption(
            Action(set_result("1_processing")),
            BTConsideration(
                lambda env: (0, 1.0, 1.0),
                name="1",
            ),
        ),
    )
    env = dict()
    ai(env)
    assert env == dict(result="1_processing")
