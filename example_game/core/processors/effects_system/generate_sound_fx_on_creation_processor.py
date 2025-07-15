__all__ = ['GenerateSoundFXOnCreationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.sound_fx_on_creation import SoundFXOnCreation
from core.components.flag_generated_from_factory import FlagGeneratedFromFactory

# Logger init
logger = logging.getLogger(__name__)

class GenerateSoundFXOnCreationProcessor(Processor):
    ''' Generates sound effect when entity is created from factory

    Involved components:
        -   SoundFXOnCreation
        -   FlagGeneratedFromFactory

    Related processors:
        -   PerformFactoryGenerationProcessor

    What if this processor is disabled?
        -   sound effect is not played

    Where the processor should be planned?
        -   after PerformFactoryGenerationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'factory_system:PerformFactoryGenerationProcessor'
    ]

    __slots__ = ['play_sound_fnc']

    def __init__(self, FNC_PLAY_SOUND, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.play_sound_fnc = FNC_PLAY_SOUND


    def process(self, *args, **kwargs):
        ''' Generates sound effect when entity is created from factory.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (flag_generated_from_factory, sfx_on_creation) in self.world.get_components(FlagGeneratedFromFactory, SoundFXOnCreation):

            # Use play sound fnc to play the effect
            self.play_sound_fnc(sfx_on_creation.sound)

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced sound fx {sfx_on_creation.sound} upon creation.')

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
