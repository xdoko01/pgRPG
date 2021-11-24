__all__ = ['NewRemoveFlagWasArmedAsWeaponByProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewRemoveFlagWasArmedAsWeaponByProcessor(esper.Processor):
    ''' Removes the flag that the entity was armed as a weapon.

    Involved components:
        -   NewFlagWasArmedAsWeaponBy

    Related processors:
        -   NewGenerateArmWeaponProcessor
        -   NewPerformArmWeaponProcessor
        -   NewRemoveFlagIsAboutToArmWeaponProcessor
        -   NewRemoveFlagHasArmedWeaponProcessor

    What if this processor is disabled?
        -   unexpected behavior during arming of a weapon

    Where the processor should be planned?
        -   after NewPerformArmWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.arm_weapon_system.new_perform_arm_weapon_processor', 'NewPerformArmWeaponProcessor')
        ]


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that the entity was armed as a weapon.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(components.NewFlagWasArmedAsWeaponBy):

            self.world.remove_component(ent, components.NewFlagWasArmedAsWeaponBy)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagWasArmedAsWeaponBy" was removed.')


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

