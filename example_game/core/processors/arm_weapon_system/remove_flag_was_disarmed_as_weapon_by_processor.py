__all__ = ['RemoveFlagWasDisarmedAsWeaponByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_was_disarmed_as_weapon_by import FlagWasDisarmedAsWeaponBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagWasDisarmedAsWeaponByProcessor(Processor):
    ''' Removes the flag that the entity was disarmed as a weapon.

    Involved components:
        -   FlagWasDisarmedAsWeaponBy

    Related processors:
        -   GenerateDisarmWeaponProcessor
        -   PerformDisarmWeaponProcessor
        -   RemoveFlagIsAboutToDisarmWeaponProcessor
        -   RemoveFlagHasDisarmedWeaponProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of a weapon

    Where the processor should be planned?
        -   after PerformDisarmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'arm_weapon_system.perform_disarm_weapon_processor:PerformDisarmWeaponProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the entity was disarmed as a weapon.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagWasDisarmedAsWeaponBy):

            self.world.remove_component(ent, FlagWasDisarmedAsWeaponBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagWasDis=aArmedAsWeaponBy" was removed.')

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

