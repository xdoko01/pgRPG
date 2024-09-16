__all__ = ['GenerateSoundFXOnDamageProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.sound_fx_on_damage import SoundFXOnDamage
from core.components.flag_was_damaged_by import FlagWasDamagedBy

# Logger init
logger = logging.getLogger(__name__)

class GenerateSoundFXOnDamageProcessor(Processor):
    ''' Plays sound upon entity being damaged.

    Involved components:
        -   SoundFXOnDamage
        -   FlagWasDamagedBy

    Related processors:
        -   PerformDamageProcessor

    What if this processor is disabled?
        -   sound effect is not played upon damage

    Where the processor should be planned?
        -   after PerformDamageProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.damage_system:PerformDamageProcessor'
    ]

    __slots__ = ['play_sound_fnc']

    def __init__(self, FNC_PLAY_SOUND, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.play_sound_fnc = FNC_PLAY_SOUND

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Plays sound upon entity being damaged.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (flag_was_damaged_by, sfx_on_damage) in self.world.get_components_ex(FlagWasDamagedBy, SoundFXOnDamage):

            # Use play sound fnc to play the effect
            self.play_sound_fnc(sfx_on_damage.sound)

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced sound fx {sfx_on_damage.sound} upon damage.')

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
