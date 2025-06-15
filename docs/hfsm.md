Hierarchical Finite State Machines (HFSM)
-----------------------------------------

In academic literature, a Finite State Machine (FSM) consists of a set
of states, each having a set of transitions to other states, which are
activated upon a certain event, causing the FSM to change its active
state from the one that is currently in to the one that the transition
leads to. What state the FSM is in afterwards defines the behavior that
an AI should now exhibit.

For pragmatic reason, `pychology` uses a list of conditions instead of
events; When calling the AI, it will check one condition of the current
state after the other, and changing the state if a condition is
fulfilled. Additionally, states have functions that are called when the
state is entered or exited.

As the number of states that an FSM has grows, so does the number of
possible transitions, and with it the complexity of maintaining the
FSM. This burden can be lowered by introducing metastates. Each
metastate is a grouping of states and/or metastates, creating a
tree-like hierarchy (hence HFSM), where the root is the HFSM, the leaves
are the states, and the inner nodes are the metastates.

When the HFSM is called, conditions are checked on the path from the
root to the current state. If a transition is triggered, the lowest
common node of the hierarchy is determined. All exit functions from the
current node to below the lowest common node are performed, and then all
entries back down to the new current node are performed.

Unlike states, metastates do not define a behavior. Transitions to
metastates are possible, but these will then have to transition the HFSM
onward, until it settles on an actual state.

In `pychology`, a state's behavior is, to the HFSM, an arbitrary object.
It can be a symbol or string that is used in purpose-written AI code,
but behavior trees are often a solid choice.
