"""Tests for sim/render stage classification of processors.

The engine already supported named processor groups (the 'pause' group used by
seven scenes). Stages are an orthogonal axis: a processor declares STAGE on its
class, so the sim/render split needs no scene-file changes.
"""

from pgrpg.core.ecs import World, Component, Processor, SkipProcessorExecution


class Counter(Component):
    __slots__ = ['sim', 'render']

    def __init__(self):
        self.sim = 0
        self.render = 0


class SimProcessor(Processor):
    """Default STAGE — no declaration needed."""

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return
        for _, counter in self.world.get_component(Counter):
            counter.sim += 1


class RenderProcessor(Processor):
    STAGE = 'render'

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return
        for _, counter in self.world.get_component(Counter):
            counter.render += 1


def test_stage_defaults_to_sim():
    """Every existing processor must keep working without declaring a stage."""
    assert Processor.STAGE == 'sim'
    assert SimProcessor().STAGE == 'sim'


def test_processors_are_grouped_by_group_and_stage():
    world = World()
    world.add_processor(SimProcessor())
    world.add_processor(RenderProcessor())

    assert ('default', 'sim') in world._processors
    assert ('default', 'render') in world._processors
    assert len(world._processors[('default', 'sim')]) == 1
    assert len(world._processors[('default', 'render')]) == 1


def test_running_one_stage_does_not_run_the_other():
    world = World()
    world.add_processor(SimProcessor())
    world.add_processor(RenderProcessor())
    entity = world.create_entity(Counter())

    world.process(stage='sim')
    world.process(stage='sim')
    world.process(stage='render')

    counter = world.component_for_entity(entity, Counter)
    assert (counter.sim, counter.render) == (2, 1)


def test_stage_is_orthogonal_to_the_scene_authored_group():
    """A scene may put a render processor in the 'pause' group."""
    world = World()
    world.add_processor(RenderProcessor(), proc_group_id='pause')
    entity = world.create_entity(Counter())

    world.process(proc_group_id='default', stage='render')
    assert world.component_for_entity(entity, Counter).render == 0

    world.process(proc_group_id='pause', stage='render')
    assert world.component_for_entity(entity, Counter).render == 1


def test_get_processor_searches_every_group_and_stage_by_default():
    """PREREQ checks call get_processor with no group; they must still resolve.

    Before stages existed this only searched 'default', so a prerequisite
    registered into 'pause' was invisible. Searching everything by default
    fixes that latent bug too.
    """
    world = World()
    world.add_processor(RenderProcessor(), proc_group_id='pause')

    assert world.get_processor(RenderProcessor) is not None
    assert world.get_processor(RenderProcessor, proc_group_id='pause') is not None
    assert world.get_processor(RenderProcessor, proc_group_id='default') is None


def test_clear_processors_empties_every_stage():
    world = World()
    world.add_processor(SimProcessor())
    world.add_processor(RenderProcessor())

    world.clear_processors()

    assert all(not procs for procs in world._processors.values())


def test_finalize_reaches_every_stage():
    calls = []

    class FinalizingRender(Processor):
        STAGE = 'render'

        def process(self, *args, **kwargs):
            pass

        def finalize(self, *args, **kwargs):
            calls.append('render')

    class FinalizingSim(Processor):
        def process(self, *args, **kwargs):
            pass

        def finalize(self, *args, **kwargs):
            calls.append('sim')

    world = World()
    world.add_processor(FinalizingSim())
    world.add_processor(FinalizingRender())

    world.finalize()

    assert sorted(calls) == ['render', 'sim']
