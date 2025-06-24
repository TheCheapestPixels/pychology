import pytest

from pychology.knowledge import KnowledgeBase
from pychology.knowledge import Variable as V
from pychology.knowledge import ArityError
from pychology.knowledge import RelationError


def test_create_knowledge_base():
    kb = KnowledgeBase()


def test_assert_fact_makes_symbol_representation():
    kb = KnowledgeBase()
    kb.fact('is', 'life', 'life')
    facts = kb.facts['is']
    first_fact = facts[0]
    [life_1, life_2] = first_fact
    assert life_1 is life_2


def test_arity_error_on_facts():
    kb = KnowledgeBase()
    kb.fact('unary', 'x')
    with pytest.raises(ArityError) as e:
        kb.fact('unary', 'x', 'y')
        assert e.relation == 'unary'
        assert e.arity == 1
        assert e.num_args != 1
    with pytest.raises(ArityError) as e:
        kb.rule(
            ('unary', 'x', 'y'),
            ('binary', 'x', 'y'),
        )
        assert e.relation == 'unary'
        assert e.arity == 1
        assert e.num_args != 1
    with pytest.raises(ArityError) as e:
        kb.rule(
            ('binary', 'x', 'y'),
            ('unary', 'x', 'y'),
        )
        assert e.relation == 'unary'
        assert e.arity == 1
        assert e.num_args != 1


def test_arity_error_on_rules():
    kb = KnowledgeBase()
    kb.rule(
        ('binary', 'x', 'y'),
        ('unary', 'x')
    )
    with pytest.raises(ArityError) as e:
        kb.rule(
            ('binary', 'x', 'y', 'z'),
            ('unary', 'y')
        )
        assert e.relation == 'binary'
        assert e.arity == 2
        assert e.num_args != 2
    with pytest.raises(ArityError) as e:
        kb.rule(
            ('binary', 'x', 'y'),
            ('unary', 'y', 'z')
        )
        assert e.relation == 'unary'
        assert e.arity == 1
        assert e.num_args != 1


def test_query_errors():
    kb = KnowledgeBase()
    with pytest.raises(RelationError) as e:
        next(kb.query('foo', V('x')))
        assert e.relation == 'foo'
    kb.fact('foo', 'something')
    with pytest.raises(ArityError) as e:
        next(kb.query('foo', V('x'), V('y')))
        assert e.relation == 'foo'
        assert e.arity == 1
        assert e.num_args != 1


def test_fact_queries():
    kb = KnowledgeBase()
    kb.fact('unary', 'foo')
    kb.fact('unary', 'bar')
    kb.fact('unary', 'baz')
    results = list(kb.query('unary', V('X')))
    assert len(results) == 3
    found_substitutions = []
    for result in results:
        assert isinstance(result, dict)
        assert len(result) == 1
        assert kb.variables['X'] in result
        found_substitutions.append(result[kb.variables['X']])
    assert kb.values['foo'] in found_substitutions
    assert kb.values['bar'] in found_substitutions
    assert kb.values['baz'] in found_substitutions


def test_complex():
    kb = KnowledgeBase()
    # Static binary sex is a bad model in application, but a sufficient
    # example, so here is a family tree:
    #
    #  Hern,m  Ava,f Bronk,m Oila,f  Niemand,m
    #   |       |      |      |
    #   +---+---+      +------+
    #       |          |      |
    #     Erena,f    Warr,m Krota,f
    #       |          |
    #       +-----+----+
    #             |
    #           Brut,m
    kb.fact('female', 'Ava')
    kb.fact('male', 'Hern')
    kb.fact('female', 'Erena')
    kb.fact('parent', 'Ava', 'Erena')
    kb.fact('parent', 'Hern', 'Erena')
    # A mother is a female parent.
    kb.rule(
        ('mother', V('X'), V('Y')),
        ('parent', V('X'), V('Y')),
        ('female', V('X')),
    )
    # A father is a male parent.
    kb.rule(
        ('father', V('father'), V('child')),
        ('parent', V('father'), V('child')),
        ('male', V('father')),
    )
    # An ancestor is either a direct parent...
    kb.rule(
        ('ancestor', V('ancestor'), V('descendant')),
        ('parent', V('ancestor'), V('descendant')),
    )
    # ...or a transitive one.
    kb.rule(
        ('ancestor', V('ancestor'), V('descendant')),
        ('ancestor', V('ancestor'), V('intermediate')),
        ('parent', V('intermediate'), V('descendant')),
    )

    # Who is Erena's mother?
    assert kb.query('mother', V('mother'), 'Erena') == [{'mother': 'Ava'}]

    # Who are Brut's ancestors?
    # Who are Bronk's descendants?
    # Who has Niemand as their ancestor?
    # Is Erena related to Krota?
    # Ancestry / Progeny
    # Common ancestry / progeny
    # Most recent common ancestor / earliest common progeny
