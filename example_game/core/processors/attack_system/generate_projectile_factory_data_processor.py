__all__ = ['GenerateProjectileFactoryDataProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.position import Position
from core.components.flag_is_animation_action_frame import FlagIsAnimationActionFrame
from core.components.has_weapon import HasWeapon
from core.components.weapon_in_use import WeaponInUse
from core.components.flag_create_from_factory import FlagCreateFromFactory
from core.components.collidable import Collidable

# Logger init
logger = logging.getLogger(__name__)

class GenerateProjectileFactoryDataProcessor(Processor):
    ''' Detects attacking entities that are about to generate
    a weapon attack (projectile) and prepare information necessary
    for successful generation of new entity from the weapon generator
    factory (AmmoPack).

    Involved components:
        -   Position
        -   FlagIsAnimationActionFrame - indicating that in this cycle projectile needs to be created
        -   HasWeapon - for getting the Factory(AmmoPack) from which the projectile will be generated
        -   WeaponInUse - to determine which weapon to search for in HasWeapon component
        -   FlagCreateFromFactory

    Related processors:
        -   PerformFrameUpdateProcessor - processor that generates FlagIsAnimationActionFrame

    What if this processor is disabled?
        -   projectiles are not generated and hence weapons are not attacking

    Where the processor should be planned?
        -   after PerformFrameUpdateProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.animation_system.perform_frame_update_processor:PerformFrameUpdateProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Get all generator components that should generate the projectile
        and add FlagCreateFromFactory to them containing all the data necessary
        for correct generation.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get entities that in this cycle have all what it needs to generate projectile
        # Return also Collidable component if the entity has it, otherwise return None
        for parent, (position, is_action_frame, has_weapon, weapon_in_use, collidable) in self.world.get_components_opt(Position, FlagIsAnimationActionFrame, HasWeapon, WeaponInUse, optional=Collidable):

            # Calculate position for the new projectile based on position of the parent and collision zones of the parent.
            # The aim is to avoid collision zone with the parent
            (parent_col_x, parent_col_y, parent_col_dx, parent_col_dy) = (collidable.x, collidable.y, collidable.dx, collidable.dy) if collidable else (0, 0, 0, 0)
            (projectile_pos_x, projectile_pos_y) = (int(position.x + (position.direction[0] * (parent_col_x)) + parent_col_dx), int(position.y + (position.direction[1] * (parent_col_y)) + parent_col_dy))
            
            # Create component FlagCreateFromFactory and add it to Generator entity
            self.world.add_component(has_weapon.weapons[weapon_in_use.type]["generator"],
                                    FlagCreateFromFactory(

                                        adjust_position={
                                                # Originaly, the centre of parent entity
                                                #"x" : int(position.x),
                                                #"y" : int(position.y),
                                                #"dir_name" : position.dir_name,
                                                #"map" : position.map

                                                "x" : projectile_pos_x,
                                                "y" : projectile_pos_y,
                                                "dir_name" : position.dir_name,
                                                "map" : position.map
                                        },

                                        adjust_collision={
                                                "ignore_collision_with" : [parent],
                                                # Here we can use data from the weapon/character to modify the collision zone for the projectile. For example if character is skilled,
                                                # the projectile collision zone is greater than normal in order to hit more enemies in one go.
                                                "x_fnc" : [lambda x: x, lambda x: x*1.5],
                                                "y_fnc" : [lambda x: x, lambda x: x*1.5]
                                        },
                                        adjust_movement={
                                                # Here we can use data from weapon/character to modify the movement characteristics
                                                "velocity_fnc" : [lambda x: x],
                                                "accelerate_fnc" : [lambda x: x]
                                        },
                                        adjust_damaging={
                                                "parent": parent,
                                                "damage_fnc": [lambda x: x]
                                        },
                                        id_suffix='projectile',
                                        register=False
                                        )
                                    )

            logger.debug(f'({self.cycle}) - Entity {parent}, AmmoPack {has_weapon.weapons[weapon_in_use.type]["generator"]} is about to generate projectile.')

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
