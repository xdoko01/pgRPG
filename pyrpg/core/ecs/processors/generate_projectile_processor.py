__all__ = ['GenerateProjectileProcessor']

import pygame
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

class GenerateProjectileProcessor(esper.Processor):
    ''' Generate projectiles
        
        - planned before all collision processors
        - planned after command processor - Attack command
    '''

    __slots__ = ['create_entity_fnc']

    def __init__(self, create_entity_fnc=None):
        super().__init__()

        self.create_entity_fnc = create_entity_fnc

    def process(self, *args, **kwargs):
        ''' TODO - is there any variable from the global world that we want to use here?
        '''

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

                # Check if more projectiles can be created and continue, if yes
                if len(has_weapon.projectiles) < weapon.max_projectiles:


                    # Original function from Factory component is used, newly rewritten to processor
                    #new_projectile = factory.create_entity(owner=ent, pos=(pos_x, pos_y, position.dir_name, pos_map), container=has_weapon, reg_at_engine=False)

                    id_str = f'{factory.prescription.get("id", "")}OWN{ent}ORD{factory.units}TS{pygame.time.get_ticks()}'
                    factory.prescription.update({"id": id_str})

                    new_entity = self.create_entity_fnc(
                            factory.prescription,

                            # Do not register in engine global variable alias_to_entity - not needed
                            register=False
                        )

                    # Add position component pos = (pos_x, pos_y, pos_dir, pos_map)
                    # calculate position for the new projectile
                    (ent_col_x, ent_col_y) = (collidable.x, collidable.y) if collidable else (0, 0)
                    (pos_x, pos_y, pos_map) = (int(position.x + (position.direction[0] * (ent_col_x + 30))), int(position.y + (position.direction[1] * (ent_col_y + 30))), position.map)
                    self.world.add_component(new_entity, components.Position(x=pos_x, y=pos_y, dir=position.dir_name, map=pos_map))

                    # Add container component
                    self.world.add_component(new_entity, components.Container(contained_in=has_weapon))

                    has_weapon.projectiles.add(new_entity)
                    print(f'Projectile {new_entity} created. List of projectiles {has_weapon.projectiles}')
