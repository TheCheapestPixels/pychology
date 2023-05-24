pychology
=========

Simple Python implementations of popular game AI techniques.

Current State: Alpha. Only behavior trees and the basics of directed
graph search are implemented.


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


Directed Graph Search
---------------------

Consider games like Tic Tac Toe, Four in a Row, Checkers, Chess, Go.
They can all be modeled in terms of current states, actions that players
are able to take when the game is in a certain state, and successor
states that the game will be in if a certain set of actions is taken.
This principle also applies to complex video games, especially when it
comes to problems like pathfinding and action planning.

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

To make a problem tractable to search, it has to be formulated as
functions:

* `players()` returns a list of players in the game,
* `game_winner(state)` determines whether a player has won in the given
  state,
* `legal_moves(state)` gives a list of actions that each player can
  take, and
* `make_moves(state, moves)` returns the state that the game is in when
  the players make the indicated moves.

In addition to these core functions, different aspects that may be used
in the search may require additional functions:

* `hash_state(state)` creates a value that identifies the state. It
  should do so uniquely, meaning that no two states have the same hash;
  However, hash functions for which that is not guaranteed have been
  used successfully, e.g. Zobrist hashing for chess.

  This function is used by the `TranspositionTable` implementation for
  state storage, allowing states to be stored as a directed graph
  instead of a tree, which allows for states to be reused, should
  different sequences of moves lead to them.

  FIXME: There are still some occurrences of `hash_state` in the code
  that are not yet contained in the `TranspositionTable`.
* `evaluate_state(state)` generates a numerical value that expresses how
  good the given state is for the player; If one of two states is better
  than the other, its evaluation should be higher than the other's.

  This entry is special as the game should provide a dictionary of
  evaluation functions. This allows for configuring the playing strength
  of the search.

  FIXME: This function should default to using the result of
  `game_winner` to generate basic valuations (`math.inf` / `-math.inf` /
  0 for winning, losing, and a draw respectively), so that providing an
  evaluation function truly is optional. Similarly the MCTS evaluation
  function should be selectable without being specified in the game.
  Both these features still need to be implemented.

Finally, there is a set of functions used by the `repl.py` command line
tool to provide a textual interface to games.

* `initial_state()` defines the state of the board at the beginning of
  the game.
* `query_ai_players()` returns a list of players that should be played
  by the search.
* `visualize_state(state)` unsurprisingly outputs the state for the
  user.
* `query_action()` asks the user(s) which move they want to make.

All of these functions then are put together in a class which gets
passed to the search on its creation time, together with the current
state and the player for which the search should find the best action:

```python
from pychology.search import Search


search = Search(game, state, player)
action = search.run()
```

Note that this example is wrong, as `Search` is merely the base class
from which actual search classes are created by inheriting both it and
the classes which define the different capabilities of the search. If
you run the code as shown, it *will* fail with an exception, as it is
merely meant to be an illustration. However, multiple preconfigured
searches currently exist, so if you exchange `Search` for
`StateOfTheArt`, `FixedPliesAI`, or `RandomAI`, the code would work.
...after a fashion.

FIXME: Here should follow a section explaining the expansion/evaluation
cycle, and the different categories of extensions as well as their
different implementations.


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
  * Documentation
    * Separate detailed page
* Search
  * Algorithms
    * Alpha-Beta Pruning
    * Quiescence Search
    * Bidirectional Search
    * Pondering
      * State graph garbage collection
      * Reevaluation on change of player
    * Demonstrate machine learning wherever applicable
    * Counterfactual Regret Minimization
      * https://en.wikipedia.org/wiki/Regret_(decision_theory)
      * http://modelai.gettysburg.edu/2013/cfr/cfr.pdf
      * https://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf
      * https://towardsdatascience.com/counterfactual-regret-minimization-ff4204bf4205?gi=a09c56e9300c
    * Action selection: Shortest beat path
  * Hacks
    * Early termination of expansion if the root node has only one
      action available
    * A state, once expanded, is not used anymore, and can be removed
      from memory; Only its metadata is what we are after.
  * Tooling
    * REPL
      * Command line arguments
        * Tournament parametrization
	* Make more things available through `repl.assemble_search`.
      * CSV / JSON output
  * Cleanup
    * State selection
      * Add priority queue
    * Action evaluation
      * Make default evaluation based on `game_winner` available without
        accessing a game's evaluation function dictionary.
      * Make MCTS (currently in `four_in_a_row.py`) available without
        accessing a game's evaluation function dictionary.
  * Documentation
    * README: More explanations
    * Separate, detailed page, akin to a course
    * Docstrings; Especially descriptions of lists / dicts transferred.
  * Compilation: Refactor code for use with Cython / PyPy / mypyc and
    test speed improvements
* Planning
  * Goal-Oriented Action Planning (GOAP): Everything
  * Hierarchical Task Planning (HTN): Everything
* [Whatever this is](https://www.youtube.com/watch?v=Z-xU96pAuqs)
* Tolman-Eichenbaum machine
  * https://web.archive.org/web/20200325015457id_/https://www.biorxiv.org/content/biorxiv/early/2019/09/16/770495.full.pdf
  * https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7707106/
