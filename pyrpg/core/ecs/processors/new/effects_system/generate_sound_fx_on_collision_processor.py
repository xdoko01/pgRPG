__all__ = ['GenerateSoundFXOnCollisionProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.sound_fx_on_collision import SoundFXOnCollision
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided

# Logger init
logger = logging.getLogger(__name__)

class GenerateSoundFXOnCollisionProcessor(Processor):
    ''' Creates new entity containing visual fx on the collision spot.

    Involved components:
        -   SoundFXOnCollision
        -   FlagHasCollided

    Related processors:
        -   GenerateEntityCollisionsProcessor

    What if this processor is disabled?
        -   sound effect is not played

    Where the processor should be planned?
        -   after GenerateEntityCollisionsProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.collision_system:GenerateCollisionsProcessor'
    ]

    __slots__ = ['play_sound_fnc']

    def __init__(self, FNC_PLAY_SOUND):
        ''' Init the processor.
        '''
        super().__init__()
        self.play_sound_fnc = FNC_PLAY_SOUND

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the FlagHasCollided flag.
        '''
        self.cycle += 1

        for ent, (flag_has_collided, sfx_on_collision) in self.world.get_components(FlagHasCollided, SoundFXOnCollision):

            # Use play sound fnc to play the effect
            self.play_sound_fnc(sfx_on_collision.sound)

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced sound fx {sfx_on_collision.sound} upon collision.')

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
