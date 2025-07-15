__all__ = ['ListComponentsProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Logger init
logger = logging.getLogger(__name__)

class ListComponentsProcessor(Processor):
    ''' Help to debug the values of components in different stages of the 
    game cycle.
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    def __init__(self, comp_name, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        self.comp_name = comp_name
        self.comp_class = eval(f'components.{comp_name}')


    def process(self, *args, **kwargs):
        ''' Get all components comp_name and list their values
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Iterate all interesting components
        for ent, (component) in self.world.get_component(self.comp_class):

            logger.debug(f'({self.cycle}) - Entity {ent}, component {self.comp_name}, values {component} ')


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