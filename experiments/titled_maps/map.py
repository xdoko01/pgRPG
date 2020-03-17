''' Experiments with Tiled maps

Requirements
	-	pytmx-3.21.7

Features

	-	multiple layers - ground, sky
	-	animated tiles (burning fires)
	-	support existing game Entity models
'''
import pytmx

tiled_map = pytmx.TiledMap('experiments/titled_maps/resources/maps/test_simple.tmx')

print(tiled_map.get_tile_properties(0,0,1))