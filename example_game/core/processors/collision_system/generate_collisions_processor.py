__all__ = [
    'GenerateCollisionsOptimizedProcessor',
    'GenerateCollisionsOptimizedFullProcessor',
    'GenerateCollisionsNotOptimizedProcessor',
    'GenerateCollisionsNotOptimizedFullProcessor'
]

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.camera import Camera
from core.components.position import Position
from core.components.collidable import Collidable
from core.components.flag_has_collided import FlagHasCollided

# For creation of events
from pyrpg.core.events.event import Event

from collections import namedtuple # for representation of vectors
from ..functions import filter_only_visible_on_camera # for filtering only entities with position on the cameras
from pyrpg.functions import sign
from pyrpg.functions import allow_deny_list_filter, allow_deny_item_filter

# Logger init
logger = logging.getLogger(__name__)

# For collision correction vector
Vect = namedtuple('Vect', ['x', 'y'])

''' Object to be passed in the list of collisions

Terminology:
  - `moved entity` ... entity being moved/adjusted by the collision object. It is entity whose FlagHasCollided
  component is being processed.
  - `other entity` ... entity that is trying to adjust the position of moved entity. It is the entity that is 
  specified in collision.entity variable.

Collision object bears following important information:
  - entity ... it is `other entity as specified above
  - corr_vect ... if applied on `moved entity`, it will omit collision with `other entity`
  - (apply_fix) apply_fix ... answers the question if `other entity` can/wants to push/adjust `moved entity` position
  - (allow_fix) accept_fix ... answers the question if `moved entity` can/wants to be pushed by `other entity`
'''
Collision = namedtuple('Collision', ['entity', 'corr_vect', 'apply_fix', 'accept_fix', 'walkaround_mode'])

class GenerateCollisionsOptimizedProcessor(Processor):
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
    PREREQ = ['allOf',
        'movement_system.perform_movement_processor:PerformMovementProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        ''' Detect all collisions between visible entities and record them into 
        the new component FlagHasCollided.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(Camera):

            # Get the list of entities together with components on the camera - exclude those whose collisions has been already calculated
            collision_candidates = list(filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components_ex(Position, Collidable, exclude=FlagHasCollided)))

            # Get only set of involved entities
            collision_candidates_entities = set([ent for ent, [*_] in collision_candidates])

            # NEW - final collisions
            coll_list = [list() for _ in collision_candidates]

            # NEW - allowed collisions
            allowed_collisions = [allow_deny_list_filter(input=collision_candidates_entities, allowlist=coll_comp.allowlist, denylist=coll_comp.denylist) for _, (pos_comp, coll_comp) in collision_candidates]
            
            # NEW - position_fix_other
            position_fix_other = [allow_deny_list_filter(input=allowed_collisions[collision_candidates_idx], allowlist=coll_comp.apply_pos_fix_to_allowlist, denylist=coll_comp.apply_pos_fix_to_denylist) for collision_candidates_idx, (_, (pos_comp, coll_comp)) in enumerate(collision_candidates)]

            # NEW - position_fix_self
            position_fix_self = [allow_deny_list_filter(input=allowed_collisions[collision_candidates_idx], allowlist=coll_comp.accept_pos_fix_from_allowlist, denylist=coll_comp.accept_pos_fix_from_denylist) for collision_candidates_idx, (_, (pos_comp, coll_comp)) in enumerate(collision_candidates)]

            # Get all entities that have Position, Collidable + are on some camera
            #for ent_moved, (pos_moved, coll_moved) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, Collidable)):
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

                    # AABB comparison - Collision happened
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
                                    # Ask ent_other_id entity if it can apply fix to ent_moved_id 
                                    apply_fix=ent_moved_id in position_fix_other[ent_other_idx],
                                    # Ask ent_moved_id entity if it allows to be fixed by ent_other_id entity
                                    accept_fix=ent_other_id in position_fix_self[ent_moved_idx],
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
                                    apply_fix=ent_other_id in position_fix_other[ent_moved_idx],
                                    accept_fix=ent_moved_id in position_fix_self[ent_other_idx],
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

class GenerateCollisionsOptimizedFullProcessor(Processor):
    ''' Detects collisions amongst all objects (not only those visible on camera)
    and stores them into the component FlagHasCollided.

    Involved components:
        -   Camera
        -   Position
        -   Collidable
        -   FlagHasCollided

    Related processors:
        -   RemoveFlagHasCollidedProcessor
        -   GenerateCollisionsProcessor

    What if this processor is disabled?
        -   entities are not colliding

    Where the processor should be planned?
        -   after PerformMovementProcessor - first entities must change position
        -   before RemoveFlagHasCollidedProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'movement_system.perform_movement_processor:PerformMovementProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        ''' Detect all collisions between visible entities and record them into 
        the new component FlagHasCollided.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get the list of entities together with components on the camera - exclude those whose collisions has been already calculated
        collision_candidates = list(self.world.get_components_ex(Position, Collidable, exclude=FlagHasCollided))

        # Get only set of involved entities
        collision_candidates_entities = set([ent for ent, [*_] in collision_candidates])

        # NEW - final collisions
        coll_list = [list() for _ in collision_candidates]

        # NEW - allowed collisions
        allowed_collisions = [allow_deny_list_filter(input=collision_candidates_entities, allowlist=coll_comp.allowlist, denylist=coll_comp.denylist) for _, (pos_comp, coll_comp) in collision_candidates]
        
        # NEW - position_fix_other
        position_fix_other = [allow_deny_list_filter(input=allowed_collisions[collision_candidates_idx], allowlist=coll_comp.apply_pos_fix_to_allowlist, denylist=coll_comp.apply_pos_fix_to_denylist) for collision_candidates_idx, (_, (pos_comp, coll_comp)) in enumerate(collision_candidates)]

        # NEW - position_fix_self
        position_fix_self = [allow_deny_list_filter(input=allowed_collisions[collision_candidates_idx], allowlist=coll_comp.accept_pos_fix_from_allowlist, denylist=coll_comp.accept_pos_fix_from_denylist) for collision_candidates_idx, (_, (pos_comp, coll_comp)) in enumerate(collision_candidates)]

        # Get all entities that have Position, Collidable + are on some camera
        #for ent_moved, (pos_moved, coll_moved) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, Collidable)):
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
                                apply_fix=ent_other_id in position_fix_other[ent_moved_idx],
                                accept_fix=ent_other_id in position_fix_self[ent_moved_idx],
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
                                apply_fix=ent_moved_id in position_fix_other[ent_other_idx],
                                accept_fix=ent_moved_id in position_fix_self[ent_other_idx],
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

class GenerateCollisionsNotOptimizedProcessor(Processor):
    ''' Detects collisions amongst objects visible on camera and stores them
    into the component FlagHasCollided.

    Not optimized version that unneceserilly iterates all the entities.

    Involved components:
        -   Camera
        -   Position
        -   Collidable
        -   FlagHasCollided

    Related processors:
        -   RemoveFlagHasCollidedProcessor
        -   GenerateCollisionsProcessor - optimized version

    What if this processor is disabled?
        -   entities are not colliding

    Where the processor should be planned?
        -   after PerformMovementProcessor - first entities must change position
        -   before RemoveFlagHasCollidedProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'movement_system.perform_movement_processor:PerformMovementProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        ''' Detect all collisions between visible entities and record them into 
        the new component FlagHasCollided.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(Camera):

            # Get all entities that have Position, Collidable + are on some camera
            for ent_moved, (pos_moved, coll_moved) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, Collidable)):

                # Store the collisions
                collisions = set()

                # Get all the entities again
                for ent_other, (pos_other, coll_other) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, Collidable)):

                    # If entity is to ignore
                    #if ent_other in coll_moved.ignore_collision_with: continue
                    if not allow_deny_item_filter(input=ent_other, allowlist=coll_moved.allowlist, denylist=coll_moved.denylist): continue

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
                        collisions.add(
                            Collision(
                                entity=ent_other,
                                corr_vect=correction_vect,
                                accept_fix=allow_deny_item_filter(
                                    input=coll_other,
                                    allowlist=coll_moved.accept_pos_fix_from_allowlist,
                                    denylist=coll_moved.accept_pos_fix_from_denylist
                                ),
                                apply_fix=allow_deny_item_filter(
                                    input=coll_other,
                                    allowlist=coll_moved.apply_pos_fix_to_allowlist,
                                    denylist=coll_moved.apply_pos_fix_to_denylist
                                ),
                                walkaround_mode=coll_other.position_fix_walkaround_mode
                            )
                        )

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

                # Create new FlagHasCollided component for ent_moved
                if collisions: 
                    self.world.add_component(ent_moved, FlagHasCollided(collisions=collisions))
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

class GenerateCollisionsNotOptimizedFullProcessor(Processor):
    ''' Detects collisions amongst ALL (not only those objects visible on camera)
    and stores them into the component FlagHasCollided.

    Not optimized version that unneceserilly iterates all the entities.

    Involved components:
        -   Position
        -   Collidable
        -   FlagHasCollided

    Related processors:
        -   RemoveFlagHasCollidedProcessor
        -   GenerateCollisionsProcessor

    What if this processor is disabled?
        -   entities are not colliding

    Where the processor should be planned?
        -   after PerformMovementProcessor - first entities must change position
        -   before RemoveFlagHasCollidedProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'movement_system.perform_movement_processor:PerformMovementProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        ''' Detect all collisions between ALL entities and record them into
        the new component FlagHasCollided.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Position + Collidable regardless if visible or not
        for ent_moved, (pos_moved, coll_moved) in self.world.get_components(Position, Collidable):

            # Store the collisions
            collisions = set()

            # Get all the entities again
            for ent_other, (pos_other, coll_other) in self.world.get_components(Position, Collidable):

                # If entity is to ignore
                if not allow_deny_item_filter(input=ent_other, allowlist=coll_moved.allowlist, denylist=coll_moved.denylist): continue

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
                    collisions.add(
                        Collision(
                            entity=ent_other,
                            corr_vect=correction_vect,
                            accept_fix=allow_deny_item_filter(
                                input=coll_other,
                                allowlist=coll_moved.accept_pos_fix_from_allowlist,
                                denylist=coll_moved.accept_pos_fix_from_denylist
                            ),
                            apply_fix=allow_deny_item_filter(
                                input=coll_other,
                                allowlist=coll_moved.apply_pos_fix_to_allowlist,
                                denylist=coll_moved.apply_pos_fix_to_denylist
                            ),
                            walkaround_mode=coll_other.position_fix_walkaround_mode
                        )
                    )

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

