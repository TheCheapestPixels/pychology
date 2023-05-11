import math


X = 1
O = 2
DRAW = 3

ROWS = 6
COLUMNS = 7


def players():
    return [X, O]


def initial_state():
    board = {c: [] for c in range(COLUMNS)}
    player = X
    return dict(board=board, player=player)


def game_winner(state):
    board = state['board']
    def get_tile(column_id, row_id):
        if row_id < len(board[column_id]):
            return board[column_id][row_id]
        else:
            raise KeyError
    # Columns
    for c_id in range(COLUMNS):
        for r_id in range(ROWS - 3):
            try:
                t_1 = get_tile(c_id, r_id)
                t_2 = get_tile(c_id, r_id + 1)
                t_3 = get_tile(c_id, r_id + 2)
                t_4 = get_tile(c_id, r_id + 3)
                if t_1 == t_2 == t_3 == t_4:
                    return t_1
            except KeyError:
                pass
    # Rows
    for r_id in range(ROWS):
        for c_id in range(COLUMNS - 3):
            try:
                t_1 = get_tile(c_id, r_id)
                t_2 = get_tile(c_id + 1, r_id)
                t_3 = get_tile(c_id + 2, r_id)
                t_4 = get_tile(c_id + 3, r_id)
                if t_1 == t_2 == t_3 == t_4:
                    return t_1
            except KeyError:
                pass
    # Upward Diagonals
    for r_id in range(ROWS - 3):
        for c_id in range(COLUMNS - 3):
            try:
                t_1 = get_tile(c_id, r_id)
                t_2 = get_tile(c_id + 1, r_id + 1)
                t_3 = get_tile(c_id + 2, r_id + 2)
                t_4 = get_tile(c_id + 3, r_id + 3)
                if t_1 == t_2 == t_3 == t_4:
                    return t_1
            except KeyError:
                pass
    # Downward Diagonals
    for r_id in range(ROWS - 3):
        for c_id in range(COLUMNS - 3):
            try:
                t_1 = get_tile(c_id, r_id + 3)
                t_2 = get_tile(c_id + 1, r_id + 2)
                t_3 = get_tile(c_id + 2, r_id + 1)
                t_4 = get_tile(c_id + 3, r_id)
                if t_1 == t_2 == t_3 == t_4:
                    return t_1
            except KeyError:
                pass
    # If the board is filled and there is no winner, it's a draw.
    if all([len(c)==ROWS for c in state['board'].values()]):
        return DRAW
    # So there's no winner, and the board isn't full; The game goes on.
    return None


def legal_moves(state):
    moves = {player: [] for player in players()}
    actual_moves = [c_id
                    for c_id, c in state['board'].items()
                    if len(c)<ROWS]
    moves[state['player']] = actual_moves
    return moves


def make_move(state, moves):
    player = state['player']
    move = moves[player]
    new_board = {c_id: [t for t in c]
                 for c_id, c in state['board'].items()}
    new_board[move].append(player)
    if player == X:
        new_player = O
    else:
        new_player = X
    return dict(board=new_board, player=new_player)


def hash_state(state):
    board = state['board']
    tiles = []
    for c_id in range(COLUMNS):
        for t_id in range(ROWS):
            if (len(board[c_id]) - 1) < t_id:
                tiles.append(".")
            else:
                if board[c_id][t_id] == X:
                    tiles.append("X")
                else:
                    tiles.append("O")
    return ''.join(tiles)                    


def evaluate_state(state):
    winner = game_winner(state)
    if winner == X:
        return {X: math.inf, O: -math.inf}
    elif winner == O:
        return {X: -math.inf, O: math.inf}
    else:
        return {X: 0, O: 0}


def visualize_state(state):
    print()
    board = state['board']
    lines = []
    for r_id in range(ROWS-1, -1, -1):
        tiles = []
        for c_id in range(COLUMNS):
            if (len(board[c_id]) - 1) < r_id:
                tiles.append(".")
            else:
                if board[c_id][r_id] == X:
                    tiles.append("X")
                else:
                    tiles.append("O")
        lines.append(' '.join(tiles))
    lines.append(' '.join(str(r_id) for r_id in range(COLUMNS)))
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
        if state['player'] == X:
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
    legal_moves = legal_moves
    make_move = make_move
    players = players
    hash_state = hash_state
    evaluate_state = evaluate_state
    query_ai_players = query_ai_players
    visualize_state = visualize_state
    query_action = query_action
