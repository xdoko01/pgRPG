from  pyrpg.functions import translate # for translation of entity alias to entity id

#####################################################################
## Package core.ecs.components
#####################################################################


########################################################
### Package init commands
########################################################

#if not pygame.get_init(): pygame.init()
#if not pygame.freetype.get_init(): pygame.freetype.init() 

########################################################
### Module globals
########################################################

# Available components - if component is not defined here (Flags typically), it will not be
# able to add it to the entity from definition. Such components (Flags) are for the internal
# use by the system.
ALL_COMPONENTS = ['Debug', 'Labeled', 'Controllable', 'Renderable', 'Position',\
    'Collidable', 'Camera', 'Brain', 'CanTalk', 'Pickable', 'HasInventory',\
    'Teleport', 'Teleportable', 'Motion', 'RenderableModel', 'HasScore', 'ScorableOnDamage',\
    'ScorableOnDestroy', 'Wearable',\
    'CanWear', \
    'Weapon', 'AmmoPack', 'HasWeapon', 'Damageable', 'Damaging', 'Temporary',\
    'Factory', 'LinearMotion', 'DeleteOnCollision',\
    'IsDead',\
    'NewControllable', 'NewMovable', 'NewCollidable', 'NewFlagHasCollided',\
    'NewHasInventory', 'NewFlagIsAboutToPickEntity', 'NewFlagWasPickedBy', 'NewFlagHasPicked',\
    'NewFlagIsAboutToBeTeleportedBy', 'NewTeleportable',\
    'NewFlagIsAboutToArmWeapon', 'NewFlagHasArmedWeapon', 'NewFlagWasArmedAsWeaponBy', 'NewWeaponInUse', 'NewHasWeapon',\
    'NewFlagIsAboutToArmAmmo', 'NewFlagHasArmedAmmo', 'NewFlagWasArmedAsAmmoBy',\
    'NewFlagIsAnimationActionFrame',\
    'NewFlagDoAttack',\
    'NewRenderDataFromParent',\
    'NewDebug',\
    'NewFlagCreateFromFactory', 'NewFactory'
    ]

########################################################
### Module functions
########################################################

def create_component(world, alias_dict, entity: int, comp_class: str, comp_params: dict):
    ''' Add a new component to the given entity in given world.

    Parameters:
        :param world: ECS world in which the component should be created.
        :type world: esper.World()

        :param alias_dict: Reference to dictionary holding information about translation from entity alias name to entity id.
        :type alias_dict: dict

        :param entity: Entity to which component should be assigned.
        :type entity: int

        :param comp_class: Name of the component class.
        :type comp_class: str

        :param comp_params: Parameters for initiation of component instance.
        :type comp_params: dict

        :return: Returns 0 if component instance was successfully created and assigned.

        :raises: ValueException, if component instance cannot be created

    Called from:
        engine module -> create_entity function
    '''

    # Get the component class - check if such class exists and is allowed
    try:
        # Check if component exists
        assert comp_class in ALL_COMPONENTS, f'Trying to assign unknown component {comp_class} to entity {entity}.'

        comp_name = globals()[comp_class]

    except (AssertionError, KeyError):
        print(f'Trying to assign unknown component {comp_class} to entity {entity}.')
        raise ValueError

    # Try to create instance of the component
    try:
        # Use alias_dict to seach the values and translate them from string to entity id integers here!!!
        # Every value is searched in alias_dict keys and if found, value is substituted with entity id 
        # integer from alias_dict values.

        # New dictionary containing aliases substituted with integer entity IDs
        comp_params_substituted = translate(alias_dict, comp_params)

        # Create the instance of the component
        comp_inst = comp_name(**comp_params_substituted)

    except ValueError:
        print(f'Incorrect parameters while creating component {comp_class} for entity {entity}')
        raise ValueError

    # Add new component to the world
    world.add_component(entity, comp_inst)

    # Return entity and the new component
    return (entity, comp_inst)

# Load all component modules

from .ammo_pack import *
from .brain import *
from .camera import *
from .can_talk import *
from .can_wear import *
from .collidable import *
from .controllable import *
from .damageable import *
from .damaging import *
from .debug import *
from .delete_on_collision import *
from .factory import *
from .has_inventory import *
from .has_weapon import *
from .labeled import *
from .linear_motion import *
from .motion import *
from .pickable import *
from .position import *
from .renderable_model import *
from .renderable import *
from .teleport import *
from .teleportable import *
from .temporary import *
from .weapon import *
from .wearable import *
from .has_score import *
from .scorable_on_damage import *
from .scorable_on_destroy import *
from .is_destroyed import *

from .flag_create_from_factory import *
from .flag_factory_depleted import *
from .flag_ammo_pack_armed import *
from .flag_add_score import *
from .flag_add_damage import *
from .flag_no_health import *

# Movement system
from .new_controllable import *
from .new_movable import *
from .new_flag_do_move import *

# Collision system
from .new_collidable import *
from .new_flag_has_collided import *

# PickUp system
from .new_has_inventory import *
from .new_flag_is_about_to_pick_entity import *
from .new_flag_was_picked_by import *
from .new_flag_has_picked import *

# Teleport system
from .new_flag_is_about_to_be_teleported_by import *
from .new_flag_was_teleported_by import *
from .new_flag_has_teleported import *
from .new_teleportable import *

# Arm Weapon system
from .new_flag_is_about_to_arm_weapon import *
from .new_flag_was_armed_as_weapon_by import *
from .new_flag_has_armed_weapon import *
from .new_weapon_in_use import *
from .new_has_weapon import *

# Arm Ammo system
from .new_flag_is_about_to_arm_ammo import *
from .new_flag_was_armed_as_ammo_by import *
from .new_flag_has_armed_ammo import *

# Animation system
from .new_flag_is_animation_action_frame import *

# Attack system
from .new_flag_do_attack import *

# Factory system
from .new_flag_create_from_factory import *
from .new_factory import *

# Render System
from .new_render_data_from_parent import *
from .new_debug import *

# Not used
#from .container import *
#from .state import *


# Make only following modules visible in the  package
__all__ = [
    'AmmoPack',
    'Brain',
    'Camera',
    'CanTalk',
    'CanWear',
    'Collidable',
    'Controllable',
    'Damageable',
    'Damaging',
    'Debug',
    'DeleteOnCollision',
    'Factory',
    'HasInventory',
    'HasWeapon',
    'Labeled',
    'LinearMotion',
    'Motion',
    'Pickable',
    'Position',
    'RenderableModel',
    'Renderable',
    'Teleport',
    'Teleportable',
    'Temporary',
    'Weapon',
    'Wearable',
    'HasScore',
    'ScorableOnDestroy',
    'ScorableOnDamage',
    'IsDestroyed',

    # Flags are temorary components add/removed during one game cycle
    'FlagCreateFromFactory',
    'FlagFactoryDepleted',
    'FlagAmmoPackArmed',
    'FlagAddScore',
    'FlagAddDamage',
    'FlagNoHealth',

    # Components used for the new solution
    'NewControllable',
    'NewMovable',
    'NewFlagDoMove',

    'NewCollidable',
    'NewFlagHasCollided',

    'NewHasInventory',
    'NewFlagIsAboutToPickEntity',
    'NewFlagWasPickedBy',
    'NewFlagHasPicked',
    'NewIsPickedBy',

    'NewFlagIsAboutToBeTeleportedBy',
    'NewFlagWasTeleportedBy',
    'NewFlagHasTeleported',
    'NewTeleportable',

    'NewFlagIsAboutToArmWeapon',
    'NewFlagWasArmedAsWeaponBy',
    'NewFlagHasArmedWeapon',
    'NewWeaponInUse',
    'NewHasWeapon',

    'NewFlagIsAboutToArmAmmo',
    'NewFlagWasArmedAsAmmoBy',
    'NewFlagHasArmedAmmo',

    'NewFlagIsAnimationActionFrame',

    'NewFlagDoAttack',

    'NewRenderDataFromParent',
    'NewDebug',

    'NewFlagCreateFromFactory',
    'NewFactory'

    # Not used
    #'State',
    #'Container',

    ]
