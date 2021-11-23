__all__ = ['RemoveDepletedAmmoPackProcessor']

import pyrpg.core.ecs.esper as esper    # for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components

class RemoveDepletedAmmoPackProcessor(esper.Processor):

    __slots__ = ['remove_entity_fnc']

    def __init__(self, remove_entity_fnc):

        super().__init__()

        self.remove_entity_fnc = remove_entity_fnc

    def process(self, *args, **kwargs):

        for ent, (ammo_pack, factory, flag_factory_depleted) in self.world.get_components(components.AmmoPack, components.Factory, components.FlagFactoryDepleted):

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
