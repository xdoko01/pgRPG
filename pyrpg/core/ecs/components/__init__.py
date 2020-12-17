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

# Available components - if component is not defined here, it will not be 
# assigned to the entity
ALL_COMPONENTS = ['Debug', 'Labeled', 'Controllable', 'Renderable', 'Position',\
    'Collidable', 'Camera', 'Brain', 'CanTalk', 'Pickable', 'HasInventory',\
    'Teleport', 'Teleportable', 'Motion', 'RenderableModel', 'State', 'Wearable',\
    'CanWear', \
    'Weapon', 'HasWeapon', 'Damageable', 'Damaging', 'Temporary', 'Container',\
    'Factory', 'LinearMotion', 'DeleteOnCollision',\
    'IsDead']

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

from .brain import *
from .camera import *
from .can_talk import *
from .can_wear import *
from .collidable import *
from .container import *
from .controllable import *
from .damageable import *
from .damaging import *
from .debug import *
from .delete_on_collision import *
from .factory import *
from .has_inventory import *
from .has_weapon import *
from .is_dead import *
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

# Not used
#from .state import *


# Make only following modules visible in the  package
__all__ = [
    'Brain',
    'Camera',
    'CanTalk',
    'CanWear',
    'Collidable',
    'Container',
    'Controllable',
    'Damageable',
    'Damaging',
    'Debug',
    'DeleteOnCollision',
    'Factory',
    'HasInventory',
    'HasWeapon',
    'IsDead',
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
    'Wearable'

    # Not used
    #'State',

    ]
