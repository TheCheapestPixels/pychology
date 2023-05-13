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


import random
import itertools
from collections import defaultdict
import math


global timing
timing = []


class Search:
    def __init__(self, game, state, player):
        self.game = game
        self.player = player
        self.current_state = state
        self.setup_storage()
        self.store_state(state)
        self.enqueue_for_expansion(state)

    def setup_storage(self):
        raise NotImplementedError

    def store_state(self, state):
        """
        Returns True if the state has been added to storage, False if it
        has already been present.
        """
        raise NotImplementedError

    def enqueue_for_expansion(self, state):
        raise NotImplementedError
        
    def store_transition(self, state, action, successor):
        raise NotImplementedError

    def select_states_to_expand(self):
        """
        Returns a list of states to expand.
        """
        raise NotImplementedError

    def get_expanding_actions(self, state):
        raise NotImplementedError

    def step(self):
        """
        Returns True if states were expanded, False otherwise.
        """
        states = self.select_states_to_expand()
        if not states:
            return False  # Nothing left to expand
        for state in states:
            if self.game.game_winner(state):
                continue  # Terminal states can't be expanded.
            actions = self.get_expanding_actions(state)
            for action in actions:
                successor = self.game.make_move(state, action)
                successor_is_new_state = self.store_state(successor)
                self.store_transition(state, action, successor)
                if successor_is_new_state:
                    successor_hash = self.game.hash_state(successor)
                    self.value[successor_hash] = self.evaluate_state(successor)
                    self.enqueue_for_expansion(successor)
            self.backpropagate(state)
        return True  # Keep running

    def build_tree(self):
        raise NotImplementedError

    def evaluate_state(self, state):
        """
        Determine the heuristic value of the state, without having to
        resort to expanded states.
        """
        raise NotImplementedError

    def reevaluate_node(self, state):
        """
        Determine the actual value of the node based on states expanded
        from it.
        """
        raise NotImplementedError

    def backpropagate(self, state):
        """
        Determine the actual value of the node based on states expanded
        from it.
        """
        raise NotImplementedError

    def select_action(self):
        raise NotImplementedError

    def run(self):
        import datetime
        t_0 = datetime.datetime.now()
        self.build_tree()
        t_1 = datetime.datetime.now()
        timing.append((t_1-t_0).total_seconds())
        self.analyze()
        return self.select_action()

    def analyze(self):
        """
        Optional step at the end of running the search.
        """
        pass


### Modular extensions to the search core.

# Storage

class TranspositionTable:
    def setup_storage(self):
        self.known_states = {}  # hash -> state
        self.expansion_queue = []  # hashes
        self.terminal_states = {}  # hash -> winner
        self.children = defaultdict(list)  # hash -> [(hash, action)]
        self.parents = defaultdict(list)  # hash -> [(hash, action)]
        self.value = {}  # hash -> value
        self.opinion = {}  # hash -> (value, [action])

    def store_state(self, state):
        state_hash = self.game.hash_state(state)
        # If the state is known already, no need for further processing.
        if state_hash in self.known_states:
            return False
        self.known_states[state_hash] = state
        return True

    def store_transition(self, state, action, successor):
        state_hash = self.game.hash_state(state)
        successor_hash = self.game.hash_state(successor)
        self.children[state_hash].append((successor_hash, action))
        self.parents[successor_hash].append((state_hash, action))

    def backpropagate(self, state):
        state_hash = self.game.hash_state(state)
        states_to_update = [state_hash]
        while states_to_update:
            state_hash = states_to_update.pop(0)
            state = self.known_states[state_hash]
            state_value, best_actions = self.reevaluate_node(state)
            self.opinion[state_hash] = (state_value, best_actions)
            if state_hash not in self.value:
                # Apparently this is the root node, and hasn't gotten a
                # heuristic valuation at the beginning. FIXME: We should
                # still propagate, as cycles may exist in the graph.
                self.value[state_hash] = state_value
            elif self.value[state_hash] != state_value:
                self.value[state_hash] = state_value
                for s, a in self.parents[state_hash]:
                    states_to_update.append(s)


# Tree expansion

class NoExpansion:
    def build_tree(self):
        pass


class FullExpansion:
    def build_tree(self):
        while self.step():
            pass


class LimitedExpansion:
    def build_tree(self):
        while self.step() and len(self.known_states) < self.node_limit:
            pass


# State selection

class TTSingleNodeBreadthSearch:
    def enqueue_for_expansion(self, state):
        self.expansion_queue.append(state)

    def select_states_to_expand(self):
        try:
            state = self.expansion_queue.pop(0)
        except IndexError:
            return []
        return [state]


class TTSingleNodeDepthSearch:
    def enqueue_for_expansion(self, state):
        self.expansion_queue.append(state)

    def select_states_to_expand(self):
        try:
            state = self.expansion_queue.pop(-1)
        except IndexError:
            return []
        return [state]


class TTBreadthSearch:
    def enqueue_for_expansion(self, state):
        self.expansion_queue.append(state)

    def select_states_to_expand(self):
        try:
            states = self.expansion_queue
            self.expansion_queue = []
        except IndexError:
            return []
        return states


# Action expansion

class AllCombinations:
    def get_expanding_actions(self, state):
        moves = self.game.legal_moves(state)
        combos = self.generate_move_combinations(state, moves)
        return combos

    def generate_move_combinations(self, state, moves):
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


class Portfolio(AllCombinations):
    def get_expanding_actions(self, state):
        moves = self.game.legal_moves(state)
        players = list(moves.keys())
        portfolios = self.game.portfolios
        portfolio = {}
        for player in players:
            behavior = portfolios['ncw'](state, moves)
            if not behavior:  # A portfolio can't generate any moves...
                return []  # ...and thus this whole state is abandoned.
            portfolio[player] = behavior
        #import pdb; pdb.set_trace()
        return self.generate_move_combinations(state, portfolio)

    
# State evaluation

class ZeroSumPlayer:
    """
    Every point that the player has is counted. Every point that another
    player has is substracted from that. This is not properly zero sum,
    but should serve the same effect.
    """
    def evaluate_state(self, state):
        slate = self.evaluate_state_by_player(state)
        oppo_slate = [v for p, v in slate.items() if p != self.player]
        value = slate[self.player] - sum(oppo_slate)
        return value


class RacerPlayer:
    """
    If the player is not the one with the most points, the value is how
    many points behind the maximum score it is (as a negative value). If
    the player does have first place, the value is how far ahead of the
    next-valued player it is.
    """
    def evaluate_state(self, state):
        slate = self.game.evaluate_state(state)
        player_points = slate[self.player]
        all_points = list(sorted(slate.values()))
        if player_points == all_points[0]:  # Player leads
            value = player_points - all_points[1]
        else:
            value = player_points - all_points[0]
        return value


# Action evalution

class GameBasedEvaluation:
    evaluation_function = 'default'

    def evaluate_state_by_player(self, state):
        return self.game.evaluation_funcs[self.evaluation_function](state)


class Minimax(GameBasedEvaluation):
    def reevaluate_node(self, state):
        score = defaultdict(lambda: math.inf)
        state_hash = self.game.hash_state(state)
        children = self.children[state_hash]
        if not children:  # This state has been dropped from expansion.
            return (-math.inf, None)
        for successor_hash, actions in children:
            player_action = actions[self.player]
            successor_value = self.value[successor_hash]
            score[player_action] = min(score[player_action], successor_value)
        state_value = max(score.values())
        best_actions = [action
                        for action, points in score.items()
                        if points==state_value]
        return state_value, best_actions


# Action selection

class RandomChooser:
    """
    Chooses randomly among the available moves.
    """
    def select_action(self):
        options = self.game.legal_moves(self.current_state)[self.player]
        return random.choice(options)


class BestMovePlayer:
    """
    """
    def select_action(self):
        state_hash = self.game.hash_state(self.current_state)
        value, actions = self.opinion[state_hash]
        return random.choice(actions)


### Analysis

class TTAnalysis:
    def analyze(self):
        print(f"Time: {timing[-1]} seconds")
        state_hash = self.game.hash_state(self.current_state)
        value, options = self.opinion[state_hash]
        print(f"Position score: {value}")
        print(f"Action options: {', '.join(str(o) for o in options)}")
        print(f"Known states: {len(self.known_states)}")
        # States per depth level
        visited_states = set()
        level = -1
        level_states = set([state_hash])
        while level_states:
            level += 1
            print(f"Level {level}: {len(level_states)}")
            visited_states |= level_states
            state_hashes = level_states
            level_states = set()
            for state_hash in state_hashes:
                children = self.children[state_hash]
                for child, action in children:
                    if (child not in visited_states) and (child not in level_states):
                        level_states.add(child)


### Complete searches.

class StateOfTheArt(
        TranspositionTable,         # Storage
        LimitedExpansion,           # Tree expansion
        TTSingleNodeBreadthSearch,  # State selection
        #Portfolio,                  # Action expansion
        AllCombinations,
        ZeroSumPlayer,              # State evaluation
        Minimax,                    # Action evaluation
        BestMovePlayer,             # Action selection
        TTAnalysis,                 # Analysis (optional)
        Search,
):
    node_limit = 50000  # LimitedExpansion


class RandomAI(
        TranspositionTable,
        NoExpansion,
        AllCombinations,
        ZeroSumPlayer,
        Minimax,
        RandomChooser,
        Search,
): pass


### Game-independent core; REPL and run stub.

def repl(game, state, ai_players, visuals=True, ai_classes=None):
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
                    actions[player] = game.query_action(
                        player,
                        player_moves,
                    )
                else: actions[player] = []
            else:
                moves = game.legal_moves(state)[player]
                if moves:
                    if ai_classes is None:
                        ai_class = StateOfTheArt
                    else:
                        ai_class = ai_classes[player]
                        
                    search = ai_class(game, state, player)
                    actions[player] = search.run()
                else:
                    actions[player] = []
        state = game.make_move(state, actions)
    return winner


def play_interactively(game):
    X=1
    O=2
    ai_players = game.query_ai_players()
    ai_classes = {X: StateOfTheArt, O: LineRewardingAI}
    state = game.initial_state()
    repl(game, state, ai_players, ai_classes=ai_classes)


### Tournament glue code

class LineRewardingAI(StateOfTheArt):
    evaluation_function = 'line_rewarder'


def auto_tournament(game):
    X=1
    O=2
    DRAW=3
    results = {k: 0 for k in [1,2,3]} #game.players()}
    ai_players = game.players()
    ai_classes = {X: LineRewardingAI, O: LineRewardingAI}
    for i in range(100):
        print(i)
        state = game.initial_state()
        winner = repl(
            game, state, ai_players,
            visuals=False, ai_classes=ai_classes,
        )
        results[winner] += 1
    max_time = max(timing)
    min_time = min(timing)
    mean_time = sum(timing) / len(timing)
    median_time = sorted(timing)[int(len(timing)/2.0)]
    print(f"Min: {min_time}, Max: {max_time}, Mean: {mean_time}, Median: {median_time}")
    print(f"X   : {results[X]}\nO   : {results[O]}\nDraw: {results[DRAW]}\n")


if __name__ == '__main__':
    #from games.tic_tac_toe import Game
    #from games.ten_trick_take import Game
    from games.four_in_a_row import Game
    #from games.labyrinth import Game
    play_interactively(Game)
    #auto_tournament(Game)
