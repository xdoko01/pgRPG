__all__ = ['GenerateSoundFXOnMovementProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.sound_fx_on_movement import SoundFXOnMovement
from core.components.flag_do_move import FlagDoMove

# Logger init
logger = logging.getLogger(__name__)

class GenerateSoundFXOnMovementProcessor(Processor):
    ''' Plays sound if entity is moving.

    Involved components:
        -   SoundFXOnMovement
        -   FlagDoMove

    Related processors:
        -   PerformMovementProcessor

    What if this processor is disabled?
        -   sound effect is not played

    Where the processor should be planned?
        -   after PerformMovementProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'movement_system:PerformMovementProcessor'
    ]

    __slots__ = ['play_sound_fnc']

    def __init__(self, FNC_PLAY_SOUND, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.play_sound_fnc = FNC_PLAY_SOUND


    def process(self, *args, **kwargs):
        ''' Play the sound if entity is moving.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (flag_do_move, sfx_on_movement) in self.world.get_components(FlagDoMove, SoundFXOnMovement):

            # Set the volume for the sound
            sfx_on_movement.sound.set_volume(sfx_on_movement.volume)

            # Use play sound fnc to play the effect
            self.play_sound_fnc(sfx_on_movement.sound)

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced sound fx {sfx_on_movement.sound} upon movement.')

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
