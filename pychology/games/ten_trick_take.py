import math


full_hand = [1, 2, 3]


### Game-defining functions

def players():
    return [1, 2, 3]


def initial_state():
    players = 3
    cards = {p + 1: full_hand.copy() for p in range(players)}
    points = {1: 0, 2: 0, 3: 0}
    dealer = 1
    state = dict(cards=cards, points=points, dealer=dealer)
    return state


def game_winner(state):
    if len(state['cards'][1]) > 0:  # Is game even done?
        return None
    res = reversed(sorted(state['points'].items(), key=lambda s: s[1]))
    res = list(res)
    winners = [pl for pl, po in res if po == res[0][1]]
    return winners


def legal_moves(state):
    return state['cards']


def make_move(state, moves):
    new_cards = {p: [c for c in state['cards'][p] if c != moves[p]]
                 for p in players()}
    points = sum(moves.values())
    takes = list(reversed(sorted(moves.items(), key=lambda m: m[1])))
    take_val = takes[0][1]
    takers = [p for p, c in takes if c==take_val]
    if len(takers) > 1:
        dealer = state['dealer']
        order = [((p + dealer - 1) % len(players())) + 1
                 for p in range(0, len(players()))]
        for p in order:
            if p in takers:
                taker = p
                break
    else:
        taker = takers[0]
    new_points = {k: v for k, v in state['points'].items()}
    new_points[taker] += points
    new_dealer = state['dealer'] % len(players()) + 1
    new_state = dict(
        cards=new_cards,
        points=new_points,
        dealer=new_dealer,
    )
    return new_state


### Game-interpreting functions

def hash_state(state):
    hash_str = ""
    for hand in state['cards'].values():
        for full in full_hand:
            if full in hand:
                hash_str += str(full)
            else:
                hash_str += "-"
        hash_str += "|"
    hash_str += "|"
    for p in state['points'].values():
        hash_str += str(p) + "|"
    return hash_str


def evaluate_state(state):
    winner = game_winner(state)
    if winner is not None:
        res = {p: -math.inf for p in players()}
        for w in winner:
            res[w] = math.inf
        return res
    else:
        return {p: state['points'][p] + sum(state['cards'][p]) for p in players()}


### User interaction

def visualize_state(state):
    for p in players():
        cards = ', '.join([str(c) for c in state['cards'][p]])
        points = state['points'][p]
        print(f"{p} ({points} points): {cards}")
    if (winner := game_winner(state)) is not None:
        print(f"Winners: {', '.join([str(w) for w in winner])}")


def query_action(player, moves):
    while True:
        choice = input(f"Your choice, player {player}: ")
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
    print(f"Which players should I play?")
    ai_players = None
    while ai_players is None:
        i = input("> ")
        try:
            players = i.split(" ")
            ai_players = [int(p) for p in players]
        except:
            print("Please enter 1, 2, and/or 3, separated by spaces.")
    return ai_players


class Game:
    initial_state = initial_state
    game_winner = game_winner
    legal_moves = legal_moves
    make_move = make_move
    players = players
    hash_state = hash_state
    evaluation_funcs = {'default': evaluate_state}
    query_ai_players = query_ai_players
    visualize_state = visualize_state
    query_action = query_action
