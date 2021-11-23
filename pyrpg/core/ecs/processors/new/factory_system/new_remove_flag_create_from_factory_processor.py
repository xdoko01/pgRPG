__all__ = ['NewRemoveFlagCreateFromFactoryProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewRemoveFlagCreateFromFactoryProcessor(esper.Processor):
    ''' Removes the flag that the entity should be generated from the factory.

    Involved components:
        -   NewFlagCreateFromFactory

    Related processors:
        -   NewGenerateProjectileFactoryDataProcessor

    What if this processor is disabled?
        -   entities will keep generatinge from factories

    Where the processor should be planned?
        -   after NewGenerateProjectileFactoryDataProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.attack_system.new_generate_projectile_factory_data_processor', 'NewGenerateProjectileFactoryDataProcessor')
        ]


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Removes the flag with data for generation from the factory.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(components.NewFlagCreateFromFactory):

            self.world.remove_component(ent, components.NewFlagCreateFromFactory)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagCreateFromFactory" was removed.')


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
