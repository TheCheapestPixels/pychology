import pytest

from pychology.behavior_trees import NodeState
from pychology.behavior_trees import BehaviorTree
from pychology.behavior_trees import Action
from pychology.behavior_trees import Priorities
from pychology.behavior_trees import Chain
from pychology.behavior_trees import ReturnActiveOnDone
from pychology.behavior_trees import DoneOnPrecondition
from pychology.behavior_trees import FailOnPrecondition
from pychology.behavior_trees import FailOnPrecounter
#from pychology.behavior_trees import 


class Environment:
    def __init__(self, door_params=None):
        # World state
        if door_params is None:
            door_params = []
        self.entity_has_passed_door = False
        self.door_is_open = 'closed' not in door_params
        self.door_is_locked = 'locked' in door_params
        self.door_is_hardened = 'hardened' in door_params

        # Actions
        self.entity_opens_door = False
        self.entity_passes_door = False
        self.entity_unlocks_door = False
        self.entity_kicks_in_door = False

        # Other
        self.log = []

    def tick(self):
        if self.entity_kicks_in_door:
            if not self.door_is_hardened:
                self.door_is_open = True
                self.log.append("kicks_in_door")
            else:
                self.log.append("kicks_at_door")
        self.entity_kicks_in_door = False

        if self.entity_unlocks_door:
            self.door_is_locked = False
            self.log.append("unlock_door")
        self.entity_unlocks_door = False

        if self.entity_opens_door:
            if not self.door_is_open and not self.door_is_locked:
                self.door_is_open = True
                self.log.append("opens_door")
        self.entity_opens_door = False

        if self.entity_passes_door:
            self.entity_has_passed_door = True
            self.log.append("passes_door")
        self.entity_passes_door = False

    def kick_in_door(self):
        self.entity_kicks_in_door = True
        return True
        
    def unlock_door(self):
        if self.door_is_locked:
            self.entity_unlocks_door = True
            return True
        return False
        
    def pick_door_lock(self):
        if self.door_is_locked:
            self.entity_unlocks_door = True
            return True
        return False
        
    def open_door(self):
        if not self.door_is_open and not self.door_is_locked:
            self.entity_opens_door = True
            return True
        return False

    def walk_through_door(self):
        if self.door_is_open:
            self.entity_passes_door = True
            return True
        return False


class Entity:
    def __init__(self, environment, items=None):
        self.environment = environment
        if items is None:
            items = []
        self.has_key = 'key' in items
        self.has_lockpicks = 'lockpicks' in items


# Decorator conditions

def is_door_open(entity): return entity.environment.door_is_open


# Action functions

def walk_through_door(entity):
    if entity.environment.entity_has_passed_door:
        return NodeState.DONE
    success = entity.environment.walk_through_door()
    if success:
        return NodeState.ACTIVE
    else:
        return NodeState.FAILED


def open_door(entity):
    if entity.environment.door_is_open:
        return NodeState.DONE
    success = entity.environment.open_door()
    if success:
        return NodeState.ACTIVE
    else:
        return NodeState.FAILED


def unlock_door(entity):
    if not entity.has_key:
        return NodeState.FAILED
    if not entity.environment.door_is_locked:
        return NodeState.DONE
    success = entity.environment.unlock_door()
    if success:
        return NodeState.ACTIVE
    else:
        return NodeState.FAILED


def pick_door_lock(entity):
    if not entity.has_lockpicks:
        return NodeState.FAILED
    if not entity.environment.door_is_locked:
        return NodeState.DONE
    success = entity.environment.pick_door_lock()
    if success:
        return NodeState.ACTIVE
    else:
        return NodeState.FAILED


def kick_in_door(entity):
    if entity.environment.door_is_open:
        return NodeState.DONE
    success = entity.environment.kick_in_door()
    if success:
        return NodeState.ACTIVE
    else:
        return NodeState.FAILED


# ([door_params], [items], should_tree_suceed, [log_entries])
demo_params = [
    ([], [], True, ['passes_door']),
    (['closed'], [], True, ['opens_door', 'passes_door']),
    (['closed', 'locked'], ['key'], True,
     ['unlock_door', 'opens_door', 'passes_door']),
    (['closed', 'locked'], ['lockpicks'], True,
     ['unlock_door', 'opens_door', 'passes_door']),
    (['closed', 'locked'], [], True,
     ['kicks_in_door', 'passes_door']),
    (['closed', 'hardened'], [], True,
     ['opens_door', 'passes_door']),
    (['closed', 'hardened', 'locked'], [], False,
     ['kicks_at_door', 'kicks_at_door', 'kicks_at_door']),
    (['closed', 'hardened', 'locked'], ['key'], True,
     ['unlock_door', 'opens_door', 'passes_door']),
]


behavior_tree_a = BehaviorTree(
    Priorities(
        FailOnPrecondition(
            lambda e: not is_door_open(e),
            Action(walk_through_door),
        ),
        ReturnActiveOnDone(
            Action(open_door),
        ),
        ReturnActiveOnDone(
            Priorities(
                Action(unlock_door),
                Action(pick_door_lock),
                FailOnPrecounter(
                    4,
                    Action(kick_in_door),
                ),
            ),
        ),
    ),
)


behavior_tree_b = BehaviorTree(
    Chain(
        DoneOnPrecondition(
            is_door_open,
            Priorities(
                Action(open_door),
                ReturnActiveOnDone(
                    Action(unlock_door),
                ),
                ReturnActiveOnDone(
                    Action(pick_door_lock),
                ),
                FailOnPrecounter(
                    4,
                    Action(kick_in_door),
                ),
            ),
        ),
        Action(walk_through_door),
    ),
)


@pytest.mark.parametrize(
    'door_params, items, expectation,log',
    demo_params,
)
@pytest.mark.parametrize(
    'tree',
    [behavior_tree_a, behavior_tree_b],
)
def test_demo_game(door_params, items, expectation, log, tree):
    environment = Environment(door_params=door_params)
    entity = Entity(environment, items=items)
    behavior = tree

    max_steps = 200
    tree_state = NodeState.ACTIVE
    while tree_state == NodeState.ACTIVE and max_steps > 0:
        max_steps -= 1
        environment.tick()
        tree_state = behavior(entity)
    if max_steps == 0:
        assert False  # You ran out of 200 steps
    if expectation:
        assert environment.entity_has_passed_door
        assert tree_state == NodeState.DONE
    else:
        assert not environment.entity_has_passed_door
        assert tree_state == NodeState.FAILED
    assert log == environment.log
