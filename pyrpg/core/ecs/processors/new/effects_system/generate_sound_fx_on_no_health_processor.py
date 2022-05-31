__all__ = ['GenerateSoundFXOnNoHealthProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.sound_fx_on_no_health import SoundFXOnNoHealth
from pyrpg.core.ecs.components.new.flag_has_no_health import FlagHasNoHealth

# Logger init
logger = logging.getLogger(__name__)

class GenerateSoundFXOnNoHealthProcessor(Processor):
    ''' Plays sound upon entity having no health.

    Involved components:
        -   SoundFXOnNoHealth
        -   FlagNoHealth

    Related processors:
        -   PerformDamageProcessor

    What if this processor is disabled?
        -   sound effect is not played upon no health

    Where the processor should be planned?
        -   after PerformDamageProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.damage_system:PerformDamageProcessor'
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
        ''' Plays sound upon entity having no health.
        '''
        self.cycle += 1

        for ent, (flag_has_no_health, sfx_on_no_health) in self.world.get_components(FlagHasNoHealth, SoundFXOnNoHealth):

            # Use play sound fnc to play the effect
            self.play_sound_fnc(sfx_on_no_health.sound)

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced sound fx {sfx_on_no_health.sound} upon no health.')

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
