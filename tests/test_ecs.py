
from pgrpg.core.ecs import World, Component, Processor, SkipProcessorExecution

# Dummy components
class Position(Component):
    __slots__ = ['x', 'y']
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Velocity(Component):
    __slots__ = ['vx', 'vy']
    def __init__(self, vx=0, vy=0):
        self.vx = vx
        self.vy = vy

# Dummy processor
class MoveProcessor(Processor):
    def process(self):
        super().process()
        for ent, (pos, vel) in self.world.get_components(Position, Velocity):
            pos.x += vel.vx
            pos.y += vel.vy

def test_entity_creation_and_component_assignment():
    world = World()
    entity = world.create_entity(Position(1, 2), Velocity(3, 4))

    pos = world.component_for_entity(entity, Position)
    vel = world.component_for_entity(entity, Velocity)

    assert pos.x == 1 and pos.y == 2
    assert vel.vx == 3 and vel.vy == 4
    assert world.has_components(entity, Position, Velocity)

def test_component_retrieval_and_deletion():
    world = World()
    entity = world.create_entity(Position(5, 5))
    assert isinstance(world.component_for_entity(entity, Position), Position)

    world.remove_component(entity, Position)
    assert not world.has_component(entity, Position)

def test_try_component_methods():
    world = World()
    e = world.create_entity(Position(1, 2))
    assert world.try_component(e, Position) is not None
    assert world.try_component(e, Velocity) is None

    # Add Velocity, try_components should yield both
    world.add_component(e, Velocity(3, 4))
    comps = list(world.try_components(e, Position, Velocity))
    assert len(comps) == 1 and isinstance(comps[0][0], Position)

def test_add_and_remove_processor():
    world = World()
    proc = MoveProcessor()
    world.add_processor(proc)
    assert world.get_processor(MoveProcessor) is proc

    world.remove_processor(MoveProcessor)
    assert world.get_processor(MoveProcessor) is None

def test_processor_execution_control():
    world = World()
    entity = world.create_entity(Position(0, 0), Velocity(1, 1))

    proc = MoveProcessor(step=2)  # Executes every 2nd cycle
    world.add_processor(proc)

    world.process()
    pos = world.component_for_entity(entity, Position)
    assert pos.x == 0 and pos.y == 0  # Not updated on first cycle

    world.process()
    assert pos.x == 1 and pos.y == 1  # Updated on second cycle

def test_deferred_entity_deletion():
    world = World()
    e = world.create_entity(Position(0, 0))
    world.delete_entity(e)
    assert e in world._dead_entities

    world.process()
    assert e not in world._entities

def test_get_components_variants():
    world = World()
    e1 = world.create_entity(Position(1, 1), Velocity(1, 1))
    e2 = world.create_entity(Position(2, 2))

    comps = world.get_components(Position, Velocity)
    assert len(comps) == 1 and comps[0][0] == e1

    comps_ex = world.get_components_ex(Position, exclude=Velocity)
    assert len(comps_ex) == 1 and comps_ex[0][0] == e2

    comps_exs = world.get_components_exs(include=(Position,), exclude=(Velocity,))
    assert len(comps_exs) == 1 and comps_exs[0][0] == e2

    comps_opt = world.get_components_opt(Position, optional=Velocity)
    assert len(comps_opt) == 2
