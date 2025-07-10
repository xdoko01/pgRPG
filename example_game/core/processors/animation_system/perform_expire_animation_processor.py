__all__ = ['PerformExpireAnimationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.camera import Camera
from core.components.position import Position
from core.components.renderable_model import RenderableModel
from core.components.is_destroyed import IsDestroyed

# Support functions
from ..functions import filter_only_visible_on_camera

# Logger init
logger = logging.getLogger(__name__)

class PerformExpireAnimationProcessor(Processor):
    ''' Sets expire animation for all RenderableModel entities.

    Involved components:
        -   RenderableModel
        -   IsDestroyed

    Related processors:
        -   PerformMovementAnimationProcessor
        -   PerformActionAnimationProcessor
        -   PerformActionIdleAnimationProcessor
        -   PerformIdleAnimationProcessor

    What if this processor is disabled?
        -   entities are not put into expire animation

    Where the processor should be planned?
        -   after PerformCommandProcessor
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
        ''' Get all entities with renderable model that has not perform any action and update their action to idle.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Iterate all cameras
        for _, (camera) in self.world.get_component(Camera):

            # Search for entities that contain Position + RenderableModel and at the same time do not have FlagDoMove and FlagDoAttack component
            for ent, (_, renderable_model, is_destroyed) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, RenderableModel, IsDestroyed)):

                # Update to proper animation - if not specified in IsDestroyed it is 'expire'
                renderable_model.set_action(is_destroyed.action)
                logger.debug(f'({self.cycle}) - Entity {ent} action animation updated to "{is_destroyed.action}" action.')

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