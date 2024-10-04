__all__ = ['RemoveFlagWasArmedAsWeaponByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_was_armed_as_weapon_by import FlagWasArmedAsWeaponBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagWasArmedAsWeaponByProcessor(Processor):
    ''' Removes the flag that the entity was armed as a weapon.

    Involved components:
        -   FlagWasArmedAsWeaponBy

    Related processors:
        -   GenerateArmWeaponProcessor
        -   PerformArmWeaponProcessor
        -   RemoveFlagIsAboutToArmWeaponProcessor
        -   RemoveFlagHasArmedWeaponProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of a weapon

    Where the processor should be planned?
        -   after PerformArmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'arm_weapon_system.perform_arm_weapon_processor:PerformArmWeaponProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that the entity was armed as a weapon.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagWasArmedAsWeaponBy):

            self.world.remove_component(ent, FlagWasArmedAsWeaponBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagWasArmedAsWeaponBy" was removed.')

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

