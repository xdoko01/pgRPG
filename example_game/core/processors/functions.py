from math import sin, cos, sqrt

from core.components.position import Position
from core.components.camera import Camera
from pyrpg.core.maps.map import Map

def filter_only_not_behind_wall(ent_pos_comp: Position, map: Map, comp_tuple: tuple) -> bool:
    ''' Filter that is used for filtering of entities that are not hidden
    behind some wall from the entity.
    '''
    
    # Select position component from the return tuple. Must be the first
    _, (oth_pos_comp, *_) = comp_tuple

    # We are interested only in entities NOT hidden beneath the wall
    return not map.check_collision_in_line((ent_pos_comp.x, ent_pos_comp.y), (oth_pos_comp.x, oth_pos_comp.y))


def filter_only_specific_entity_ids(list_of_entity_ids: list, comp_tuple: tuple) -> bool:
    '''Filter that is used for filtering of only specific entity_ids.
    '''
    # If list is empty, consider entity as valid
    if not list_of_entity_ids: return True

    ent_id, _ = comp_tuple

    if ent_id not in list_of_entity_ids: 
        return False
    else:
        return True


def filter_only_within_distance_from_ent(ent_pos_comp: Position, max_distance: int, comp_tuple: tuple) -> bool:
    '''Filter that is used for selection of only those entities
    that are within the max_distance from the entity.
    '''

    # Select position component from the return tuple. Must be the first
    _, (oth_pos_comp, *_) = comp_tuple

    # Entity cannot hear itself
    if ent_pos_comp == oth_pos_comp: return False

    # Entity cannot hear other entity on other map
    if ent_pos_comp.map != oth_pos_comp.map: return False

    # Distance of entity from other entity on x, y and total
    dx = oth_pos_comp.x - ent_pos_comp.x
    dy = oth_pos_comp.y - ent_pos_comp.y
    dist = sqrt(dx*dx + dy*dy)

    # Chect that other entity is still in audible distance
    if dist > max_distance: 
        return False

    return True

def filter_only_in_view_angle_of_ent(ent_pos_comp: Position, sin_angle: float, comp_tuple: tuple) -> bool:
    '''Filter that is used for selection of only those entities
    that are in the view angle of the entity.
    '''

    # Select position component from the return tuple. Must be the first
    _, (oth_pos_comp, *_) = comp_tuple

    # Entity cannot see itself
    if ent_pos_comp == oth_pos_comp: return False

    # Entity cannot see other entity on other map
    if ent_pos_comp.map != oth_pos_comp.map: return False

    # Distance of entity from other entity on x, y and total
    dx = oth_pos_comp.x - ent_pos_comp.x
    dy = oth_pos_comp.y - ent_pos_comp.y
    dist = sqrt(dx*dx + dy*dy)

    sin_angle_oth_vert = abs(dx/dist)
    sin_angle_oth_horiz = abs(dy/dist)

    # Check that oth ent position is in the viewable range
    if (
        (sin_angle_oth_vert <= sin_angle and dy > 0 and ent_pos_comp.direction[1] > 0) or  #(0,1)
        (sin_angle_oth_vert <= sin_angle and dy < 0 and ent_pos_comp.direction[1] < 0) or  #(0,-1)
        (sin_angle_oth_horiz <= sin_angle and dx > 0 and ent_pos_comp.direction[0] > 0) or #(1,0)
        (sin_angle_oth_horiz <= sin_angle and dx < 0 and ent_pos_comp.direction[0] < 0) #(-1,0)
    ):
        return True

    return False

"""
def filter_only_in_sight_of_ent(ent_pos_comp: Position, max_distance: int, sin_angle: float, comp_tuple: tuple) -> bool:
    '''Filter that is used for selection of only those entities
    that are within the visible range of the entity.
    '''

    # Select position component from the return tuple. Must be the first
    _, (oth_pos_comp, *_) = comp_tuple

    # Entity cannot see itself
    if ent_pos_comp == oth_pos_comp: return False

    # Entity cannot see other entity on other map
    if ent_pos_comp.map != oth_pos_comp.map: return False

    # Distance of entity from other entity on x, y and total
    dx = oth_pos_comp.x - ent_pos_comp.x
    dy = oth_pos_comp.y - ent_pos_comp.y
    dist = sqrt(dx*dx + dy*dy)

    # Chect that other entity is still in viewable distance
    if dist > max_distance: return False

    sin_angle_oth_vert = abs(dx/dist)
    sin_angle_oth_horiz = abs(dy/dist)

    # Check that oth ent position is in the viewable range
    if (
        (sin_angle_oth_vert <= sin_angle and dy > 0 and ent_pos_comp.direction[1] > 0) or  #(0,1)
        (sin_angle_oth_vert <= sin_angle and dy < 0 and ent_pos_comp.direction[1] < 0) or  #(0,-1)
        (sin_angle_oth_horiz <= sin_angle and dx > 0 and ent_pos_comp.direction[0] > 0) or #(1,0)
        (sin_angle_oth_horiz <= sin_angle and dx < 0 and ent_pos_comp.direction[0] < 0) #(-1,0)
    ):
        return True

    return False
"""

def filter_only_visible_on_camera(camera: Camera, comp_tuple: tuple, corr: int=32) -> bool:
    ''' Filter that is used for selection of only those entities
    that are within visible scope of the camera screen.

    Correction corr is by default 32 pixels

    !! Position component must be the first component in the tuple in order to work !!
    '''
    # Displayable part of the map in pixel coordinates
    rect = camera.map_screen_rect

    # Correction corr - part of sprite must be visible even if
    # position is beneath borders

    # Select position component from the return tuple. Must be the first
    _, (position, *_) = comp_tuple

    # True, if position is within rectancle of camera screen
    return rect[0] - corr < position.x < rect [2] + corr and rect[1] - corr < position.y < rect[3] + corr


def get_arrow_points(direction, length, position=(0, 0)):
    '''Get the 3 points used for drawing of arrow. Used in Render debug processor for
    displaying of direction and velocity arrows
    '''

    # First point is start of the arrow, second is tip of the arrow followed by left and right arm and end by tip again
    arrow = {'up' : ((0, 0), (0, -1), (-0.2, -0.8), (0.2, -0.8), (0, -1)),
             'down' : ((0, 0), (0, 1), (-0.2, 0.8), (0.2, 0.8), (0, 1)),
             'left' : ((0, 0), (-1, 0), (-0.8, 0.2), (-0.8, -0.2), (-1, 0)),
             'right' : ((0, 0), (1, 0), (0.8, 0.2), (0.8, -0.2), (1, 0))
    }

    # list of points that are increased by length
    inc_arrow_list = tuple(
                        tuple(
                            map(
                                lambda x: x*length,
                                point
                            )
                        )
                        for point in arrow[direction]
                    )

    # move the points to the required position and return it as tuple
    return tuple(
                map(
                    lambda p: (p[0] + position[0], p[1] + position[1]),
                    inc_arrow_list
                )
            )

def get_view_points(direction: str, distance: int, angle: int, position: tuple) -> tuple:
    '''Get the 3 points used for drawing of view area. Used in Render debug processor for
    displaying of view range. Angle is in radians
    '''

    sin_angle = sin(angle)
    cos_angle = cos(angle)
    
    view_matrix = {'up': ((-sin_angle, -cos_angle), (0,0), (sin_angle, -cos_angle)),
                   'down': ((-sin_angle, cos_angle), (0,0), (sin_angle, cos_angle)),
                   'left': ((-cos_angle, -sin_angle), (0,0), (-cos_angle, sin_angle)),
                   'right': ((cos_angle, -sin_angle), (0,0), (cos_angle, sin_angle))
    }
    
    # list of points increased by distance
    view_points = tuple(
                        tuple(
                            map(
                                lambda x: x*distance,
                                point
                            )
                        )
                        for point in view_matrix[direction]
                    )

    # move the points to the required position and return it as tuple
    return tuple(
                map(
                    lambda p: (int(p[0] + position[0]), int(p[1] + position[1])),
                    view_points
                )
            )

if __name__ == '__main__':
    
    print(get_arrow_points('up', 10, (2,3)))
    print(get_view_points('up', 100, 0.5235987756, (0,0)))
    print(get_view_points('down', 100, 0.5235987756, (0,0)))
    print(get_view_points('left', 100, 0.5235987756, (0,0)))
    print(get_view_points('right', 100, 0.5235987756, (0,0)))