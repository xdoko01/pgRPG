__all__ = ['DisarmDepletedAmmoPackProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.ammo_pack import AmmoPack
from pyrpg.core.ecs.components.original.factory import Factory
from pyrpg.core.ecs.components.original.flag_factory_depleted import FlagFactoryDepleted
from pyrpg.core.ecs.components.original.flag_ammo_pack_armed import FlagAmmoPackArmed
from pyrpg.core.ecs.components.original.has_weapon import HasWeapon

# For creation of events
from pyrpg.core.events.event import Event

class DisarmDepletedAmmoPackProcessor(Processor):
    ''' Aim of this processor is to remove reference on AmmoPack entity
    from the HasWeapon component. Just deleting the AmmoPack entity using
    RemoveDepletedAmmoPack processor is not enough, because that would still
    leave reference to the AmmoPack entity in HasWeapon component.
    '''

    def __init__(self, ammo_pack_event_queue, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.ammo_pack_event_queue = ammo_pack_event_queue

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (ammo_pack, factory, flag_factory_depleted, flag_ammo_pack_armed) in self.world.get_components(AmmoPack, Factory, FlagFactoryDepleted, FlagAmmoPackArmed):
            
            # Get HasWeapon component from armed entity stored in FlagAmmoPackArmed component
            has_weapon = self.world.component_for_entity(flag_ammo_pack_armed.armed_entity, HasWeapon)

            # Remove it from generator position - set to none
            has_weapon.weapons.get(ammo_pack.weapon).update({'generator' : None})

            disarmed_event = event.Event('AMMO_PACK_DISARMED', ent, flag_ammo_pack_armed.armed_entity, params={'ammo_pack' : ent, 'armed_entity' : flag_ammo_pack_armed.armed_entity})
            self.ammo_pack_event_queue.append(disarmed_event)

            # Remove the FlagAmmoPackArmed component
            self.world.remove_component(ent, FlagAmmoPackArmed)

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

