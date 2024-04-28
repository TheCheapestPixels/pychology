from pychology.utility import (
    Reasoner,
    Option,
    TuningConsideration,
    Consideration,
    OptIn,
    OptOut,
)


### Predicates

def bb_true(field):
    def inner(env):
        return env[field]
    return inner


def bb_false(field):
    def inner(env):
        return not env[field]
    return inner


def is_badly_hurt(env):
    return env['hit_points'] < 50.0


### Utility functions

def enemy_closeness(env):
    rank = -1
    bonus = 0
    multiplier = max(0.0, (5 - env['foot_distance_to_enemy']) * 0.2)
    return (rank, bonus, multiplier)


def enemy_farness(env):
    rank = -1
    bonus = 0
    multiplier = min(1.0, (env['foot_distance_to_enemy']) * 0.2)
    return (rank, bonus, multiplier)


### AI factory

def make_fighter():
    return Reasoner(
        Option(
            'patrol',
            TuningConsideration(),
            OptOut(bb_true('sees_enemy')),
        ),
        Option(
            'melee',
            TuningConsideration(rank=-1),
            OptOut(bb_false('has_sword')),
            OptIn(bb_true('sees_enemy'), opt_in_rank=1),
            Consideration(enemy_closeness),
        ),
        Option(
            'ranged',
            TuningConsideration(rank=-1),
            OptOut(bb_false('has_gun')),
            OptIn(bb_true('sees_enemy'), opt_in_rank=1),
            Consideration(enemy_farness),
        ),
        Option(
            'flee',
            TuningConsideration(rank=-1),
            OptIn(is_badly_hurt, opt_in_rank=2),
        ),
    )    


### The game

if __name__ == '__main__':
    env = dict(
        distance_to_enemy=2.0,
        foot_distance_to_enemy=3.0,
        sees_enemy=True,
        hit_points=130.0,
        has_sword=True,
        has_gun=True,
    )
    ai = make_fighter()
    plan = ai(env)
    print(f"Plan: {plan}")
