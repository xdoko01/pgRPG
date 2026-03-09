__all__ = ['PerformIdleAnimationProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

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

class PerformIdleAnimationProcessor(Processor):
    ''' Sets movement animation for all RenderableModel entities. This is later overwritten by other 
    Animation processors.

    Involved components:
        -   RenderableModel

    Related processors:
        -   PerformMovementAnimationProcessor

    What if this processor is disabled?
        -   entities are not put into idle animation after other action

    Where the processor should be planned?
        -   after PerformCommandProcessor - due to movement commands generating FlagDoMove
        -   before PerformMovementAnimationProcessor
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

        # Remember updated entities - to prevent several updates on single entity in case same entity is on more cameras
        already_updated = set()

        # Iterate all cameras
        for _, (camera) in self.world.get_component(Camera):

            # Search for entities that contain Position + RenderableModel and at the same time do not have FlagDoMove and FlagDoAttack component
            for ent, (_, renderable_model) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components_exs(include=(Position, RenderableModel), exclude=(FlagDoMove, FlagDoAttack, WeaponInUse, IsDestroyed))):

                # If already updated skip
                if ent in already_updated:
                    continue

                # Update to proper animation
                renderable_model.set_action('idle')

                # NOTE: debug logging commented out — f-string formatting on every entity every frame
                # degrades performance significantly even when DEBUG level is not active.
                # logger.debug(f'({self.cycle}) - Entity {ent} action animation updated to "idle" action.')

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