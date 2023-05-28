import sys
from itertools import permutations

from pychology.search import TranspositionTable
from pychology.search import NoExpansion
from pychology.search import FullExpansion
from pychology.search import NodeLimitedExpansion
from pychology.search import StepLimitedExpansion
from pychology.search import SingleNodeBreadthSearch
from pychology.search import BreadthSearch
from pychology.search import AllCombinations
from pychology.search import ZeroSumPlayer
from pychology.search import Minimax
from pychology.search import RandomChooser
from pychology.search import BestMovePlayer
from pychology.search import Search
from pychology.search import TTAnalysis

from pychology.search import StateOfTheArt
from pychology.search import RandomAI


class DefaultAI(StateOfTheArt):
    node_limit = 10000


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


def play_interactively(game, ai_classes=None):
    ai_players, ai_classes = map_ais_to_players(game, ai_classes)
    state = game.initial_state()
    repl(game, state, ai_players, ai_classes=ai_classes)


def auto_tournament(game, ai_classes=None, rounds=100):
    results = {o: 0 for o in game.outcomes().keys()}
    ai_players, ai_classes = map_ais_to_players(game, ai_classes)
    for i in range(rounds):
        print(i)
        state = game.initial_state()
        winner = repl(
            game, state, ai_players,
            visuals=False, ai_classes=ai_classes,
        )
        results[winner] += 1
    # max_time = max(timing)
    # min_time = min(timing)
    # mean_time = sum(timing) / len(timing)
    # median_time = sorted(timing)[int(len(timing)/2.0)]
    # print(f"Min: {min_time}, Max: {max_time}, Mean: {mean_time}, Median: {median_time}")
    for player, result in results.items():
        player_str = game.outcomes()[player]
        print(f"{player_str}: {result}")


def map_ais_to_players(game, ai_classes):
    if ai_classes is None:
        ai_players = game.query_ai_players()
        ai_classes = {p: DefaultAI for p in game.players()}
    elif len(ai_classes) == 1:  # One spec given; Use for all AIs
        ai_players = game.query_ai_players()
        ai_classes = {p: ai_classes[0] for p in game.players()}
    else:  # More than one spec; Map to players
        # FIXME: This should be a matter of passing `strict=True` to
        # zip, but that only works for Python 3.10+
        if len(ai_classes) != len(game.players()):
            raise Exception("Number of AI players differs from game player number.")
        ai_classes = {p: ai
                      for p, ai in zip(
                              game.players(),
                              ai_classes,
                      )}
        ai_players = [p for p, ai in ai_classes.items() if ai is not None]
    return ai_players, ai_classes


def assemble_search(spec_str):
    properties = dict(
        storage='tt',
        limit_type='none',
        select_action='best',
        analysis=False,
    )

    # Pre-defined AIs
    if spec_str == 'human':
        return None
    elif spec_str == 'sota':
        return StateOfTheArt
    elif spec_str == 'random':
        return RandomAI
    
    # Parse the configuration string
    for prop_spec in spec_str.split(","):
        prop_type, _, prop_value = prop_spec.partition("=")
        if prop_value:
            properties[prop_type] = prop_value
        else:
            properties[prop_type] = True

    # Assemble the class
    bases = []
    attribs = {}

    storage_type = properties['storage']
    if storage_type == 'tt':
        bases.append(TranspositionTable)
    else:
        raise Exception(f"Unknown storage type '{storage_type}'.")

    limit_type = properties["limit_type"]
    if limit_type == "none":
        bases.append(FullExpansion)
    elif limit_type == "no_exp":
        bases.append(NoExpansion)
    elif limit_type == "plies":
        bases.append(StepLimitedExpansion)
        bases.append(BreadthSearch)
        if 'limit' in properties:
            attribs['expansion_steps'] = int(properties['limit'])
    elif limit_type == 'nodes':
        bases.append(NodeLimitedExpansion)
        bases.append(SingleNodeBreadthSearch)
        if 'limit' in properties:
            attribs['node_limit'] = int(properties['limit'])
    else:
        raise Exception(f"Unknown limit type '{limit_type}'.")

    bases.append(AllCombinations)
    bases.append(ZeroSumPlayer)
    bases.append(Minimax)
    if 'eval_func' in properties:
        attribs['evaluation_function'] = properties['eval_func']

    action_selection = properties["select_action"]
    if action_selection == 'best':
        bases.append(BestMovePlayer)
    elif action_selection == 'random':
        bases.append(RandomChooser)
    else:
        raise Exception(f"Unknown action selector '{action_selection}'.")

    if properties.get('analysis', False):
        if storage_type == 'tt':
            bases.append(TTAnalysis)
        else:
            raise Exception("Storage lacks corresponding analysis capability.")

    bases.append(Search)

    search = type('AssembledSearch', tuple(bases), attribs)
    return search


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
    parser.add_argument(
        '-r', '--rounds',
        help="Collects statistics of AIs playing against each other.",
    )
    parser.add_argument(
        'ai',
        nargs='*',
        help="Specifications for AI players.",
    )
    args = parser.parse_args()

    try:
        game = importlib.import_module(args.game)
    except Exception as e:
        print(f"Can't import game module {args.game}")
        raise e

    if not args.ai:
        ai_classes = [DefaultAI]
    elif len(args.ai) == 1:
        ai_classes = [assemble_search(args.ai[0])]
    else:
        ai_classes = [assemble_search(ai) for ai in args.ai]

    # Run
    if args.tournament:
        kwargs = dict(ai_classes=ai_classes)
        if args.rounds:
            kwargs['rounds'] = int(args.rounds)
        auto_tournament(game.Game, **kwargs)
    else:
        play_interactively(game.Game, ai_classes=ai_classes)
