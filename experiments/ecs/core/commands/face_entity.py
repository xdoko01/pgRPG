''' Module implementing face_entity command
'''

import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)

def cmd_face_entity(*args, **kwargs):
    ''' Change the direction of the entity so that it faces other entity.
    '''

    # Get the entity whose direction needs to be changed
    entity = kwargs.get("entity", None)

    # Get the entity towards the entity should face
    face_to = kwargs.get("face", None)

    face_ent = engine._entity_map.get(face_to, face_to)
    assert(isinstance(face_ent, int), f'Entity {face_ent} is not defined and/or must be an integer')

    # Sign function
    sign = lambda x: -1 if x<0 else (1 if x>0 else 0)

    try:
        # Get the Position component from the entity
        pos_entity = engine.world.component_for_entity(entity, components.Position)

        # Get the Position component from the Face to entity
        pos_face = engine.world.component_for_entity(face_ent, components.Position)

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
