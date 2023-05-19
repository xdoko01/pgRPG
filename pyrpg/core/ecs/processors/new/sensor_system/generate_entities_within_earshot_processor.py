__all__ = [
    'GenerateEntitiesWithinEarshotProcessor',
    'GenerateEntitiesWithinEarshotFullProcessor'
]

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.can_hear import CanHear
from pyrpg.core.ecs.components.new.camera import Camera
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove

from ..functions import filter_only_within_earshot_of_ent
from ..functions import filter_only_visible_on_camera

# Logger init
logger = logging.getLogger(__name__)

class GenerateEntitiesWithinEarshotProcessor(Processor):
    ''' Detects entities that are within earshot and stores them on CanHear
    component in a form of a list.

    Involved components:
        -   CanHear
        -   Position
        -   FlagDoMove

    Related processors:

    What if this processor is disabled?
        -   No entities are being heard

    Where the processor should be planned?
        -   after PerformCommandProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
    ]

    def __init__(self, FNC_GET_MAP, *args, **kwargs):
        ''' Init the processor.

        Parameters:
            :param FNC_GET_MAP: Reference to the dictionary of maps.
            :param FNC_GET_MAP: reference
        '''
        super().__init__(*args, **kwargs)
        self.fnc_get_map = FNC_GET_MAP

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are within earshot.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # For all who has CanHear component and are displayed on any of the cameras
        for _, (camera) in self.world.get_component(Camera):

            for ent, (ent_pos, ent_can_hear) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, CanHear)):

                # Lets assume that entity ent does not see any other entity at the beginning
                ent_can_hear.ent_within_earshot = set()

                # Get map that is on the object in camera's focus
                map = self.fnc_get_map(ent_pos.map)

                # 1/ filter all entities with pos component in radius and angle (and optionally displayed on the camera)
                for oth_ent, (oth_pos, _) in filter(lambda x: filter_only_within_earshot_of_ent(ent_pos, ent_can_hear, x), self.world.get_components(Position, FlagDoMove)):

                    logger.debug(f'({self.cycle}) - Checking if Entity {ent} hears entity {oth_ent} with pos comp: {oth_pos}.')

                    # 2/ for every such entity check if there is no wall between
                    if not map.check_collision_in_line((ent_pos.x, ent_pos.y), (oth_pos.x, oth_pos.y)):

                        # 3/ write to CanSee component
                        ent_can_hear.ent_within_earshot.add(oth_ent)
                        logger.debug(f'({self.cycle}) - Entity {ent} has seen entity {oth_ent}.')


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

class GenerateEntitiesWithinEarshotFullProcessor(Processor):
    ''' Detects entities that are within earshot and stores them on CanSee
    component in a form of a list.

    Involved components:
        -   CanHear
        -   Position
        -   FlagDoMove

    Related processors:

    What if this processor is disabled?
        -   No entities are being seen

    Where the processor should be planned?
        -   after PerformCommandProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
    ]

    def __init__(self, FNC_GET_MAP, *args, **kwargs):
        ''' Init the processor.

        Parameters:
            :param FNC_GET_MAP: Reference to the dictionary of maps.
            :param FNC_GET_MAP: reference
        '''
        super().__init__(*args, **kwargs)
        self.fnc_get_map = FNC_GET_MAP

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''  Detects entities that are in sight.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # For all who has CanHear component - also for those that are not on camera
        for ent, (ent_pos, ent_can_hear) in self.world.get_components(Position, CanHear):

            # Lets assume that entity ent does not hear any other entity at the beginning
            ent_can_hear.ent_within_earshot = set()

            # Get map that is on the object in camera's focus
            map = self.fnc_get_map(ent_pos.map)

            # 1/ filter all entities with pos component in radius and angle (and optionally displayed on the camera)
            for oth_ent, (oth_pos, _) in filter(lambda x: filter_only_within_earshot_of_ent(ent_pos, ent_can_hear, x), self.world.get_components(Position, FlagDoMove)):

                logger.debug(f'({self.cycle}) - Checking if Entity {ent} hears entity {oth_ent} with pos comp: {oth_pos}.')

                # 2/ for every such entity check if there is no wall between
                if not map.check_collision_in_line((ent_pos.x, ent_pos.y), (oth_pos.x, oth_pos.y)):

                    # 3/ write to CanSee component
                    logger.debug(f'({self.cycle}) - Entity {ent} has heard entity {oth_ent}.')
                    ent_can_hear.ent_witin_earshot.add(oth_ent)

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
