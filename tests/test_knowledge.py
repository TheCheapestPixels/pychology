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
    assert kb.fact('rel', 'arg1', 'arg2')
    assert not kb.fact('rel', 'arg1', 'arg2')
    assert len(kb.facts[kb.relations['rel']]) == 1


def test_query_fact():
    kb = KnowledgeBase()
    kb.fact('rel', 'arg1', 'arg2')
    matches = list(kb.query('rel', '?X', '?Y'))

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


def test_query_facts_of_nonexistent_relation():
    kb = KnowledgeBase()
    matches = list(kb.query('rel', '?X', '?Y'))
    assert len(matches) == 0


def test_query_multiple_facts():
    kb = KnowledgeBase()
    kb.fact('rel', 'arg1', 'arg2')
    kb.fact('rel', 'arg1', 'arg3')
    kb.fact('rel', 'arg2', 'irrelevant')
    matches = list(kb.query('rel', 'arg1', '?Y'))
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
    m = kb.query('child', 'Bob', 'Alice')
    m = list(m)
    assert len(m) == 1
    assert len(m[0]) == 0
