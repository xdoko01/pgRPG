__all__ = ['RemoveFlagCreateFromFactoryProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.flag_create_from_factory import FlagCreateFromFactory

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagCreateFromFactoryProcessor(Processor):
    ''' Removes the flag that the entity should be generated from the factory.

    Involved components:
        -   FlagCreateFromFactory

    Related processors:
        -   GenerateProjectileFactoryDataProcessor

    What if this processor is disabled?
        -   entities will keep generatinge from factories

    Where the processor should be planned?
        -   after GenerateProjectileFactoryDataProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.attack_system.generate_projectile_factory_data_processor:GenerateProjectileFactoryDataProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag with data for generation from the factory.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(FlagCreateFromFactory):

            self.world.remove_component(ent, FlagCreateFromFactory)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagCreateFromFactory" was removed.')

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
