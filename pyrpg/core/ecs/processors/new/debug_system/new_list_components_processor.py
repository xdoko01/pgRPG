__all__ = ['NewListComponentsProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewListComponentsProcessor(esper.Processor):
    ''' Help to debug the values of components in different stages of the 
    game cycle.
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    def __init__(self, comp_name):
        ''' Init the processor.
        '''
        super().__init__()

        self.comp_name = comp_name
        self.comp_class = eval(f'components.{comp_name}')

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Get all components comp_name and list their values
        '''
        self.cycle += 1

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