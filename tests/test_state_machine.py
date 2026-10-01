import pytest

from pychology.state_machine import ExitTrigger
from pychology.state_machine import State
from pychology.state_machine import MetaState
from pychology.state_machine import HFSM


# How about we log what is happening in a list? Here's a handy function
# to do that.
def log_action(log, message):
    def inner(env):
        log.append(message)
    return inner


# We will also need exit triggers. Here is one that checks whether a key
# on the blackboard (a dict) is of value True.
def switch(key):
    def inner(bb):
        return bb[key]
    return inner


# Set a blackboard key to False.
def reset_bb(key):
    def inner(bb):
        bb[key] = False
    return inner


# Got more than one function that you want to run? Use this.
def seq(*funcs):
    def inner(env):
        for f in funcs:
            f(env)
    return inner


# Okay, time for actual tests.
def test_basic_state_machine():
    # As the environment / AI / blackboard / whatever-you-wanna-call-
    # that-which-is-passed-first, we use a dict, and we'll have that
    # list that we log to.
    bb = dict(a=False, b=False)
    log = []

    # Now, the actual HFSM, without any MetaStates, so actually, this is
    # an FSM.
    # It has two states, 'a' and 'b'. they have exit triggers, namely
    # that when the BB value stored under the state name's key is True
    # (In state 'a', if bb['a'], then exit; Parallel for 'b'), then we
    # change to the other state. To prevent an infinite loop (if both
    # BB values are True), we set the value for the current state to
    # False. In short:
    #   State a: If bb.a, set it to False, and transition to b.
    #   State b: If bb.b, set it to False, and transition to a.
    hfsm = HFSM(
        State(
            'a',  # Name of the state
            'a',  # Plan of the state
            ExitTrigger(
                switch('a'),  # Condition; Transition if bb.a is True
                ['b']),  # Target; It's a list because it's a path
            on_entry=log_action(log, "entering a"),  # Log state entry
            on_exit=seq(  # When transitioning out of the state, ...
                reset_bb('a'),  # ...reset BB value, and...
                log_action(log, "exiting a"),  # ...log the exit.
            ),
        ),
        State(  # The same, with 'a' and 'b' swapped.
            'b', 'b',
            ExitTrigger(switch('b'), ['a']),
            on_entry=log_action(log, "entering b"),
            on_exit=seq(reset_bb('b'), log_action(log, "exiting b")),
        ),
        start=['a'],  # On startup, the HFSM will enter this state.
    )

    # So we *should* enter state 'a' on startup.
    assert log == []
    assert hfsm(bb) == 'a'
    assert not bb['a']
    assert not bb['b']
    assert log == ['entering a']
    log.clear()

    # Let's cause an exit.
    bb['a'] = True

    assert hfsm(bb) == 'b'
    assert not bb['a']
    assert not bb['b']
    assert log == ['exiting a', 'entering b']
    log.clear()

    # Switching back to a.
    bb['b'] = True

    assert hfsm(bb) == 'a'
    assert not bb['a']
    assert not bb['b']
    assert log == ['exiting b', 'entering a']
    log.clear()

    # Switching there and back again.
    bb['a'] = True
    bb['b'] = True

    assert hfsm(bb) == 'a'
    assert not bb['a']
    assert not bb['b']
    assert log == ['exiting a', 'entering b', 'exiting b', 'entering a']
    log.clear()


def test_state_machine_with_metastates():
    # This is basically the same test as above, except that we now
    # introduce MetaStates.
    bb = dict(a=False, b=False)
    log = []

    # Also, let's make our states and metastates named objects, because
    # that should be easier to read.
    # So, instead of letting the HFSM hold the two states directly, we
    # give it the metastates 'group_a' and 'group_b', which each hold
    # 'a' / 'b' respectively.
    state_a = State(
        'a', 'a',
        ExitTrigger(switch('a'), ['group_b', 'b']),  # Note the path.
        on_entry=log_action(log, "enter a"),
        on_exit=seq(
            reset_bb('a'),
            log_action(log, "exit a"),
        ),
    )
    # As a MetaState is not a proper state with a plan, but only a
    # container that we add for administrative purposes, it cannot be
    # run. Should the HFSM transition to it as its active state, the
    # metastate needs another state as its delegate, meaning that the
    # HFSM then transitions on to that one. Practical example: A guard
    # NPC switches to the 'combat' metastate, which passes on to
    # 'combat.use_your_head_first' as its default behavior.
    group_a = MetaState(
        'group_a',
        state_a,
        delegate=['group_a', 'a'],
        exit_triggers=[],
        on_entry=log_action(log, "enter group_a"),
        on_exit=log_action(log, "exit group_a"),
    )
    # Again, same for 'b', except that this time, we put the exit
    # trigger on the metastate, and let it point to the other metastate.
    state_b = State(
        'b', 'b',
        on_entry=log_action(log, "enter b"),
        on_exit=seq(
            reset_bb('b'),
            log_action(log, "exit b"),
        ),
    )
    group_b = MetaState(
        'group_b',
        state_b,
        delegate=['group_b', 'b'],
        exit_triggers=[
            ExitTrigger(switch('b'), ['group_a']),
        ],
        on_entry=log_action(log, "enter group_b"),
        on_exit=log_action(log, "exit group_b"),
    )

    # ...and now for the very, *very* readable HFSM...
    hfsm = HFSM(
        group_a,
        group_b,
        start=['group_a'],
    )

    # Startup... Calling the HFSM returns the active state's plan.
    assert hfsm(bb) == 'a'
    assert not bb['a']
    assert not bb['b']
    assert log == ['enter group_a', 'enter a']
    log.clear()

    # Switching to 'b'...
    bb['a'] = True

    assert hfsm(bb) == 'b'
    assert not bb['a']
    assert not bb['b']
    assert log == ['exit a', 'exit group_a', 'enter group_b', 'enter b']
    log.clear()

    # Back to 'a'...
    bb['b'] = True

    assert hfsm(bb) == 'a'
    assert not bb['a']
    assert not bb['b']
    assert log == ['exit b', 'exit group_b', 'enter group_a', 'enter a']
    log.clear()

    # ...and back and forth.
    bb['a'] = True
    bb['b'] = True

    assert hfsm(bb) == 'a'
    assert not bb['a']
    assert not bb['b']
    assert log == [
        'exit a',
        'exit group_a',
        'enter group_b',
        'enter b',
        'exit b',
        'exit group_b',
        'enter group_a',
        'enter a',
    ]
    log.clear()
