__all__ = ['HandleDestroyedEntitiesProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.is_destroyed import IsDestroyed
from pyrpg.core.ecs.components.original.motion import Motion
from pyrpg.core.ecs.components.original.flag_no_health import FlagNoHealth
from pyrpg.core.ecs.components.original.brain import Brain
from pyrpg.core.ecs.components.original.collidable import Collidable
from pyrpg.core.ecs.components.original.camera import Camera
from pyrpg.core.ecs.components.original.temporary import Temporary

# For creation of events
from pyrpg.core.events.event import Event

import pyrpg.core.config.config as config # for the time before dead body disappears

class HandleDestroyedEntitiesProcessor(Processor):

    def __init__(self, destroy_event_queue, *args, **kwargs):
        self.destroy_event_queue = destroy_event_queue
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return
        # Select all entities that have been destroyed in this cycle
        for ent, (destroyed) in self.world.get_component(FlagNoHealth):

            # Generate DESTROYED event
            kill_event = Event('KILL', ent, destroyed.src_entity, params={'killed_by' : ent, 'killed' : destroyed.src_entity})
            self.destroy_event_queue.append(kill_event)

            # Add IsDestroyed component to the entity so that animation can be processed correctly
            self.world.add_component(ent, IsDestroyed())

            # Remove Motion component from the entity - nobody wants to see dead body moving
            try:
                self.world.remove_component(ent, Motion)
            except KeyError:
                pass

            # Remove Brain component from the entity - nobody wants to see dead body performing commands
            try:
                self.world.remove_component(ent, Brain)
            except KeyError:
                pass

            # Remove Collidable component from the entity - dead body does not colide with anything
            try:
                self.world.remove_component(ent, Collidable)
            except KeyError:
                pass

            # Remove Camera component from the entity - dead entity is no longer focused
            try:
                self.world.remove_component(ent, Camera)
            except KeyError:
                pass

            # Add temporary component to the entity - visible for 20s
            self.world.add_component(ent, Temporary(ttl=config.DEAD_TIME_TO_DISAPPEAR))

