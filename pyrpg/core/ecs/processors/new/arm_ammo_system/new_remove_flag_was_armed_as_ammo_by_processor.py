__all__ = ['NewRemoveFlagWasArmedAsAmmoByProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.new_flag_was_armed_as_ammo_by import NewFlagWasArmedAsAmmoBy

# Logger init
logger = logging.getLogger(__name__)

class NewRemoveFlagWasArmedAsAmmoByProcessor(Processor):
    ''' Removes the flag that the entity was armed as an ammo.

    Involved components:
        -   NewFlagWasArmedAsAmmoBy

    Related processors:
        -   NewGenerateArmAmmoProcessor
        -   NewPerformArmAmmoProcessor
        -   NewRemoveFlagIsAboutToArmAmmoProcessor
        -   NewRemoveFlagHasArmedAmmoProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of an ammo

    Where the processor should be planned?
        -   after NewPerformArmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.arm_ammo_system.new_perform_arm_ammo_processor:NewPerformArmAmmoProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that the entity was armed as an ammo.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(NewFlagWasArmedAsAmmoBy):

            self.world.remove_component(ent, NewFlagWasArmedAsAmmoBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagWasArmedAsAmmoBy" was removed.')

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

