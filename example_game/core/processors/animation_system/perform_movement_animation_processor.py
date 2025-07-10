__all__ = ['PerformMovementAnimationProcessor']

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

# Support functions
from ..functions import filter_only_visible_on_camera

# Logger init
logger = logging.getLogger(__name__)

class PerformMovementAnimationProcessor(Processor):
    ''' Sets movement animation for RenderableModel entities that have moved and are displayed.

    Involved components:
        -   RenderableModel
        -   FlagDoMove

    Related processors:
        -   PerformIdleAnimationProcessor
        -   PerformFrameUpdateProcessor

    What if this processor is disabled?
        -   entities are not animated while moving

    Where the processor should be planned?
        -   after PerformCommandProcessor - due to movement commands generating FlagDoMove
        -   after PerformIdleAnimationProcessor - so that entity switches to idle when not walking
        -   before PerformFrameUpdateProcessor - so that walking is animated
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
        ''' Get all components with renderable model that have moved and update their action and frame
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Iterate all cameras
        for _, (camera) in self.world.get_component(Camera):

            # Get all entities with Position, RenderableModel and FlagDoMove
            for ent, (_, renderable_model, _) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components_ex(Position, RenderableModel, FlagDoMove, exclude=FlagDoAttack)):

                # Update to proper animation
                renderable_model.set_action('move')
                logger.debug(f'({self.cycle}) - Entity {ent} action animation updated to "move" action.')

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