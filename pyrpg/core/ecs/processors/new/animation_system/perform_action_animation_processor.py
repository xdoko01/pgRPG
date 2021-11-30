__all__ = ['PerformActionAnimationProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.camera import Camera
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.renderable_model import RenderableModel
from pyrpg.core.ecs.components.new.flag_do_attack import FlagDoAttack
from pyrpg.core.ecs.components.new.new_weapon_in_use import NewWeaponInUse

# Support functions
from ..functions import filter_only_visible

# Logger init
logger = logging.getLogger(__name__)

class PerformActionAnimationProcessor(Processor):
    ''' Sets action animation for RenderableModel entities that have performed attack
    and are displayed.

    Involved components:
        -   RenderableModel
        -   FlagDoAttack
        -   WeaponInUse

    Related processors:
        -   PerformIdleAnimationProcessor
        -   PerformFrameUpdateProcessor

    What if this processor is disabled?
        -   entities are not animated while attacking

    Where the processor should be planned?
        -   after PerformCommandProcessor - due to movement commands generating FlagDoMove
        -   after PerformIdleAnimationProcessor - so that entity switches to idle when not attacking
        -   after PerformMovementAnimationProcessor - so that entity switches to walking when not attacking
        -   before PerformFrameUpdateProcessor - so that attack is animated
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.command_system.perform_command_processor:PerformCommandProcessor', 
        'new.animation_system.perform_movement_animation_processor:PerformMovementAnimationProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Get all components with renderable model that have attacked and have some weapon in use 
        and update their action.
        '''
        self.cycle += 1

        # Iterate all cameras
        for _, (camera) in self.world.get_component(Camera):

            # Get all entities that are in the process of attacking
            for ent, (_, renderable_model, _, weapon_in_use) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, RenderableModel, FlagDoAttack, NewWeaponInUse)):

                # Update to proper animation
                renderable_model.set_action(weapon_in_use.action)
                logger.debug(f'({self.cycle}) - Entity {ent} action animation updated to "{weapon_in_use.action}" action.')


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