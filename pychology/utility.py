def evaluate_utilities(specs):
    def inner(perceptions):
        utilities = {
            need: func(perceptions)
            for need, func in specs.items()
        }
        return utilities
    return inner


def normal_clip(v):
    return max(0.0, min(1.0, v))


def invert(v):
    return 1.0 - v
