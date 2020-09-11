''' Module implementing set_quest_phase command
'''

import pyrpg.core.engine as engine # To reference the world

def cmd_set_quest_phase(*args, **kwargs):
    ''' In the game cinematics processor, it may come to the point when I want to proceed
    to the next phase of the game.
    To enable that from global game cinematics processor, I can see 2 ways:
        - I can invoke command that change the phase
        - I can invoke event from the global brain command and let the quest to change the phase

    Let's go with the first option and see

    TODO - this is dirty - accessing engine quest dict directly
    '''

    # Get quest id and the new phase id
    quest = kwargs.get("quest", None)
    phase = kwargs.get("phase", None)	

    # Update the quest's phase
    try:
        engine.quests.get(quest, None).set_phase(phase)

        # Everything went smoothly
        return 0
    
    except:
        # Error occured
        return -1
