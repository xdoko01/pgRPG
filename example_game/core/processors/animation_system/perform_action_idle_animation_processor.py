__all__ = ['PerformActionIdleAnimationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.camera import Camera
from core.components.position import Position
from core.components.renderable_model import RenderableModel
from core.components.flag_do_attack import FlagDoAttack
from core.components.weapon_in_use import WeaponInUse
from core.components.flag_do_move import FlagDoMove
from core.components.is_destroyed import IsDestroyed


# Support functions
from ..functions import filter_only_visible_on_camera

# Logger init
logger = logging.getLogger(__name__)

class PerformActionIdleAnimationProcessor(Processor):
    ''' Sets action idle animation for RenderableModel entities that are armed,
    idled, and displayed.

    Involved components:
        -   RenderableModel
        -   WeaponInUse

    Related processors:
        -   PerformIdleAnimationProcessor
        -   PerformActionAnimationProcessor
        -   PerformMovementAnimationProcessor
        -   PerformFrameUpdateProcessor

    What if this processor is disabled?
        -   entities are not animated while being idle wearing weapon

    Where the processor should be planned?
        -   see README.md
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
                'command_system.perform_command_processor:PerformCommandProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

    def process(self, *args, **kwargs):
        ''' Get all components with renderable model that have weapon armed and at
        the same time did not move nor attack.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Iterate all cameras
        for _, (camera) in self.world.get_component(Camera):

            # Get all entities with Position, RenderableModel + are armed and did not move nor attack nor are dying
            for ent, (_, renderable_model, weapon_in_use) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components_exs(include=(Position, RenderableModel, WeaponInUse), exclude=(FlagDoAttack, FlagDoMove, IsDestroyed))):

                # Update to proper animation
                renderable_model.set_action(weapon_in_use.idle_action)
                logger.debug(f'({self.cycle}) - Entity {ent} idle action animation updated to "{weapon_in_use.idle_action}" action.')


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