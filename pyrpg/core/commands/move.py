''' Module implementing move command
'''

import pyrpg.core.engine as engine # To reference the world 
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)
from pyrpg.core.ecs.components.original.motion import Motion


def cmd_move(*args, **kwargs):
    ''' Pass whatever information you think are necessary for the command
    and let the command utilize them or not
    '''
    # Get parameters for movement
    entity = kwargs.get("entity")

    # It is important to return None if parameter is not passed and not 0
    # The reason is that several commands may come in one loop and we do not
    # want to change the results of the previous command - enable diagonal
    # scrolling.
    dx = kwargs.get("dx", None)
    dy = kwargs.get("dy", None)

    # if Move component does not exist on entity then error is not raised
    try:
        # Get the motion component from the entity
        motion = engine.world.component_for_entity(entity, Motion)

        # Change the motion if parameter passed in the command
        # What if there are several commands in the queue for motion - like move 5x to the left?
        # In that case, what is written below will not work

        #motion.dx = dx if dx else motion.dx
        #motion.dy = dy if dy else motion.dy

        # This is more correct as it is not ignoring multiple movement commands for one entity
        motion.dx = motion.dx + dx if dx else motion.dx
        motion.dy = motion.dy + dy if dy else motion.dy

        return 0

    except KeyError:

        return -1
