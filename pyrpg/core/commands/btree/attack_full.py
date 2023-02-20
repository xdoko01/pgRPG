''' Module implementing attack command
'''
import pygame
from pyrpg.core.ecs.components.new.flag_do_attack import FlagDoAttack # To work with components in commands (remove search add ...)

def cmd_attack_full(*args, **kwargs):
    ''' Add FlagDoAttack to the entity so long to fill the full attack animation cycle

  *Goal*
    - Use weapon on the current position/direction for given time period
  *Results*
    - `SUCCESS` - time `attack_time_ms` is over
    - `RUNNING` - attack in progress
    - `FAILURE` - no more ammo or entity destroyed or target destroyed
  *Params*
    - `attack_time_ms` - how long to generate the attack commands
  *Steps*
    Save target health component
    Save entity health component

    Check, if entity/target destroyed
      - if YES,
        - finish with `FAILURE`

    Check, if within `attack_duration_ms`
      - if YES,
        - assign `FlagHasAttacked` component to entity
        - finish with `RUNNING`
      - if NO,
        - finish with `SUCCESS`

    '''
    # Get the blackboard for the BTree
    bb_globals = kwargs["brain"].blackboard

    # Get the blackboard for this particular command - i.e running behavior
    bb_locals = kwargs["brain"].blackboard.running_behavior.bb

    # Get the entity and the target Position components
    target_damageable_comp = bb_globals.get(kwargs["target_damageable_comp"])
    entity_damageable_comp = bb_globals.get(kwargs["entity_damageable_comp"])

    if target_damageable_comp.health <=0 or entity_damageable_comp.health <= 0:
        return 'FAILURE'

    if kwargs["brain"].blackboard.running_behavior.duration >= kwargs.get("attack_time_ms", 500):
        # Unit has been executed long enough - continue without exception
        return 'SUCCESS'
    else:
        # There is still time to execute - return exception
        kwargs["world"].add_component(kwargs["entity"], FlagDoAttack())
        return 'RUNNING'
