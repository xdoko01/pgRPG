__all__ = ['RenderModelWorldProcessorDifferentFramesOnCameras']

import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

class RenderModelWorldProcessorDifferentFramesOnCameras(esper.Processor):
    ''' 
    WHY OBSOLETE?
    ^^^^^^^^^^^^^
    NOTE - This version was marked as obsolete because of the problem 
    with generating of weapon collision zone when Renderable model weapon
    action reaches the last animation frame.

    The problem is that in this implementation if one character is shown 
    on multiple cameras, the frame can be on every camera different. The
    reason is that for each camera iteration the processor is asking for 
    the model frame again - and in this get_frame function, changing of frame
    can happen (due to change of animation duration).

    This processor will be substituted by the new version that will always
    display same model frame on all cameras. This will be achieved by adding
    new processor that will update all models once and new RenderModelWorldProcessor
    will only read the frame from RenderableModel - not any shifts in frames.

    Draws the entities in the world. Unlike RenderWorldProcessor
    this one supports animated models.

    It draws only those entities that are displayable on the screen
    by using filter function.
    
    Input parameters:
        -	window - reference to main game screen
        -	debug

    Involved components:
        -	Position
        -	Camera
        -	RenderableModel
        -	CanTalk
    
    Related processors:
        -	UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect

    What if this processor is disabled?
        -	entities will be not shown on the game window
    
    Where the processor should be planned?
        -	before RenderDebugProcessor - in order not to overwrite the debug info
        -	after UpdateCameraOffsetProcessor - in order to display scrolling
        -	after RenderMapProcessor - in order to display map
    '''

    __slots__ = ['window', 'debug']

    def __init__(self, window, debug=False):
        ''' Initiation of RenderProcessor processor.
        
        Parameters:
            :param window: Reference to the main game surface
            :type window: pygame.Surface

            :param debug: Tag if processor should run in debug mode
            :type debug: bool
        '''

        super().__init__()

        self.window = window
        self.debug = debug

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Draws screen for every camera. Every screen draws entities
        and dialog texts. Check the following video for more details about camera 
        implementation of scrolling https://youtu.be/3zV2ewk-IGU.
        '''
        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(components.Camera):

            #####
            # Blit body
            #####

            # Blit all the Entities that have Renderable and Position components - only visible entities
            for ent, (position, renderable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.RenderableModel)):
                camera.screen.blit(renderable.get_frame(position.dir_name, renderable.action), camera.apply(renderable.topleft((position.x, position.y))))

                #####
                # Blit wearables for those displayable- using body information in order to sync the animations
                #####

                # Blit all wearables for the above Entity - if possible
                if self.world.has_component(ent, components.CanWear):

                    # Get the CanWear component of the entity that picked up Wearable
                    can_wear = self.world.component_for_entity(ent, components.CanWear)

                    # Iterate the wearables dictionary and blit them
                    for w_part, w_entity in can_wear.wearables.items():

                        # Get the wearable entity - RenderableModel
                        if w_entity: 
                            w_renderable = self.world.component_for_entity(w_entity, components.RenderableModel)

                            # Blit it on the screen the wearable - using state / position and frame id from the character's RenderableModel
                            camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))

                #####
                # Blit weapons for those displayable- using body information in order to sync the animations
                #####

                # Blit all weapons for the above Entity - if possible
                if self.world.has_component(ent, components.HasWeapon):

                    # Get the HasWeapon component of the entity that picked up Weapon
                    has_weapon = self.world.component_for_entity(ent, components.HasWeapon)

                    # Get the weapon entity - RenderableModel
                    if has_weapon.weapon:
                        w_renderable = self.world.component_for_entity(has_weapon.weapon, components.RenderableModel)

                        # Blit it on the screen the weapon - using state / position and frame id from the character's RenderableModel
                        camera.screen.blit(w_renderable.get_frame(position.dir_name, renderable.action, renderable.last_frame), camera.apply(w_renderable.topleft((position.x, position.y))))


            #####
            # Blit text bubbles
            #####

            # Blit all Texts that are entities saying (CanSpeak + Position component)
            for _, (position, can_talk, renderable) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.CanTalk, components.RenderableModel)):

                # If there is something to say
                if can_talk.text:
                    
                    # Blit the text bubble on the position offset specified by CanTalk component
                    
                    if position.direction == (1,0): # RIGHT
                        camera.screen.blit(can_talk.text_surf, 
                            camera.apply((position.x - renderable.model.d_w - can_talk.text_rect[2], position.y - can_talk.text_rect[3])))
                    
                    elif position.direction == (-1,0): # if direction is (-1, 0) LEFT
                        camera.screen.blit(can_talk.text_surf, 
                            camera.apply((position.x + renderable.model.d_w, position.y - can_talk.text_rect[3])))

                    elif position.direction == (0,-1): # if direction is (0,-1) UP
                        camera.screen.blit(can_talk.text_surf, 
                            camera.apply((position.x - can_talk.text_rect[2] / 2, position.y + renderable.model.d_h )))

                    else: # if direction is (0,1) DOWN
                        camera.screen.blit(can_talk.text_surf, 
                            camera.apply((position.x - can_talk.text_rect[2] / 2, position.y - renderable.model.d_h - can_talk.text_rect[3])))


            # Blit the camera screen on the main game window
            self.window.blit(camera.screen, (camera.screen_pos_x, camera.screen_pos_y))

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components (window).
        '''
        self.window = None

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to window again.
        '''
        self.window = window
