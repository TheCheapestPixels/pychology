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


### Game-defining functions

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
    return {state['player']: moves}


def make_move(state, moves):
    move = moves[state['player']]
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


### User interaction

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
        moves = legal_moves(state)[state['player']]
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


def query_ai_players():
    print(f"Should I play X, O, or XO (both?)")
    ai_players = None
    while ai_players is None:
        i = input("> ")
        if i in ['X', 'x']:
            ai_players = [X]
        elif i in ['O', 'o']:
            ai_players = [O]
        elif i in ['XO', 'xo']:
            ai_players = [X, O]
        else:
            print("Please enter X, O, or XO.")
    return ai_players


if __name__ == '__main__':

    ai_players = query_ai_players()
    state = initial_state()

    while True:
        visualize_state(state)
        if game_winner(state) is not None:
            break

        moves = legal_moves(state)
        actions = {}
        for player, player_moves in moves.items():
            if player not in ai_players:
                actions[player] = query_action(player_moves)
            else:
                import random
                actions[player] = random.choice(player_moves)
        state = make_move(state, actions)
