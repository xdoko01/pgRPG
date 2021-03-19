''' Module implementing show_dialog command

    Example of show_dialog commands:

    - Dialog text displayed at one and displayed 3s - cannot be skipped by pressing RETURN
        "show_dialog", {"time" : 3000, "text" : "... Somebody please\nhelp me !!", "can_skip" : false}

'''
import pyrpg.core.engine as engine # To reference the world
import pyrpg.core.ecs.components as components # To work with components in commands (remove search add ...)
import pygame

from pyrpg.core.config.fonts import PLAYER_TALK_FONT
from pyrpg.core.config.frames import PLAYER_TALK_FRAME

from pyrpg.core.config.keys import K_SUBMIT

def cmd_show_dialog_dynamic(*args, **kwargs):
    ''' Show text dialog - dynamic
    Speed of text displaying is managed by CanTalk parameter speed
    '''

    # Get entity from cmd parameters
    entity = kwargs.get("entity", None)

    # Get brain component and all the other cmd parameters
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
            if event.key == K_SUBMIT and can_skip:
                can_talk.text = ''
                return 0

    # Only for the first time it is called last_idx <> next_idx, generate the frame
    if brain.last_cmd_idx != brain.next_cmd_idx:
        (can_talk.frame_surf, can_talk.frame_text_offset) = PLAYER_TALK_FRAME.render_frame_only(PLAYER_TALK_FONT.get_text_dim(text), alpha=127)
        can_talk.frame_dim = (can_talk.frame_surf.get_width(), can_talk.frame_surf.get_height())

    # Get the time since beginning
    elapsed_time = (pygame.time.get_ticks() - brain.cmd_first_call_time)

    # How many characters from the text to display
    char_to_show = elapsed_time // can_talk.text_speed

    if elapsed_time < time + (char_to_show * len(text)):

        can_talk.text = text[:int(char_to_show)]
        can_talk.text_surf = PLAYER_TALK_FONT.render(can_talk.text, color=can_talk.text_color, align='LEFT')
        can_talk.text_dim = (can_talk.text_surf.get_width(), can_talk.text_surf.get_height())

        return -1

    else:

        can_talk.text = ''

        return 0


def cmd_show_dialog_static(*args, **kwargs):
    ''' Show text dialog at once - no animation effect
    
    Example of the command usage:
      -  "show_dialog", {"time" : 3000, "text" : "... Somebody please\nhelp me !!", "can_skip" : false}
    '''

    # Get entity from cmd parameters
    entity = kwargs.get("entity", None)

    # Get brain component (for first call time) and all the other cmd parameters
    brain = kwargs.get("brain", None)
    text = kwargs.get("text", '')
    # Default 3s for showing the dialog text
    time = kwargs.get("time", 3000)

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
            if event.key == K_SUBMIT and can_skip:
                can_talk.text = ''
                return 0

    # Get current time
    current_time = pygame.time.get_ticks()

    # If text displayed long enough, finish the dialog
    if (current_time - brain.cmd_first_call_time >= time):

        # Text has been shown long enough - continue without exception and reset the text
        # in can_talk component (as a result it will not be drawn by the render function)
        can_talk.text = ''

        return 0

    else:

        # Only show for the first time it is called last_idx <> next_idx condition
        if brain.last_cmd_idx != brain.next_cmd_idx:

            # Update information of CanTalk component so that Talk processor can use them for displaying dialogs 
            can_talk.text = text

            can_talk.text_surf = PLAYER_TALK_FONT.render(can_talk.text, color=can_talk.text_color, align='CENTER')
            can_talk.text_dim = (can_talk.text_surf.get_width(), can_talk.text_surf.get_height())

            (can_talk.frame_surf, can_talk.frame_text_offset) = PLAYER_TALK_FRAME.render_frame_only(PLAYER_TALK_FONT.get_text_dim(can_talk.text), alpha=127)
            can_talk.frame_dim = (can_talk.frame_surf.get_width(), can_talk.frame_surf.get_height())

        return -1