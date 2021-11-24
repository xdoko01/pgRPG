__all__ = ['NewGenerateProjectileFactoryDataProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)

class NewGenerateProjectileFactoryDataProcessor(esper.Processor):
    ''' Detects attacking entities that are about to generate
    a weapon attack (projectile) and prepare information necessary
    for successful generation of new entity from the weapon generator
    factory (AmmoPack).

    Involved components:
        -   Position
        -   NewFlagIsAnimationActionFrame - indicating that in this cycle projectile needs to be created
        -   NewHasWeapon - for getting the Factory(AmmoPack) from which the projectile will be generated
        -   NewWeaponInUse - to determine which weapon to search for in NewHasWeapon component

    Related processors:
        -   NewPerformFrameUpdateProcessor - processor that generates NewFlagIsAnimationActionFrame

    What if this processor is disabled?
        -   projectiles are not generated and hence weapons are not attacking

    Where the processor should be planned?
        -   after NewPerformFrameUpdateProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.animation_system.new_perform_frame_update_processor', 'NewPerformFrameUpdateProcessor')
        ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Get all generator components that should generate the projectile
        and add NewFlagCreateFromFactory to them containing all the data necessary
        for correct generation.
        '''
        self.cycle += 1

        # Get entities that in this cycle have all what it needs to generate projectile
        for _, (position, is_action_frame, has_weapon, weapon_in_use) in self.world.get_components(components.Position, components.NewFlagIsAnimationActionFrame, components.NewHasWeapon, components.NewWeaponInUse):

            # calculate position for the new projectile
            ##(ent_col_x, ent_col_y) = (collidable.x, collidable.y) if collidable else (0, 0)
            ##(pos_x, pos_y, pos_map) = (int(position.x + (position.direction[0] * (ent_col_x))), int(position.y + (position.direction[1] * (ent_col_y))), position.map)

            # Create component NewFlagCreateFromFactory and add it to Generator entity
            self.world.add_component(has_weapon.weapons[weapon_in_use.type]["generator"],
                                    components.NewFlagCreateFromFactory(
                                        position=(int(position.x), int(position.y), position.dir_name, position.map),
                                        id_suffix='projectile'
                                        )
                                    )

            logger.debug(f'({self.cycle}) - Entity {_}, AmmoPack {has_weapon.weapons[weapon_in_use.type]["generator"]} is about to generate projectile.')

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
