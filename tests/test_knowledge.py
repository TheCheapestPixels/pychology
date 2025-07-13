import pytest

from pychology.knowledge import KnowledgeBase
from pychology.knowledge import ArityError
from pychology.knowledge import RelationError


def test_kb_instantiation():
    kb = KnowledgeBase()


def test_fact_storage():
    kb = KnowledgeBase()
    # Let's assert a fact with external representations.
    kb.fact('rel', 'arg1', 'arg2')
    # Has the mapping from external to internal representation of the
    # relation be stored?
    assert 'rel' in kb.relations
    assert 'arg1' in kb.values
    assert 'arg2' in kb.values
    assert not kb.variables

    # Has the fact been stored?
    rel = kb.relations['rel']
    assert rel in kb.facts
    assert len(kb.facts[rel]) == 1
    fact = kb.facts[rel][0]
    # Have the arguments similarly been internalized and stored?
    assert len(fact.arguments) == 2
    for idx, external_value_symbol in enumerate(['arg1', 'arg2']):
        value = kb.values[external_value_symbol]
        assert fact.arguments[idx] is value


def test_kb_rejects_duplicate_facts():
    kb = KnowledgeBase()
    assert kb.fact('rel', 'arg1', 'arg2') is not False
    assert not kb.fact('rel', 'arg1', 'arg2')
    assert len(kb.facts[kb.relations['rel']]) == 1


def test_query_fact():
    kb = KnowledgeBase()
    kb.fact('rel', 'arg1', 'arg2')
    matches = list(kb.query('rel', '?X', '?Y', ext_symbols=False))

    # Did we pollute the KB's namespace?
    assert '?X' not in kb.variables
    assert '?Y' not in kb.variables
    # Is the result correct?
    assert len(matches) == 1
    match = matches[0]
    assert len(match) == 2
    returned_variables = set(variable.symbol for variable in match.keys())
    assert returned_variables == set(['?X', '?Y'])
    for variable, value in match.items():
        if variable.symbol == '?X':
            assert value.symbol == 'arg1'
        else:
            assert value.symbol == 'arg2'


def test_query_fact_wit_external_symbols():
    kb = KnowledgeBase()
    kb.fact('rel', 'arg1', 'arg2')
    matches = list(kb.query('rel', '?X', '?Y'))
    assert matches == [{'?X': 'arg1', '?Y': 'arg2'}]


def test_query_facts_of_nonexistent_relation():
    kb = KnowledgeBase()
    matches = list(kb.query('rel', '?X', '?Y', ext_symbols=False))
    assert len(matches) == 0


def test_query_multiple_facts():
    kb = KnowledgeBase()
    kb.fact('rel', 'arg1', 'arg2')
    kb.fact('rel', 'arg1', 'arg3')
    kb.fact('rel', 'arg2', 'irrelevant')
    matches = list(kb.query('rel', 'arg1', '?Y', ext_symbols=False))
    matches = list(
        {
            var.symbol: val.symbol
            for var, val in match.items()
        }
        for match in matches
    )
    assert {'?Y': 'arg2'} in matches
    assert {'?Y': 'arg3'} in matches


def test_store_rule():
    kb = KnowledgeBase()
    kb.rule(
        ('child', '?child', '?parent'),
        ('parent', '?parent', '?child'),
    )
    # FIXME: Tests?


def test_inference():
    kb = KnowledgeBase()
    kb.rule(
        ('child', '?child', '?parent'),
        ('parent', '?parent', '?child'),
    )
    kb.fact('parent', 'Alice', 'Bob')
    m = kb.query('child', 'Bob', 'Alice', ext_symbols=False)
    m = list(m)
    assert len(m) == 1
    assert len(m[0]) == 0


def test_save():
    kb = KnowledgeBase()
    kb.rule(
        ('child', '?child', '?parent'),
        ('parent', '?parent', '?child'),
    )
    kb.fact('parent', 'Alice', 'Bob')
    knowledge = kb.save()
    expected_knowledge = {
        'facts': [  # FIXME: Order of facts may vary.
            ('parent', 'Alice', 'Bob'),
            ('child', 'Bob', 'Alice'),
        ],
        'rules': [
            [  # FIXME: Order of rules may vary, too, even that of body clauses.
                ('child', '?child', '?parent'),
                ('parent', '?parent', '?child'),
            ],
        ],
    }
    assert knowledge == expected_knowledge


def test_load_without_inference():
    given_knowledge = {
        'facts': [
            ('parent', 'Alice', 'Bob'),
        ],
        'rules': [
            [
                ('child', '?child', '?parent'),
                ('parent', '?parent', '?child'),
            ],
        ],
    }
    kb = KnowledgeBase()
    kb.load(given_knowledge, infer=False)
    # Are the facts correct? There should be one relation, and it should
    # have one element.
    assert len(kb.facts) == 1
    assert len(kb.facts[kb.relations['parent']]) == 1
    # Is that the fact that we gave it?
    fact = kb.facts[kb.relations['parent']][0]
    assert fact.relation.symbol == 'parent'
    assert fact.arguments[0].symbol == 'Alice'
    assert fact.arguments[1].symbol == 'Bob'
    # And the rules?
    assert len(kb.rules) == 1
    rule = kb.rules[kb.relations['child']][0]
    # Let's doublecheck the head.
    head = rule.head
    assert head.relation.symbol == 'child'
    assert head.arguments[0].symbol == '?child'
    assert head.arguments[1].symbol == '?parent'
    # Now for the body.
    assert len(rule.body) == 1
    body = rule.body[0]
    assert body.relation.symbol == 'parent'
    assert body.arguments[0].symbol == '?parent'
    assert body.arguments[1].symbol == '?child'


def test_load_with_inference():
    given_knowledge = {
        'facts': [
            ('parent', 'Alice', 'Bob'),
        ],
        'rules': [
            [
                ('child', '?child', '?parent'),
                ('parent', '?parent', '?child'),
            ],
        ],
    }
    kb = KnowledgeBase()
    kb.load(given_knowledge, infer=True)
    # Are the facts correct?
    # There should be one each of parent and child relation.
    assert len(kb.facts) == 2
    assert len(kb.facts[kb.relations['parent']]) == 1
    assert len(kb.facts[kb.relations['child']]) == 1
    # Is the parent fact correct?
    fact = kb.facts[kb.relations['parent']][0]
    assert fact.relation.symbol == 'parent'
    assert fact.arguments[0].symbol == 'Alice'
    assert fact.arguments[1].symbol == 'Bob'
    # Is the child fact correct?
    fact = kb.facts[kb.relations['child']][0]
    assert fact.relation.symbol == 'child'
    assert fact.arguments[0].symbol == 'Bob'
    assert fact.arguments[1].symbol == 'Alice'
    # The rule check is the same as for loading without inference.
    assert len(kb.rules) == 1
    rule = kb.rules[kb.relations['child']][0]
    # Head
    head = rule.head
    assert head.relation.symbol == 'child'
    assert head.arguments[0].symbol == '?child'
    assert head.arguments[1].symbol == '?parent'
    # Body
    assert len(rule.body) == 1
    body = rule.body[0]
    assert body.relation.symbol == 'parent'
    assert body.arguments[0].symbol == '?parent'
    assert body.arguments[1].symbol == '?child'
