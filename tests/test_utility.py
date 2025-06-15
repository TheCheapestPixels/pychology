from pychology.utility import Reasoner
from pychology.utility import Option
from pychology.utility import Consideration
from pychology.utility import TuningConsideration
from pychology.utility import OptOut
from pychology.utility import OptIn


def test_tuning_consideration():
    consideration = TuningConsideration()
    rank, bonus, multiplier = consideration(None)
    assert rank == 0
    assert bonus == 1.0
    assert multiplier == 1.0


def test_consideration():
    def utility_func(env):
        return (1, 2.0, 3.0)
    consideration = Consideration(utility_func)
    rank, bonus, multiplier = consideration(None)
    assert rank == 1
    assert bonus == 2.0
    assert multiplier == 3.0


def test_opt_out_off():
    def predicate(env):
        return False
    consideration = OptOut(predicate)
    rank, bonus, multiplier = consideration(None)
    assert multiplier == 1.0


def test_opt_out_on():
    def predicate(env):
        return True
    consideration = OptOut(predicate)
    rank, bonus, multiplier = consideration(None)
    assert multiplier == 0.0


def test_opt_in_off():
    def predicate(env):
        return False
    consideration = OptIn(predicate, opt_in_rank=1)
    rank, bonus, multiplier = consideration(None)
    assert rank < 0
    assert bonus == 0.0
    assert multiplier == 1.0


def test_opt_in_on():
    def predicate(env):
        return True
    consideration = OptIn(predicate, opt_in_rank=1)
    rank, bonus, multiplier = consideration(None)
    assert rank == 1
    assert bonus == 0.0
    assert multiplier == 1.0


def test_option():
    option = Option(
        'plan',
        TuningConsideration(),
    )
    option, rank, weight = option(None)
    assert option.plan == 'plan'
    assert rank == 0
    assert weight == 1.0


def test_reasoner():
    ai = Reasoner(
        Option(
            'default',
            TuningConsideration(),
        ),
    )
    plan = ai(None)
    assert plan == 'default'


def test_empty_ranks_are_ignored():
    ai = Reasoner(
        Option(
            'default',
            TuningConsideration(),
        ),
        Option(
            'high_ranking_no_weight',
            TuningConsideration(rank=1, multiplier=0.0),
        ),
        Option(
            'even_higher_ranking_no_weight',
            TuningConsideration(rank=2, multiplier=0.0),
        ),
    )
    assert ai(None) == 'default'


# FIXME: I need to decide on hos this case should make itself known.
# def test_all_ranks_are_empty():
#     ai = Reasoner(
#         Option(
#             'default',
#             TuningConsideration(multiplier=0.0),
#         ),
#     )
#     assert ai(None) == 'default'


def test_opt_out_reasoner():
    def predicate(env):
        return env
    ai = Reasoner(
        Option(
            'default',
            TuningConsideration(),
        ),
        Option(
            'special_case',
            TuningConsideration(rank=1),
            OptOut(predicate),
        ),
    )
    plan = ai(True)
    assert plan == 'default'
    plan = ai(False)
    assert plan == 'special_case'


def test_opt_in_reasoner():
    def predicate(env):
        return env
    ai = Reasoner(
        Option(
            'default',
            TuningConsideration(),
        ),
        Option(
            'special_case',
            TuningConsideration(rank=-1),
            OptIn(predicate, opt_in_rank=1),
        ),
    )
    plan = ai(False)
    assert plan == 'default'
    plan = ai(True)
    assert plan == 'special_case'
