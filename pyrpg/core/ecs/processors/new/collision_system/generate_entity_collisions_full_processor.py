__all__ = ['GenerateEntityCollisionsFullProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.collidable import Collidable
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided

# for creation of events
from pyrpg.core.events.event import Event

# Logger init
logger = logging.getLogger(__name__)

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

class GenerateEntityCollisionsFullProcessor(Processor):
    ''' Detects collisions amongst ALL (not only those objects visible on camera)
    and stores them into the component FlagHasCollided.

    Involved components:
        -   Position
        -   Collidable
        -   FlagHasCollided

    Related processors:
        -   RemoveFlagHasCollidedProcessor
        -   NewGenerateCollisionsProcessor

    What if this processor is disabled?
        -   entities are not colliding

    Where the processor should be planned?
        -   after PerformMovementProcessor - first entities must change position
        -   before RemoveFlagHasCollidedProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.movement_system.perform_movement_processor:PerformMovementProcessor'
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
        ''' Detect all collisions between ALL entities and record them into
        the new component FlagHasCollided.
        '''
        self.cycle += 1

        # Get all entities that have Position + Collidable regardless if visible or not
        for ent_moved, (pos_moved, coll_moved) in self.world.get_components(Position, Collidable):

            # Store the collisions
            collisions = set()

            # Get all the entities again
            for ent_other, (pos_other, coll_other) in self.world.get_components(Position, Collidable):

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
                    e2e1vx = (pos_moved.x + coll_moved.dx) - (pos_other.x + coll_other.dx)
                    e2e1vy = (pos_moved.y + coll_moved.dy) - (pos_other.y + coll_other.dy)
                    centres_vect = (e2e1vx, e2e1vy)
                    centres_sign_vect = (sign(e2e1vx), sign(e2e1vy))
                    
                    # Calculate how much are the collision zones overlaping on x and y axis (both in positive numbers)
                    overlap_vect =(coll_moved.x + coll_other.x - abs(e2e1vx), coll_moved.y + coll_other.y - abs(e2e1vy))

                    # Correction vector - apply this vector on ent_moved and it will avoid end_other
                    correction_vect = (overlap_vect[0] * centres_sign_vect[0], overlap_vect[1] * centres_sign_vect[1])

                    # Add entity that has been touched + its component + vector to fix collision with entity that has been touched
                    # Pass also information if entity wants to have ignored correction
                    collisions.add((ent_other, pos_other, correction_vect, coll_other.ignore_position_fix))

                    # Report that entity collision occured - generate event
                    self.add_event_fnc(Event('COLLISION', ent_moved, ent_other, params={'entity1' : ent_moved, 'entity2' : ent_other}))
                    logger.debug(f'({self.cycle}) - Collision event between {ent_moved} and {ent_other} has been queued.')

            # Create new FlagHasCollided component
            if collisions: 
                self.world.add_component(ent_moved, FlagHasCollided(collisions=collisions))
                logger.debug(f'({self.cycle}) - Entity {ent_moved} has collided with {collisions}')

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

