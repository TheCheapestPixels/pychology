from pychology.knowledge import KnowledgeBase


def make_query(*args):
    relation, arguments = args[0], args[1:]
    print(f"Query: {relation}({', '.join(arguments)})")
    result = list(kb.query(*args))
    if not result:
        print("* No result found.")
    for match in result:
        if not match:  # No variables were queried for.
            print("* Match found.")
        else:
            for idx, (variable, value) in enumerate(match.items()):
                if idx == 0:
                    print(f"* {variable}: {value}")
                else:
                    print(f"  {variable}: {value}")


kb = KnowledgeBase()
kb.fact('parent', 'Alice', 'Bob')
kb.fact('parent', 'Bob', 'Claudia')
kb.fact('parent', 'Claudia', 'Damien')
kb.fact('parent', 'Damien', 'Eve')
kb.fact('parent', 'Niemand', 'Niemand')
print(kb)
print()
make_query('parent', 'Alice', '?child')
print()
make_query('parent', '?parent', 'Eve')
print()
make_query('parent', 'Alice', 'Bob')
print()
make_query('parent', 'Alice', 'Eve')
print()
make_query('parent', '?selfcreator', '?selfcreator')
print()


print("--- Querying non-recursive rules ---")
kb.rule(
    ('ancestor', '?X', '?Y'),
    ('parent', '?X', '?Y'),
)
print(kb)
print()
make_query('ancestor', '?ancestor', 'Eve')
print()


print("--- Querying recursive rules ---")
kb.rule(
    ('ancestor', '?X', '?Y'),
    ('parent', '?Z', '?Y'),
    ('ancestor', '?X', '?Z'),
)
print(kb)
print()
make_query('ancestor', '?ancestor', 'Eve')
