''' Module implementing show_dialog command
'''

import core.engine as engine # To reference the world 
import core.ecs.components as components # To work with components in commands (remove search add ...)
import pygame

def cmd_show_dialog(*args, **kwargs):
    ''' Show text dialog
    '''

    # Get entity from cmd parameters
    entity = kwargs.get("entity", None)

    # Get can talk component from entity
    can_talk = engine.world.component_for_entity(entity, components.CanTalk)

    # Get brain component(timer) and all the other cmd parameters
    brain = kwargs.get("brain", None)
    text = kwargs.get("text", '')
    time = kwargs.get("time", 0)

    # Read the pressed keys
    keys = pygame.key.get_pressed()	

    current_time = pygame.time.get_ticks()

    # time for every character to display
    d_char = time / len(text) if len(text) != 0 else 0

    # If RETURN is pressed, finish displaying the dialog
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            #if pygame.key.get_pressed()[pygame.K_RETURN]:
            can_talk.text = ''
            return 0

    # If text displayed long enough, finish the dialog
    if (current_time - brain.cmd_first_call_time >= time):

        # Text has been shown long enough - continue without exception and reset the text
        # in can_talk component (as a result it will not be drawn by the render function)
        can_talk.text = ''

        return 0
    else:
        # There is still some time to display the text - return exception

        # Only show for the first time it is called last_idx <> next_idx condition
        if brain.last_cmd_idx != brain.next_cmd_idx:
            can_talk.text = text
            (can_talk.text_surf, can_talk.text_rect) = can_talk.font_object.render(can_talk.text, (0,0,255), None)

        # Display text as animated effect
        # each character must be displayed time/length
        #char_to_show = (current_time - brain.cmd_first_call_time) // d_char

        #can_talk.text = text[:int(char_to_show)]
        #(can_talk.text_surf, can_talk.text_rect) = can_talk.font_object.render(can_talk.text, (0,0,255), None)

        return -1
