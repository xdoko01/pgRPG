__all__ = ['GenerateSoundFXOnArmWeaponProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.sound_fx_on_arm_weapon import SoundFXOnArmWeapon
from core.components.flag_was_armed_as_weapon_by import FlagWasArmedAsWeaponBy

# Logger init
logger = logging.getLogger(__name__)

class GenerateSoundFXOnArmWeaponProcessor(Processor):
    ''' Produces a sound at the moment of arming a weapon.

    Involved components:
        -   SoundFXOnArmWeapon
        -   FlagWasArmedAsWeaponBy

    Related processors:
        -   PerformArmWeaponProcessor

    What if this processor is disabled?
        -   sound effect is not played

    Where the processor should be planned?
        -   after PerformArmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'arm_weapon_system.perform_arm_weapon_processor:PerformArmWeaponProcessor'
    ]

    __slots__ = ['play_sound_fnc']

    def __init__(self, FNC_PLAY_SOUND, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.play_sound_fnc = FNC_PLAY_SOUND


    def process(self, *args, **kwargs):
        ''' Removes the FlagHasCollided flag.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_, sfx_on_arm_weapon) in self.world.get_components(FlagWasArmedAsWeaponBy, SoundFXOnArmWeapon):

            # Use play sound fnc to play the effect
            self.play_sound_fnc(sfx_on_arm_weapon.sound)

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced sound fx {sfx_on_arm_weapon.sound} upon arming.')

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
