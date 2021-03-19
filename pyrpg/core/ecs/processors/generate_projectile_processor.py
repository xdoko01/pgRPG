__all__ = ['GenerateProjectileProcessor', 'PrepareProjectileProcessor', 'CreateEntityOnPositionProcessor']

import pygame
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

class PrepareProjectileProcessor(esper.Processor):

    def __init__(self):
        super().__init__()

    def process(self, *args, **kwargs):

        # Get entities capable of producing projectiles - HasWeapon, on the last attack frame RenderableModel
        for ent, (has_weapon, renderable_model, position) in self.world.get_components(components.HasWeapon, components.RenderableModel, components.Position):
            
            # Check if Model is in the action status and last frame of the action is happening and there is some weapon actually in use
            if has_weapon.get_weapon_in_use() and has_weapon.get_generator_in_use() and renderable_model.action == self.world.component_for_entity(has_weapon.get_weapon_in_use(), components.Weapon).action and renderable_model.is_action_frame:

                # Collidable is optional component - entities who are not collidable can generate projectiles
                collidable = self.world.try_component(ent, (components.Collidable))

                # calculate position for the new projectile
                (ent_col_x, ent_col_y) = (collidable.x, collidable.y) if collidable else (0, 0)
                (pos_x, pos_y, pos_map) = (int(position.x + (position.direction[0] * (ent_col_x))), int(position.y + (position.direction[1] * (ent_col_y))), position.map)

                # Create component FlagCreateFromFactory and add it to Generator entity
                self.world.add_component(has_weapon.get_generator_in_use(),
                                        components.FlagCreateFromFactory(
                                            position={'x' : pos_x, 'y' : pos_y, 'dir' : position.dir_name, 'map' : pos_map},
                                            adjust_col=True,
                                            parent=ent,
                                            register=False,
                                            id_suffix='projectile')
                                        )

                print(f'Component FlagCreateFromFactory created.')


class CreateEntityOnPositionProcessor(esper.Processor):

    __slots__ = ['create_entity_fnc']

    def __init__(self, create_entity_fnc=None):
        super().__init__()

        self.create_entity_fnc = create_entity_fnc

    def process(self, *args, **kwargs):

        for ent, (factory, flag_create_from_factory) in self.world.get_components(components.Factory, components.FlagCreateFromFactory):

            # Prepare ID for the new entity
            id_str = f'ORIG_ID:{factory.prescription.get("id", "")}:SUFF_ID:{flag_create_from_factory.id_suffix}:PARENT_ENT:{flag_create_from_factory.parent}:FACT_ENT:{ent}:TS:{pygame.time.get_ticks()}'

            new_entity = self.create_entity_fnc(
                factory.prescription,

                # New ID for new Entity
                entity_id=id_str,

                # Do not register in engine global variable alias_to_entity - not needed
                register=False
            )

            # If position is passed in FlagCreateFromFactory, add the Position component to the new entity
            if flag_create_from_factory.position:

                self.world.add_component(new_entity, components.Position(**flag_create_from_factory.position))

                # If adjustment of the position needs to take into account collition zone of the newly generated entity
                if flag_create_from_factory.adjust_col:

                    # Try to adjust the position component of the new entity further. Might happen that new entity does
                    # not have collision component
                    try:
                        new_entity_collidable = self.world.component_for_entity(new_entity, components.Collidable)
                        new_entity_position = self.world.component_for_entity(new_entity, components.Position)

                        new_entity_position.x += int(new_entity_position.direction[0] * (new_entity_collidable.x + 1))
                        new_entity_position.y += int(new_entity_position.direction[1] * (new_entity_collidable.y + 1))

                    except KeyError:
                        return None

            # Remove the component flag_create_from_factory as entity was successfully generated
            self.world.remove_component(ent, components.FlagCreateFromFactory)

            # Count new entity to the total number of entities created by the Factory
            factory.current_units += 1

            # If there are no more entities to produce, just remove the flag FlagCreateFromFactory and end
            if factory.max_units is not None and (factory.max_units <= factory.current_units):
                self.world.add_component(ent, components.FlagFactoryDepleted())
                print(f'Cannot generate further entities - factory depleted')

            # Print information about successful generation
            print(f'Entity {new_entity} created. No of generated entities: {factory.current_units}. No of remaining units {factory.max_units - factory.current_units}')


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
            #if renderable_model.action == has_weapon.get_weapon_action_anim() and renderable_model.is_action_frame:
            if renderable_model.action == self.world.component_for_entity(has_weapon.get_weapon_in_use(), components.Weapon).action and renderable_model.is_action_frame:

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
                if len(factory.list_of_entities) < weapon.max_projectiles:


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
                    #self.world.add_component(new_entity, components.Container(contained_in=has_weapon))
                    self.world.add_component(new_entity, components.Container(contained_in=factory))

                    factory.list_of_entities.add(new_entity)
                    print(f'Projectile {new_entity} created. List of projectiles {factory.list_of_entities}')
