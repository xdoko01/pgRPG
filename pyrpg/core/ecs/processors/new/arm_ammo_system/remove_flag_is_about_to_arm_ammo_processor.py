__all__ = ['RemoveFlagIsAboutToArmAmmoProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_is_about_to_arm_ammo import FlagIsAboutToArmAmmo

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagIsAboutToArmAmmoProcessor(Processor):
    ''' Removes the flag that the entity has been considered for picking
    up of an ammo at the end of the cycle.

    Involved components:
        -   FlagIsAboutToArmAmmo

    Related processors:
        -   GenerateArmAmmoProcessor
        -   PerformArmAmmoProcessor
        -   RemoveFlagWasArmedAsAmmoByProcessor
        -   RemoveFlagHasArmedAmmoProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of an ammo

    Where the processor should be planned?
        -   after PerformArmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.arm_ammo_system.perform_arm_ammo_processor:PerformArmAmmoProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that the item has been considered for arming
        an ammo at the end of the cycle.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(FlagIsAboutToArmAmmo):

            self.world.remove_component(ent, FlagIsAboutToArmAmmo)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagIsAboutToArmAmmo" was removed.')

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

