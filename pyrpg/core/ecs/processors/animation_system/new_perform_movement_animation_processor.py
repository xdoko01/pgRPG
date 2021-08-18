__all__ = ['NewPerformMovementAnimationProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

from ..functions import filter_only_visible


# Logger init
logger = logging.getLogger(__name__)


class NewPerformMovementAnimationProcessor(esper.Processor):
    ''' Sets movement animation for RenderableModel entities that have moved and are displayed.

    Involved components:
        -   RenderableModel
        -   FlagDoMove

    Related processors:
        -   NewPerformIdleAnimationProcessor
        -   NewPerformFrameUpdateProcessor

    What if this processor is disabled?
        -   entities are not animated while moving

    Where the processor should be planned?
        -   after NewPerformCommandProcessor - due to movement commands generating FlagDoMove
        -   after NewPerformIdleAnimationProcessor - so that entity switches to idle when not walking
        -   before NewPerformFrameUpdateProcessor - so that walking is animated
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['NewPerformCommandProcessor', 'NewPerformIdleAnimationProcessor']

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Get all components with renderable model that have moved and update their action and frame
        '''
        self.cycle += 1

        # Iterate all cameras
        for _, (camera) in self.world.get_component(components.Camera):

            # Get all entities with Position, RenderableModel and FlagDoMove
            for ent, (_, renderable_model, _) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.RenderableModel, components.NewFlagDoMove)):

                # Update to proper animation
                renderable_model.set_action('walk')
                logger.debug(f'({self.cycle}) - Entity {ent} action animation updated to "walk" action.')


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