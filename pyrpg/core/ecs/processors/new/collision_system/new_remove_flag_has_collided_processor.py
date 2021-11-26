__all__ = ['NewRemoveFlagHasCollidedProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.new_flag_has_collided import NewFlagHasCollided

# Logger init
logger = logging.getLogger(__name__)

class NewRemoveFlagHasCollidedProcessor(Processor):
    ''' Removes NewFlagHasCollided flag after the cycle.

    Involved components:
        -   NewFlagHasCollided

    Related processors:
        -   NewGenerateCollisionsProcessor
        -   NewGenerateCollisionsFullProcessor

    What if this processor is disabled?
        -   entities are constantly colliding

    Where the processor should be planned?
        -   after NewGenerateCollisionsProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.collision_system.new_generate_entity_collisions_processor:NewGenerateEntityCollisionsProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the NewFlagHasCollided flag.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(NewFlagHasCollided):

            self.world.remove_component(ent, NewFlagHasCollided)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagHasCollided" was removed.')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components
        '''
        pass

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the lost reference again
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
