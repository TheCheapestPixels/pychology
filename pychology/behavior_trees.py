import enum

"""
NodeState
BehaviorTree

Node
+- Decorator
|  +- DebugPrint(text, tree): Print text and run tree
|  +- DebugPrintOnEnter(text, tree): Print text only after a reset
|  +- DebugPrintOnReset(text, tree): Print text when resetting
|  +- RewriteArguments(rewrite_func, tree): pass args and kwargs through rewrite_func
|  +- ReturnValueAlways(tree)
|  |  +- ReturnActiveAlways: After running the tree, return ACTIVE
|  |  +- ReturnDoneAlways: After running the tree, return DONE
|  |  +- ReturnFailedAlways: After running the tree, return FAILED
|  +- ReturnValueOnValue(tree): Change what the tree returns
|  |  +- ReturnFailedOnActive: If tree returns ACTIVE, return FAILED
|  |  +- ReturnDoneOnActive: If tree returns ACTIVE, return DONE
|  |  +- ReturnActiveOnDone: If tree returns DONE, return ACTIVE
|  |  +- ReturnFailedOnDone: If tree returns DONE, return FAILED
|  |  +- ReturnActiveOnFailed: If tree returns FAILED, return ACTIVE
|  |  +- ReturnDoneOnFailed: If tree returns FAILED, return DONE
|  +- RewriteReturnValues(active, done, failed, tree): Specify what to rewrite any return value to.
|  +- Condition(condition_func, tree)
|  |  +- Precondition: Check condition_func before running the tree, and if true, return...
|  |  |  +- FailOnPrecondition: FAILED
|  |  |  +- ActiveOnPrecondition: ACTIVE
|  |  |  +- DoneOnPrecondition: DONE
|  |  +- Postcondition: After running the tree, check condition_func, and if true, return...
|  |     +- FailOnPostcondition: FAILED
|  |     +- ActiveOnPostcondition: ACTIVE
|  |     +- DoneOnPostcondition: DONE
|  +- Counter(timeout, tree): Count up each time the node is run.
|     +- Precounter: Count up before running the tree. If timeout is reached, return...
|     |  +- FailOnPrecounter: FAILED
|     |  +- ActiveOnPrecounter: ACTIVE
|     |  +- DoneOnPrecounter: DONE
|     +- Postcounter: Count up after running the tree. If timeout is reached, return...
|        +- FailOnPostcounter: FAILED
|        +- ActiveOnPostcounter: ACTIVE
|        +- DoneOnPostcounter: DONE
+- Multinode(*trees)
|  +- Chain: Run one tree after another until each is DONE. Return FAILED if any tree fails.
|  +- Priorities: Run trees in order until one does not return FAILED.
|  +- Parallel: Run all trees, fail if any has FAILED, succeed when all are DONE.
+- Leaf
   +- Action(action_func): Run the action_func
   +- ReturnActive: Returns ACTIVE.
   +- ReturnDone: Returns DONE.
   +- ReturnFailed: Returns FAILED.
"""


### Leaf states

class NodeState(enum.Enum):
    """
    When a leaf (or subtree) is being run, it will return one of three
    values: FAILED, ACTIVE, or DONE.
    * FAILED indicates that the leaf's action is not possible at the
      moment.
    * ACTIVE means that the action has been begun or is still running,
      but could not yet be completed.
    * DONE shows that the action has been finished.
    """
    FAILED = 1
    ACTIVE = 2
    DONE = 3


### De-/Serialization

state_to_name_map = {
    NodeState.FAILED: 'FAILED',
    NodeState.ACTIVE: 'ACTIVE',
    NodeState.DONE: 'DONE',
}
def state_to_name(state):
    return state_to_name_map[state]
name_to_state_map = {
    name: state
    for state, name in state_to_name_map.items()
}
def name_to_state(name):
    return name_to_state_map[name]


# These classes are mixed in with the node type hierarchy laid out
# above:
# BTSaveBase: Runs the serialization process. 
# +- BTSaveNone: Base class for leaf nodes, which have no children
# +- BTSaveSingle: Base class for decorators, which have exactly one child
# +- BTSaveMulti: Base class for multinodes, which have a list of children
#
# They take care of representing a node's children; This makes it
# necessary though to conform to the convention that a node's children
# are an arbitrary number of args passed to the node's `__init__` after
# all other arguments.
# The node itself (or one that the node inherits from) still has to
# implement how to de-/serialize the node's own data (both static and
# state), if it carries any; If they don't, then `BTSaveBase`'s suffice.
# Specifically, `_save_data` turns the node's state into a dictionary,
# while `_load_data`turns that dict back into the args and kwargs passed
# to the `__init__` of the node class.
#
# class Example(BTSaveMulti):
#     def __init__(self, first_arg, *children, node_state=None):
#         self.first_arg = first_arg
#         self.node_state = node_state
#         // ...
#
#     def _save_data(self, with_state=False):
#         node_data = dict(
#             name_in_data_structure=self.first_arg,
#         )
#         if with_state:
#             node_data.update(dict(state=self.node_state))
#         return node_data
# 
#     @classmethod
#     def _load_data(cls, loader, node_data, with_state=False):
#         args = [node_data['name_in_data_structure']]
#         kwargs = dict()
#         if with_state:
#             kwargs.update(node_state=node_data['state'])
#         return args, kwargs

class BTSaveBase:
    def _save(self, with_state=False):
        data = dict(
            cls=self.pych_cls,
        )
        data.update(self._save_data(with_state=with_state))
        data.update(self._save_children(with_state=with_state))
        return data

    def _save_data(self, with_state=False):
        """
        Turn a node's configuration (apart from its children) into a
        dictionary.

        Overwrite this method on node types that do store any data.
        """
        return dict()

    @classmethod
    def _load(cls, loader, node_data):
        args, kwargs = cls._load_data(loader, node_data)
        children = cls._load_children(loader, node_data)
        return cls(*args, *children, **kwargs)

    @classmethod
    def _load_data(cls, loader, node_data):
        """
        Extracts the positional and keyword arguments (except for 
        children) to use on instantiation.

        Overwrite this where you also overwrite _save_data, as that 
        produces the data that is extracted again here.
        """
        return [], {}


class BTSaveNone(BTSaveBase):
    def _save_children(self, with_state=False):
        return []

    @classmethod
    def _load_children(cls, loader, node_data):
        return []


class BTSaveSingle(BTSaveBase):
    def _save_children(self, with_state=False):
        return dict(
            child=self.tree._save(with_state=with_state)
        )

    @classmethod
    def _load_children(cls, loader, node_data):
        return [loader.load(node_data['child'])]


class BTSaveMulti(BTSaveBase):
    def _save_children(self, with_state=False):
        return dict(
            children=[
                c._save(with_state=with_state)
                for c in self.children
            ]
        )

    @classmethod
    def _load_children(cls, loader, node_data):
        return [loader.load(c) for c in node_data['children']]


# Since we can't save the functions that our AIs use, we do the next
# best thing: Save names referencing the functions. For this, we've got
# this little helper class that simply wraps any arbitrary function that
# we throw into it, and takes a name that we can reference.
# However, we can do one better: By having multiple types of saveable
# functions, we can indicate to other tools, e.g. an AI debugger, what
# the role of the function is, and therefore what protocols it will
# adhere to.
#
# SaveableFunction
# +- ActionFunction: Returns a `NodeState`
# +- ConditionFunction: Returns `True` or `False`

class SaveableFunction:
    pych_cls = 'TLSaveableFunction'

    """
    Wrapper for functions, so that they can be referenced during
    de-/serialization.

    saveable_func = ActionFunction(basic_behavior_func, name='foo')
    bt = Action(saveable_func)
    bt._save()
    """
    def __init__(self, func, name):
        self.func = func
        self.name = name

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def _save(self):
        return dict(
            cls=self.pych_cls,
            name=self.name,
        )


class ActionFunction(SaveableFunction):
    pych_cls = 'TLActionFunction'


class ConditionFunction(SaveableFunction):
    pych_cls = 'TLConditionFunction'


function_classes = [
    SaveableFunction,
    ActionFunction,
    ConditionFunction,
]


# Now we can throw all our `SaveableFunction`s into a loader, and let
# that recreate our tree from the data structure that `bt._save()`
# returned.
class BehaviorTreeLoader:
    def __init__(self, *action_funcs):
        self.funcs = {af.name: af for af in action_funcs}
        self.classes  = {
            cls.pych_cls: cls
            for cls in node_classes + function_classes
        }

    def load(self, tree_data):
        top_level_cls = tree_data['cls']
        cls = self.classes[top_level_cls]
        args, kwargs = cls._load_data(self, tree_data)
        children = cls._load_children(self, tree_data)
        bt = cls(*args, *children, **kwargs)
        return bt

    def get_func(self, func_data):
        cls = func_data['cls']
        name = func_data['name']
        return self.classes[cls](self.funcs[name], name=name)


### Behavior Trees

class BehaviorTree(BTSaveSingle):
    """
    To make an entity behave the way that is defined by a BehaviorTree,
    call the tree with the entity and any relevant normal and keyword
    arguments. Example:

        rv = walking_behavior(my_entity, target_coords)

    This returns:
    * FAILED if running the tree has failed (it is automatically reset),
    * ACTIVE if the tree is still running.
    
    If the tree has finished (DONE), it resets the tree, then calls its
    `done` method and returns what it returns. This is a base class, so
    you will have to override the done method to serve your needs. 
    """
    pych_cls = 'BTBehaviorTree'

    def __init__(self, tree):
        self.tree = tree
        self.tree.reset()

    def __call__(self, entity, *args, **kwargs):
        rv = self.tree(entity, *args, **kwargs)
        if rv == NodeState.DONE:
            self.tree.reset()
            return self.done(entity)
        elif rv == NodeState.FAILED:
            self.tree.reset()
            return self.failed(entity)
        else:
            return NodeState.ACTIVE

    def reset(self):
        self.tree.reset()

    def failed(self, entity):
        return NodeState.FAILED

    def done(self, entity):
        return NodeState.DONE


### Basic Node types

class Node:
    """
    Base class for the nodes of BehaviorTrees.
    """
    def __call__(self, entity, *args, **kwargs):
        raise NotImplementedError


### Decorators

class Decorator(Node, BTSaveSingle):
    """
    Decorators are inner nodes of the behavior tree that let the 
    designer add preconditions and postconditions, change the NodeState
    returned, or execute other code; They are also handy for debugging.
    """
    def __call__(self, entity, *args, **kwargs):
        return self.tree(entity, *args, **kwargs)

    def reset(self):
        self.tree.reset()


# Debug Decorators

class DebugPrintBase(Decorator):
    def _save_data(self, with_state=False):
        return dict(text=self.text)

    @classmethod
    def _load_data(cls, loader, node_data):
        return [node_data['text']], {}


class DebugPrint(DebugPrintBase):
    pych_cls = 'BTDebugPrint'

    def __init__(self, text, tree):
        self.text = text
        self.tree = tree

    def __call__(self, entity, *args, **kwargs):
        print(self.text)
        return self.tree(entity, *args, **kwargs)


class DebugPrintOnEnter(DebugPrintBase):
    pych_cls = 'BTDebugPrintOnEnter'

    def __init__(self, text, tree, fresh=True):
        self.text = text
        self.tree = tree
        self.fresh = fresh

    def __call__(self, entity, *args, **kwargs):
        if self.fresh:
            print(self.text)
            self.fresh = False
        return self.tree(entity, *args, **kwargs)

    def reset(self):
        self.fresh = True
        super().reset()


class DebugPrintOnReset(DebugPrintBase):
    pych_cls = 'BTDebugPrintOnReset'

    def __init__(self, text, tree):
        self.text = text
        self.tree = tree

    def reset(self):
        print(self.text)
        super().reset()


# Argument rewriting

class RewriteArguments(Decorator):
    pych_cls = 'BTRewriteArguments'

    def __init__(self, rewrite_func, tree):
        self.rewrite_func = rewrite_func
        self.tree = tree

    def __call__(self, entity, *args, **kwargs):
        new_args, new_kwargs = self.rewrite_func(*args, **kwargs)
        return self.tree(entity, *new_args, **new_kwargs)

    def _save_data(self, with_state=False):
        return dict(func=self.rewrite_func._save())

    @classmethod
    def _load_data(cls, loader, node_data, with_state=False):
        return [loader.get_func(node_data['func'])], dict()


# Return value rewriting

class ActiveOnCondition:
    def reaction(self):
        return NodeState.ACTIVE
    

class DoneOnCondition:
    def reaction(self):
        return NodeState.DONE


class FailOnCondition:
    def reaction(self):
        return NodeState.FAILED


class ReturnValueAlways(Decorator):
    def __init__(self, tree):
        self.tree = tree

    def __call__(self, entity, *args, **kwargs):
        self.tree(entity, *args, **kwargs)
        return self.reaction()


class ReturnActiveAlways(ReturnValueAlways, ActiveOnCondition):
    pych_cls = 'BTReturnActiveAlways'
class ReturnDoneAlways(ReturnValueAlways, DoneOnCondition):
    pych_cls = 'BTReturnDoneAlways'
class ReturnFailedAlways(ReturnValueAlways, FailOnCondition):
    pych_cls = 'BTReturnFailedAlways'


class ReturnValueOnValue(Decorator):
    def __init__(self, tree):
        self.tree = tree

    def __call__(self, entity, *args, **kwargs):
        rv = self.tree(entity, *args, **kwargs)
        if rv == NodeState.DONE:
            return self.done()
        elif rv == NodeState.ACTIVE:
            return self.active()
        else:  # rv == NodeState.FAILED:
            return self.failed()

    def active(self):
        return NodeState.ACTIVE

    def done(self):
        return NodeState.DONE

    def failed(self):
        return NodeState.FAILED

    
class ReturnValueOnActive(ReturnValueOnValue):
    def active(self):
        return self.reaction()


class ReturnValueOnDone(ReturnValueOnValue):
    def done(self):
        return self.reaction()


class ReturnValueOnFailed(ReturnValueOnValue):
    def failed(self):
        return self.reaction()


class ReturnFailedOnActive(ReturnValueOnActive, FailOnCondition):
    pych_cls = 'BTReturnFailedOnActive'
class ReturnDoneOnActive(ReturnValueOnActive, DoneOnCondition):
    pych_cls = 'BTReturnDoneOnActive'
class ReturnActiveOnDone(ReturnValueOnDone, ActiveOnCondition):
    pych_cls = 'BTReturnActiveOnDone'
class ReturnFailedOnDone(ReturnValueOnDone, FailOnCondition):
    pych_cls = 'BTReturnFailedOnDone'
class ReturnActiveOnFailed(ReturnValueOnFailed, ActiveOnCondition):
    pych_cls = 'BTReturnActiveOnFailed'
class ReturnDoneOnFailed(ReturnValueOnFailed, DoneOnCondition):
    pych_cls = 'BTReturnDoneOnFailed'


class RewriteReturnValues(Decorator):
    pych_cls = 'BTRewriteReturnValues'

    def __init__(self, active, done, failed, tree):
        self.on_active = active
        self.on_done = done
        self.on_failed = failed
        self.tree = tree

    def __call__(self, entity, *args, **kwargs):
        rv = self.tree(entity, *args, **kwargs)
        if rv == NodeState.DONE:
            return self.on_done
        elif rv == NodeState.ACTIVE:
            return self.on_active
        else:  # rv == NodeState.FAILED:
            return self.on_failed

    def _save_data(self, with_state=False):
        return dict(
            on_active=state_to_name(self.on_active),
            on_done=state_to_name(self.on_done),
            on_failed=state_to_name(self.on_failed),
        )
    @classmethod
    def _load_data(cls, loader, node_data, woth_state=False):
        return [
            name_to_state(node_data['on_active']),
            name_to_state(node_data['on_done']),
            name_to_state(node_data['on_failed']),            
        ], {}


# Condition Decorators

class Condition(Decorator):
    """
    Conditions are decorators that, if a given condition is met, returns
    a certain NodeState. This check is performed either before the child
    node is called (precondition) or afterwards (postcondition). If the
    check succeeds, the decorator will return depending on its type
    (FAILED, ACTIVE, or DONE), otherwise it will return what the child 
    node returned.

    The classes to use are thus:
        FailOnPrecondition
        ActiveOnPrecondition
        DoneOnPrecondition
        FailOnPostcondition
        ActiveOnPostcondition
        DoneOnPostcondition

    and are used like this:
        FailOnPrecondition(condition_func, child_tree)

    condition_func will be called with the same arguments as this
    decorator.
    """
    def __init__(self, condition, tree):
        self.condition = condition
        self.tree = tree

    def _save_data(self, with_state=False):
        return dict(cond=self.condition._save())

    @classmethod
    def _load_data(cls, loader, node_data, woth_state=False):
        func = loader.get_func(node_data['cond'])        
        return [func], {}


class Precondition(Condition):
    def __call__(self, entity, *args, **kwargs):
        if self.condition(entity, *args, **kwargs):
            return self.reaction()
        return self.tree(entity, *args, **kwargs)


class Postcondition(Condition):
    def __call__(self, entity, *args, **kwargs):
        rv = self.tree(entity, *args, **kwargs)
        if self.condition(entity, *args, **kwargs):
            return self.reaction()
        return rv
    

class FailOnPrecondition(Precondition, FailOnCondition):
    pych_cls = 'BTFailOnPrecondition'
class ActiveOnPrecondition(Precondition, ActiveOnCondition):
    pych_cls = 'BTActiveOnPrecondition'
class DoneOnPrecondition(Precondition, DoneOnCondition):
    pych_cls = 'BTDoneOnPrecondition'
class FailOnPostcondition(Postcondition, FailOnCondition):
    pych_cls = 'BTFailOnPostcondition'
class ActiveOnPostcondition(Postcondition, ActiveOnCondition):
    pych_cls = 'BTActiveOnPostcondition'
class DoneOnPostcondition(Postcondition, DoneOnCondition):
    pych_cls = 'BTDoneOnPostcondition'


# Counter Decorators

class Counter(Decorator):
    def __init__(self, timeout, tree, counter=0):
        self.counter = counter
        self.timeout = timeout
        self.tree = tree

    def reset(self):
        self.counter = 0
        self.tree.reset()

    def _save_data(self, with_state=False):
        data = dict(timeout=self.timeout)
        if with_state:
            data.update(dict(counter=self.counter))
        return data

    @classmethod
    def _load_data(cls, loader, node_data, with_state=False):
        timeout = node_data['timeout']
        kwargs = {}
        if with_state:
            kwargs['counter'] = node_data['counter']
        return [timeout], kwargs


class Precounter(Counter):
    def __call__(self, entity, *args, **kwargs):
        self.counter += 1
        if self.counter == self.timeout:
            return self.reaction()
        return self.tree(entity, *args, **kwargs)


class Postcounter(Counter):
    def __call__(self, entity, *args, **kwargs):
        rv = self.tree(entity, *args, **kwargs)
        self.counter += 1
        if self.counter == self.timeout:
            return self.reaction()
        return rv


class FailOnPrecounter(Precounter, FailOnCondition):
    pych_cls = 'BTFailOnPrecounter'
class ActiveOnPrecounter(Precounter, ActiveOnCondition):
    pych_cls = 'BTActiveOnPrecounter'
class DoneOnPrecounter(Precounter, DoneOnCondition):
    pych_cls = 'BTDoneOnPrecounter'
class FailOnPostcounter(Postcounter, FailOnCondition):
    pych_cls = 'BTFailOnPostcounter'
class ActiveOnPostcounter(Postcounter, ActiveOnCondition):
    pych_cls = 'BTActiveOnPostcounter'
class DoneOnPostcounter(Postcounter, DoneOnCondition):
    pych_cls = 'BTDoneOnPostcounter'


# Multinodes

class Multinode(Node, BTSaveMulti):
    """
    Multinodes are inner nodes of a behavior trees that have multiple
    children. For practical applications, see Chain and Priorities.
    """
    def __init__(self, *children, active_child=None):
        self.active_child = active_child
        self.children = children

    def reset(self):
        for child in self.children:
            child.reset()

    def _save_data(self, with_state=False):
        data = dict()
        if with_state:
            data.update(dict(active=self.active_child))
        return data

    @classmethod
    def _load_data(cls, loader, node_data, with_state=False):
        kwargs = dict()
        if with_state:
            kwargs.update(dict(active_child=node_data['active']))
        return [], kwargs


class Chain(Multinode):
    """
    A Chain (Sequence) node has two or more children that are called in
    order. If any child returns FAILED at any time, the chain also 
    fails.
    
    The Chain calls its first child repeatedly as long as it returns
    ACTIVE. When it returns DONE, the Chain moves on to the next node,
    and so on. When the last child is DONE, so is the Chain.
    """
    pych_cls = 'BTChain'

    def __call__(self, entity, *args, **kwargs):
        if self.active_child is None:
            self.active_child = 0
        for child in self.children[self.active_child:]:
            rv = child(entity, *args, **kwargs)
            if rv == NodeState.FAILED:
                child.reset()
                return rv
            elif rv == NodeState.ACTIVE:
                return rv
            else:  # rv == NodeState.DONE:
                child.reset()
                self.active_child += 1

        # We processed the whole list? Then we really are done.
        self.active_child = None
        return NodeState.DONE

    def reset(self):
        self.active_child = None
        super().reset()


class Priorities(Multinode):
    """
    The Priorities (a.k.a. Selector, or Fallback) node has two or more
    children, and when called, runs them in order of priority until one
    has not FAILED. If all fail, so does this node, otherwise it returns
    what the successful node returns (ACTIVE or DONE).
    """
    pych_cls = 'BTPriorities'

    def __call__(self, entity, *args, **kwargs):
        for idx, child in enumerate(self.children):
            rv = child(entity, *args, **kwargs)
            if rv == NodeState.ACTIVE or rv == NodeState.DONE:
                if idx != self.active_child and self.active_child is not None:
                    previous_child = self.children[self.active_child]
                    previous_child.reset()
                self.active_child = idx
                return rv
        if self.active_child is not None:
            previous_child = self.children[self.active_child]
            previous_child.reset()
        self.active_child = None
        return NodeState.FAILED


class Parallel(Multinode):
    """
    The Parallel node has two or more children, and when called, runs
    all of them on each tick. If any of them fail, this node returns
    FAILED, and when all children are finished, it returns DONE.
    """
    pych_cls = 'BTParallel'

    # Parallel is an atypical Multinode as it does not have an active
    # child node; All its children are active all the time. That's why
    # we overwrite __init__, _save_data and _load_data again.
    def __init__(self, *children):
        self.children = children

    def __call__(self, entity, *args, **kwargs):
        rvs = [c(entity, *args, **kwargs) for c in self.children]
        if any([rv == NodeState.FAILED for rv in rvs]):
            for child in self.children:
                child.reset()
            return NodeState.FAILED
        if all([rv == NodeState.DONE for rv in rvs]):
            for child in self.children:
                child.reset()
            return NodeState.DONE
        return NodeState.ACTIVE

    def reset(self):
        for child in self.children:
            child.reset()

    def _save_data(self, with_state=False):
        return dict()

    @classmethod
    def _load_data(cls, loader, node_data, with_state=False):
        return [], {}


### Leaves of the tree

class Leaf(Node, BTSaveNone):
    def reset(self):
        pass


class Action(Leaf):
    pych_cls = 'BTAction'
    """
    Action nodes (usually called Tasks) wrap atomic behavior. They are
    the leaves of the behavior tree and have no children.
    Atomic behaviors consists of functions that are called with the
    entity as first argument, followed by the arguments that the tree
    has received (subject to mangling by decorators), and return a 
    NodeState.

    These functions then are simply passed to the node:

        Action(walk_straight)
    """
    def __init__(self, func, pass_entity=True):
        """
        func:
            The atomic behavior; A function that takes the acting entity
            as its first argument, and positional and keyword arguments
            that have been passed to the BehaviorTree.
        """
        self.func = func
        self.pass_entity = pass_entity
        
    def __call__(self, entity, *args, **kwargs):
        if self.pass_entity:
            rv = self.func(entity, *args, **kwargs)
        else:
            rv = self.func(*args, **kwargs)
        if rv not in [NodeState.ACTIVE, NodeState.DONE, NodeState.FAILED]:
            raise Exception(f"Action function must return a NodeState, but returned:\n{rv}\n")
        return rv

    def _save_data(self, with_state=False):
        return dict(
            func=self.func._save(),
            pass_entity=self.pass_entity,
        )

    @classmethod
    def _load_data(cls, loader, node_data):
        func = loader.get_func(node_data['func'])
        pass_entity = node_data['pass_entity']
        return [func], dict(pass_entity=pass_entity)


class ReturnValue(Leaf):
    def __call__(self, entity, *args, **kwargs):
        return self.return_value


class ReturnActive(ReturnValue):
    pych_cls = 'BTReturnActive'
    return_value = NodeState.ACTIVE


class ReturnDone(ReturnValue):
    pych_cls = 'BTReturnDone'
    return_value = NodeState.DONE


class ReturnFailed(ReturnValue):
    pych_cls = 'BTReturnFailed'
    return_value = NodeState.FAILED


node_classes = [
    BehaviorTree,
    DebugPrint, DebugPrintOnEnter, DebugPrintOnReset,
    ReturnActiveAlways, ReturnDoneAlways, ReturnFailedAlways,
    ReturnFailedOnActive, ReturnDoneOnActive, ReturnActiveOnDone, 
    ReturnFailedOnDone, ReturnActiveOnFailed, ReturnDoneOnFailed,
    RewriteReturnValues,
    FailOnPrecondition, ActiveOnPrecondition, DoneOnPrecondition,
    FailOnPostcondition, ActiveOnPostcondition, DoneOnPostcondition,
    FailOnPrecounter, ActiveOnPrecounter, DoneOnPrecounter,
    FailOnPostcounter, ActiveOnPostcounter, DoneOnPostcounter,
    Action, ReturnActive, ReturnDone, ReturnFailed,
    RewriteArguments,
    Chain, Priorities, Parallel,
]
