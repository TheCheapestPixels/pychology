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
+- Action(action_func): Run the action_func
"""


# Leaf states

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


# Behavior Trees

class BehaviorTree:
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


# Basic Node types

class Node:
    """
    Base class for the nodes of BehaviorTrees.
    """
    def __call__(self, entity, *args, **kwargs):
        raise NotImplementedError


### Decorators

class Decorator(Node):
    """
    Decorators are inner nodes of the behavior tree that let the 
    designer add preconditions and postconditions, change the NodeState
    returned, or execute other code; They are also handy for debugging.
    """
    def __call__(self, entity, *args, **kwargs):
        return self.tree(entity, *args, **kwargs)

    def reset(self):
        self.tree.reset()


class FailOnCondition:
    def reaction(self):
        return NodeState.FAILED
    

class ActiveOnCondition:
    def reaction(self):
        return NodeState.ACTIVE
    

class DoneOnCondition:
    def reaction(self):
        return NodeState.DONE


# Debug Decorators

class DebugPrint(Decorator):
    def __init__(self, text, tree):
        self.text = text
        self.tree = tree

    def __call__(self, entity, *args, **kwargs):
        print(self.text)
        return self.tree(entity, *args, **kwargs)


class DebugPrintOnEnter(Decorator):
    def __init__(self, text, tree):
        self.text = text
        self.tree = tree
        self.fresh = True

    def __call__(self, entity, *args, **kwargs):
        if self.fresh:
            print(self.text)
            self.fresh = False
        return self.tree(entity, *args, **kwargs)

    def reset(self):
        self.fresh = True
        super().reset()


class DebugPrintOnReset(Decorator):
    def __init__(self, text, tree):
        self.text = text
        self.tree = tree

    def reset(self):
        print(self.text)
        super().reset()


# Argument rewriting

class RewriteArguments(Decorator):
    def __init__(self, rewrite_func, tree):
        self.rewrite_func = rewrite_func
        self.tree = tree

    def __call__(self, entity, *args, **kwargs):
        new_args, new_kwargs = self.rewrite_func(*args, **kwargs)
        return self.tree(entity, *new_args, **new_kwargs)


# Return value rewriting

class ReturnValueAlways(Decorator):
    def __init__(self, tree):
        self.tree = tree

    def __call__(self, entity, *args, **kwargs):
        self.tree(entity, *args, **kwargs)
        return self.reaction()


class ReturnActiveAlways(ReturnValueAlways, ActiveOnCondition): pass
class ReturnDoneAlways(ReturnValueAlways, DoneOnCondition): pass
class ReturnFailedAlways(ReturnValueAlways, FailOnCondition): pass


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


class ReturnFailedOnActive(ReturnValueOnActive, FailOnCondition): pass
class ReturnDoneOnActive(ReturnValueOnActive, DoneOnCondition): pass
class ReturnActiveOnDone(ReturnValueOnDone, ActiveOnCondition): pass
class ReturnFailedOnDone(ReturnValueOnDone, FailOnCondition): pass
class ReturnActiveOnFailed(ReturnValueOnFailed, ActiveOnCondition): pass
class ReturnDoneOnFailed(ReturnValueOnFailed, DoneOnCondition): pass


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
    

class FailOnPrecondition(Precondition, FailOnCondition): pass
class ActiveOnPrecondition(Precondition, ActiveOnCondition): pass
class DoneOnPrecondition(Precondition, DoneOnCondition): pass
class FailOnPostcondition(Postcondition, FailOnCondition): pass
class ActiveOnPostcondition(Postcondition, ActiveOnCondition): pass
class DoneOnPostcondition(Postcondition, DoneOnCondition): pass


# Counter Decorators

class Counter(Decorator):
    def __init__(self, timeout, tree):
        self.counter = 0
        self.timeout = timeout
        self.tree = tree

    def reset(self):
        self.counter = 0
        self.tree.reset()


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


class FailOnPrecounter(Precounter, FailOnCondition): pass
class ActiveOnPrecounter(Precounter, ActiveOnCondition): pass
class DoneOnPrecounter(Precounter, DoneOnCondition): pass
class FailOnPostcounter(Postcounter, FailOnCondition): pass
class ActiveOnPostcounter(Postcounter, ActiveOnCondition): pass
class DoneOnPostcounter(Postcounter, DoneOnCondition): pass


# Multinodes

class Multinode(Node):
    """
    Multinodes are inner nodes of a behavior trees that have multiple
    children. For practical applications, see Chain and Priorities.
    """
    def __init__(self, *children):
        self.children = children
        self.active_child = None
        self.past_child = None

    def reset(self):
        for child in self.children:
            child.reset()


class Chain(Multinode):
    """
    A Chain (Sequence) node has two or more children that are called in
    order. If any child returns FAILED at any time, the chain also 
    fails.
    
    The Chain calls its first child repeatedly as long as it returns
    ACTIVE. When it returns DONE, the Chain moves on to the next node,
    and so on. When the last child is DONE, so is the Chain.
    """
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
    The Priorities (a.k.a. Selector) node has two or more children, and
    when called, runs them in order of priority until one has not 
    FAILED. If all fail, so does this node, otherwise it returns what
    the successful node returns (ACTIVE or DONE).
    """
    def __init__(self, *children):
        self.active_child = None
        self.children = children

    def __call__(self, entity, *args, **kwargs):
        for idx, child in enumerate(self.children):
            rv = child(entity, *args, **kwargs)
            if rv == NodeState.ACTIVE or rv == NodeState.DONE:
                if idx != self.active_child and self.active_child is not None:
                    previous_child = self.children[self.active_child]
                    previous_child.reset()
                    print("Reset previous choice")
                self.active_child = idx
                return rv
        if self.active_child is not None:
            previous_child = self.children[self.active_child]
            previous_child.reset()
        self.active_child = None
        return NodeState.FAILED


### Action

class Action(Node):
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
    def __init__(self, func):
        """
        func:
            The atomic behavior; A function that takes the acting entity
            as its first argument, and positional and keyword arguments
            that have been passed to the BehaviorTree.
        """
        self.func = func
        
    def __call__(self, entity, *args, **kwargs):
        return self.func(entity, *args, **kwargs)

    def reset(self):
        pass
