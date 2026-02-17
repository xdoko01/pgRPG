__all__ = ['RemoveFlagIsAboutToDisarmWeaponProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_is_about_to_disarm_weapon import FlagIsAboutToDisarmWeapon

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagIsAboutToDisarmWeaponProcessor(Processor):
    ''' Removes the flag that the entity has been considered for disarming.

    Involved components:
        -   FlagIsAboutToDisarmWeapon

    Related processors:
        -   GenerateDisarmWeaponProcessor
        -   PerformDisarmWeaponProcessor
        -   RemoveFlagWasDisarmedAsWeaponByProcessor
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
        ''' Removes the flag that the item has been considered for disarming
        at the end of the cycle.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagIsAboutToDisarmWeapon):

            self.world.remove_component(ent, FlagIsAboutToDisarmWeapon)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagIsAboutToDisarmWeapon" was removed.')

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

