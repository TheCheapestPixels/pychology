# **Basic tree search**: You have a current world state as the root of
# the state tree. You can choose a state the tree to expand, generating
# a set of successor nodes. You have an evaluation function that says
# how desirable a given state is to you. After expansion and evaluation
# of the new successors, a minimax recalculates the value of each node
# by taking the minimum or maximum of the child nodes (propagating from
# leaves to root), based on which player is acting during that node's
# move. Thus whenever the search is stopped, the best currently known
# action is the one leading to the child node with the highest value.
#
# **Better tree representation**
# DAG: Given a game state, there are often different action sequences
# leading to the same successor game state. In a tree, these are treated
# as two different objects, and expanded separately from each other,
# multiplying the time and space spent on that state.
# Similar states: Different game states can be similar enough to each
# other to be considered the same for game purposes; Board states may be
# mappable to each other. In Tic Tac Toe, for example, if two game
# states can be turned into each other through rotation and mirroring,
# they can be treated as the same state for rules purposes. Employing
# a state hash function that generates a transformation-independent
# hash will cut down on the state tree size; 
# 
# **Choosing the node to expand**
# Depth-first: Simulates one possible game session from beginning to
# end, then considers other possible final moves, and so on. This only
# works if the state space is small, like for Tic-Tac-Toe.
# Breadth-first: Expand all nodes on a given depth level of a tree
# before expanding any deeper ones. Simple, but actually works.
# A*: Nodes to expand are sorted by their estimated distance to a goal
# state. This estimation has to be optimistic, otherwise it is not
# guaranteed that the ideal path will be found.
# Alpha-Beta Pruning: Resources for deeper search can be freed up by not
# expanding nodes of apparent bad moves. For optimal performance,
# expanded nodes have to be sorted
# Quiescense search: Unstable states are ones that bear a greater risk
# than others as defined under some stability criterion, e.g. "Is the
# chess player's queen under threat?". These can be expanded before more
# stable ones, focusing search resources so that players don't leave
# themselves open for stupid mistakes because more stable parts of the
# tree were expanded first.
#
# **Choosing which actions to expand the node with**
# Hierarchical Portfolio Search: Designers build sets of behaviors,
# which are function that, given a state, produce actions. They then
# build portfolios, which are functions that, given a game state,
# produce combinations of behaviors. During expansion, these portfolios
# choose the actions to expand a node with. Thus, the branching factor
# is cut down, and designers can build desired behaviors.
# 
# **Evaluating states**
# Explicit function: For a given game, bespoke functions can be written
# to encapsulate the developer's knowledge about a game.
# Monte Carlo Tree Search: Starting at the state, the rest of the game
# is played out to its end by using random actions, and the end state's
# value is used for propagation. Simulating these play-outs multiple
# times leads to more accurate values. This approach does not require
# a-priori knowledge about how to play a game well, only to know its
# rules.
# 
# **Higher-level techniques**
# Bi-directional path search: If a desired goal state can be defined,
# and possible antecedent states for a given state can be derived, then
# expansion can happen from the goal backwards as well as from the
# current states forwards, and a path between them found more quickly
# than by searching only forwards. This optimizes GOAP.
# Machine Learning: Apply it to choosing the expansion and evaluation
# functions, train it on Monte Carlo Tree Search, and you basically have
# AlphaGo.
#
#
#
# game = (initial_state, game_winner, legal_moves, make_move)
# player = (evaluation)
# ui = (visualize_state, query_actions)
# search = (state_table, transposition_table, expansions_container)

import random
import itertools


class RandomChooser:
    def __init__(self, game, state, player):
        self.game = game
        self.state = state
        self.player = player

    def step(self):
        moves = self.game.legal_moves(self.state)[self.player]
        self.favorite_move = random.choice(moves)
        return False

    def decide(self):
        return self.favorite_move


class Search:
    def __init__(self, game, state, player):
        self.expansion_queue = [state]
        self.game = game
        self.state = state
        self.player = player

    def select_state_to_expand(self):
        state = self.expansion_queue.pop(0)
        return state

    def get_expanding_actions(self, state):
        moves = self.game.legal_moves(state)
        players = list(moves.keys())
        # Some players may not have any move available. The basic
        # product of moves would thus contain no moves. So here we use
        # None to fake a "pass" move.
        for k in moves.keys():
            if not moves[k]:
                moves[k] = [None]
        # Now we figure out all possible combinations...
        combos = list(itertools.product(*[moves[p] for p in players]))
        # ...and turn them back into move format.
        combos = [dict(zip(players, combi)) for combi in combos]
        return combos

    def step(self):
        if not self.expansion_queue:  # Queue is empty
            return False
        # Select node to expand
        state = self.select_state_to_expand()
        # Choose expansions
        moves = self.get_expanding_actions(state)
        successors = [self.game.make_move(state, m) for m in moves]
        import pdb; pdb.set_trace()
        # Evaluate expansions
        # Backpropagate values
        # Done
        return True

    def select_action(self):
        return action

    def run(self):
        if self.expansion_queue:
            self.step()
        return self.select_action()





















### Game-independent core; REPL and run stub.

def repl(game, state, ai_players, visuals=True):
    while True:
        if visuals:
            game.visualize_state(state)
        winner = game.game_winner(state)
        if winner is not None:
            break

        moves = game.legal_moves(state)
        actions = {}
        for player, player_moves in moves.items():
            if player not in ai_players:
                if player_moves:
                    actions[player] = game.query_action(player_moves)
                else: actions[player] = []
            else:
                moves = game.legal_moves(state)[player]
                if moves:
                    #search = RandomChooser(game, state, player)
                    search = Search(game, state, player)
                    while search.step():
                        pass
                    actions[player] = search.decide()
                else:
                    actions[player] = []
        state = game.make_move(state, actions)
    return winner


def play_interactively(game):
    ai_players = game.query_ai_players()
    state = game.initial_state()
    repl(game, state, ai_players)


def auto_tournament():
    results = {X: 0, O: 0, DRAW: 0}
    ai_players = [X, O]
    for _ in range(10000):
        state = initial_state()
        results[repl(state, ai_players, visuals=False)] += 1
    print(f"X   : {results[X]}\nO   : {results[O]}\nDraw: {results[DRAW]}\n")


if __name__ == '__main__':
    from games.tic_tac_toe import Game
    play_interactively(Game)
    #auto_tournament()


