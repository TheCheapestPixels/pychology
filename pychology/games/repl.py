import sys
from pychology.search import FixedPliesAI
from pychology.search import StateOfTheArt


# Experimental code

class LineRewardingAI(StateOfTheArt):
    evaluation_function = 'line_rewarder'
    node_limit = 10000


class MonteCarloAI(StateOfTheArt):
    evaluation_function = 'mcts'


# The actual code

class DefaultAI(FixedPliesAI):
    expansion_steps = 8


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
                        ai_class = DefaultAI
                    else:
                        ai_class = ai_classes[player]
                        
                    search = ai_class(game, state, player)
                    actions[player] = search.run()
                else:
                    actions[player] = []
        state = game.make_move(state, actions)
    return winner


def play_interactively(game):
    ai_players = game.query_ai_players()
    ai_classes = {p: DefaultAI for p in game.players()}
    state = game.initial_state()
    repl(game, state, ai_players, ai_classes=ai_classes)


def auto_tournament(game):
    results = {p: 0 for p in game.players()}
    ai_players = game.players()
    ai_classes = {p: StateOfTheArt for p in game.players()}
    for i in range(100):
        print(i)
        state = game.initial_state()
        winner = repl(
            game, state, ai_players,
            visuals=True, ai_classes=ai_classes,
        )
        results[winner] += 1
    max_time = max(timing)
    min_time = min(timing)
    mean_time = sum(timing) / len(timing)
    median_time = sorted(timing)[int(len(timing)/2.0)]
    print(f"Min: {min_time}, Max: {max_time}, Mean: {mean_time}, Median: {median_time}")
    print(f"X   : {results[X]}\nO   : {results[O]}\nDraw: {results[DRAW]}\n")


if __name__ == '__main__':
    from argparse import ArgumentParser
    import importlib

    parser = ArgumentParser(
        description="Frontend for pychology.search, applied to game modules. You can play interactively, or ",
        epilog="",
    )
    parser.add_argument(
        "game",
        help="The module name of the game to be played.",
    )
    parser.add_argument(
        '-t', '--tournament',
        action='store_true',
        help="Collects statistics of AIs playing against each other.",
    )
    args = parser.parse_args()

    #try:
    game = importlib.import_module(args.game)
    #except Exception as e:
    #    print(f"Can't import game module {args.game}")
    #    sys.exit(1)
    if args.tournament:
        auto_tournament(game.Game)
    else:
        play_interactively(game.Game)
