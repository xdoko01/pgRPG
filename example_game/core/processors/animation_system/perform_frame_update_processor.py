__all__ = ['PerformFrameUpdateProcessor']

import logging
import pygame

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.camera import Camera
from core.components.position import Position
from core.components.renderable_model import RenderableModel
from core.components.flag_is_animation_action_frame import FlagIsAnimationActionFrame

# Support functions
from ..functions import filter_only_visible_on_camera

# Logger init
logger = logging.getLogger(__name__)

class PerformFrameUpdateProcessor(Processor):
    ''' Shifts animation to the next frame on all visible entities.

    Involved components:
        -   RenderableModel

    Related processors:
        -   PerformIdleAnimationProcessor
        -   PerformMovementAnimationProcessor

    What if this processor is disabled?
        -   animation is not happening, frames are not shifted

    Where the processor should be planned?
        -   after PerformCommandProcessor - due to movement commands generating FlagDoMove
        -   after PerformMovementAnimationProcessor
        -   after PerformIdleAnimationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Get all components with renderable model and update their animation by one frame.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Remember updated entities - to prevent several updates on single entity in case same entity is on more cameras
        already_updated = set()

        # Call pygame.time.get_ticks() once for all entities — avoids repeated Python-C crossings
        current_time = pygame.time.get_ticks()

        # Iterate all cameras
        for cam, (camera) in self.world.get_component(Camera):

            # Get all entities with Position, RenderableModel
            for ent, (position, renderable_model) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, RenderableModel)):

                # If already updated skip
                if ent in already_updated:
                    continue

                # Update to the next proper animation frame
                renderable_model.update_frame(position.dir_name, current_time)

                # NOTE: debug logging commented out — f-string formatting on every entity every frame
                # degrades performance significantly even when DEBUG level is not active.
                # logger.debug(f'({self.cycle}) - Entity {ent} animation frame updated to {renderable_model.last_frame} for direction {position.dir_name}.')

                # Set Flag in case that the new frame is action frame (and hence some projectile might be generated)
                if renderable_model.is_action_frame:
                    self.world.add_component(ent, FlagIsAnimationActionFrame())

                    # NOTE: debug logging commented out — same performance reason as above.
                    # logger.debug(f'({self.cycle}) - Entity {ent} animation frame {renderable_model.last_frame} is action frame.')

                # Remember that entity was updated - not to update it again on other camera
                already_updated.add(ent)


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