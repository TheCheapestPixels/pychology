import math
import random


X = 1
O = 2
DRAW = 3

ROWS = 6
COLUMNS = 7

exponents = range(ROWS * COLUMNS)

win_lines = []
# Vertical lines
for c in range(COLUMNS):
    for r in range(ROWS - 3):
        tile = r * COLUMNS + c
        t_1 = tile
        t_2 = tile + COLUMNS
        t_3 = tile + COLUMNS * 2
        t_4 = tile + COLUMNS * 3
        win_lines.append((t_1, t_2, t_3, t_4))
# Horizontal lines
for r in range(ROWS):
    for c in range(COLUMNS - 3):
        tile = r * COLUMNS + c
        t_1 = tile
        t_2 = tile + 1
        t_3 = tile + 2
        t_4 = tile + 3
        win_lines.append((t_1, t_2, t_3, t_4))
# Upward Diagonals
for r in range(ROWS - 3):
    for c in range(COLUMNS - 3):
        tile = r * COLUMNS + c
        t_1 = tile
        t_2 = tile + 1 + COLUMNS
        t_3 = tile + 2 + COLUMNS * 2
        t_4 = tile + 3 + COLUMNS * 3
        win_lines.append((t_1, t_2, t_3, t_4))
# Downward Diagonals
for r in range(ROWS - 3):
    for c in range(COLUMNS - 3):
        tile = r * COLUMNS + c
        t_1 = tile + COLUMNS * 3
        t_2 = tile + 1 + COLUMNS * 2
        t_3 = tile + 2 + COLUMNS
        t_4 = tile + 3
        win_lines.append((t_1, t_2, t_3, t_4))


def players():
    return [X, O]


def outcomes():
    return {X: 'X', O: 'O', DRAW: 'Draw'}


def initial_state():
    board = [0 for _ in range(ROWS * COLUMNS)]
    return board


def game_winner(state):
    # Is there a regular winner?
    for t_1, t_2, t_3, t_4 in win_lines:
        if state[t_1] != 0:
            if state[t_1] == state[t_2] == state[t_3] == state[t_4]:
                return state[t_1]
    # If the board is filled and there is no winner, it's a draw.
    legal = [c for c in range(COLUMNS)
             if state[c + (ROWS - 1) * COLUMNS] == 0]
    if len(legal) == 0:
        return DRAW
    # So there's no winner, and the board isn't full; The game goes on.
    return None


def legal_moves(state):
    if sum(state) % 3 == 0:
        player = X
    else:
        player = O
    moves = {player: [] for player in players()}
    legal = [c for c in range(COLUMNS)
             if state[c + (ROWS - 1) * COLUMNS] == 0]
    moves[player] = legal
    return moves


def make_move(state, moves):
    if sum(state) % 3 == 0:
        player = X
    else:
        player = O
    column = moves[player]
    new_board = [t for t in state]
    for r in range(ROWS):
        tile = r * COLUMNS + column
        if new_board[tile] == 0:
            new_board[tile] = player
            break
    return new_board


def hash_state(state):
    return sum(b * 3**e for b, e in zip(state, exponents))


def evaluate_state_naively(state):
    winner = game_winner(state)
    if winner == X:
        return {X: math.inf, O: -math.inf}
    elif winner == O:
        return {X: -math.inf, O: math.inf}
    else:
        return {X: 0, O: 0}


def evaluate_state_mcts(state):
    winner = game_winner(state)
    if winner == X:
        return {X: math.inf, O: -math.inf}
    elif winner == O:
        return {X: -math.inf, O: math.inf}
    else:
        while not (winner := game_winner(state)):
            moves = legal_moves(state)
            choices = {player: None for player in moves}
            for player, options in moves.items():
                if options:
                    choices[player] = random.choice(options)
            state = make_move(state, choices)
        if winner == DRAW:
            return {X: 0, O: 0}
        score = {X: -1, O: -1}
        score[winner] = 1
        return score


def evaluate_state_heuristically(state):
    def has_won(player):
        score = {p: -math.inf for p in players()}
        score[player] = math.inf
        return score
    def draw():
        return {p: 0 for p in players()}

    line_chances = draw()
    # Is there a regular winner?
    for tile_ids in win_lines:
        tiles = t_1, t_2, t_3, t_4 = [state[t] for t in tile_ids]
        if t_1 != 0:
            if t_1 == t_2 == t_3 == t_4:
                return has_won(t_1)
            for p in players():
                player_tiles_in_line = [t==p for t in tiles]
                if len(player_tiles_in_line) > 0:
                    if all(t==0 or t==p for t in tiles):
                        num_own_tiles = len(player_tiles_in_line)
                        line_chances[p] += 4 ** (num_own_tiles - 1)
    # If the board is filled and there is no winner, it's a draw.
    legal = [c for c in range(COLUMNS)
             if state[c + (ROWS - 1) * COLUMNS] == 0]
    if len(legal) == 0:
        return draw()
    # So there's no winner, and the board isn't full; The game goes on.
    return line_chances


def visualize_state(state):
    if sum(state) % 3 == 0:
        player = X
    else:
        player = O

    print()
    lines = []
    for r in range(ROWS-1, -1, -1):
        tiles = []
        for c in range(COLUMNS):
            t = state[r * COLUMNS + c]
            if t == 0:
                tiles.append(".")
            elif t == X:
                tiles.append("X")
            else:
                tiles.append("O")
        lines.append(' '.join(tiles))
    lines.append(' '.join(str(r) for r in range(COLUMNS)))
    print('\n'.join(lines))
    print()
    winner = game_winner(state)
    if winner is not None:
        if winner == X:
            print(f"Winner: X")
        elif winner == O:
            print(f"Winner: O")
        else:  # winner == DRAW
            print("Game ended in a draw.")
    else:
        if player == X:
            print(f"Move: X")
        else:
            print(f"Move: O")


def query_action(player, moves):
    while True:
        choice = input("Your choice: ")
        try:
            choice = int(choice)
        except ValueError:
            pass
        if choice not in moves:
            print("Invalid move.")
        else:
            break
    print()
    return choice


def query_ai_players():
    print(f"Should I play X, O, XO (both), or N (neither)?")
    ai_players = None
    while ai_players is None:
        i = input("> ")
        if i in ['X', 'x']:
            ai_players = [X]
        elif i in ['O', 'o']:
            ai_players = [O]
        elif i in ['XO', 'xo']:
            ai_players = [X, O]
        elif i in ['N', 'n']:
            ai_players = []
        else:
            print("Please enter X, O, XO, or N.")
    return ai_players


class Game:
    initial_state = initial_state
    game_winner = game_winner
    outcomes = outcomes
    legal_moves = legal_moves
    make_move = make_move
    players = players
    hash_state = hash_state
    query_ai_players = query_ai_players
    evaluation_funcs = {
        'default': evaluate_state_naively,
        'line_rewarder': evaluate_state_heuristically,
        'mcts': evaluate_state_mcts,
    }
    visualize_state = visualize_state
    query_action = query_action
