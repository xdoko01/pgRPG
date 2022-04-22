__all__ = ['NewGenerateCollisionsProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.camera import Camera
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.collidable import Collidable
from pyrpg.core.ecs.components.new.flag_has_collided import FlagHasCollided

# For creation of events
from pyrpg.core.events.event import Event

from collections import namedtuple # for representation of vectors
from ..functions import filter_only_visible # for filtering only entities with position on the cameras
from pyrpg.functions import sign
from pyrpg.functions import allow_deny_list_filter

# Logger init
logger = logging.getLogger(__name__)

# For collision correction vector
Vect = namedtuple('Vect', ['x', 'y'])

# Object to be passed in the list of collisions
Collision = namedtuple('Collision', ['entity', 'corr_vect', 'pos_fix_other', 'pos_fix_self', 'walkaround_mode'])


class GenerateCollisionsProcessor(Processor):
    ''' Detects collisions amongst objects visible on camera and stores them
    into the component FlagHasCollided.

    Involved components:
        -   Camera
        -   Position
        -   Collidable
        -   FlagHasCollided

    Related processors:
        -   RemoveFlagHasCollidedProcessor
        -   GenerateCollisionsFullProcessor

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
        ''' Detect all collisions between visible entities and record them into 
        the new component FlagHasCollided.
        '''
        self.cycle += 1

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(Camera):

            # Get the list of entities together with components on the camera - exclude those whose collisions has been already calculated
            collision_candidates = list(filter(lambda x: filter_only_visible(camera, x), self.world.get_components_ex(Position, Collidable, exclude=FlagHasCollided)))

            # Get only set of involved entities
            collision_candidates_entities = set([ent for ent, [*_] in collision_candidates])

            # NEW - final collisions
            coll_list = [list() for _ in collision_candidates]

            # NEW - allowed collisions
            allowed_collisions = [allow_deny_list_filter(input=collision_candidates_entities, allowlist=coll_comp.allowlist, denylist=coll_comp.denylist) for _, (pos_comp, coll_comp) in collision_candidates]
            
            # NEW - position_fix_other
            position_fix_other = [allow_deny_list_filter(input=allowed_collisions[collision_candidates_idx], allowlist=coll_comp.position_fix_others_allowlist, denylist=coll_comp.position_fix_others_denylist) for collision_candidates_idx, (_, (pos_comp, coll_comp)) in enumerate(collision_candidates)]

            # NEW - position_fix_self
            position_fix_self = [allow_deny_list_filter(input=allowed_collisions[collision_candidates_idx], allowlist=coll_comp.position_fix_self_allowlist, denylist=coll_comp.position_fix_self_denylist) for collision_candidates_idx, (_, (pos_comp, coll_comp)) in enumerate(collision_candidates)]

            # Get all entities that have Position, Collidable + are on some camera
            #for ent_moved, (pos_moved, coll_moved) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(Position, Collidable)):
            #for ent_moved, (pos_moved, coll_moved) in collision_candidates:
            # NEW
            for ent_moved_idx, ent_moved in enumerate(collision_candidates):

                # Unpack ent_moved
                ent_moved_id, (pos_moved, coll_moved) = ent_moved

                # Get all the other entities
                for ent_other_idx, ent_other in enumerate(collision_candidates[ent_moved_idx+1:]):

                    # Unpack ent_other
                    ent_other_id, (pos_other, coll_other) = ent_other

                    # Position of the other entity in collision_candidates
                    ent_other_idx = ent_moved_idx + 1 + ent_other_idx

                    # AABB comaprison - Collision happened
                    if (pos_moved.map == pos_other.map and
                        pos_moved.x + coll_moved.dx - coll_moved.x < pos_other.x + coll_other.dx + coll_other.x and
                        pos_moved.x + coll_moved.dx + coll_moved.x > pos_other.x + coll_other.dx - coll_other.x and
                        pos_moved.y + coll_moved.dy - coll_moved.y < pos_other.y + coll_other.dy + coll_other.y and
                        pos_moved.y + coll_moved.dy + coll_moved.y > pos_other.y + coll_other.dy - coll_other.y):

                        logger.debug(f'({self.cycle}) - Entity {ent_moved} has collided with Entity {ent_other}.')

                        # Calculate vector from ent_other to ent_moved. Signs of this vector will be used for later calculation.
                        centres_vect = Vect((pos_moved.x + coll_moved.dx) - (pos_other.x + coll_other.dx), (pos_moved.y + coll_moved.dy) - (pos_other.y + coll_other.dy))
                        centres_sign_vect = Vect(sign(centres_vect.x), sign(centres_vect.y))
                        
                        # Calculate how much are the collision zones overlaping on x and y axis (both in positive numbers)
                        overlap_vect = Vect(coll_moved.x + coll_other.x - abs(centres_vect.x), coll_moved.y + coll_other.y - abs(centres_vect.y))

                        # Correction vector - apply this vector on ent_moved and it will avoid ent_other on both axis x and y
                        correction_vect = Vect(overlap_vect.x * centres_sign_vect.x, overlap_vect.y * centres_sign_vect.y)

                        # Can ent_moved can collide of ent_other
                        if ent_other_id in allowed_collisions[ent_moved_idx]:
                            self.add_event_fnc(Event('COLLISION', ent_moved_id, ent_other_id, params={'entity1' : ent_moved_id, 'entity2' : ent_other_id}))
                            logger.debug(f'({self.cycle}) - Collision event between {ent_moved_id} and {ent_other_id} has been queued.')

                            coll_list[ent_moved_idx].append(
                                Collision(
                                    entity=ent_other_id, 
                                    corr_vect=correction_vect, 
                                    pos_fix_other=ent_other_id in position_fix_other[ent_moved_idx],
                                    pos_fix_self=ent_other_id in position_fix_self[ent_moved_idx],
                                    walkaround_mode=coll_other.position_fix_walkaround_mode
                                )
                            )

                        # Can ent_other can collide of ent_moved
                        if ent_moved_id in allowed_collisions[ent_other_idx]:
                            self.add_event_fnc(Event('COLLISION', ent_other_id, ent_moved_id, params={'entity1' : ent_other_id, 'entity2' : ent_moved_id}))
                            logger.debug(f'({self.cycle}) - Collision event between {ent_other_id} and {ent_moved_id} has been queued.')

                            coll_list[ent_other_idx].append(
                                Collision(
                                    entity=ent_moved_id, 
                                    corr_vect=Vect(x=-1*correction_vect.x,y=-1*correction_vect.y),
                                    pos_fix_other=ent_moved_id in position_fix_other[ent_other_idx],
                                    pos_fix_self=ent_moved_id in position_fix_self[ent_other_idx],
                                    walkaround_mode=coll_moved.position_fix_walkaround_mode
                                )
                            )



                
                if coll_list[ent_moved_idx]:
                    self.world.add_component(ent_moved_id, FlagHasCollided(collisions=coll_list[ent_moved_idx]))
                    logger.debug(f'({self.cycle}) - Entity {ent_moved_id} has collided with {coll_list[ent_moved_idx]}.')



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

