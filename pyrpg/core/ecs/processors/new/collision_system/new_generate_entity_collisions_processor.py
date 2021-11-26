__all__ = ['NewGenerateEntityCollisionsProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.camera import Camera
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.new_collidable import NewCollidable
from pyrpg.core.ecs.components.new.new_flag_has_collided import NewFlagHasCollided

# For creation of events
from pyrpg.core.events.event import Event

from collections import namedtuple # for representation of vectors
from ..functions import filter_only_visible # for filtering only entities with position on the cameras

# Logger init
logger = logging.getLogger(__name__)

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

Vect = namedtuple('Vect', ['x', 'y'])

class NewGenerateEntityCollisionsProcessor(Processor):
    ''' Detects collisions amongst objects visible on camera and stores them
    into the component NewFlagHasCollided.

    Involved components:
        -   Camera
        -   Position
        -   NewCollidable
        -   NewFlagHasCollided

    Related processors:
        -   NewRemoveFlagHasCollidedProcessor
        -   NewGenerateCollisionsFullProcessor

    What if this processor is disabled?
        -   entities are not colliding

    Where the processor should be planned?
        -   after NewPerformMovementProcessor - first entities must change position
        -   before NewRemoveFlagHasCollidedProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.movement_system.new_perform_movement_processor:NewPerformMovementProcessor'
    ]

    def __init__(self, add_event_fnc):
        ''' Init the processor.
        '''
        super().__init__()

        self.add_event_fnc = add_event_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Detect all collisions between visible entities and record them into 
        the new component NewFlagHasCollided.
        '''
        self.cycle += 1

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(Camera):

            # Get all entities that have Position, NewCollidable + are on some camera
            for ent_moved, (pos_moved, coll_moved) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, NewCollidable)):

                # Store the collisions
                collisions = set()

                # Get all the entities again
                for ent_other, (pos_other, coll_other) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, NewCollidable)):

                    # If entity is to ignore
                    if coll_moved.ignore_collision_with == ent_other: continue

                    # Heuristic no.1 - Skip if testing itself
                    if ent_moved == ent_other: continue

                    # Heuristic no 1.5 - Test only entities on the same map
                    if pos_moved.map != pos_other.map: continue

                    # Heuristic no.2 - Test only those in close distance
                    #if abs(pos_moved.x - pos_other.y) > 200 or abs(pos_moved.y - pos_other.y) > 200: continue 

                    # AABB comaprison - Collision
                    if( pos_moved.x + coll_moved.dx - coll_moved.x < pos_other.x + coll_other.dx + coll_other.x and
                        pos_moved.x + coll_moved.dx + coll_moved.x > pos_other.x + coll_other.dx - coll_other.x and
                        pos_moved.y + coll_moved.dy - coll_moved.y < pos_other.y + coll_other.dy + coll_other.y and
                        pos_moved.y + coll_moved.dy + coll_moved.y > pos_other.y + coll_other.dy - coll_other.y):

                        ###
                        # Calculate the vector that (when applied on ent_moved) will avoid the collision with ent_other
                        ###

                        # Calculate vector from ent_other to ent_moved. Signs of this vector will be used for later calculation.
                        #e2e1vx = (pos_moved.x + coll_moved.dx) - (pos_other.x + coll_other.dx)
                        #e2e1vy = (pos_moved.y + coll_moved.dy) - (pos_other.y + coll_other.dy)
                        #centres_vect = (e2e1vx, e2e1vy)
                        centres_vect = Vect((pos_moved.x + coll_moved.dx) - (pos_other.x + coll_other.dx), (pos_moved.y + coll_moved.dy) - (pos_other.y + coll_other.dy))
                        centres_sign_vect = Vect(sign(centres_vect.x), sign(centres_vect.y))
                        
                        # Calculate how much are the collision zones overlaping on x and y axis (both in positive numbers)
                        overlap_vect = Vect(coll_moved.x + coll_other.x - abs(centres_vect.x), coll_moved.y + coll_other.y - abs(centres_vect.y))

                        # Correction vector - apply this vector on ent_moved and it will avoid end_other
                        correction_vect = Vect(overlap_vect.x * centres_sign_vect.x, overlap_vect.y * centres_sign_vect.y)

                        # Add entity that has been touched + its component + vector to fix collision with entity that has been touched
                        # Pass also information if entity wants to have ignored correction
                        collisions.add((ent_other, pos_other, correction_vect, coll_other.ignore_position_fix))

                        logger.debug(f'({self.cycle}) - Entity {ent_moved} has collided with Entity {ent_other}.')
                        logger.debug(f'({self.cycle}) - Entity {ent_moved} position centre is ({pos_moved.x}, {pos_moved.y}).')
                        logger.debug(f'({self.cycle}) - Entity {ent_moved} collision centre is ({pos_moved.x + coll_moved.dx}, {pos_moved.y + coll_moved.dy}).')
                        logger.debug(f'({self.cycle}) - Entity {ent_moved} collision box (({pos_moved.x + coll_moved.dx - coll_moved.x}, {pos_moved.y + coll_moved.dy - coll_moved.y}), ({pos_moved.x + coll_moved.dx + coll_moved.x}, {pos_moved.y + coll_moved.dy - coll_moved.y}), (({pos_moved.x + coll_moved.dx + coll_moved.x}, {pos_moved.y + coll_moved.dy + coll_moved.y})), (({pos_moved.x + coll_moved.dx - coll_moved.x}, {pos_moved.y + coll_moved.dy + coll_moved.y}))).')
                        logger.debug(f'({self.cycle}) - Entity {ent_other} position centre is ({pos_other.x}, {pos_other.y}).')
                        logger.debug(f'({self.cycle}) - Entity {ent_other} collision centre is ({pos_other.x + coll_other.dx}, {pos_other.y + coll_other.dy}).')
                        logger.debug(f'({self.cycle}) - Entity {ent_other} collision box (({pos_other.x + coll_other.dx - coll_other.x}, {pos_other.y + coll_other.dy - coll_other.y}), ({pos_other.x + coll_other.dx + coll_other.x}, {pos_other.y + coll_other.dy - coll_other.y}), (({pos_other.x + coll_other.dx + coll_other.x}, {pos_other.y + coll_other.dy + coll_other.y})), (({pos_other.x + coll_other.dx - coll_other.x}, {pos_other.y + coll_other.dy + coll_other.y}))).')
                        logger.debug(f'({self.cycle}) - Vector from {ent_other} centre to {ent_moved} centre is [{centres_vect}] which signes {centres_sign_vect}')
                        logger.debug(f'({self.cycle}) - Overlap_vect = {overlap_vect}')
                        logger.debug(f'({self.cycle}) - Correction_vect = {correction_vect}')

                        # Report that entity collision occured - generate event
                        self.add_event_fnc(Event('COLLISION', ent_moved, ent_other, params={'entity1' : ent_moved, 'entity2' : ent_other}))
                        logger.debug(f'({self.cycle}) - Collision event between {ent_moved} and {ent_other} has been queued.')

                # Create new NewFlagHasCollided component for ent_moved
                if collisions: 
                    self.world.add_component(ent_moved, NewFlagHasCollided(collisions=collisions))
                    logger.debug(f'({self.cycle}) - Entity {ent_moved} has collided with {collisions}.')

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

