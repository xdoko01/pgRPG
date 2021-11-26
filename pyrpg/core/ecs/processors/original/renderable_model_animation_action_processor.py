__all__ = ['RenderableModelAnimationActionProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.original.renderable_model import RenderableModel
from pyrpg.core.ecs.components.original.motion import Motion
from pyrpg.core.ecs.components.original.has_weapon import HasWeapon
from pyrpg.core.ecs.components.original.weapon import Weapon
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.camera import Camera
from pyrpg.core.ecs.components.original.is_destroyed import IsDestroyed


from .functions import filter_only_visible

class RenderableModelAnimationActionProcessor2(Processor):
    ''' Change the action of renderable model in order to display
    correct action animation.

    co takhle prepsat to jako erastotenovo sito
        - a potom porovnat performance
        - novej procesor
            - for RenderableModel -> IDLE
            - for RenderableModel, HasWeapon -> ACTION ANIM, IDLE ANIM
            - for RenderableModel, Motion -> WALK
        - potom aktualizovat frame
            - for RenderableModel, Position - pouze ty na kamerach novy filter filter_only_visible(all_cameras, x)
                - update_frame() ... bez argumentu
    '''
    def __init__(self):
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        
        changed_ent = set()
        
        for ent, (renderable_model, motion) in self.world.get_components(RenderableModel, Motion):
            if motion.has_moved:
                renderable_model.set_action('walk')
                changed_ent.add(ent)
        
        for ent, (renderable_model, has_weapon) in self.world.get_components(RenderableModel, HasWeapon):
            if has_weapon.has_attacked and has_weapon.weapon and ent not in changed_ent:
                #renderable_model.set_action(has_weapon.get_weapon_action_anim())
                renderable_model.set_action(self.world.component_for_entity(has_weapon.get_weapon_in_use(), Weapon).action)

                has_weapon.has_attacked = False
                changed_ent.add(ent)

            elif has_weapon.weapon and ent not in changed_ent:
                #renderable_model.set_action(has_weapon.get_weapon_idle_anim())
                renderable_model.set_action(self.world.component_for_entity(has_weapon.get_weapon_in_use(), Weapon).idle)

                changed_ent.add(ent)

        for ent, renderable_model in self.world.get_component(RenderableModel):	
            if ent not in changed_ent:
                renderable_model.set_action('idle')




class RenderableModelAnimationActionProcessor(Processor):
    ''' Change the action of renderable model in order to display
    correct action animation.

    co takhle prepsat to jako erastotenovo sito
        - a potom porovnat performance
        - novej procesor
            - for RenderableModel -> IDLE
            - for RenderableModel, HasWeapon -> ACTION ANIM, IDLE ANIM
            - for RenderableModel, Motion -> WALK
        - potom aktualizovat frame
            - for RenderableModel, Position - pouze ty na kamerach novy filter filter_only_visible(all_cameras, x)
                - update_frame() ... bez argumentu
    '''
    def __init__(self):
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):

        # Remember updated entities - to prevent several updates on simgle entity
        already_updated = set()

        # Iterate all camaeras
        for cam, (camera) in self.world.get_component(Camera):

            # Get all states
            for ent, (position, renderable_model) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, RenderableModel)):

                if ent not in already_updated:

                    # try to get motion, has_weapon - returns None if not present
                    motion = self.world.try_component(ent, Motion)
                    has_weapon = self.world.try_component(ent, HasWeapon)
                    is_dead = self.world.try_component(ent, IsDestroyed)

                    if is_dead:
                        renderable_model.set_action('expire')
                        
                        # Direction must be down because only down direction is animated for the dead animation
                        # OBSOLETE - newly,all expire directions must be part of the model.
                        #position.set_direction('down')

                    elif motion and motion.has_moved:
                        
                        # If entity has moved, action is set to 'walk'
                        renderable_model.set_action('walk')
                    
                    elif has_weapon and has_weapon.weapon_in_use and has_weapon.has_attacked:

                        # If entity has weapon and the weapon has attacked, set action to proper value
                        # renderable_model.set_action(has_weapon.get_weapon_action_anim())
                        renderable_model.set_action(self.world.component_for_entity(has_weapon.get_weapon_in_use(), Weapon).action)

                        # Reset the attack - in case attack key is released animation of attack is no longer displayed
                        has_weapon.has_attacked = False

                    elif has_weapon and has_weapon.weapon_in_use:

                        # If entity has weapon but is not attacking, display idle weapon animation
                        #renderable_model.set_action(has_weapon.get_weapon_idle_anim())
                        renderable_model.set_action(self.world.component_for_entity(has_weapon.get_weapon_in_use(), Weapon).idle)

                    else:
                        # Has no weapon, is not moving,
                        renderable_model.set_action('idle')

                    # Remember that entity was updated
                    already_updated.add(ent)

