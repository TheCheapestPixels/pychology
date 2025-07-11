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
state and the player for which the search should find the best action.
In this example, we use a random mover "search":

```python
from pychology.search import RandomAI


search = RandomAI(game, state, player)
action = search.run()
```

To assemble and configure a search, we use the `Search` class as the
base, and add classes that implement aspects of the search, which the
base class itself does not; It only manages the core cycle of the graph
search algorithm, which consists of...

* choosing the state(s) to expand during this cycle, and for each of
  them...
* determining whether any player has won the game in it (and doing
  nothing with it if that is the case; Terminal states can not be
  expanded further),
* determining the combinations of actions that players can / might want
  to take in this state, and for each of them...
* determining the successor state that doing so would lead to,
* storing that state and transition, 
* and if the state is not known yet, evaluating the state and enqueue it
  for expansion.
* Finally, once all actions are processed and all successors created and
  evaluated, the original state is re-evaluated (now based on its
  successors' values, not its own), and the resulting value is
  recursively passed on to its parent(s), which then is also
  re-evaluated, and so on, until the updated value has reached every
  node for which it is relevant.

The core loop itself is embedded into a loop which steps it until some
termination condition is met, e.g. the search graph is fully expanded,
has grown beyond a certain number of nodes, or has completely searched
the graph up to a certain depth.

However, it specifies nothing at all about how each step in particular
should be performed, and those implementation details can radically
influence how the search performs in different scenarios. They can be
categorized into several aspects of the search, each encapsulating one
to three functions alluded to in the explanation of the core loop:

* Storage: Sets up the data structure in which states and the
  transitions between them are stored, allows for those steps to be
  done, and manages the backpropagation of updated state evaluations
  through the relevant nodes. Currently, only a transposition table is
  implemented.
* Tree expansion: Steps the core loop, within the limits it implements.
* State selection: Typically a FIFO or LIFO queue, making the search
  happen breadth-first or depth-first. A priority queue (e.g. for A*) is
  planned.
* Action expansion: Creates a list of move combinations that players may
  want to take. Typically, all legal possibilities are considered, but
  if doing so leads to too high a branching factor, functions that
  leverage expert knowledge for a game (or, theoretically at this time,
  machine learning models) may create more selective lists.
* State evaluation: A game's evaluation functions provide a value for a
  state from each player's perspective. This capability combines those
  values into one overall score, as seen from the perspective of the
  player for who we are doing the search. For example, in the game Four
  in a Row, each player's heuristic evaluation score can be based on how
  many lines there are with which the player can place winning lines,
  and how many pieces they have put into each of those lines already.
  The state evaluation then can, for example, subtract the opponent's
  value from the searching player's value, making the search consider
  blocking the opponent's lines as valuable as preparing one's own
  lines; This approach considers games to be zero sum games.
* Action evaluation: Once a state has been expanded, each action that a
  player can take can be valued based on the states that it can lead to;
  These may be multiple states if other players may also contribute
  actions to the move. By extension, the expanded state itself is also
  given a value based on those of the actions. The typical approach to
  this is minimax (the game theory one, not the tree search algorithm
  one which is based on the former). We assume that whatever we do, the
  opponent will do whatever is worst for us and selects the transition
  which will minimize the score for our action. Between those options we
  then choose the action providing the highest score (the best of all
  the worst options), or, more precisely, store all the best actions (as
  multiple may have the same value) for later action selection.
* Action selection: Chooses the action to take based on the current
  knowledge, randomness, or whatever else may come to mind.
* Analysis: With this optional capability, information about the search
  that was just performed may be extracted. Useful for debugging and
  performance measurement.


And when we put this all together:

```python
from pychology.search import TranspositionTable, NodeLimitedExpansion,
    SingleNodeBreadthSearch, AllCombinations, ZeroSumPlayer, Minimax,
    BestMovePlayer, Search


class MySearch(
    TranspositionTable,       # Storage: Directed graph
    NodeLimitedExpansion,     # Tree expansion: Abort the expansion loop
                              # once the limit set by the `node_limit`
                              # has been reached or exceeded.
    SingleNodeBreadthSearch,  # State selection: Expand one node at a
                              # time, in the order that successors are
                              # found in
    AllCombinations,          # Action expansion: Consider all
                              # combinations of legal moves.
    ZeroSumPlayer,            # State evaluation: A state's value is the
                              # player value minus all opponent values.
    Minimax,                  # Action evaluation: Expect opponents to
                              # make the move worst for us, and us to
                              # make the one best for us.
    BestMovePlayer,           # Action selection: Choose the highest-
                              # valued successor to move to.
    Search,
):
    node_limit = 10000


search = MySearch(game, state, player)
action = search.run()
```
