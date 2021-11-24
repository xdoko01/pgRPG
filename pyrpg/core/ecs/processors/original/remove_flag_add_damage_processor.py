__all__ = ['RemoveFlagAddDamageProcessor']

import pyrpg.core.ecs.esper as esper    # for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components

class RemoveFlagAddDamageProcessor(esper.Processor):


    def __init__(self):

        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):

        for ent, (_) in self.world.get_components(components.FlagAddDamage):

            self.world.remove_component(ent, components.FlagAddDamage)

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