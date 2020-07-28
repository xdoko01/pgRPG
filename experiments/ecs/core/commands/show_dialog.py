''' Module implementing show_dialog command

    Example of show_dialog commands:

    "show_dialog", {"time" : 3000, "text" : "... Somebody please\nhelp me !!", "can_skip" : false}
    "show_dialog", {"entity" : "player01", "time" : 5000, "text" : "Hi,\ndo jou have\nsome job for me?"}

'''
import core.engine as engine # To reference the world
import core.ecs.components as components # To work with components in commands (remove search add ...)
import pygame

from core.config.fonts import PLAYER_TALK_FONT
from core.config.frames import PLAYER_TALK_FRAME

def cmd_show_dialog(*args, **kwargs):
    ''' Show text dialog
    '''

    # Get entity from cmd parameters
    entity = kwargs.get("entity", None)

    # Get brain component(timer) and all the other cmd parameters
    brain = kwargs.get("brain", None)
    text = kwargs.get("text", '')
    time = kwargs.get("time", None)

    # Can the text be skipped by pressing ENTER?
    can_skip = kwargs.get("can_skip", True)

    # Read the keys and events in order to be able to skip the text
    keys = kwargs.get("keys", [])
    events = kwargs.get("events", [])

    # Get can talk component from entity
    can_talk = engine.world.component_for_entity(entity, components.CanTalk)

    # If RETURN is pressed and the text can be skipped, finish displaying the dialog
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and can_skip:
                can_talk.text = ''
                return 0

    # Get current time
    current_time = pygame.time.get_ticks()

    # Static text for given period of time
    if time is not None:
        # If text displayed long enough, finish the dialog
        if (current_time - brain.cmd_first_call_time >= time):

            # Text has been shown long enough - continue without exception and reset the text
            # in can_talk component (as a result it will not be drawn by the render function)
            can_talk.text = ''

            return 0

        else:

            # Only show for the first time it is called last_idx <> next_idx condition
            if brain.last_cmd_idx != brain.next_cmd_idx:
                can_talk.text = text
                can_talk.text_surf = PLAYER_TALK_FRAME.render(PLAYER_TALK_FONT.render(can_talk.text, color=can_talk.text_color, align='CENTER'))
                can_talk.text_dim = (can_talk.text_surf.get_width(), can_talk.text_surf.get_height())

            return -1

    else:

        # Display text as animated effect

        # Each character must be displayed time/length
        char_to_show = (current_time - brain.cmd_first_call_time) // can_talk.text_speed if can_talk.text_speed > 0 else len(text)

        if char_to_show == len(text):
            can_talk.text = ''
            return 0
        else:

            can_talk.text = text[:int(char_to_show)]
            can_talk.text_surf = PLAYER_TALK_FRAME.render(PLAYER_TALK_FONT.render(can_talk.text, color=can_talk.text_color, align='CENTER'))
            can_talk.text_dim = (can_talk.text_surf.get_width(), can_talk.text_surf.get_height())

            return -1