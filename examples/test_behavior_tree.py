from pychology.behavior_trees import NodeState

from pychology.behavior_trees import SaveableFunction
from pychology.behavior_trees import ActionFunction
from pychology.behavior_trees import ConditionFunction
from pychology.behavior_trees import BehaviorTreeLoader

from pychology.behavior_trees import BehaviorTree
from pychology.behavior_trees import Priorities
from pychology.behavior_trees import Chain
from pychology.behavior_trees import Action
from pychology.behavior_trees import DoneOnPrecondition


def dummy_func(*args, **kwargs):
    raise Exception


af_a = ActionFunction(dummy_func, name='a')
af_b = ActionFunction(dummy_func, name='b')
af_c = ActionFunction(dummy_func, name='c')
af_d = ActionFunction(dummy_func, name='d')
af_e = ActionFunction(dummy_func, name='e')

df_f = ConditionFunction(dummy_func, name='f')


bt = BehaviorTree(
    Priorities(
        Chain(
            DoneOnPrecondition(
                df_f,
                Action(af_a),
            ),
            Action(af_b),
            Action(af_c),
        ),
        Action(af_d),
        Action(af_e),
    )
)


bt_data = bt._save()


def query_user(name, cls):
    if cls == SaveableFunction.pych_cls:
        def query(*args, **kwargs):
            response = input(f"Function {name}: ")
            return eval(response)
    elif cls == ActionFunction.pych_cls:
        def query(*args, **kwargs):
            while True:
                response = input(f"Action {name} [A]ctive/[D]one/[F]ailed: ")
                if response in 'aA':
                    return NodeState.ACTIVE
                elif response in 'dD':
                    return NodeState.DONE
                elif response in 'fF':
                    return NodeState.FAILED
    elif cls == ConditionFunction.pych_cls:
        def query(*args, **kwargs):
            while True:
                response = input(f"Condition {name} [T]rue/[F]alse: ")
                if response in 'tT':
                    return True
                elif response in 'fF':
                    return False
            return state
    return query


class TestLoader(BehaviorTreeLoader):
    def get_func(self, func_data):
        name = func_data['name']
        cls = func_data['cls']
        print(f"Creating wrapper for {cls} {name}")
        if name not in self.funcs:
            self.funcs[name] = query_user(name, cls)
        return self.funcs[name]


loader = TestLoader()
bt = loader.load(bt_data)
while True:
    print(f"----- new tick")
    rv = bt(object())
    print(f"----- Behavior Tree returned: {rv}")
#import pdb; pdb.set_trace()
