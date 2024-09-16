__all__ = ['RemoveFlagGeneratedFromFactoryProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_generated_from_factory import FlagGeneratedFromFactory

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagGeneratedFromFactoryProcessor(Processor):
    ''' Removes the flag that the entity was generated from the factory.

    Involved components:
        -   FlagGeneratedFromFactory

    Related processors:
        -   PerformFactoryGenerationProcessor

    What if this processor is disabled?
        -   repeating effects that are bound to entity creation

    Where the processor should be planned?
        -   after PerformFactoryGenerationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.factory_system:PerformFactoryGenerationProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that entity was generated from the factory.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagGeneratedFromFactory):

            self.world.remove_component(ent, FlagGeneratedFromFactory)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagGeneratedFromFactory" was removed.')

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
