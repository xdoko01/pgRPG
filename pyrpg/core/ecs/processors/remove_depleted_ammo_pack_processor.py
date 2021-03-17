__all__ = ['DisarmDepletedAmmoPackProcessor', 'RemoveDepletedAmmoPackProcessor']

import pyrpg.core.ecs.esper as esper    # for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components

class DisarmDepletedAmmoPackProcessor(esper.Processor):

    def __init__(self):

        super().__init__()

    def process(self, *args, **kwargs):

        for ent, (ammo_pack, factory, flag_factory_depleted, flag_ammo_pack_armed) in self.world.get_components(components.AmmoPack, components.Factory, components.FlagFactoryDepleted, components.FlagAmmoPackArmed):
            
            # Get HasWeapon component from armed entity stored in FlagAmmoPackArmed component
            has_weapon = self.world.component_for_entity(flag_ammo_pack_armed.armed_entity, components.HasWeapon)

            # Remove it from generator position - set to none
            has_weapon.weapons.get(ammo_pack.weapon).update({'generator' : None})

            # Remove the FlagAmmoPackArmed component
            self.world.remove_component(ent, components.FlagAmmoPackArmed)

            print(f'AmmoPack disarmed from the entity {ent}')


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

class RemoveDepletedAmmoPackProcessor(esper.Processor):

    __slots__ = ['remove_entity_fnc']

    def __init__(self, remove_entity_fnc=None):

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
