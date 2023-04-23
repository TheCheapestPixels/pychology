X = 1
O = 2
DRAW = 3

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
    # Proper winner
    for player in [X, O]:
        for line in lines:
            if all(board[tile] == player for tile in line):
                return player
    # Draw
    if all(t in [X, O] for t in board):
        return DRAW
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
    def tile(p, idx=None):
        if p == X:
            return " X "
        elif p == O:
            return " O "
        else:
            if idx is None:
                return "   "
            else:
                return f" {str(idx)} "
    board = state['board']
    v = [tile(b, idx=idx) for idx, b in enumerate(board)]
    winner = game_winner(state)
    print(f"{v[0]}|{v[1]}|{v[2]}\n---+---+---\n{v[3]}|{v[4]}|{v[5]}\n---+---+---\n{v[6]}|{v[7]}|{v[8]}")
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


###

def repl(state, ai_players, visuals=True):
    while True:
        if visuals:
            visualize_state(state)
        winner = game_winner(state)
        if winner is not None:
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
    return winner


### Main program

def play_interactively():
    ai_players = query_ai_players()
    state = initial_state()
    repl(state, ai_players)


def auto_tournament():
    results = {X: 0, O: 0, DRAW: 0}
    ai_players = [X, O]
    for _ in range(100000):
        state = initial_state()
        results[repl(state, ai_players, visuals=False)] += 1
    print(f"X   : {results[X]}\nO   : {results[O]}\nDraw: {results[DRAW]}\n")


if __name__ == '__main__':
    play_interactively()
    #auto_tournament()
