__all__ = ['RemoveFlagNoHealthProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.flag_no_health import FlagNoHealth

class RemoveFlagNoHealthProcessor(Processor):


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return
        for ent, (_) in self.world.get_components(FlagNoHealth):

            self.world.remove_component(ent, FlagNoHealth)

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