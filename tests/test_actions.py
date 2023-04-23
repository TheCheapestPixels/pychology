import pytest

from pychology.behavior_trees import NodeState
from pychology.behavior_trees import Action


def condition_true(entity):
    return True


def condition_false(entity):
    return False


class return_value:
    def __init__(self):
        self.has_been_called = False
        self.times_called = 0
        self.last_entity = None
        self.last_args = None
        self.last_kwargs = None
        self.has_been_reset = False

    def __call__(self, entity, *args, **kwargs):
        self.has_been_called = True
        self.times_called += 1
        self.last_entity = entity
        self.last_args = args
        self.last_kwargs = kwargs
        return self.ret_val()

    def reset(self):
        self.has_been_reset = True


class return_done(return_value):
    def ret_val(self):
        return NodeState.DONE


class return_active(return_value):
    def ret_val(self):
        return NodeState.ACTIVE


class return_failed(return_value):
    def ret_val(self):
        return NodeState.FAILED


@pytest.mark.parametrize(
    'func, end_state',
    [
        (return_done, NodeState.DONE),
        (return_active, NodeState.ACTIVE),
        (return_failed, NodeState.FAILED),
    ],
)
def test_action(func, end_state):
    node = Action(func())
    assert node(0) == end_state


from pychology.behavior_trees import ReturnActiveAlways
from pychology.behavior_trees import ReturnDoneAlways
from pychology.behavior_trees import ReturnFailedAlways


@pytest.mark.parametrize(
    'decorator_class, action_class, end_state',
    [
        (ReturnActiveAlways, return_active, NodeState.ACTIVE),
        (ReturnActiveAlways, return_done,   NodeState.ACTIVE),
        (ReturnActiveAlways, return_failed, NodeState.ACTIVE),
        (ReturnDoneAlways,   return_active, NodeState.DONE),
        (ReturnDoneAlways,   return_done,   NodeState.DONE),
        (ReturnDoneAlways,   return_failed, NodeState.DONE),
        (ReturnFailedAlways, return_active, NodeState.FAILED),
        (ReturnFailedAlways, return_done,   NodeState.FAILED),
        (ReturnFailedAlways, return_failed, NodeState.FAILED),
    ],
)
def test_return_value_decorator(decorator_class, action_class, end_state):
    node = decorator_class(action_class())
    assert node(0) == end_state


from pychology.behavior_trees import FailOnPrecondition
from pychology.behavior_trees import ActiveOnPrecondition
from pychology.behavior_trees import DoneOnPrecondition
from pychology.behavior_trees import FailOnPostcondition
from pychology.behavior_trees import ActiveOnPostcondition
from pychology.behavior_trees import DoneOnPostcondition


@pytest.mark.parametrize(
    'decorator_class, condition, action, end_state, action_entered',
    [
        (ActiveOnPrecondition,  condition_false, return_active, NodeState.ACTIVE, True),
        (  DoneOnPrecondition,  condition_false, return_active, NodeState.ACTIVE, True),
        (  FailOnPrecondition,  condition_false, return_active, NodeState.ACTIVE, True),
        (ActiveOnPrecondition,  condition_false, return_done,   NodeState.DONE,   True),
        (  DoneOnPrecondition,  condition_false, return_done,   NodeState.DONE,   True),
        (  FailOnPrecondition,  condition_false, return_done,   NodeState.DONE,   True),
        (ActiveOnPrecondition,  condition_false, return_failed, NodeState.FAILED, True),
        (  DoneOnPrecondition,  condition_false, return_failed, NodeState.FAILED, True),
        (  FailOnPrecondition,  condition_false, return_failed, NodeState.FAILED, True),
        (ActiveOnPrecondition,  condition_true,  return_active, NodeState.ACTIVE, False),
        (  DoneOnPrecondition,  condition_true,  return_active, NodeState.DONE,   False),
        (  FailOnPrecondition,  condition_true,  return_active, NodeState.FAILED, False),
        (ActiveOnPrecondition,  condition_true,  return_done,   NodeState.ACTIVE, False),
        (  DoneOnPrecondition,  condition_true,  return_done,   NodeState.DONE,   False),
        (  FailOnPrecondition,  condition_true,  return_done,   NodeState.FAILED, False),
        (ActiveOnPrecondition,  condition_true,  return_failed, NodeState.ACTIVE, False),
        (  DoneOnPrecondition,  condition_true,  return_failed, NodeState.DONE,   False),
        (  FailOnPrecondition,  condition_true,  return_failed, NodeState.FAILED, False),
        (ActiveOnPostcondition, condition_false, return_active, NodeState.ACTIVE, True),
        (  DoneOnPostcondition, condition_false, return_active, NodeState.ACTIVE, True),
        (  FailOnPostcondition, condition_false, return_active, NodeState.ACTIVE, True),
        (ActiveOnPostcondition, condition_false, return_done,   NodeState.DONE,   True),
        (  DoneOnPostcondition, condition_false, return_done,   NodeState.DONE,   True),
        (  FailOnPostcondition, condition_false, return_done,   NodeState.DONE,   True),
        (ActiveOnPostcondition, condition_false, return_failed, NodeState.FAILED, True),
        (  DoneOnPostcondition, condition_false, return_failed, NodeState.FAILED, True),
        (  FailOnPostcondition, condition_false, return_failed, NodeState.FAILED, True),
        (ActiveOnPostcondition, condition_true,  return_active, NodeState.ACTIVE, True),
        (  DoneOnPostcondition, condition_true,  return_active, NodeState.DONE,   True),
        (  FailOnPostcondition, condition_true,  return_active, NodeState.FAILED, True),
        (ActiveOnPostcondition, condition_true,  return_done,   NodeState.ACTIVE, True),
        (  DoneOnPostcondition, condition_true,  return_done,   NodeState.DONE,   True),
        (  FailOnPostcondition, condition_true,  return_done,   NodeState.FAILED, True),
        (ActiveOnPostcondition, condition_true,  return_failed, NodeState.ACTIVE, True),
        (  DoneOnPostcondition, condition_true,  return_failed, NodeState.DONE,   True),
        (  FailOnPostcondition, condition_true,  return_failed, NodeState.FAILED, True),
    ],
)
def test_condition_decorator(decorator_class, condition, action, end_state, action_entered):
    action_node = action()
    node = decorator_class(condition, Action(action_node))
    assert node(0) == end_state
    assert action_node.has_been_called == action_entered


from pychology.behavior_trees import ReturnFailedOnActive
from pychology.behavior_trees import ReturnDoneOnActive
from pychology.behavior_trees import ReturnActiveOnDone
from pychology.behavior_trees import ReturnFailedOnDone
from pychology.behavior_trees import ReturnActiveOnFailed
from pychology.behavior_trees import ReturnDoneOnFailed

    
@pytest.mark.parametrize(
    'decorator_class, action, end_state',
    [
        (ReturnFailedOnActive, return_active, NodeState.FAILED),
        (ReturnFailedOnActive, return_done,   NodeState.DONE),
        (ReturnFailedOnActive, return_failed, NodeState.FAILED),
        (  ReturnDoneOnActive, return_active, NodeState.DONE),
        (  ReturnDoneOnActive, return_done,   NodeState.DONE),
        (  ReturnDoneOnActive, return_failed, NodeState.FAILED),
        (ReturnActiveOnDone,   return_active, NodeState.ACTIVE),
        (ReturnActiveOnDone,   return_done,   NodeState.ACTIVE),
        (ReturnActiveOnDone,   return_failed, NodeState.FAILED),
        (ReturnFailedOnDone,   return_active, NodeState.ACTIVE),
        (ReturnFailedOnDone,   return_done,   NodeState.FAILED),
        (ReturnFailedOnDone,   return_failed, NodeState.FAILED),
        (ReturnActiveOnFailed, return_active, NodeState.ACTIVE),
        (ReturnActiveOnFailed, return_done,   NodeState.DONE),
        (ReturnActiveOnFailed, return_failed, NodeState.ACTIVE),
        (  ReturnDoneOnFailed, return_active, NodeState.ACTIVE),
        (  ReturnDoneOnFailed, return_done,   NodeState.DONE),
        (  ReturnDoneOnFailed, return_failed, NodeState.DONE),
    ],
)
def test_return_value_rewriting_decorator(decorator_class, action, end_state):
    node = decorator_class(Action(action()))
    assert node(0) == end_state


from pychology.behavior_trees import RewriteArguments


def test_argument_rewriting_decorator():
    def rewriting_func(*args, **kwargs):
        new_args = (1, )
        new_kwargs = {'foo': 1}
        return new_args, new_kwargs

    action_node = return_done()
    node = RewriteArguments(rewriting_func, Action(action_node))

    node(0)
    assert action_node.last_entity == 0
    assert action_node.last_args == (1, )
    assert action_node.last_kwargs == {'foo': 1}


from pychology.behavior_trees import FailOnPrecounter
from pychology.behavior_trees import ActiveOnPrecounter
from pychology.behavior_trees import DoneOnPrecounter
from pychology.behavior_trees import FailOnPostcounter
from pychology.behavior_trees import ActiveOnPostcounter
from pychology.behavior_trees import DoneOnPostcounter


@pytest.mark.parametrize(
    'decorator_class, action, end_state, calls',
    [
        (  FailOnPrecounter,  return_active, NodeState.FAILED, 1),
        (ActiveOnPrecounter,  return_active, NodeState.ACTIVE, 1),
        (  DoneOnPrecounter,  return_active, NodeState.DONE,   1),
        (  FailOnPostcounter, return_active, NodeState.FAILED, 2),
        (ActiveOnPostcounter, return_active, NodeState.ACTIVE, 2),
        (  DoneOnPostcounter, return_active, NodeState.DONE,   2), 
        (  FailOnPrecounter,  return_done,   NodeState.FAILED, 1),
        (ActiveOnPrecounter,  return_done,   NodeState.ACTIVE, 1),
        (  DoneOnPrecounter,  return_done,   NodeState.DONE,   1),
        (  FailOnPostcounter, return_done,   NodeState.FAILED, 2),
        (ActiveOnPostcounter, return_done,   NodeState.ACTIVE, 2),
        (  DoneOnPostcounter, return_done,   NodeState.DONE,   2), 
        (  FailOnPrecounter,  return_failed, NodeState.FAILED, 1),
        (ActiveOnPrecounter,  return_failed, NodeState.ACTIVE, 1),
        (  DoneOnPrecounter,  return_failed, NodeState.DONE,   1),
        (  FailOnPostcounter, return_failed, NodeState.FAILED, 2),
        (ActiveOnPostcounter, return_failed, NodeState.ACTIVE, 2),
        (  DoneOnPostcounter, return_failed, NodeState.DONE,   2), 
    ],
)
def test_counter_decorators(decorator_class, action, end_state, calls):
    action_node = action()
    node = decorator_class(2, Action(action_node))
    node(0)
    assert node(0) == end_state
    assert action_node.times_called == calls


from pychology.behavior_trees import Chain
from pychology.behavior_trees import Priorities
from pychology.behavior_trees import Parallel


@pytest.mark.parametrize(
    'action_a, action_b, end_state, calls_a, calls_b',
    [
        (return_active, return_active, NodeState.ACTIVE, 1, 0),
        (return_active, return_done,   NodeState.ACTIVE, 1, 0),
        (return_active, return_failed, NodeState.ACTIVE, 1, 0),
        (return_done,   return_active, NodeState.ACTIVE, 1, 1),
        (return_done,   return_done,   NodeState.DONE,   1, 1),
        (return_done,   return_failed, NodeState.FAILED, 1, 1),
        (return_failed, return_active, NodeState.FAILED, 1, 0),
        (return_failed, return_done,   NodeState.FAILED, 1, 0),
        (return_failed, return_failed, NodeState.FAILED, 1, 0),
    ],
)
def test_chain(action_a, action_b, end_state, calls_a, calls_b):
    a = action_a()
    b = action_b()
    node = Chain(
        a,
        b,
    )

    assert node(0) == end_state
    assert a.times_called == calls_a
    assert b.times_called == calls_b


@pytest.mark.parametrize(
    'action_a, action_b, end_state, calls_a, calls_b',
    [
        (return_active, return_active, NodeState.ACTIVE, 1, 0),
        (return_active, return_done,   NodeState.ACTIVE, 1, 0),
        (return_active, return_failed, NodeState.ACTIVE, 1, 0),
        (return_done,   return_active, NodeState.DONE,   1, 0),
        (return_done,   return_done,   NodeState.DONE,   1, 0),
        (return_done,   return_failed, NodeState.DONE,   1, 0),
        (return_failed, return_active, NodeState.ACTIVE, 1, 1),
        (return_failed, return_done,   NodeState.DONE,   1, 1),
        (return_failed, return_failed, NodeState.FAILED, 1, 1),
    ],
)
def test_priorities(action_a, action_b, end_state, calls_a, calls_b):
    a = action_a()
    b = action_b()
    node = Priorities(
        a,
        b,
    )

    assert node(0) == end_state
    assert a.times_called == calls_a
    assert b.times_called == calls_b


@pytest.mark.parametrize(
    'action_a, action_b, end_state, calls_a, calls_b',
    [
        (return_active, return_active, NodeState.ACTIVE, 1, 1),
        (return_active, return_done,   NodeState.ACTIVE, 1, 1),
        (return_active, return_failed, NodeState.FAILED, 1, 1),
        (return_done,   return_active, NodeState.ACTIVE, 1, 1),
        (return_done,   return_done,   NodeState.DONE,   1, 1),
        (return_done,   return_failed, NodeState.FAILED, 1, 1),
        (return_failed, return_active, NodeState.FAILED, 1, 1),
        (return_failed, return_done,   NodeState.FAILED, 1, 1),
        (return_failed, return_failed, NodeState.FAILED, 1, 1),
    ],
)
def test_parallel(action_a, action_b, end_state, calls_a, calls_b):
    a = action_a()
    b = action_b()
    node = Parallel(
        a,
        b,
    )

    assert node(0) == end_state
    assert a.times_called == calls_a
    assert b.times_called == calls_b
