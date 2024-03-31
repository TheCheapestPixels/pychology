from pychology.utility import evaluate_utilities
from pychology.utility import invert
from pychology.utility import normal_clip


class Body:
    def __init__(self, hydration=1.0, bladder=1.0, energy=1.0):
        self.action = None

        self.hydration = hydration
        self.bladder = bladder
        self.energy = energy

    def tick(self, dt):
        did_action = False
        # Perform the intended action if possible.
        if self.action == 'pee':
            if self.energy > 0.3:
                self.bladder = 1.0
                self.energy = normal_clip(self.energy - 0.3)
                self.action = None
                did_action = True
        elif self.action == 'drink':
            if self.energy > 0.3:
                self.hydration = normal_clip(self.hydration + 0.3)
                self.energy = normal_clip(self.energy - 0.3)
                self.action = None
                did_action = True
        # If nothing has been done, we regenerate.
        if not did_action:
            self.energy = normal_clip(self.energy + 0.075 * dt)
        
        kidney_intake_rate = 0.05
        kidney_output_factor = 3.0
        intended_quantity = kidney_intake_rate * dt
        transferred_quantity = min(self.hydration, intended_quantity)
        self.hydration -= transferred_quantity
        self.bladder -= transferred_quantity * kidney_output_factor

    def get_stats(self):
        return dict(
            hydration=self.hydration,
            bladder=self.bladder,
            energy=self.energy,
        )

    def act(self, name):
        self.action = name


class Mind:
    def __init__(self, body, evaluator):
        self.body = body
        self.evaluator = evaluator
        self.calculate_action_utilites()

    def calculate_action_utilites(self):
        body_stats = self.body.get_stats()
        self.utilities = self.evaluator(body_stats)

    def get_stats(self):
        return self.utilities

    def set_goal(self):
        needs = self.get_stats()
        priorities = reversed(sorted([(p, need) for need, p in needs.items() if p > 0.5]))
        self.goals = [(need, p) for p, need in priorities]
        if self.goals:
            self.body.act(self.goals[0][0])


class StatsIndicators:
    def __init__(self, names, left=True):
        from direct.gui.DirectGui import DirectWaitBar
        from panda3d.core import TextNode
        bar_height = 0.10
        bar_offset = 0.0
        self.bars = {}
        if left:
            parent = base.a2dTopLeft
            frameSize=(0, 1, -bar_height, 0)
            text_align=TextNode.ALeft
            text_pos=(0.05, -bar_height / 2.0)
        else:
            parent = base.a2dTopRight
            frameSize=(-1, 0, -bar_height, 0)
            text_align=TextNode.ARight
            text_pos=(-0.05, -bar_height / 2.0)
        for name in names:
            self.bars[name] = DirectWaitBar(
                parent=parent,
                pos=(0, 0, -bar_offset),
                frameSize=frameSize,
                text_pos=text_pos,
                text_align=text_align,
                text_scale=0.05,
                text=name,
                range=1.0,
                value=0.5,
            )
            bar_offset += bar_height

    def tick(self, stats):
        for name, value in stats.items():
            self.bars[name]['value'] = value


class GoalIndicator:
    def __init__(self, mind):
        self.mind = mind
        from direct.gui.DirectGui import DirectLabel
        from panda3d.core import TextNode
        self.text = DirectLabel(
            parent=base.a2dTopCenter,
            pos=(0, 0, 0),
            frameSize=(-0.3, 0.3, -1, 0),
            text_pos=(-0.3, -0.1),
            text_align=TextNode.ALeft,
            text_scale=0.05,
            text="",
        )

    def tick(self):
        self.text['text'] = '\n'.join(
            [
                f"{need}: {p:.2f}"
                for need, p in self.mind.goals
            ]
        )


if __name__ == '__main__':
    from direct.showbase.ShowBase import ShowBase
    ShowBase()
    base.accept('escape', base.task_mgr.stop)

    # Body
    b = Body()
    # Mind
    def thirst(perceptions):
        hydration = perceptions['hydration']
        v = normal_clip(invert(hydration) * 2 - 1) ** 2
        return v
    def need_to_pee(perceptions):
        bladder = perceptions['bladder']
        v = normal_clip(invert(bladder) * 5 - 4)
        return v
    def be_lazy(perceptions):
        return min(0.8, invert(perceptions['energy']))
    utilities = dict(
        drink=thirst,
        pee=need_to_pee,
        be_lazy=be_lazy,
    )
    m = Mind(b, evaluate_utilities(utilities))
    # Tooling
    bi = StatsIndicators(b.get_stats().keys())
    mi = StatsIndicators(m.get_stats().keys(), left=False)
    gi = GoalIndicator(m)
    def make_things_happen(task):
        b.tick(globalClock.dt)
        m.calculate_action_utilites()
        m.set_goal()
        bi.tick(b.get_stats())
        mi.tick(m.get_stats())
        gi.tick()
        return task.cont
    base.task_mgr.add(make_things_happen)
    base.run()
