__all__ = ['RemoveDepletedAmmoPackProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.ammo_pack import AmmoPack
from pyrpg.core.ecs.components.original.factory import Factory
from pyrpg.core.ecs.components.original.flag_factory_depleted import FlagFactoryDepleted

class RemoveDepletedAmmoPackProcessor(Processor):

    __slots__ = ['remove_entity_fnc']

    def __init__(self, remove_entity_fnc):

        super().__init__()

        self.remove_entity_fnc = remove_entity_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):

        for ent, (ammo_pack, factory, flag_factory_depleted) in self.world.get_components(AmmoPack, Factory, FlagFactoryDepleted):

            # Remove and unregister entity from global dicts
            self.remove_entity_fnc(ent)

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
