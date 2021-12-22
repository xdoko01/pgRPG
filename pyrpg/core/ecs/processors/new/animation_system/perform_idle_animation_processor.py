__all__ = ['PerformIdleAnimationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.camera import Camera
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.renderable_model import RenderableModel
from pyrpg.core.ecs.components.new.flag_do_attack import FlagDoAttack
from pyrpg.core.ecs.components.new.weapon_in_use import WeaponInUse
from pyrpg.core.ecs.components.new.flag_do_move import FlagDoMove
from pyrpg.core.ecs.components.new.is_destroyed import IsDestroyed

# Support functions
from ..functions import filter_only_visible

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
    PREREQ = [
        'new.command_system.perform_command_processor:PerformCommandProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Get all entities with renderable model that has not perform any action and update their action to idle.
        '''
        self.cycle += 1

        # Iterate all cameras
        for _, (camera) in self.world.get_component(Camera):

            # Search for entities that contain Position + RenderableModel and at the same time do not have FlagDoMove and FlagDoAttack component
            for ent, (_, renderable_model) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components_exs(include=(Position, RenderableModel), exclude=(FlagDoMove, FlagDoAttack, WeaponInUse, IsDestroyed))):

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