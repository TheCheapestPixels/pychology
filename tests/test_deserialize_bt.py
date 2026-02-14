import pytest

from pychology.behavior_trees import NodeState
from pychology.behavior_trees import BehaviorTreeLoader
from pychology.behavior_trees import SaveableFunction
from pychology.behavior_trees import ActionFunction
from pychology.behavior_trees import ConditionFunction

from pychology.behavior_trees import BehaviorTree

from pychology.behavior_trees import DebugPrint
from pychology.behavior_trees import DebugPrintOnEnter
from pychology.behavior_trees import DebugPrintOnReset

from pychology.behavior_trees import RewriteArguments

from pychology.behavior_trees import ReturnActiveAlways
from pychology.behavior_trees import ReturnDoneAlways
from pychology.behavior_trees import ReturnFailedAlways
from pychology.behavior_trees import ReturnFailedOnActive
from pychology.behavior_trees import ReturnDoneOnActive
from pychology.behavior_trees import ReturnActiveOnDone
from pychology.behavior_trees import ReturnFailedOnDone
from pychology.behavior_trees import ReturnActiveOnFailed
from pychology.behavior_trees import ReturnDoneOnFailed

from pychology.behavior_trees import RewriteReturnValues

from pychology.behavior_trees import FailOnPrecondition
from pychology.behavior_trees import ActiveOnPrecondition
from pychology.behavior_trees import DoneOnPrecondition
from pychology.behavior_trees import FailOnPostcondition
from pychology.behavior_trees import ActiveOnPostcondition
from pychology.behavior_trees import DoneOnPostcondition

from pychology.behavior_trees import FailOnPrecounter
from pychology.behavior_trees import ActiveOnPrecounter
from pychology.behavior_trees import DoneOnPrecounter
from pychology.behavior_trees import FailOnPostcounter
from pychology.behavior_trees import ActiveOnPostcounter
from pychology.behavior_trees import DoneOnPostcounter

from pychology.behavior_trees import Chain
from pychology.behavior_trees import Priorities
from pychology.behavior_trees import Parallel

from pychology.behavior_trees import Action
from pychology.behavior_trees import ReturnActive
from pychology.behavior_trees import ReturnDone
from pychology.behavior_trees import ReturnFailed


def test_action_save():
    def action_func():
        return NodeState.Done
    bt = Action(ActionFunction(action_func, name='demo_action'))
    bt_data = bt._save()
    assert bt_data == dict(
        cls='BTAction',
        func={'cls': 'TLActionFunction', 'name': 'demo_action'},
        pass_entity=True,
    )


def test_action_load():
    entity = object()
    def action_func(*args, **kwargs):
        assert args == (entity, )
        assert kwargs == dict()
        return NodeState.DONE
    af = ActionFunction(action_func, name='demo_action')
    loader = BehaviorTreeLoader(af)
    
    bt_data = dict(
        cls='BTAction',
        func={'cls': 'TLActionFunction', 'name': 'demo_action'},
        pass_entity=True,
    )

    bt = loader.load(bt_data)
    rv = bt(entity)
    assert rv is NodeState.DONE


@pytest.mark.parametrize(
    "cls", [ReturnActive, ReturnDone, ReturnFailed]
)
def test_leaf_returnstatic_saveload(cls):
    bt = cls()
    bt_data = bt._save()
    assert bt_data == dict(
        cls=cls.pych_cls,
    )
    loader = BehaviorTreeLoader()
    new_bt = loader.load(bt_data)
    assert isinstance(bt, cls)


### Decorators

@pytest.fixture
def loader_with_dummy_action():
    def action_func(*args, **kwargs):
        return NodeState.DONE
    wrapper = ActionFunction(action_func, name='demo_action')
    loader = BehaviorTreeLoader(wrapper)
    data = dict(
        cls='BTAction',
        func={'cls': 'TLActionFunction', 'name': 'demo_action'},
        pass_entity=True,
    )
    return loader, wrapper, data


@pytest.fixture
def loader_with_dummy_action_and_condition():
    def action_func(*args, **kwargs):
        return NodeState.DONE
    action_wrapper = ActionFunction(
        action_func,
        name='demo_action',
    )
    def condition_func(*args, **kwargs):
        return True
    condition_wrapper = ConditionFunction(
        condition_func,
        name='demo_condition',
    )
    loader = BehaviorTreeLoader(action_wrapper, condition_wrapper)
    action_data = dict(
        cls='BTAction',
        func={'cls': 'TLActionFunction', 'name': 'demo_action'},
        pass_entity=True,
    )
    return loader, action_wrapper, condition_wrapper, action_data


def test_behaviortree_saveload(loader_with_dummy_action):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action
    bt = BehaviorTree(Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls='BTBehaviorTree',
        child=dummy_action_data,
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, BehaviorTree)


debug_print_decorators = [
    DebugPrint, DebugPrintOnEnter, DebugPrintOnReset,
]


@pytest.mark.parametrize(
    "cls", debug_print_decorators
)
def test_debug_print_saveload(loader_with_dummy_action, cls):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action
    bt = cls("debug text", Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls=cls.pych_cls,
        text="debug text",
        child=dummy_action_data,
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, cls)
    assert bt.text == "debug text"


return_decorators = [
    ReturnActiveAlways, ReturnDoneAlways, ReturnFailedAlways,
    ReturnFailedOnActive, ReturnDoneOnActive, ReturnActiveOnDone, 
    ReturnFailedOnDone, ReturnActiveOnFailed, ReturnDoneOnFailed,
]


@pytest.mark.parametrize(
    "cls", return_decorators
)
def test_returndecorators_saveload(loader_with_dummy_action, cls):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action
    bt = cls(Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls=cls.pych_cls,
        child=dummy_action_data,
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, cls)


def test_rewrite_return_values_saveload(loader_with_dummy_action):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action

    bt = RewriteReturnValues(
        NodeState.ACTIVE, NodeState.DONE, NodeState.FAILED,
        Action(dummy_action),
    )
    bt_data = bt._save()
    assert bt_data == dict(
        cls='BTRewriteReturnValues',
        on_active='ACTIVE',
        on_failed='FAILED',
        on_done='DONE',
        child=dummy_action_data,
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, RewriteReturnValues)


conditional_decorators = [
    FailOnPrecondition, ActiveOnPrecondition, DoneOnPrecondition,
    FailOnPostcondition, ActiveOnPostcondition, DoneOnPostcondition
]


@pytest.mark.parametrize(
    "cls", conditional_decorators
)
def test_condition_decorators_saveload(loader_with_dummy_action_and_condition, cls):
    loader, dummy_action, dummy_condition, dummy_action_data = loader_with_dummy_action_and_condition
    bt = cls(dummy_condition, Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls=cls.pych_cls,
        child=dummy_action_data,
        cond={'cls': 'TLConditionFunction', 'name': 'demo_condition'}
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, cls)


counter_decorators = [
    FailOnPrecounter, ActiveOnPrecounter, DoneOnPrecounter,
    FailOnPostcounter, ActiveOnPostcounter, DoneOnPostcounter,
]


@pytest.mark.parametrize(
    "cls", counter_decorators
)
def test_counter_decorators_saveload(loader_with_dummy_action, cls):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action
    bt = cls(3, Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls=cls.pych_cls,
        child=dummy_action_data,
        timeout=3,
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, cls)


def test_rewrite_arguments_saveload(loader_with_dummy_action):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action


    def action_func(*args, **kwargs):
        return NodeState.DONE
    action_func_obj = ActionFunction(action_func, name='demo_action')
    def rewrite_func(*args, **kwargs):
        return args, kwargs
    rewrite_func_obj = SaveableFunction(
        rewrite_func,
        name='demo_rewrite',
    )
    loader = BehaviorTreeLoader(action_func_obj, rewrite_func_obj)

    bt = RewriteArguments(rewrite_func_obj, Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls='BTRewriteArguments',
        child=dummy_action_data,
        func={'cls': 'TLSaveableFunction', 'name': 'demo_rewrite'},
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, RewriteArguments)


### Multinodes

def test_chain_saveload(loader_with_dummy_action):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action
    bt = Chain(Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls='BTChain',
        children=[dummy_action_data],
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, Chain)


def test_priorities_saveload(loader_with_dummy_action):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action
    bt = Priorities(Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls='BTPriorities',
        children=[dummy_action_data],
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, Priorities)


def test_priorities_saveload(loader_with_dummy_action):
    loader, dummy_action, dummy_action_data = loader_with_dummy_action
    bt = Parallel(Action(dummy_action))
    bt_data = bt._save()
    assert bt_data == dict(
        cls='BTParallel',
        children=[dummy_action_data],
    )
    new_bt = loader.load(bt_data)
    assert isinstance(bt, Parallel)
