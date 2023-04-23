X = 1
O = 2

lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
]


def initial_state():
    board = [None, None, None, None, None, None, None, None, None]
    player = X
    state = dict(board=board, player=player)
    return state


def game_winner(state):
    board = state['board']
    for player in [X, O]:
        for line in lines:
            if all(board[tile] == player for tile in line):
                return player
    return None


def legal_moves(state):
    board = state['board']
    moves = []
    for idx, tile_state in enumerate(state['board']):
        if tile_state is None:
            moves.append(idx)
    return moves


def make_move(state, move):
    new_state = dict(board=[t for t in state['board']], player=state['player'])
    new_state['board'][move] = new_state['player']
    winner = game_winner(new_state)
    if winner is None:
        if new_state['player'] == X:
            new_state['player'] = O
        else:
            new_state['player'] = X
    else:
        new_state['player'] = None
    return new_state


if __name__ == '__main__':
    def visualize_state(state):
        def tile(p):
            if p == X:
                return ' X '
            elif p == O:
                return ' O '
            else:
                return '   '
        board = state['board']
        v = [tile(b) for b in board]
        winner = game_winner(state)
        print(f"{v[0]}|{v[1]}|{v[2]}\n---+---+---\n{v[3]}|{v[4]}|{v[5]}\n---+---+---\n{v[6]}|{v[7]}|{v[8]}")
        if winner is not None:
            if winner == X:
                print(f"Winner: X")
            else:
                print(f"Winner: O")
        else:
            if state['player'] == X:
                print(f"Move: X")
            else:
                print(f"Move: O")
            moves = legal_moves(state)
            print(f"Legal moves: {', '.join(str(m) for m in moves)}")

    def query_action(moves):
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
        return choice

    state = initial_state()

    while True:
        visualize_state(state)
        if game_winner(state) is not None:
            break

        moves = legal_moves(state)
        action = query_action(moves)
        state = make_move(state, action)
