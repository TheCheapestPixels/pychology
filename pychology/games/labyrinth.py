import math


level_1 = "I...O"


level_2 = """
..I.. ...
  .   .
..... ...
.     .
....... .
.       .
. .......
. .   . .
... ... .
        .
.........
      .
      O"""[1:]


level_3 = """
I.                                                                                                   
...... ....... ........... . ......... ......... . ....... . . . . ... ... ......... ..... ..... . . 
   .   .       . .         . . .     .     .     .       . . . . .   .   .     .       .   .     . . 
 ..... ....... . ....... . ... ..... ................. . ... ....... ... ..... ..... ..... . ..... . 
     . . .     . .     . .   .   . .     .     .   . . . .       . . .   .   . .         . .     . . 
 ... . . ... ... ... ... . ..... . . ......... ... . . ... ... ... . ....... ..... ... . . . ..... . 
 . . .   . .   .       . . .   . .     .   .   .   . . .     .   .     .   . . .   .   . . . . . . . 
 . ..... . ..... . . ......... . . . ... ..... . . . ..... . . . ... ... ... . . ............. . ... 
 .   .     . . . . . . .   .   .   .         . . . .   .   . . . .       .       .     . .   .     . 
 . ..... . . . . . . . ... ... . ........... . ... . . ..... ......... ... ..... ..... . . ..... ... 
   .     .       . .     . .   . . .   .     .   .   .     . .   .     .   .   .   . .   .     .     
 . ... . ..... . ..... ... ... . . ... . ....... . ..... ..... . ... ....... ..... . . ... . ....... 
 . .   . .     .   . . .   .     .           .   .   . .       .   . .   .     .     .   . . . .     
 . ... ....... ... . ... ... . ........... . . ....... ......... ... . ... ..... . ... ... ... ..... 
 .   . . .   . . .       . . .   .   . . . .     .         .       . .         . . .     .   .     . 
 ....... . ..... ..... ... . ..... . . . . . ....... . . ..... . ......... ... ..... ..... . ... ... 
 . .           . .       . .     . .     . .   . .   . .   .   .     .       .           . .       . 
 . ... ..... . . . . . . . . ....... . ..... ... . ... ......... ... ... ... ... ... ..... ....... . 
 .   .   .   . .   . . .   .       . .     .       . . .     .     .     .     .   . . .   . .       
 . ..... ... ... ....... ....... . ... ..... ..... . . ..... ..... ... ......... ..... . ... . ... . 
     .   .   .       . . . .     . .     .   .   .   .     .     . .   . . .       .     .     . . . 
 . ... . . ... . . ... ... . ... ..... . ... . ....... ....... ... ... . . . ..... . . ... . ... ... 
 . .   . . .   . .     . .   .         .   .         .     .       .       . . .   . .   . .     . . 
 ......... ... ....... . . ... . ..... . . ... . . ......... . ......... . ... ... ... ......... . . 
   .   .   . . .           .   .   .   . . . . . . . .     . . .     . . . .   .     . .   .     .   
 . ... ... . ... ... ..... ......... ..... . ....... ... . ... ... ... ... . ... ... . ... . . ... . 
 .   .     . .     . .     . .   .   .       .   .     . . .     .   . . . . . . .   . . .   . . . . 
 ......... . . ... . ....... ... ......... ... ... . ... ... ....... . . . . . . ....... . . ... . . 
 . .     . .     . . .   .       .       .         . .   .       .   . .     .       .     . .   . . 
 . . ... . ......... ... ... ....... ... ... . ....... ......... . ... ... . ... ............. ..... 
   . . . .     . .   . .           .   . . . . .   . .       .           . . . .   . . .       . .   
 ... . ..... . . ..... . ... ..... . . ... ..... . . . ..... . ... . ... ..... ... . . . ... . . . . 
 . . . . .   .     . .   . .     . . .     .     . .   . . . . .   . . . .     . . . .     . . .   . 
 . . . . . ....... . ... . ............... . ... ... . . . . . ....... ... ..... . . ......... ..... 
 . . . .     .   .   .     .   .       .   .   . .   .   .   . . .   .   .         . . . .         . 
 . . . ... . ... . ... ... ... ... ... ... ..... ... ... ....... . . . ..... ... ... . . . . ... ... 
     . .   . .     .   . .   .   . .   .   .         .   . .   . . .   . .     . .   .     . . .     
 ..... ... ..... ....... . ... ... ....... ... . ... ... . ... . ..... . ... . ..... . ..... . . ... 
   .   .     .   . .   . .     . .   .     .   .   . . . .     .   .   .   . . .   .       . .   .   
 ..... ..... ..... ... . ..... . . ... ......... ..... ... ....... ... . ..... ... .................
                                                                                                   O"""[1:]


level = level_2


### Game definition

def players():
    return None

def initial_state():
    position = None
    way_out = None
    tiles = set()
    moves_made = []

    for l_idx, line in enumerate(level.split('\n')):
        for t_idx, tile in enumerate(line):
            if tile in '.IO':
                coord = (l_idx, t_idx)
                tiles.add(coord)
                if tile=='I':
                    position = coord
                elif tile=='O':
                    way_out = coord
    return dict(tiles=tiles, position=position, way_out=way_out, moves_made=moves_made)


def game_winner(state):
    if state['position'] == state['way_out']:
        return [None]


def legal_moves(state):
    moves = []
    tiles = state['tiles']
    l, t = state['position']
    if (l-1, t) in tiles:
        moves.append('w')
    if (l+1, t) in tiles:
        moves.append('s')
    if (l, t-1) in tiles:
        moves.append('a')
    if (l, t+1) in tiles:
        moves.append('d')
    return {None: moves}


def make_move(state, moves):
    tiles = state['tiles']
    old_position = state['position']
    l, t = old_position
    moves_made = state['moves_made']
    move = moves[None]
    if move == "w":
        position = (l-1, t)
    elif move == "s":
        position = (l+1, t)
    elif move == "a":
        position = (l, t-1)
    elif move == "d":
        position = (l, t+1)
    way_out = state['way_out']
    path = moves_made + [old_position]
    return dict(tiles=tiles, position=position, way_out=way_out, moves_made=path)


### Expert knowledge

def evaluate_state(state):
    score = -len(state['moves_made'])
    l_p, t_p = state['position']
    l_o, t_o = state['way_out']
    #dist = math.sqrt((l_o - l_p)**2 + (t_o - t_p)**2)
    dist = 0
    return {None: score-dist}


def non_cyclic_walker(state, moves):
    filtered_moves = []
    for move in moves[None]:
        successor = make_move(state, {None: move})
        if successor['position'] in state['moves_made']:
            # Drop this cyclical move.
            continue
        filtered_moves.append(move)
    return filtered_moves


portfolios = {'ncw': non_cyclic_walker}


### Tooling

def hash_state(state):
    return (*state['moves_made'], state['position'])


def visualize_state(state):
    tiles = state['tiles']
    position = state['position']
    moves_made = state['moves_made']
    way_out = state['way_out']
    lines = max(l for l,t in tiles) + 1
    columns = max(t for l,t in tiles) + 1
    board_repr = []
    for l_idx in range(lines):
        line_repr = []
        for t_idx in range(columns):
            coord = (l_idx, t_idx)
            if coord in tiles:
                if coord == position:
                    line_repr.append('X')
                elif coord == way_out:
                    line_repr.append('O')
                else:
                    line_repr.append(' ')
            else:
                line_repr.append('#')
        board_repr.append(''.join(line_repr))
    print('\n'.join(board_repr))
    print(f"Moves made: {len(moves_made)}")
    if game_winner(state):
        print(f"You made it in {len(moves_made)} moves!")


def query_action(player, moves):
    while True:
        choice = input(f"Your choice ({', '.join(moves)}): ")
        if choice not in moves:
            print("Invalid move.")
        else:
            break
    print()
    return choice


def query_ai_players():
    print(f"Should I play?")
    ai_players = None
    while ai_players is None:
        i = input("> ")
        if i in ['Y', 'y']:
            ai_players = [None]
        elif i in ['N', 'n']:
            ai_players = []
        else:
            print("Please enter Y or N.")
    return ai_players


class Game:
    initial_state = initial_state
    game_winner = game_winner
    legal_moves = legal_moves
    make_move = make_move
    players = players
    hash_state = hash_state
    evaluation_funcs = {'default': evaluate_state}
    portfolios = portfolios
    query_ai_players = query_ai_players
    visualize_state = visualize_state
    query_action = query_action
