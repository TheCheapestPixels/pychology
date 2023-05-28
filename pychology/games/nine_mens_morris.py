from enum import Enum
import math


#  1---------- 2---------- 3
#  |           |           |
#  |   4-------5-------6   |
#  |   |       |       |   |
#  |   |   7---8---9   |   |
#  |   |   |       |   |   |
# 10--11--12      13--14--15
#  |   |   |       |   |   |
#  |   |  16--17--18   |   |
#  |   |       |       |   |
#  |  19------20------21   |
#  |           |           |
# 22----------23----------24


lines = [
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 9),
    (10, 11, 12),
    (13, 14, 15),
    (16, 17, 18),
    (19, 20, 21),
    (22, 23, 24),
    (1, 10, 22),
    (4, 11, 19),
    (7, 12, 16),
    (2, 5, 8),
    (17, 20, 23),
    (9, 13, 18),
    (6, 14, 21),
    (3, 15, 24),
]
tile_adjacency = {
    1: [2, 10],
    2: [1, 3, 5],
    3: [2, 15],
    4: [5, 11],
    5: [2, 4, 6, 8],
    6: [5, 14],
    7: [8, 12],
    8: [5, 7, 9],
    9: [8, 13],
    10: [1, 11, 22],
    11: [4, 10, 12, 19],
    12: [7, 11, 16],
    13: [9, 14, 18],
    14: [6, 13, 15, 21],
    15: [3, 14, 24],
    16: [12, 17],
    17: [16, 18, 20],
    18: [13, 17],
    19: [11, 20],
    20: [17, 19, 21, 23],
    21: [14, 20],
    22: [10, 23],
    23: [20, 22, 24],
    24: [15, 23],
}
lines = [[t-1 for t in l] for l in lines]
tile_adjacency = {t-1: [g-1 for g in n] for t,n in tile_adjacency.items()}


MEN = 9
FLYING = True


class Player(Enum):
    X = 1
    O = 2


class Phase(Enum):
    SETTING = 1
    MOVING = 2


def closes_mill(state, tile_idx, target_idx):
    board = [t for t in state['board']]
    player = state['player']
    if tile_idx is not None:
        board[tile_idx] = None
    board[target_idx] = player
    for line in lines:
        if target_idx in line:
            if all(board[tile]==player for tile in line):
                return True
    return False


def players():
    return [Player.X, Player.O]


def outcomes():
    return {Player.X: 'X', Player.O: 'O'}


def initial_state():
    board = [None] * 24
    men_set = 0
    phase = Phase.SETTING
    player = Player.X
    return dict(board=board, men_set=men_set, phase=phase, player=player)
# def initial_state():
#     board = [None] * 24
#     board[0] = Player.X
#     board[1] = Player.X
#     board[14] = Player.X
#     board[9] = Player.O
#     board[15] = Player.O
#     board[22] = Player.O
#     men_set = 2
#     phase = Phase.MOVING
#     player = Player.X
#     return dict(board=board, men_set=men_set, phase=phase, player=player)


def legal_moves(state):
    actions = {player: [] for player in players()}
    player = state['player']
    board = state['board']
    if state['phase'] == Phase.SETTING:
        targets = [idx for idx, tile in enumerate(board) if tile is None]
        for target_idx in targets:
            if closes_mill(state, None, target_idx):
                enemies = [idx for idx, t in enumerate(board)
                           if board[idx] not in [None, player]]
                enemies_not_in_mills = []
                for enemy in enemies:
                    for line in lines:
                        if enemy in line:
                            if all(board[tile] not in [player, None] for tile in line):
                                # enemy is in a mill
                                break
                    else:  # Enemy is not in a mill
                        enemies_not_in_mills.append(enemy)
                if enemies_not_in_mills:  # Not all enemy stones are in mills
                    enemies = enemies_not_in_mills  # ...otherwise, all enemy stones are capturable
                for enemy in enemies:
                    actions[player].append((None, target_idx, enemy))
            else:  # No mill closed
                actions[player].append((None, target_idx, None))
    else:
        if FLYING and len(tiles := [idx for idx, tile in enumerate(board) if tile==player]) == 3:  # Flying enabled
            moves = [(tile_idx, target_idx)
                     for tile_idx in tiles
                     for target_idx, target in enumerate(board)
                     if target is None]
        else:
            moves = [(tile_idx, target_idx)
                     for tile_idx, tile in enumerate(board)
                     if tile == player
                     for target_idx in tile_adjacency[tile_idx]
                     if board[target_idx] is None]
        for tile_idx, target_idx in moves:
            # Move can be made; Does it close a mill?
            if closes_mill(state, tile_idx, target_idx):
                enemies = [idx for idx, t in enumerate(board)
                           if board[idx] not in [None, player]]
                for enemy in enemies:
                    actions[player].append((tile_idx, target_idx, enemy))
            else:  # No mill closed
                actions[player].append((tile_idx, target_idx, None))
    return actions


def make_move(state, all_actions):
    new_board = [t for t in state['board']]
    player = state['player']
    action = all_actions[player]
    tile_idx, target_idx, enemy_idx = action

    if tile_idx is not None:  # Moving a man, clearing up old tile
        new_board[tile_idx] = None
    new_board[target_idx] = player  # Occupying new tile
    if enemy_idx is not None:  # Capturing
        new_board[enemy_idx] = None

    new_men_set = state['men_set']
    new_phase = state['phase']
    if state['phase'] == Phase.SETTING:
        if player == Player.O:
            new_men_set += 1
            if new_men_set == MEN:
                new_phase = Phase.MOVING

    if player == Player.X:
        new_player = Player.O
    else:
        new_player = Player.X

    return dict(board=new_board, men_set=new_men_set, phase=new_phase, player=new_player)


def game_winner(state):
    if state['phase'] == Phase.SETTING:
        return None  # FIXME: Can I prove that you can't win yet?
    if len([t for t in state['board'] if t==Player.X]) < 3:
        return Player.O
    elif len([t for t in state['board'] if t==Player.O]) < 3:
        return Player.X
    elif len(legal_moves(state)[state['player']]) == 0:  # Win by immobilizing opponent
        if state['player'] == Player.X:
            return Player.O
        else:
            return Player.X
    else:
        return None


def hash_state(state):
    str_reprs = {
        Player.X: 'X',
        Player.O: 'O',
        None: '.',
    }
    board_str = ''.join(str_reprs[t] for t in state['board'])
    men_set_str = str(state['men_set'])
    phase_str = {Phase.SETTING: 'S', Phase.MOVING: 'M'}[state['phase']]
    player_str = str_reprs[state['player']]
    return ''.join([board_str, men_set_str, phase_str, player_str])


def evaluate_state(state):
    winner = game_winner(state)
    if winner == Player.X:
        return {Player.X: math.inf, Player.O: -math.inf}
    elif winner == Player.O:
        return {Player.X: -math.inf, Player.O: math.inf}
    else:
        return {p: len([t for t in state['board'] if t==p]) for p in players()}


def visualize_state(state):
    str_reprs = {
        Player.X: 'X',
        Player.O: 'O',
        None: '.',
    }
    s = [str_reprs[t] for t in state['board']]
    board_str = f"""
 {s[0]}-----------{s[1]}-----------{s[2]}        1-----------2-----------3
 |           |           |        |           |           |
 |   {s[3]}-------{s[4]}-------{s[5]}   |        |   4-------5-------6   |
 |   |       |       |   |        |   |       |       |   |
 |   |   {s[6]}---{s[7]}---{s[8]}   |   |        |   |   7---8---9   |   |
 |   |   |       |   |   |        |   |   |       |   |   |
 {s[9]}---{s[10]}---{s[11]}       {s[12]}---{s[13]}---{s[14]}       10--11--12      13--14--15
 |   |   |       |   |   |        |   |   |       |   |   |
 |   |   {s[15]}---{s[16]}---{s[17]}   |   |        |   |  16--17--18   |   |
 |   |       |       |   |        |   |       |       |   |
 |   {s[18]}-------{s[19]}-------{s[20]}   |        |  19------20------21   |
 |           |           |        |           |           |
 {s[21]}-----------{s[22]}-----------{s[23]}       22----------23----------24
"""[1:]
    print(board_str)
    print()
    if state['phase'] == Phase.SETTING:
        print(f"Phase: Setting men ({state['men_set']+1} of {MEN})")
    else:
        print("Phase: Moving men")
    winner = game_winner(state)
    if winner is not None:
        if winner == Player.X:
            print(f"Winner: X")
        elif winner == Player.O:
            print(f"Winner: O")
        else:  # winner == DRAW
            print("Game ended in a draw.")
    else:
        if state['player'] == Player.X:
            print(f"Move: X")
        else:
            print(f"Move: O")


def move_to_string(move):
    tile, target, enemy = move
    if tile is None:
        if enemy is None:
            return f"{target+1}"
        else:
            return f"{target+1}x{enemy+1}"
    else:
        if enemy is None:
            return f"{tile+1}-{target+1}"
        else:
            return f"{tile+1}-{target+1}x{enemy+1}"


def query_action(player, moves):
    str_to_move = {move_to_string(move): move
                   for move in moves}
    print(f"Legal moves: {', '.join(str_to_move.keys())}")
    while True:
        choice = input("Your choice: ")
        if choice not in str_to_move:
            print("Invalid move.")
        else:
            action = str_to_move[choice]
            break
    print()
    return action


def query_ai_players():
    print(f"Should I play X, O, XO (both), or N (neither)?")
    ai_players = None
    while ai_players is None:
        i = input("> ")
        if i in ['X', 'x']:
            ai_players = [Player.X]
        elif i in ['O', 'o']:
            ai_players = [Player.O]
        elif i in ['XO', 'xo']:
            ai_players = [Player.X, Player.O]
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
        'default': evaluate_state,
    }
    visualize_state = visualize_state
    query_action = query_action
