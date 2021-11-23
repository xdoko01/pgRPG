__all__ = ['NewRemoveFlagDoAttackProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewRemoveFlagDoAttackProcessor(esper.Processor):
    ''' Removes the flag that fighter has attacked.

    Involved components:
        -   NewFlagDoAttack

    Related processors:

    What if this processor is disabled?
        -   entity attacks always regardless on input

    Where the processor should be planned?
        -   after NewPerformCommandProcessor
        -   after NewPerformActionAnimationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.command_system.new_perform_command_processor', 'NewPerformCommandProcessor')
        ]


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Removes the flag that the entity has attacked.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(components.NewFlagDoAttack):

            self.world.remove_component(ent, components.NewFlagDoAttack)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagDoAttack" was removed.')


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

