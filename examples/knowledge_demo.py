from pychology.knowledge import KnowledgeBase


def state_fact(*args):
    kb.fact(*args)
    print(f"Asserting: {args[0]}({', '.join(args[1:])})")

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
    print()


kb = KnowledgeBase()
kb.rule(
    ('ancestor', '?X', '?Y'),
    ('parent', '?X', '?Y'),
)
kb.rule(
    ('ancestor', '?X', '?Y'),
    ('parent', '?Z', '?Y'),
    ('ancestor', '?X', '?Z'),
)
print("KnowledgeBase state:")
print(kb)
print()
state_fact('parent', 'Alice', 'Bob')
state_fact('parent', 'Bob', 'Claudia')
state_fact('parent', 'Claudia', 'Damien')
state_fact('parent', 'Damien', 'Eve')
state_fact('parent', 'Niemand', 'Niemand')
print()
print("KnowledgeBase state:")
print(kb)
print()
make_query('parent', 'Alice', '?child')
make_query('parent', '?parent', 'Eve')
make_query('parent', 'Alice', 'Bob')
make_query('parent', 'Alice', 'Eve')
make_query('parent', '?selfcreator', '?selfcreator')
make_query('ancestor', '?ancestor', 'Eve')
