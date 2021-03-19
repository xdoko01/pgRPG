from assets import *

def test_model_grey_key():
	pygame.init()
	window = pygame.display.set_mode([640,480])
	
	model = Assets.get_entity_model('grey_key')
	
	assert model.model_name == 'Grey key'
	assert model.texture_offset == [0, 0]
	assert model.collision_area == [0.25, 0.25]
	assert model.texture_file == 'textures/keys.json'
	assert model.texture_length == { 'default' : 3}
	assert model.texture_dynamic == {'default' : False}
	
	assert len(Assets._all_tile_models) == 1

def test_model_key():
	pygame.init()
	window = pygame.display.set_mode([640,480])
	
	model = Assets.get_entity_model('key')
	
	assert model.model_name == 'Key'
	assert model.texture_offset == [0, 0]
	assert model.collision_area == [0.25, 0.25]
	assert model.texture_file == 'textures/keys.json'
	assert model.texture_length == { 'default' : 1}
	assert model.texture_dynamic == {'default' : False}
	
	assert len(Assets._all_tile_models) == 2

def test_model_item():
	pygame.init()
	window = pygame.display.set_mode([640,480])
	
	model = Assets.get_entity_model('item')
	
	assert model.model_name == 'Item'
	assert model.texture_offset == [0, 0]
	assert model.collision_area == [0, 0]
	assert model.texture_file == 'textures/keys.json'
	assert model.texture_length == { 'default' : 2}
	assert model.texture_dynamic == {'default' : True}
	
	assert len(Assets._all_tile_models) == 3

def test_model_generic():
	pygame.init()
	window = pygame.display.set_mode([640,480])
	
	model = Assets.get_entity_model('generic')
	
	assert model.model_name == 'Generic Model'
	assert model.texture_offset == [0, 0]
	assert model.collision_area == [0, 0]
	
	assert len(Assets._all_tile_models) == 4