import logging
from pyrpg.core.quests.quest import Quest
from pyrpg.core.events.event import Event

# Create logger
logger = logging.getLogger(__name__)

class QuestManager:

    def __init__(self) -> None:
        self._quests = {}
        logger.info(f'QuestManager initiated.')


    def add_quest(self, quest_name: str, quest_obj: Quest) -> None:
        '''Adds new quest to the game'''

        self._quests.update({quest_name : quest_obj})

    def handle_event(self, event: Event) -> None:
        '''Send every event to every quest for handling'''

        for quest_name, quest_object in self._quests.items():
            quest_object.event_handler(event)
            logger.info(f'Event "{event.event_type}" was passed to quest "{quest_name}" for handling.')

    def clear_quests(self) -> None:
        ''' Clears all the loaded quests.'''

        self._quests.clear()
        logger.info(f'Quests cleared.')
