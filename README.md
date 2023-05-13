pychology
=========

Simple Python implementations of popular game AI techniques.

Current State: Alpha. Only behavior trees and the basics of directed
graph search are implemented.


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

Directed Graph Search
---------------------

Consider games like Tic Tac Toe, Four in a Row, Checkers, Chess, Go.
They can all be modeled in terms of current states, actions that players
are able to take when the game is in a certain state, and successor
states that the game will be in if a certain set of actions is taken.
This principle also applies to complex video games, especially when it
comes to pathfinding and action planning.

Game states can be considered as nodes in a graph, and the corresponding
valid actions as directed edges from node to node. To play a game like
that well then means to find a path through the graph one step at a
time, trying to steer the movement into a preferable area of the graph
that will provide the most beneficial outcome, while opposing players
try to steer it into areas preferable to themselves. Graph search then
is the application of raw computing resources to build the graph of
possible future game states out from the current state, and finding the
paths through it that lead to the optimal possible future state. This
search can be improved on both by clever optimizations on the search
itself, and through expert knowledge expressed as heuristic functions.


TODO
----

* Project
  * Packaging
* Hierarchical Finite State Machines (HFSM): Everything
* Behavior Trees
  * Node types
    * Weighted Random Choice Multinode
    * Plugin point for adding subtrees at runtime; Might be sensible to
      have as a universal property?
  * Blackboard support: Just a decorator working on the entity?
  * Tooling
    * De-/Serialization
    * Debug
      * Recording activation, return values, and resets frame by frame
    * Tree visualization and editing in Panda3D
* Search
  * Algorithms
    * Alpha-Beta Pruning
    * Quiescence Search
    * Bidirectional Search
    * Pondering
      * State graph garbage collection
  * Hacks
    * Early termination of expansion if the root node has only one
      action available
  * Tooling
    * Break REPL / automatic tournaments out of search
  * Games
    * Nine Men's Morris (and variations)
* Planning
  * Goal-Oriented Action Planning (GOAP): Everything
  * Hierarchical Task Planning (HTN): Everything
* [Whatever this is](https://www.youtube.com/watch?v=Z-xU96pAuqs)
