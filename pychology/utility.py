import random
from functools import reduce
from operator import mul


def prod(seq):
    return reduce(mul, seq)


class Reasoner:
    def __init__(self, *options, name=None):
        self.options = options
        self.name = name

    def __call__(self, environment):
        option = self.select_option(environment)
        return option.plan

    def select_option(self, environment):
        valuations = [option(environment) for option in self.options]
        # Remove options with weight of 0.0
        valuations = [v for v in valuations if v[2] > 0.0]
        # Remove options with non-maximal rank
        max_rank = max(v[1] for v in valuations)
        valuations = [v for v in valuations if v[1] == max_rank]
        # Select option
        selected = random.choices(
            [v[0] for v in valuations],
            weights=[v[2] for v in valuations],
        )[0]
        # Done!
        return selected
        
    def __repr__(self):
        if self.name is not None:
            return self.name
        return self


class Option:
    def __init__(self, plan, *considerations, name=None):
        self.plan = plan
        self.considerations = considerations
        self.name = name

    def __call__(self, environment):
        valuations = [cons(environment) for cons in self.considerations]
        highest_rank = max(r for r, _, _ in valuations)
        boni = sum(b for _, b, _ in valuations)
        multiplier = prod(m for _, _, m in valuations)
        weight = boni * multiplier
        return (self, highest_rank, weight)

    def __repr__(self):
        if self.name is not None:
            return self.name
        return self


class Consideration:
    def __init__(self, utility_func, name=None):
        self.func = utility_func
        self.name = name

    def __call__(self, environment):
        return self.func(environment)

    def __repr__(self):
        if self.name is not None:
            return self.name
        return self


class TuningConsideration:
    def __init__(self, rank=0, bonus=1.0, multiplier=1.0):
        self.rank = rank
        self.bonus = bonus
        self.multiplier = multiplier

    def __call__(self, environment):
        return (self.rank, self.bonus, self.multiplier)


class OptIn:
    def __init__(self, condition, rank=-1000, opt_in_rank=1):
        self.cond = condition
        self.rank = rank
        self.opt_in_rank = opt_in_rank

    def __call__(self, environment):
        if self.cond(environment):
            return (self.opt_in_rank, 0.0, 1.0)
        return (self.rank, 0.0, 1.0)


class OptOut:
    def __init__(self, condition, rank=-1000):
        self.cond = condition
        self.rank = rank

    def __call__(self, environment):
        if self.cond(environment):
            return (self.rank, 0.0, 0.0)
        return (self.rank, 0.0, 1.0)
