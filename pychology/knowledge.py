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
        return f"{self.symbol}"


class Relation:
    def __init__(self, symbol, arity):
        self.symbol = symbol
        self.arity = arity

    def assert_arity(self, supposed_arity):
        if supposed_arity != self.arity:
            raise ArityError(self.symbol, self.arity, supposed_arity)

    def __repr__(self):
        return f"{self.symbol}"


class SymbolView:
    def __init__(self, kb):
        self.kb = kb
        self.values = {}
        self.variables = {}
        self.relations = {}

    def get_from_symbol(self, symbol, cls, arity=None):
        """
        Retrieve the view's symbol representation of the given symbol.
        This will be from the given knowledge base if it is present 
        there, or the view's local version otherwise.
        """
        kb = self.kb
        # Which dictionaries are we using?
        if cls is Value:
            kb_dict, sv_dict = kb.values, self.values
        elif cls is Variable:
            kb_dict, sv_dict = kb.variables, self.variables
        elif cls is Relation:
            kb_dict, sv_dict = kb.relations, self.relations

        if isinstance(symbol, cls):  # Value/Variable/Relation object was given.
            symbol = symbol.symbol  # What is the literal symbol?
        # Otherwise, a literal symbol (e.g. string) has been provided.

        # And what is the corresponding value? The Value may have been
        # created externally, after all, so we need the one in the view.
        if symbol in kb_dict:
            symbol_obj = kb_dict[symbol]
        elif symbol in sv_dict:
            symbol_obj = sv_dict[symbol]
        else:  # Unknown symbol
            if cls is Relation:
                symbol_obj = cls(symbol, arity)
            else:
                symbol_obj = cls(symbol)
            sv_dict[symbol] = symbol_obj
        return symbol_obj

    def value(self, value):
        return self.get_from_symbol(value, Value)

    def variable(self, variable):
        return self.get_from_symbol(variable, Variable)

    def relation(self, relation, arity):
        return self.get_from_symbol(relation, Relation, arity=arity)

    def commit(self):
        kb = self.kb
        for symbol, value in self.values.items():
            kb.values[symbol] = value
        for symbol, variable in self.variables.items():
            kb.variables[symbol] = variable
        for symbol, relation in self.relations.items():
            kb.relations[symbol] = relation


class Atom:
    def __init__(self, sv, relation, arguments, no_variables=False):
        self.sv = sv
        relation = sv.relation(relation, arity=len(arguments))
        relation.assert_arity(len(arguments))
        self.relation = relation

        # Now symbolize the arguments.
        symbolized_args = []
        for argument in arguments:
            if isinstance(argument, Value):  # Symbolized already
                argument = sv.value(argument)
            elif isinstance(argument, Variable):
                argument = sv.variable(argument)
            else:  # It's not a symbol object already.
                if isinstance(argument, str) and argument[0] == '?':
                    # It's it a string representation of a variable!
                    argument = sv.variable(argument)
                else:  # Nah, a value instead.
                    argument = sv.value(argument)
            if no_variables and isinstance(argument, Variable):
                raise FactError  # Facts may not contain variables.
            symbolized_args.append(argument)
        self.arguments = symbolized_args

    def __repr__(self):
        rel = repr(self.relation)
        args = [repr(arg) for arg in self.arguments]
        return f"{rel}({', '.join(args)})"


class Fact(Atom):
    """
    Facts are relations over Values. They represent an "It is true 
    that..." assertion.
    """
    def __init__(self, sv, relation, arguments):
        Atom.__init__(self, sv, relation, arguments, no_variables=True)

    def __repr__(self):
        return f"{Atom.__repr__(self)}."


class Rule:
    """
    Rules are "This holds true if these things also all hold true."
    assertions. "This" and "these" are represented as relations over
    Values and Variables.
    """
    def __init__(self, sv, atoms):
        if len(atoms) < 2:  # Body atoms are required!
            raise RuleError()
        self.sv = sv

        symbolized_atoms = []
        for atom in atoms:
            if not isinstance(atom, Atom):
                atom = Atom(sv, atom[0], atom[1:])
            symbolized_atoms.append(atom)
        atoms = symbolized_atoms
        head = atoms[0]
        body = atoms[1:]
        self.head, self.body = head, body        

        # FIXME: Check whether every head variable occurs in the body.
        # FIXME: Check whether rule already exists as-is.

    def __repr__(self):
        head_str = f"{self.head}"
        pad_str = " " * len(head_str)
        lines = []
        for idx, body_atom in enumerate(self.body):
            if idx == 0:
                lines.append(f"{head_str} :- {body_atom}")
            else:
                lines.append(f"{pad_str}    {body_atom}")
        clause_str = ',\n'.join(lines)
        return f"{clause_str}."


class KnowledgeBase:
    def __init__(self):
        self.values = dict()  # symbol: Value(symbol)
        self.variables = dict()  # symbol: Variable(symbol)
        self.relations = dict()  # symbol: Relation(symbol)
        self.facts = dict()  # Relation: [Atom, ...]
        self.rules = dict()  # Relation: [Rule, ...]

    def _assert_fact(self, fact):
        if list(self._unify_atom_and_all_facts(fact)):  # Fact is already known
            return False
        relation = fact.relation
        if relation in self.facts:
            self.facts[relation].append(fact)
        else:
            self.facts[relation] = [fact]
        return True
        
    def fact(self, relation, *arguments, infer=True):
        sv = SymbolView(self)
        fact = Fact(sv, relation, arguments)
        if not self._assert_fact(fact):
            return False
        sv.commit()
        self._infer()
        return True

    def _unify_atom_and_fact(self, atom, fact, substitutions=None):
        assert atom.relation is fact.relation
        if substitutions is None:
            substitutions = {}

        for arg_atom, arg_fact in zip(atom.arguments, fact.arguments):
            atom_is_value = isinstance(arg_atom, Value)
            if atom_is_value:  # If the query provides a value...
                if arg_atom is not arg_fact:  # ...that does not match the fact, ...
                    return False  # ...we abort unification, ...
                pass  # ...otherwise, just move on.
            else:  # But if the query provides a variable instead, ...
                if arg_atom in substitutions:  # ...if we have a value for it, ...
                    if substitutions[arg_atom] is not arg_fact: # ...then if that value does not match the fact, ...
                        return False  # ...again, we abort; ...
                    pass  # If it matches, we again just move on.
                else:  # But if we do not have a value for it, ...
                    substitutions[arg_atom] = arg_fact  # ...then now we do have a value from the fact.
        # If we manage to go over all arguments without aborting, we now
        # have updated the substitutions with a valid unification.
        return True

    def _unify_atom_and_all_facts(self, atom, substitutions=None):
        if substitutions is None:
            substitutions = {}
        relation = atom.relation
        if relation not in self.facts:  # If there are no facts for this, ...
            return  # ...unification (obviously) fails.
        for fact in self.facts[relation]:  # We go through all facts for the relation.
            subquery_substitutions = substitutions.copy()  # Working on a copy of the substitutions, ...
            could_unify = self._unify_atom_and_fact(  # ...we unify the current atom and the fact.
                atom,
                fact,
                subquery_substitutions,
            )
            if not could_unify:  # If that fails, ...
                continue  # ...we abort this attempt and skip to the next fact.
            yield subquery_substitutions  # Otherwise, we yield the unification.

    def _unify_multiple_atoms_and_all_facts(self, atoms, substitutions=None):
        if substitutions is None:
            substitutions = {}
        current_atom = atoms[0]
        rest_atoms = atoms[1:]

        subquery_substitutions = substitutions.copy()  # Working on a copy of the substitutions, ...
        unifications = self._unify_atom_and_all_facts(  # ...we query the current_atom's possible unifications.
            current_atom,
            subquery_substitutions,
        )
        if not rest_atoms:  # If this is the last atom to process, ...
            for unification in unifications:
                yield unification  # ...we now have finished unifications.
        else:  # ...but if there are further atoms, ...
            for unification in unifications:
                final_unifications = self._unify_multiple_atoms_and_all_facts(  # ...we feed the unifications-so-far into the recursion.
                    rest_atoms,
                    substitutions=unification,
                )
                for final_unification in final_unifications:
                    yield final_unification

    def query(self, atom_or_relation, *arguments):
        if isinstance(atom_or_relation, Atom):
            query = atom_or_relation
            # FIXME: A better exception, please
            assert not arguments, "Why did you give arguments to an existing Atom?"
        else:
            sv = SymbolView(self)  # We don't want to pollute the KB.
            query = Atom(sv, atom_or_relation, arguments)
        relation = query.relation
        for unification in self._unify_atom_and_all_facts(query):
            yield unification

    def rule(self, *atoms):
        sv = SymbolView(self)
        rule = Rule(sv, atoms)
        relation = rule.head.relation
        if relation in self.rules:
            self.rules[relation].append(rule)
        else:
            self.rules[relation] = [rule]
        sv.commit()
        self._infer()

    def _infer(self):
        new_facts = True
        while new_facts:
            new_facts = False
            for relation_rules in self.rules.values():
                for rule in relation_rules:
                    inferred_facts = self._unify_multiple_atoms_and_all_facts(rule.body)
                    inferred_facts = list(inferred_facts)
                    for inferred_fact in inferred_facts:
                        relation = rule.head.relation
                        arguments = [
                            inferred_fact[arg]
                            for arg in rule.head.arguments
                        ]
                        sv = SymbolView(self)
                        fact = Fact(sv, relation, arguments)
                        if self._assert_fact(fact):
                            sv.commit()
                            new_facts = True

    # def _query_body(self, atoms, substitutions):
    #     """
    #     Given a list of atoms, and a dictionary of substitutions, find
    #     all matches for the first atom. If there are further atoms left,
    #     recurse; If not, yield the accumulated substitutions, as they
    #     (should) represent a match for the whole list of atoms.
    #     """
    #     current_atom = atoms[0]
    #     rest_atoms = atoms[1:]
    #     # Build the subquery
    #     sq_rel = current_atom.relation
    #     sq_args = []
    #     for arg in current_atom.arguments:
    #         if arg in substitutions:
    #             sq_args.append(substitutions[arg])
    #         else:
    #             sq_args.append(arg)
    #     sv = SymbolView(self)
    #     subquery = Atom(sv, sq_rel, sq_args)
    #     # Find matches and recurse (or not)
    #     matches = self.query(subquery)
    #     if rest_atoms:  # Recurse
    #         for match in matches:
    #             subsubstitutions = substitutions.copy()
    #             subsubstitutions.update(match)
    #             self._query_body(rest_atoms, subsubstitutions)
    #     else:  # No more atoms left
    #         for match in matches:
    #             yield match

    def __repr__(self):
        fact_strs = []
        for facts in self.facts.values():
            for fact in facts:
                fact_strs.append(f"{fact}")

        rule_strs = []
        for rules in self.rules.values():
            for rule in rules:
                rule_strs.append(f"{rule}")
                
        # If there have been facts, add an empty line for legibility.
        if fact_strs and rule_strs:
            fact_strs.append('')
        clause_strs = fact_strs + rule_strs
        return '\n'.join(clause_strs)
