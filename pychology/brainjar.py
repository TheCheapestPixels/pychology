# This is a boilerplate to get an AI of an agent going.

import enum
import functools

from pychology.blackboard import Blackboard
from pychology.behavior_trees import (
    NodeState,
    BehaviorTree,
    Chain,
    Priorities,
    FailOnPrecondition,
    DoneOnPrecondition,
    Action,
    DebugPrint,  # TODO: Remove
)


# Blackboard fields
class BBField(enum.Enum):
    # Behaviors
    BEHAVIORS      = 1  # dict of name -> function
    COMMAND        = 2  # Command given to the AI; (AICommand._, *args)
    PLAN           = 3  # The AI's command for action
    IDLE_BEHAVIOR  = 4  # FIXME: This needs to go somehow.
    SENSOR         = 5
    SENSATIONS     = 6


# BBField.COMMAND is a list of a command and the arguments for it.
class AICommand(enum.Enum):
    FUNCTION = 1  # [func, *args]; Just call that func with those args.
    PLAN     = 2  # [plan]; Set the plan to the given plan.
    BEHAVIOR = 3  # [name]; Engage in the given behavior.


# Predicates

def bb_has(field):
    def inner_bb_has(ai):
        return field in ai.blackboard
    return inner_bb_has


def bb_has_not(field):
    def inner_bb_has_not(ai):
        return field not in ai.blackboard
    return inner_bb_has_not


# Actions

def perceive(ai):
    sensor_func = ai.blackboard[BBField.SENSOR]
    ai.blackboard[BBField.SENSATIONS] = sensor_func()


def set_plan_to_command(ai):
    command, arg = ai.blackboard[BBField.COMMAND]
    if command == AICommand.BEHAVIOR:
        behavior = ai.blackboard[BBField.BEHAVIORS][arg]
        ai.blackboard[BBField.PLAN] = behavior
    return NodeState.DONE


# FIXME: This should be bb_has_not((BBField.BEHAVIORS, BBField.IDLE_BEHAVIOR))
def has_no_idle_behavior(ai):
    return not BBField.IDLE_BEHAVIOR in ai.blackboard[BBField.BEHAVIORS]


def set_idle_behavior(ai):
    behavior = ai.blackboard[BBField.BEHAVIORS][BBField.IDLE_BEHAVIOR]
    ai.blackboard[BBField.PLAN] = behavior
    return NodeState.DONE


# FIXME: This looks like an `Action`?
def execute_plan(ai):
    return ai.blackboard[BBField.PLAN](ai)


def bb_del(field):
    def inner(ai):
        try:
            del ai.blackboard[field]
            return NodeState.DONE
        except KeyError:
            return NodeState.FAILED
    return inner


# Factory functions for behavior trees

def BT_think():
    return BehaviorTree(
        Chain(                                              # Run through these steps:
            DoneOnPrecondition(                             # Perception: We skip this block if
                bb_has_not(BBField.SENSOR),                 # no sensor function is present,
                Action(perceive),                           # otherwise we perceive.
            ),
            DoneOnPrecondition(                             # Command compulsion: We skip this block if
                bb_has_not(BBField.COMMAND),                # no direct command is present,
                Chain(                                      # otherwise
                    Action(set_plan_to_command),            # we set the plan to it,
                    Action(bb_del(BBField.COMMAND)),        # and clear the command field,
                ),
            ),
            DoneOnPrecondition(                             # Falling back on idle behavior: We skip this block if
                bb_has(BBField.PLAN),                       # no plan is present,
                DoneOnPrecondition(                         # also if
                    has_no_idle_behavior,                   # we don't know of an idle behavior,
                    Action(set_idle_behavior),              # otherwise we set the idle behavior as the plan.
                ),
            ),
            DoneOnPrecondition(                             # If
                bb_has_not(BBField.PLAN),                   # we have a plan,
                Chain(
                    Action(execute_plan),                   # act on it,
                    Action(bb_del(BBField.PLAN)),           # then and remove it.
                ),
            ),
        ),
    )


class BrainJar:
    def __init__(self, parent_ai=None, thought_pattern=None, on_idle=None):
        self.blackboard = Blackboard(parent=parent_ai)
        self.blackboard[BBField.BEHAVIORS] = {}
        if thought_pattern is not None:
            self.thought_pattern = thought_pattern
        else:
            self.thought_pattern = BT_think()
        self.on_idle = on_idle

    def think(self):
        rv = self.thought_pattern(self)
        if rv == NodeState.DONE and self.on_idle is not None:
            self.on_idle(self)

    def add_knowledge(self, name, fact):
        self.blackboard[name] = fact

    def add_behavior(self, name, behavior):
        self.blackboard[BBField.BEHAVIORS][name] = behavior

    def command(self, behavior, **kwargs):
        behaviors = self.blackboard[BBField.BEHAVIORS]
        if behavior not in behaviors:
            raise KeyError(f"Unknown behavior {behavior}. Available are: {', '.join(behaviors.keys())}")
        self.blackboard[BBField.COMMAND] = (AICommand.BEHAVIOR, behavior)
        for name, value in kwargs.items():
            self.blackboard[name] = value
