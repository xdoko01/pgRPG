__all__ = ['RemoveFlagAddScoreProcessor']

import pyrpg.core.ecs.esper as esper    # for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components

class RemoveFlagAddScoreProcessor(esper.Processor):


    def __init__(self):

        super().__init__()


    def process(self, *args, **kwargs):

        for ent, (_) in self.world.get_components(components.FlagAddScore):

            self.world.remove_component(ent, components.FlagAddScore)

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
