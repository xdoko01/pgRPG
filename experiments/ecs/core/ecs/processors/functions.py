__all__ = ['filter_only_visible_on_camera']

def filter_only_visible_on_camera(camera, comp_tuple, corr=32):
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

