__all__ = ['GenerateRenderDataFromParentProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.renderable_model import RenderableModel
from pyrpg.core.ecs.components.new.has_weapon import HasWeapon
from pyrpg.core.ecs.components.new.new_weapon_in_use import NewWeaponInUse
from pyrpg.core.ecs.components.new.render_data_from_parent import RenderDataFromParent

# Logger init
logger = logging.getLogger(__name__)

class GenerateRenderDataFromParentProcessor(Processor):
    ''' Adds/updates NewRenderPosition component on entities that 
    need to be rendered and do not have their own position component
    (because they are picked or used otherwise).

    Involved components:
        -   Position
        -   RenderableModel
        -   HasWeapon
        -   NewWeaponInUse
        -   RenderDataFromParent

    Related processors:
        -   PerformRenderArmedWeaponProcessor

    What if this processor is disabled?
        -   active weapons and wearables are not displayed

    Where the processor should be planned?
        -   before PerformRenderArmedWeaponProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that need to be rendered but do not have their own Position 
        component.
        '''
        self.cycle += 1

        # Get all entities that are parents of WeaponInUse
        for ent_parent, (position, renderable_model, has_weapon, weapon_in_use) in self.world.get_components(Position, RenderableModel, HasWeapon, NewWeaponInUse):

            # Prepare render data for Weapon that is armed
            ent_weapon_in_use = has_weapon.weapons[weapon_in_use.type]["weapon"]

            self.world.add_component(ent_weapon_in_use, RenderDataFromParent(x=position.x, y=position.y, dir_name=position.dir_name, action=renderable_model.action, last_frame=renderable_model.last_frame))
            logger.debug(f'({self.cycle}) - Entity {ent_weapon_in_use} gained render data from {ent_parent}.')

            # Prepare render data for Ammo that is on Weapon that is armed
            ent_ammo_in_use = has_weapon.weapons[weapon_in_use.type]["generator"]

            self.world.add_component(ent_ammo_in_use, RenderDataFromParent(x=position.x, y=position.y, dir_name=position.dir_name, action=renderable_model.action, last_frame=renderable_model.last_frame))
            logger.debug(f'({self.cycle}) - Entity {ent_ammo_in_use} gained render data from {ent_parent}.')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass

