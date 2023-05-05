__all__ = ['ClearTemporaryEntityProcessor']

import pygame	# for pygame.time.get_ticks()

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.temporary import Temporary

class ClearTemporaryEntityProcessor(Processor):
    ''' Delete for example projectiles
    '''
    __slots__ = ['remove_entity_fnc']

    def __init__(self, remove_entity_fnc, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.remove_entity_fnc = remove_entity_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all temporary components
        for ent, temporary in self.world.get_component(Temporary):

            # Compare if the entity lived long enough
            if pygame.time.get_ticks() - temporary.creation_time > temporary.ttl:

                # Remove
                self.remove_entity_fnc(ent)
