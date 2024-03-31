# This is a very simple "game" that shows how to integrate behavior
# trees in a wider AI. Thanks to BMaxV for inspiring it.

from direct.showbase.ShowBase import ShowBase
from pychology.behavior_trees import (
    NodeState,
    BehaviorTree,
    Chain,
    Priorities,
    FailOnPrecondition,
    Action,
)


# The world represents all elements of the game outside of the AI that
# has to act in the world. Here, our world is a printer. You repeatedly
# tell it to print a letter until you have invested a certain time
# doing so, and then it does print the letter. Changing your intended
# letter midway through the process resets the progress.

class World:
    printing_duration = 1.0
    def __init__(self):
        self.currently_printing = None
        self.accumulated_printing_time = 0.0

    def print_letter(self, letter):
        if letter != self.currently_printing:  # Restart printing
            self.currently_printing = letter
            self.accumulated_printing_time = 0.0
        self.accumulated_printing_time += self.dt
        if self.accumulated_printing_time >= self.printing_duration:
            # Finished!
            print(letter)
            self.currently_printing = None
            self.accumulated_printing_time = 0.0
            return NodeState.DONE
        return NodeState.ACTIVE

    def tick(self, dt):
        self.dt = dt


# The mind represents everything within the AI's mind. It
# provides `print_letter` as the action that the AI can take to interact
# with the world.

class Mind:
    def __init__(self, world, behaviors):
        self.world = world
        self.goal = ['A', 'B', 'C', 'A', 'B', 'C']
        self.behaviors = behaviors
        self.bt = behaviors[0]
        self.current_behavior = 0

    def set_bt(self, bt):
        self.bt = bt

    def toggle_behavior(self):
        self.current_behavior += 1
        self.current_behavior %= len(self.behaviors)
        self.set_bt(self.behaviors[self.current_behavior])
        
    def print_letter(self, letter):
        return self.world.print_letter(letter)

    def tick(self):
        self.bt(self)


# Because we want to specify a BT independent of a given mind, we create
# wrappers for the specification.

def goal_isnt(letter):
    def inner(entity):
        if len(entity.goal) == 0:
            return True
        return entity.goal[0] != letter
    return inner


def print_letter(letter):
    def inner(entity):
        return entity.print_letter(letter)
    return inner


def task_done(entity):
    if len(entity.goal) <= 1:
        entity.goal = []
    else:
        entity.goal = entity.goal[1:]
    return NodeState.DONE


# Let's specify the default behavior:
bt = BehaviorTree(
    Chain(  # There are two things we must do:
        Priorities(  # Print the appropriate letter.
            FailOnPrecondition(
                goal_isnt("A"),
                Action(print_letter("A"))
            ),
            FailOnPrecondition(
                goal_isnt("B"),
                Action(print_letter("B"))
            ),
            FailOnPrecondition(
                goal_isnt("C"),
                Action(print_letter("C"))
            ),
        ),
        Action(task_done),
    ),
)


# ...and a deviant behavior.
rot13 = BehaviorTree(
    Chain(  # There are two things we must do:
        Priorities(  # Print the appropriate letter.
            FailOnPrecondition(
                goal_isnt("A"),
                Action(print_letter("N"))
            ),
            FailOnPrecondition(
                goal_isnt("B"),
                Action(print_letter("O"))
            ),
            FailOnPrecondition(
                goal_isnt("C"),
                Action(print_letter("P"))
            ),
        ),
        Action(task_done),
    ),
)


if __name__ == '__main__':
    ShowBase()
    base.accept('escape', base.task_mgr.stop)
    w = World()
    m = Mind(w, [bt, rot13])

    base.accept("t", m.toggle_behavior)
    def add_goal(letter):
        m.goal.append(letter)
        print(f"Goals: {m.goal}")
    base.accept("a", add_goal, extraArgs=['A'])
    base.accept("b", add_goal, extraArgs=['B'])
    base.accept("c", add_goal, extraArgs=['C'])

    def tick(task):
        dt = globalClock.dt
        w.tick(dt)
        m.tick()
        return task.cont
    base.task_mgr.add(tick)
    base.run()
