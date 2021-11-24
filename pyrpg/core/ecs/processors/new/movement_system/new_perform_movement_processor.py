__all__ = ['NewPerformMovementProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pygame	# for pygame.time.get_ticks()

# Logger init
logger = logging.getLogger(__name__)

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

class NewPerformMovementProcessor(esper.Processor):
    ''' Updates Position component (position of an entity on the map) based on NewMovable
    component (movement).

    Input parameters:
        -   debug
        -   stand_delay_ms

    Involved components:
        -	Position
        -	NewMovable

    Related processors:
        -   NewPerformCommandProcessor - move commands generate movement

    What if this processor is disabled?
        -	movements on the map will not work

    Where the processor should be planned?
        -	before CollisionXXXProcessors - collisions are processed based on final movements
        -	before RenderXXXProcessor - camera must be updated before graphics is drawn
        -	after CommandProcessor - commands generate changes in positions
    '''

    __slots__ = ['debug']

    def __init__(self, debug=False):
        ''' Initiation of MovementProcessor processor.

        Parameters:
            :param stand_delay_ms: How long (ms) there must be no movement until direction is reset
            :type stand_delay_ms: int

            :param debug: Tag if processor should run in debug mode
            :type debug: bool
        '''
        super().__init__()

        self.debug = debug

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Process entities having Motion and Position components. Basically,
        add motion diffs to the position represented by Position component.
        '''
        self.cycle += 1

        # Get the time of processing of the frame from the game main loop in seconds
        dt = kwargs.get('dt') / 1000

        # Do not move in case that attack action is in progress - attack has priority over movement
        for _, (position, movable, flag_do_move) in self.world.get_components_ex(components.Position, components.NewMovable, components.NewFlagDoMove, exclude=components.NewFlagDoAttack):

            # Calculate the final move vector only in case no vector is provided and hence needs to be calculated from the moves
            if flag_do_move.vector is None: flag_do_move.calc_vector()
            logger.debug(f'({self.cycle}) - Entity {_} - new move vector {flag_do_move}')

            # Save last position - used for collision resolution on Map
            position.lastx = position.x
            position.lasty = position.y
            position.lastmap = position.map
            logger.debug(f'({self.cycle}) - Entity {_} - original position: [{position.x}, {position.y}]')

            # Update the position by the velocity. Compensate by dt
            position.x += flag_do_move.vector[0] * dt * movable.velocity
            position.y += flag_do_move.vector[1] * dt * movable.velocity
            logger.debug(f'({self.cycle}) - Entity {_} - new position: [{position.x}, {position.y}]')

            # Adjust the velocity by acceleration/deceleration
            movable.velocity += movable.accelerate
            movable.velocity = min(movable.velocity, 1000) if sign(movable.accelerate) == 1 else max(movable.velocity, 0)
            logger.debug(f'({self.cycle}) - Entity {_} - new velocity {movable.velocity}, accelerate {movable.accelerate}')

            # Update the direction based on flag_do_move.vector
            position.direction = (sign(flag_do_move.vector[0]), sign(flag_do_move.vector[1]))

            # If movement is in both axises then use NORD-SOUTH direction
            if flag_do_move.vector[0] != 0 and flag_do_move.vector[1] != 0:
                position.direction = (0, position.direction[1])

            # Update dir_name
            if position.direction == (1,0): position.dir_name = 'right'
            if position.direction == (-1,0): position.dir_name = 'left'
            if position.direction == (0,1): position.dir_name = 'down'
            if position.direction == (0,-1): position.dir_name = 'up'

            logger.debug(f'({self.cycle}) - Entity {_} - new direction "{position.direction}".')

            # remember last move time
            movable._last_move_time = pygame.time.get_ticks()

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
