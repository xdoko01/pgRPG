__all__ = ['HandleDestroyedEntitiesProcessor']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pyrpg.core.events.event as event # for creation of events
import pyrpg.core.config.config as config # for the time before dead body disappears

class HandleDestroyedEntitiesProcessor(esper.Processor):

    def __init__(self, destroy_event_queue):
        self.destroy_event_queue = destroy_event_queue
        super().__init__()

    def process(self, *args, **kwargs):

        # Select all entities that have been destroyed in this cycle
        for ent, (destroyed) in self.world.get_component(components.FlagNoHealth):

            # Generate DESTROYED event
            kill_event = event.Event('KILL', ent, destroyed.src_entity, params={'killed_by' : ent, 'killed' : destroyed.src_entity})
            self.destroy_event_queue.append(kill_event)

            # Add IsDestroyed component to the entity so that animation can be processed correctly
            self.world.add_component(ent, components.IsDestroyed())

            # Remove Motion component from the entity - nobody wants to see dead body moving
            try:
                self.world.remove_component(ent, components.Motion)
            except KeyError:
                pass

            # Remove Brain component from the entity - nobody wants to see dead body performing commands
            try:
                self.world.remove_component(ent, components.Brain)
            except KeyError:
                pass

            # Remove Collidable component from the entity - dead body does not colide with anything
            try:
                self.world.remove_component(ent, components.Collidable)
            except KeyError:
                pass

            # Remove Camera component from the entity - dead entity is no longer focused
            try:
                self.world.remove_component(ent, components.Camera)
            except KeyError:
                pass

            # Add temporary component to the entity - visible for 20s
            self.world.add_component(ent, components.Temporary(ttl=config.DEAD_TIME_TO_DISAPPEAR))

