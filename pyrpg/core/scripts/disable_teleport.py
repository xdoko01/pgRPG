import pyrpg.core.engine as engine
import pyrpg.core.ecs.components as components

def script_disable_teleport(event=None, *args, **kwargs):
    ''' Remove the teleport possibilities from the teleport
    '''

    engine.world.remove_component(event.generator_obj, components.Collidable)

    #Return success
    return 0