import pyrpg.core.engine as engine
import pyrpg.core.ecs.components as components

def script_modify_brain(event=None, *args, **kwargs):
    ''' Called from quest as an reaction to event fulfilled
    conditions.
    '''

    # Get the entity whose brain I will be working with
    entity = engine.alias_to_entity.get(kwargs.get("entity", None))

    # Get the brain of the entity
    try:
        brain = engine.world.component_for_entity(entity, components.Brain)

        # Stop the brain
        brain.enabled = False

        # Delete and reset the brain with the new commands
        brain.reset(kwargs.get("commands", []))

        # Everything worked fine
        return 0

    except KeyError:
        # Entity has no brain
        return -1
