__all__ = ['DisarmDepletedAmmoPackProcessor', 'RemoveDepletedAmmoPackProcessor']

import pyrpg.core.ecs.esper as esper    # for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components
import pyrpg.core.events.event as event # for creation of events

class DisarmDepletedAmmoPackProcessor(esper.Processor):
    ''' Aim of this processor is to remove reference on AmmoPack entity
    from the HasWeapon component. Just deleting the AmmoPack entity using
    RemoveDepletedAmmoPack processor is not enough, because that would still
    leave reference to the AmmoPack entity in HasWeapon component.
    '''

    def __init__(self, ammo_pack_event_queue):

        super().__init__()

        self.ammo_pack_event_queue = ammo_pack_event_queue

    def process(self, *args, **kwargs):

        for ent, (ammo_pack, factory, flag_factory_depleted, flag_ammo_pack_armed) in self.world.get_components(components.AmmoPack, components.Factory, components.FlagFactoryDepleted, components.FlagAmmoPackArmed):
            
            # Get HasWeapon component from armed entity stored in FlagAmmoPackArmed component
            has_weapon = self.world.component_for_entity(flag_ammo_pack_armed.armed_entity, components.HasWeapon)

            # Remove it from generator position - set to none
            has_weapon.weapons.get(ammo_pack.weapon).update({'generator' : None})

            disarmed_event = event.Event('AMMO_PACK_DISARMED', ent, flag_ammo_pack_armed.armed_entity, params={'ammo_pack' : ent, 'armed_entity' : flag_ammo_pack_armed.armed_entity})
            self.ammo_pack_event_queue.append(disarmed_event)

            # Remove the FlagAmmoPackArmed component
            self.world.remove_component(ent, components.FlagAmmoPackArmed)



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
