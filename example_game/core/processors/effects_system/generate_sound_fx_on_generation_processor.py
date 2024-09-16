__all__ = ['GenerateSoundFXOnGenerationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.sound_fx_on_generation import SoundFXOnGeneration
from core.components.flag_create_from_factory import FlagCreateFromFactory

# Logger init
logger = logging.getLogger(__name__)

class GenerateSoundFXOnGenerationProcessor(Processor):
    ''' Generates sound effect when factory generates the entity

    Involved components:
        -   SoundFXOnGeneration
        -   FlagCreateFromFactory

    Related processors:
        -   PerformFactoryGenerationProcessor

    What if this processor is disabled?
        -   sound effect is not played

    Where the processor should be planned?
        -   after PerformFactoryGenerationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.factory_system:PerformFactoryGenerationProcessor'
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
        ''' Generates sound effect when factory generates the entity.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (flag_create_from_factory, sfx_on_generation) in self.world.get_components(FlagCreateFromFactory, SoundFXOnGeneration):

            # Use play sound fnc to play the effect
            self.play_sound_fnc(sfx_on_generation.sound)

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced sound fx {sfx_on_generation.sound} upon generation.')

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
