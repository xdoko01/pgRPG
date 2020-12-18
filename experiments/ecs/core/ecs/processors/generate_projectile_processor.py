__all__ = ['GenerateProjectileProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components

class GenerateProjectileProcessor(esper.Processor):
    ''' Generate projectiles

        - planned before all collision processors
        - planned after command processor - Attack command
    '''

    def __init__(self):
        super().__init__()

    def process(self, *args, **kwargs):
        ''' TODO - is there any variable from the global world that we want to use here?
        '''
        print('##########################################')

        # Get entities capable of producing projectiles - HasWeapon, on the last attack frame RenderableModel
        for ent, (has_weapon, renderable_model, position) in self.world.get_components(components.HasWeapon, components.RenderableModel, components.Position):

            # Check if Model is in the action status and last frame of the action is happening
            if renderable_model.action == has_weapon.get_weapon_action_anim() and renderable_model.is_action_frame:

                # Collidable is optional component - entities who are not collidable can generate projectiles
                collidable = self.world.try_component(ent, (components.Collidable))

                # Create an projectile - collision component is passed in order that the new projectile will not collide with generator entity
                #has_weapon.create_projectile(ent, position, collidable)

                # If no weapon ot generator do not create projectile
                try:
                    # Get weapon component from the weapon
                    weapon = self.world.component_for_entity(has_weapon.get_weapon_in_use(), components.Weapon)
                    factory = self.world.component_for_entity(has_weapon.get_generator_in_use(), components.Factory)
                except KeyError:
                    return None

                print('##########################################')
                # Check if more projectiles can be created and continue, if yes
                if len(has_weapon.projectiles) < weapon.max_projectiles:

                    # calculate position for the new projectile
                    (ent_col_x, ent_col_y) = (collidable.x, collidable.y) if collidable else (0, 0)
                    (pos_x, pos_y, pos_map) = (int(position.x + (position.direction[0] * (ent_col_x + 30))), int(position.y + (position.direction[1] * (ent_col_y + 30))), position.map)

                    print(f'################################################Direction of entity {position.dir_name}')
                    new_projectile = factory.create_entity(owner=ent, pos=(pos_x, pos_y, position.dir_name, pos_map), container=has_weapon, reg_at_engine=False)

                    has_weapon.projectiles.add(new_projectile)
                    print(f'###Projectile {new_projectile} created. List of projectiles {has_weapon.projectiles}')
