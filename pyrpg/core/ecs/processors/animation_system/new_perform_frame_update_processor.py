__all__ = ['NewPerformFrameUpdateProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

from ..functions import filter_only_visible


# Logger init
logger = logging.getLogger(__name__)


class NewPerformFrameUpdateProcessor(esper.Processor):
    ''' Shifts animation to the next frame on all visible entities.

    Involved components:
        -   RenderableModel

    Related processors:
        -   NewPerformIdleAnimationProcessor
        -   NewPerformMovementAnimationProcessor

    What if this processor is disabled?
        -   animation is not happening, frames are not shifted

    Where the processor should be planned?
        -   after NewPerformCommandProcessor - due to movement commands generating FlagDoMove
        -   after NewPerformMovementAnimationProcessor
        -   after NewPerformIdleAnimationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['NewPerformIdleAnimationProcessor', 'NewPerformMovementAnimationProcessor', 'NewPerformActionAnimationProcessor']

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Get all components with renderable model and update their animation by one frame.
        '''
        self.cycle += 1

        # Remember updated entities - to prevent several updates on single entity in case same entity is on more cameras
        already_updated = set()

        # Iterate all cameras
        for cam, (camera) in self.world.get_component(components.Camera):

            # Get all entities with Position, RenderableModel and FlagDoMove
            for ent, (position, renderable_model) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.RenderableModel)):

                # If already updated skip
                if ent in already_updated:
                    continue

                # Update to the next proper animation frame
                renderable_model.update_frame(position.dir_name)
                logger.debug(f'({self.cycle}) - Entity {ent} animation frame updated to {renderable_model.last_frame}.')

                # Set Flag in case that the new frame is action frame (and hence some projectile might be generated)
                if renderable_model.is_action_frame:
                    self.world.add_component(ent, components.NewFlagIsAnimationActionFrame())
                    logger.debug(f'({self.cycle}) - Entity {ent} animation frame {renderable_model.last_frame} is action frame.')

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