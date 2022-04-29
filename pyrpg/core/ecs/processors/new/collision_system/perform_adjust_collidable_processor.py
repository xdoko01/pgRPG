__all__ = ['PerformAdjustCollidableProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.collidable import Collidable
from pyrpg.core.ecs.components.new.flag_adjust_collidable import FlagAdjustCollidable

# Logger init
logger = logging.getLogger(__name__)

class PerformAdjustCollidableProcessor(Processor):
    ''' Addjust existing Collidable component with the new parameters

    Involved components:
        -   Collidable
        -   FlagAdjustCollidable

    Related processors:
        -   GenerateCollisionsFullProcessor
        -   GenerateCollisionsProcessor
        -   RemoveFlagAdjustCollisionProcessor

    What if this processor is disabled?
        -   collisions are not modified on the factory generated entities (projectiles)

    Where the processor should be planned?
        -   before GenerateCollisionsProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' On collision, return the entity on its original position.
        '''
        self.cycle += 1

        # Get all entities that have Collidable component and flag to ignore some more entities
        for ent, (collidable, flag_adjust_collision) in self.world.get_components(Collidable, FlagAdjustCollidable):

            # Update ignore list
            logger.debug(f'({self.cycle}) - Entity {ent} - original collision ignore list: {collidable.denylist}')
            logger.debug(f'({self.cycle}) - Entity {ent} - requested additions to the ignore list: {flag_adjust_collision.ignore_collision_with}')
            collidable.denylist = {*flag_adjust_collision.ignore_collision_with, *collidable.denylist}
            logger.debug(f'({self.cycle}) - Entity {ent} - new collision ignore list: {collidable.denylist}')

            # Update collidable dimensions
            logger.debug(f'({self.cycle}) - Entity {ent} - original collision dimensions: [{collidable.x}, {collidable.y}]')
            logger.debug(f'({self.cycle}) - Entity {ent} - requested additions on the collision dimensions: [{flag_adjust_collision.x_fnc}, {flag_adjust_collision.y_fnc}]')
            for f in flag_adjust_collision.x_fnc:collidable.x = f(collidable.x)
            for f in flag_adjust_collision.y_fnc:collidable.y = f(collidable.y)
            logger.debug(f'({self.cycle}) - Entity {ent} - new collision dimensions: [{collidable.x}, {collidable.y}]')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components
        '''
        pass

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the lost reference again
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass

