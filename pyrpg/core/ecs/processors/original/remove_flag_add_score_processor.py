__all__ = ['RemoveFlagAddScoreProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.flag_add_score import FlagAddScore

class RemoveFlagAddScoreProcessor(Processor):


    def __init__(self):

        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):

        for ent, (_) in self.world.get_components(FlagAddScore):

            self.world.remove_component(ent, FlagAddScore)

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
