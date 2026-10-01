# Our state machine will use an Exception to signal to its tick call
# that the state needs to be changed, and to which state.
class ExitTriggered(Exception):
    def __init__(self, target):
        self.target = target


# These changes are caused by the conditions on the path from HFSM root
# to its currently active state.
class ExitTrigger:
    def __init__(self, condition, target):
        self.condition = condition
        self.target = target

    def __call__(self, env):
        if self.condition(env):
            raise ExitTriggered(self.target)


# Ye olde nested dictionary with paths.
class StateDict(dict):
    def __getitem__(self, key):
        # If we have an actual key, let's return its value.
        if not isinstance(key, (list, tuple)):
            return super().__getitem__(key)

        # But we have a path instead... do we?
        if not key:
            return self

        # Yes, we do. So let's look up the local element, and get the
        # rest of the path lookup from it instead.
        value = super().__getitem__(key[0])
        if len(key) == 1:
            return value
        return value[key[1:]]


# States and MetaStates have in common that they have exit triggers that
# need to be checked each tick, and that entering or exiting them may
# cause side effects.
class StateBase:
    def enter(self, env):
        if self.on_entry is not None:
            self.on_entry(env)

    def exit(self, env):
        if self.on_exit is not None:
            self.on_exit(env)

    def check_exit_triggers(self, env):
        for trigger in self.exit_triggers:
            trigger(env)


# ...and an actual State is that plus returning its plan.
class State(StateBase):
    def __init__(self, name, plan, *exit_triggers,
                 on_entry=None, on_exit=None):
        self.name = name
        self.plan = plan
        self.exit_triggers = exit_triggers
        self.on_entry = on_entry
        self.on_exit = on_exit

    def __call__(self, env):
        return self.plan

    def __getitem__(self, rest_path):
        assert not rest_path, f"State {self.name} has no children. Rest path: {rest_path}"
        return self


# A MetaState instead delegates execution to another state.
class MetaState(StateBase):
    def __init__(self, name, *states,
                 exit_triggers=None, delegate=None,
                 on_entry=None, on_exit=None):
        self.name = name
        self.states = StateDict(**{s.name: s for s in states})
        if exit_triggers is None:
            exit_triggers = []
        self.exit_triggers = exit_triggers
        self.delegate = delegate
        self.on_entry = on_entry
        self.on_exit = on_exit

    def __call__(self, env):
        if self.delegate is not None:
            raise ExitTriggered(self.delegate)
        # FIXME: Better Expection needed.
        raise Exception("Transitioned to MetaState with no delegate")

    def __getitem__(self, rest_path):
        if rest_path:
            return self.states[rest_path]
        return self


class HFSM:
    def __init__(self, *states, start=None, inited=False):
        self.states = StateDict(**{s.name: s for s in states})
        self.state_path = start
        self.inited = inited

    def __call__(self, env):
        # Have we entered the initial state yet?
        if not self.inited:
            for i in range(len(self.state_path)):
                subpath = self.state_path[:i+1]
                self.states[subpath].enter(env)
            self.inited = True

        # Run the current state, and if it makes us transition, do that
        # and repeat. Finish only once we got a plan instead of an exit.
        while True:
            try:
                # We go from root down to the state, and run all exit
                # triggers on the way.
                for i in range(len(self.state_path)):
                    subpath = self.state_path[:i+1]
                    current_state = self.states[subpath]
                    current_state.check_exit_triggers(env)
                # Run the state, get the plan, done.
                plan = current_state(env)
                return plan
            except ExitTriggered as et:
                current_path = self.state_path.copy()
                target_path = et.target.copy()

                # Figure out the path from top to lowest common ancestor
                # of current and target path.
                common_root = []
                while current_path and target_path and current_path[0] == target_path[0]:
                    common_root.append(current_path.pop(0))
                    target_path.pop(0)

                # Get that state; We'll query it for its children.
                root_state = self.states[common_root]

                # First, we go up from the current state to the common
                # root, exiting all (non-common) states. Then we go down
                # the path to the target state, entering each.
                for i in range(len(current_path), 0, -1):
                    subpath = current_path[:i]
                    root_state[subpath].exit(env)
                for i in range(len(target_path)):
                    subpath = target_path[:i+1]
                    root_state[subpath].enter(env)

                # Finally, we set the current path, and are done. The
                # new state can be (tried to be) called now.
                self.state_path = common_root + target_path
