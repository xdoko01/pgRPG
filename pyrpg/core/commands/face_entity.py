''' Module implementing face_entity command
'''

import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)

def initialize(register, module_name):
    '''Command registers itself at CommandManager'''
    # Mandatory line
    register(fnc=cmd_face_entity, alias=module_name)

def cmd_face_entity(*args, **kwargs):
    ''' Change the direction of the entity so that it faces other entity.
    '''

    # World reference
    world = kwargs.get("world")

    # Get the entity whose direction needs to be changed
    entity = kwargs.get("entity", None)

    # Get the entity towards the entity should face
    face_to = kwargs.get("face", None)

    face_ent = engine.alias_to_entity.get(face_to, face_to)
    assert(isinstance(face_ent, int), f'Entity {face_ent} is not defined and/or must be an integer')

    # Sign function
    sign = lambda x: -1 if x<0 else (1 if x>0 else 0)

    try:
        # Get the Position component from the entity
        pos_entity = world.component_for_entity(entity, components.Position)

        # Get the Position component from the Face to entity
        pos_face = world.component_for_entity(face_ent, components.Position)

        # if possitive, pos_entity must face Right
        x_dir = pos_face.x - pos_entity.x
        # if positive, pos_entity must face Down
        y_dir = pos_face.y - pos_entity.y

        # turn left or right
        if abs(x_dir) > abs(y_dir):
            pos_entity.direction = (sign(x_dir), 0)
        # turn up or down
        else:
            pos_entity.direction = (0, sign(y_dir))

        # Direction successfully updated
        print(f'Face CMD: Direction of entity {entity} changed to {pos_entity.direction }')
        return 0

    except KeyError:

        # Error, direction not updated
        return -1
