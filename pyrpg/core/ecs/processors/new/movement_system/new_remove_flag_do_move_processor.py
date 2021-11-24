__all__ = ['NewRemoveFlagDoMoveProcessor']

import logging
import pyrpg.core.ecs.esper as esper    # for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components

# Logger init
logger =  logging.getLogger(__name__)

class NewRemoveFlagDoMoveProcessor(esper.Processor):

    def __init__(self):
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        self.cycle += 1

        for ent, (_) in self.world.get_components(components.NewFlagDoMove):

            self.world.remove_component(ent, components.NewFlagDoMove)
            logger.debug(f'({self.cycle}) - Entity {ent} - Flag {_} removed.')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components (window)
        '''
        pass

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to window again
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
