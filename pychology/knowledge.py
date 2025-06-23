# Let's do some (hopefully) simple relational logic here...
# A knowledge base contains facts and rules.
# Facts are relations over values. For example, "Bob is your uncle":
# `kb.fact('uncle', 'bob', 'you')`
# Within the knowledge base, internal symbols are used so that if you
# were to assert that
# `kb.fact('parent', 'Greg', 'you')`
# `kb.fact('sibling', 'Greg', 'Bob')`
# `kb.fact('male', 'Bob')`
# then all the Bobs and Gregs refer to the same value, even though the
# strings given to `fact` are different Python objects.
# Rules are ways to infer implicitly known facts from explicitly known
# ones. For example, an uncle is the male sibling of one's parent:
# ```
# kb.rule(
#     ('uncle', Variable('UNCLE'), Variable('NEPHEW')),
#     ('parent', Variable('PARENT'), Variable('NEPHEW')),
#     ('sibling', Variable('PARENT'), Variable('UNCLE')),
#     ('male', Variable('UNCLE')),
# )
# ```
# The first line specifiess the inferable fact, and the following ones
# define the inference itself. When the knowledge base is now queried
# with "Who is your uncle?"
# `kb.query('uncle', Variable('UNCLE'), 'you')`
# it will infer that the uncle is indeed Bob (and that you have no other
# uncles) by deducing that
# * NEPHEW = you (this is given)
# * PARENT = Greg
# * UNCLE = Bob


class RelationError(Exception):
    def __init__(self, relation):
        self.relation = relation

    def __repr__(self):
        return f"Relation error: {self.relation} not in knowledge base."


class ArityError(Exception):
    def __init__(self, relation, arity, num_args):
        self.relation = relation
        self.arity = arity
        self.num_args = num_args

    def __repr__(self):
        return f"Arity error: {self.relation}({self.arity}) was given {self.num_args} arguments."


class Value:
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return f"{self.symbol}"


class Variable:
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return f"V:{self.symbol}"


class KnowledgeBase:
    def __init__(self):
        self.values = dict()  # symbol: Value(symbol)
        self.variables = dict()  # symbol: Variable(symbol)
        self.arity = dict()  # relation: number of arguments
        self.facts = dict()  # relation: [Value, ...]
        self.rules = dict()  # relation: (head_args, body_1_pred, ...)

    def _check_arity(self, relation, arguments):
        # Check arity
        if relation in self.arity:
            if self.arity[relation] != len(arguments):
                raise ArityError(relation, self.arity[relation], len(arguments))

        else:
            self.arity[relation] = len(arguments)

    def _internalize(self, arguments, no_variables=False):
        # Replace given arguments with internal representations, and
        # create those if necessary.
        replaced_arguments = list()
        for argument in arguments:
            if isinstance(argument, Variable):
                symbol = argument.symbol
                # Replace variable
                if no_variables:
                    assert False, "Facts may not have variables as arguments."
                if symbol not in self.variables:
                    self.variables[symbol] = Variable(symbol)
                replaced_arguments.append(self.variables[symbol])
            else:
                # Replace value
                if argument not in self.values:
                    self.values[argument] = Value(argument)
                replaced_arguments.append(self.values[argument])
        return replaced_arguments

    def fact(self, relation, *arguments):
        self._check_arity(relation, arguments)
        arguments = self._internalize(arguments, no_variables=True)

        if relation in self.facts:
            self.facts[relation].append(arguments)
        else:
            self.facts[relation] = [arguments]

    def rule(self, *predicates):
        assert len(predicates) > 1, "No body was given for the relation {predicates[0][0]}."
        # Check arity
        for relation, *arguments in predicates:
            self._check_arity(relation, arguments)
        # Substitute arguments for internal values
        new_preds = []
        for relation, *arguments in predicates:
            new_preds.append((relation, *self._internalize(arguments)))

        # Story
        head, body = predicates[0], predicates[1:]
        relation, arguments = head[0], head[1:]
        if relation in self.rules:
            self.rules[relation].append((arguments, body))
        else:
            self.rules[relation] = [(arguments, body)]

    def query(self, relation, *arguments):
        if relation not in self.facts and relation not in self.rules:
            raise RelationError(relation)
        self._check_arity(relation, arguments)
        arguments = self._internalize(arguments)
        import pdb; pdb.set_trace()
        pass  # FIXME

    def __repr__(self):
        
        return ''  # FIXME
