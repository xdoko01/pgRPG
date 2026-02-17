__all__ = ['RemoveFlagWasDisarmedAsAmmoByProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_was_disarmed_as_ammo_by import FlagWasDisarmedAsAmmoBy

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagWasDisarmedAsAmmoByProcessor(Processor):
    ''' Removes the flag that the entity was disarmed as a ammo.

    Involved components:
        -   FlagWasDisarmedAsAmmoBy

    Related processors:
        -   GenerateDisarmAmmoProcessor
        -   PerformDisarmAmmoProcessor
        -   RemoveFlagIsAboutToDisarmAmmoProcessor
        -   RemoveFlagHasDisarmedAmmoProcessor

    What if this processor is disabled?
        -   unexpected behavior during disarming of an ammo

    Where the processor should be planned?
        -   after PerformDisarmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'arm_ammo_system.perform_disarm_ammo_processor:PerformDisarmAmmoProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the entity was disarmed as a ammo.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagWasDisarmedAsAmmoBy):

            self.world.remove_component(ent, FlagWasDisarmedAsAmmoBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagWasDisarmedAsAmmoBy" was removed.')

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

