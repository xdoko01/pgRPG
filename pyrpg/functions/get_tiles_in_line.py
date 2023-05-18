from .sign import sign_wo_zero

def get_tiles_in_line(source_px: tuple, target_px: tuple, tile_res: int):
    '''Get the tiles between 2 points in px. Tiles coordinates are returned in
    lazy mode and in the raster specified by tile_res.

    Tiles include both starting and ending tiles.

    Parameters:
        :param source_px: Path to the package, for example pyrpg.core.ecs
        :type source_px: tuple

        :param target_px: Path to the module, relative to the package
        :type target_px: tuple

        :param tile_res: Dimension of the rectancular tile in px.
        :type tile_res: int
    '''

    dx, dy = target_px[0] - source_px[0], target_px[1] - source_px[1]
    sx, sy = sign_wo_zero(dx), sign_wo_zero(dy)

    # Starting position
    x, y = source_px[0], source_px[1]

    if abs(dx) > abs(dy): # Horizontal
        x_incr = sx * tile_res
        y_incr = x_incr * dy/dx

        while sx*x < sx*target_px[0]:
            #print(f'x:{int(x)}, y:{int(y)}, sx*x:{sx*x}, sx*target_px[0]:{sx*target_px[0]}')
            yield (x // tile_res, int(y // tile_res))
            x = x + x_incr
            y = y + y_incr

    else: # Vertical
        y_incr = sy * tile_res
        x_incr = y_incr * dx/dy

        while sy*y < sy*target_px[1]:
            #print(f'x:{int(x)}, y:{int(y)}, sy*y:{sy*y}, sy*target_px[1]:{sy*target_px[1]}')
            yield (int(x // tile_res), y // tile_res)
            x = x + x_incr
            y = y + y_incr


if __name__ == '__main__':
    for tile in get_tiles_in_line((200,200), (10, 10), 64):
        print(tile)