pychology
=========

Simple Python implementations of popular game AI techniques.

Current State: Very alpha. Only behavior trees are implemented.


Behavior Trees
--------------

Behavior trees are tree structures that represent the logic of choosing
and switching the current task. Each node in the tree can be considered
as a function that is called, and returns an indication of the current
task's state; Whether it is active, done, or has failed.

The tasks themselves are the leafs of the tree. `pychology` expects you
to provide functions to call when a task is started or continued, and
that it returns one of the above mentioned node states, namely
`NodeState.ACTIVE`, `NodeState.DONE`, or `NodeState.FAILED`. These
functions then are plugged into `pychology.behavior_trees.Action`.

Inner nodes may have a single child and do some logic; These are
called decorators, and do a lot of heavy lifting. They can change the
returning node state, prevent sub-trees from being executed, check for
conditions, count how often or for how long a sub-tree has been active,
provide debug information, and much more.

There's also nodes that (can) have multiple children. The two most
popular are the Chain (usually called Sequence), which executes a series
of tasks (or rather sub-trees) one after the other, and Priorities (also
called Selector or Fallback) which tries running one sub-tree after the
other until one reports something other than failure. Another node type
is Parallel, which executes all of its children.

The class `pychology.behavior_trees.BehaviorTree` can act as a root node
that automatically resets the tree's state after it has finished or
failed, and can also run arbitrary code to integrate with the wider
environment that the tree is embedded in.

An example on how to go through a door:

```python
BehaviorTree(
    Chain(
        DoneOnPrecondition(                  # The first task is done
            is_door_open,                    # if the door is open,
            Priorities(                      # otherwise try to
                Action(open_door),           # open it
                ReturnActiveOnDone(          # or try again after
                    Action(unlock_door),     # unlocking it,
                ),
                ReturnActiveOnDone(          # or try again after
                    Action(pick_door_lock),  # picking the lock,
                ),
                FailOnPrecounter(            # or try
                    4,                       # three times to
                    Action(kick_in_door),    # kick in the door.
                ),
            ),
        ),
        Action(walk_through_door),           # Afterwards, go through.
    ),
)
```


TODO
----

* Project
  * Packaging
* Hierarchical Finite State Machines (HFSM): Everything
* Behavior Trees
  * Multinodes: Weighted random choice
  * Decorators: More return value logic
  * Blackboard support
  * Debug tools
  * Visualization
  * De-/Serialization
* Planning
  * Goal-Oriented Action Planning (GOAP): Everything
  * Hierarchical Task Planning (HTN): Everything
* [Whatever this is](https://www.youtube.com/watch?v=Z-xU96pAuqs)
