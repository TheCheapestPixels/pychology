Behavior Trees
--------------

Behavior trees are tree structures that represent the logic of choosing
and switching the current task that a given entity should perform. The
tasks are situated at the leaves of that tree, and are defined by the
application that behavior trees are embedded in; In any given frame,
they can be active, done, or have failed. The trees inner leaves are
units of logic, and when the tree is called for execution, they route
that call through the tree to tasks, depending on current circumstances.
Multiple tasks may be executed each frame, and depending on their status
(active / done / failed), additional tasks may or may not be executed.
Note that "frame" does not actually have to correspond to a graphical
frame being rendered, or any semi-fixed time span; It is merely a good
shorthand for "an interval during which a tree is executed once."

For each task, `pychology` expects you to provide a function to call
when a task is started or continued, and that it returns one of the
above mentioned node states, namely `NodeState.ACTIVE`,
`NodeState.DONE`, or `NodeState.FAILED`. These functions then are
plugged into `pychology.behavior_trees.Action`.

Inner nodes may have a single child and do some logic; These are
called decorators, and do a lot of heavy lifting. They can change the
returning node state, prevent subtrees from being executed, check for
conditions, count how often or for how long a subtree has been active,
provide debug information, and much more. Depending on the exact type of
decorator, they may expect you to provide data or a function as well.

There are also nodes that (can) have multiple children. The two most
popular are the Chain (usually called Sequence), which executes a series
of tasks (or rather subtrees) one after the other, and Priorities (also
called Selector or Fallback) which tries running one subtree after the
other until one reports something other than failure. Another node type
is Parallel, which executes all of its children until one fails or all
are done. Note that this is not parallelism in the sense of bits of code
being executed at the same time on the CPU, but the logical parallelism
of multiple subtrees all being executed within the span of a frame.

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
