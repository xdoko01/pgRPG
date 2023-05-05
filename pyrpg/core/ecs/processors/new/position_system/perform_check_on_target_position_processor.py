__all__ = ['PerformCheckOnTargetPositionProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.has_target_position import HasTargetPosition

# For creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

class PerformCheckOnTargetPositionProcessor(Processor):
    ''' Detects entities that have some target position and compare
    their current position with the target position. Create a new 
    event with information if target was reached or not. 

    Involved components:
        -   HasTargetPosition
        -   Position

    Related processors:

    What if this processor is disabled?
        -   information about reaching of position is not shared via event

    Where the processor should be planned?
        -   after ResolveCollisionsProcessor
        -   after ResolveMapCollisionsProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
    ]

    def __init__(self, FNC_ADD_EVENT, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.add_event_fnc = FNC_ADD_EVENT

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are pickable + have collided and assigns
        the FlagIsAboutToPickEntity to their pickers
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # List of entities that reached their target
        on_target = set()

        # Get all entities that have HasTargetPosition and Position - those are for evaluation if target is reached
        for ent, (position, has_target_pos) in self.world.get_components(Position, HasTargetPosition):

            # Compare current position with all targets
            for target in has_target_pos.targets:
                if  (
                    position.map == target.map and
                    abs(position.x - target.x) <= target.radius and
                    abs(position.y - target.y) <= target.radius
                    ):
                    on_target.add(ent)
                    logger.debug(f'({self.cycle}) - Entity {ent} has reached the target position {target}.')
                    break # Skip to next entity

        # Report entities that have reached their destination was counted
        on_pos_target_event = Event('ON_POS_TARGET', None, None, params={'on_target' : on_target})
        self.add_event_fnc(on_pos_target_event)

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass

