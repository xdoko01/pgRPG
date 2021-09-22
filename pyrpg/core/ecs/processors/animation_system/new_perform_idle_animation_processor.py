__all__ = ['NewPerformIdleAnimationProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

from ..functions import filter_only_visible


# Logger init
logger = logging.getLogger(__name__)


class NewPerformIdleAnimationProcessor(esper.Processor):
    ''' Sets movement animation for all RenderableModel entities. This is later overwritten by other 
    Animation processors.

    Involved components:
        -   RenderableModel

    Related processors:
        -   NewPerformMovementAnimationProcessor

    What if this processor is disabled?
        -   entities are not put into idle animation after other action

    Where the processor should be planned?
        -   after NewPerformCommandProcessor - due to movement commands generating FlagDoMove
        -   before NewPerformMovementAnimationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['NewPerformCommandProcessor']

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Get all entities with renderable model that has not perform any action and update their action to idle.
        '''
        self.cycle += 1

        # Iterate all cameras
        for _, (camera) in self.world.get_component(components.Camera):

            # Search for entities that contain Position + RenderableModel and at the same time do not have NewFlagDoMove and NewFlagDoAttack component
            for ent, (_, renderable_model) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components_exs(include=(components.Position, components.RenderableModel), exclude=(components.NewFlagDoMove, components.NewFlagDoAttack, components.NewWeaponInUse))):

                # Update to proper animation
                renderable_model.set_action('idle')
                logger.debug(f'({self.cycle}) - Entity {ent} action animation updated to "idle" action.')

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