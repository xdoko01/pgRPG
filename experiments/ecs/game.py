########################################################
### Module Import Init - Init global variables
########################################################

global world
global maps
global quests
global alias_to_entity
global entity_to_alias # mapping of entity id to alias id - for displaying of in-game messages

maps = {}
alias_to_entity = {}
quests = {}
entity_to_alias = {}

########################################################
########################################################
###             MODULE FUNCTIONS
########################################################
########################################################

########################################################
### Module Functions - Module Init Functions
########################################################

def init_world():
    ''' Prepare ECS instances for the game
    '''

    global world

    world = esper.World(timed=False)
    create_processors(world)

########################################################
### Module Functions - Game world creator/destructor methods
########################################################


def _create_entity(json_ent_obj, register=True, child_ref=None):
    ''' Create entity from json definition. See Quest for definitions
    '''

    global world
    global alias_to_entity
    global entity_to_alias

    # Prepare new_entity obj
    new_entity_obj = None

    # Decode entity id 
    new_entity_id = json_ent_obj.get("id")

    # Create new entity obj for the root entity
    if not child_ref: 
        new_entity_obj = world.create_entity()
        print(f'\n*Creating new entity "{new_entity_id}", id: {new_entity_obj}')

    # Read the components from the templates - order matters! latter has priority and overwrites
    # the previous components
    for template in json_ent_obj.get("templates", []):

        # Read the entity.json
        try:
            with open(ENTITY_PATH / str(template + '.json'), 'r') as entity_file:
                json_entity_data = entity_file.read()
                template_entity_data = json.loads(json_entity_data)
        except FileNotFoundError:
            print(f"Entity file {ENTITY_PATH + template + '.json'} not found.")
            raise

        print(f'**Creating components from template {template + ".json"}')
        _create_entity(template_entity_data, child_ref=new_entity_obj if not child_ref else child_ref)
        print(f'**Creating components from template {template + ".json"} done.')

    # Initiate every component
    for component in json_ent_obj.get("components"):

        # Get component type
        comp_type = component.get("type")

        # Get component params
        comp_params = component.get("params", {})

        # Create component
        try:
            result = components.create_component(
                world,
                new_entity_obj if not child_ref else child_ref,
                comp_type,
                comp_params
            )

            print(f'***{result[1]} for entity {result[0]} created.')

        except ValueError:
            print(f'Error in creation of component {comp_type} with parameters {comp_params}')
            raise ValueError

    # Add entity to the entity map - for the root entity
    if not child_ref and register:
        alias_to_entity.update({new_entity_id : new_entity_obj})
        entity_to_alias.update({new_entity_obj: new_entity_id})

    return new_entity_obj

def create_processors(world):

    global window
    global event_queue
    global command_queue
    global message_queue
    global maps

    # Processor that updates constant speed movement
    linear_movement_processor = processors.LinearMovementProcessor()

    # Processor that generates projectiles
    generate_projectiles_processor = processors.GenerateProjectileProcessor()

    # Processor that deletes entities with Temporary component from the world - once ttl expires
    clear_temporary_entity_processor = processors.ClearTemporaryEntityProcessor()

    # Update the animation for rendering the model
    render_model_anim_update_processor = processors.RenderableModelAnimationUpdateProcessor()

    # Status procesor updates status of the entity - idle, walk, ...
    render_model_anim_action_processor = processors.RenderableModelAnimationActionProcessor()

    # Movement processor updates entity position based on the velocity 
    movement_processor = processors.MovementProcessor()

    # Render GAME WINDOW background procesor to display game stats and anything else
    render_background_processor = processors.RenderBackgroundProcessor(window=window)

    # Render CAMERA background processor 
    render_camera_background_processor = processors.RenderCameraBackgroundProcessor()

    # Render processor to display map
    render_map_processor = processors.RenderMapProcessor(window=window, maps=maps)

    # Render processor to place renderable entities with position on the screen
    render_world_processor = processors.RenderWorldProcessor(window=window)
    render_model_world_processor = processors.RenderModelWorldProcessor(window=window)
    render_talk_processor = processors.RenderTalkProcessor2(window=window)


    # Render debug processor to display debug information for renderable entities
    render_debug_processor = processors.RenderDebugProcessor(window=window)

    # Input processor to process keys pressed - the commands are queued and processed later by 
	# CommandProcessor
    input_processor = processors.InputProcessor(command_queue)

    # Collision Entity processor
    collision_entity_generator_processor = processors.CollisionEntityGeneratorProcessor()

    # Collision Map processor
    collision_map_processor = processors.CollisionMapProcessor(maps=maps)

    # Teleport Collision processor
    collision_teleport_processor = processors.CollisionTeleportProcessor(event_queue)

    # Damaging Collision processor
    collision_damage_processor = processors.CollisionDamageProcessor(event_queue)

    # Weapon Collision processor
    collision_weapon_processor = processors.CollisionWeaponProcessor(event_queue)

    # Wearable Collision processor
    collision_wearable_processor = processors.CollisionWearableProcessor(event_queue)

    # Item Collision processor
    collision_item_processor = processors.CollisionItemProcessor(event_queue)

    # Entity Collision processor - added command queue processor to generate corrective movements
    collision_entity_processor = processors.CollisionEntityProcessor(event_queue, command_queue)

    # Collision Deletion processor - deletes entities with component DeleteOnCollision
    collision_deletion_processor = processors.CollisionDeletionProcessor()

    # Collision position corrector processor - OBSOLETE - substituted by CollisionEntityProcessor
    #collision_corrector_processor = processors.CollisionCorrectorProcessor()

    # Camera processor - update position of the camera
    update_camera_offset_processor = processors.UpdateCameraOffsetProcessor(maps=maps)

    # Game events processor - triggers actions based on previously generated events
    game_events_processor = processors.GameEventsProcessor(process_game_events)

    # Command processor - processes all commands from the command queue
    command_processor = processors.CommandProcessor(process_game_commands)

    # Brain processor
    brain_processor = processors.BrainProcessor(command_queue)

    # Game messages processor
    game_messages_processor = processors.GameMessagesProcessor(process_game_messages)

    ##### #### #### ####
    # Beware of order of the processors
    ##### #### #### ####

    ### First lets read input from player or/and AI. The resulting commands are stored in cmd_stream
    world.add_processor(input_processor)
    world.add_processor(brain_processor)

    ### Process all the commands from the command stream
    world.add_processor(command_processor)

    ### Move the entities based on their movement vector
    world.add_processor(linear_movement_processor)  # update entities that are moving at constant speed (projectiles/arrows)
    world.add_processor(movement_processor)

    ### Generate projectiles GenerateProjectileProcessor
    world.add_processor(generate_projectiles_processor)

    ### Process all collisions and produce events where necessary
    world.add_processor(collision_map_processor)	# Resolves all the collisions on the map - correct movements and nothing more
    world.add_processor(collision_entity_generator_processor)	# Fills information about which entities collided together into the Collision components
    world.add_processor(collision_damage_processor) # Makes damage to entity if applicable
    world.add_processor(collision_teleport_processor)	# Resolves teleport collisions + generates events to the main program where those can be further processed
    world.add_processor(collision_weapon_processor)	# Resolves weapon pickups collisions + generates events to the main program where those can be further processed
    world.add_processor(collision_wearable_processor)	# Resolves wearable pickups collisions + generates events to the main program where those can be further processed
    world.add_processor(collision_item_processor)		# Resolves item pickups collisions + generates events to the main program where those can be further processed
    world.add_processor(collision_entity_processor)		# Resolves entity collisions + generates events to the main program where those can be further processed
    #world.add_processor(collision_corrector_processor)	# Fixes positions of collided entities - OBSOLETE - substituted by CollisionEntityProcessor
    world.add_processor(collision_deletion_processor)	# Deletes entities that collided and have DeleteOnCollision component


    ### Process all events that were generated by collision processors
    world.add_processor(game_events_processor)	# Based on events generated by the collisions (teleportation, item pickups) now is the time to see if there are some game actions that we want to do - e.g. cinematics


    ##################################
    ### Render the world on the screen
    ##################################
    # Update all cameras
    world.add_processor(update_camera_offset_processor)

    ### Change the entity state based on everything what has happened before rendering
    world.add_processor(render_model_anim_action_processor)

    ### Update the entity animation
    world.add_processor(render_model_anim_update_processor)

    # Render game window background - stats / inventory / picture
    world.add_processor(render_background_processor)

    # Render cameras background - in order not to have blured screen on
    # parts where map is not displayed.
    world.add_processor(render_camera_background_processor)

    # Render maps
    world.add_processor(render_map_processor)

    # Render objects with Renderable component
    world.add_processor(render_world_processor)

    # Render world entities
    #world.add_processor(render_world_processor)
    world.add_processor(render_model_world_processor)

    # Render text bubbles
    world.add_processor(render_talk_processor)

    # Render additional debug information on the screen
    world.add_processor(render_debug_processor)

    # Render game messages on the screen
    world.add_processor(game_messages_processor)

    ##################################
    ### Clearing processors
    ##################################

    # Delete entities with Temporary component from the world
    world.add_processor(clear_temporary_entity_processor)

def create_map(map_name):
    ''' Register and create new map if not already created
    Called from Quest/Phase class
    '''

    # All maps are here
    global maps

    # Create map, if not exists
    if not maps.get(map_name, None):
        new_map = map.Map(map_name)	
        maps.update({map_name : new_map})

def delete_map(map_name):
    ''' Unregister and delete the map object
    '''

    # All maps are here
    global maps

    # If map is registered - de-reference it
    # As map reference is stored only in global dictionary and
    # not on individual entities, it is enough to dereference it
    # here and not on individual entities.
    if maps.get(map_name, None):
        del maps[map_name]

def delete_entity(entity_name):
    ''' Delete and un-register entity from the world
    '''

    global world
    global alias_to_entity

    # If entity is registered, delete it
    if alias_to_entity.get(entity_name, None):

        # Delete it from Esper world
        world.delete_entity(alias_to_entity.get(entity_name))
        
        # Un-register the entity
        del alias_to_entity[entity_name]
