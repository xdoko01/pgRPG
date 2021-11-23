from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
Arrow = namedtuple('Arrow', ['start', 'tip', 'left', 'right'])

def filter_only_visible(camera, comp_tuple, corr=32):
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

if __name__ == '__main__':
    
    print(get_arrow_points('up', 10, (2,3)))
