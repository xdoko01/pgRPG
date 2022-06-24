import logging
from pyrpg.core.quests.quest import Quest, load_quest_ex
from pyrpg.core.events.event import Event

# Create logger
logger = logging.getLogger(__name__)

class QuestManager:

    def __init__(self) -> None:
        self._quests = {}
        logger.info(f'QuestManager initiated.')

    def add_quest(self, quest_name, progress, map_mng=None, dialog_mng=None, event_mng=None, ecs_mng=None, script_mng=None) -> Quest:
        '''Adds new quest to the game'''
        quest_obj = load_quest_ex(quest_name, progress, map_mng=map_mng, dialog_mng=dialog_mng, event_mng=event_mng, ecs_mng=ecs_mng, script_mng=script_mng)
        self._quests.update({quest_name : quest_obj})
        logger.info(f'Quest "{quest_name}" was added to the game.')

    def handle_event(self, event: Event) -> None:
        '''Send every event to every quest for handling'''

        for quest_name, quest_object in self._quests.copy().items(): # the copy() is there due to restart_quest script that is deleting the quests and loading new ones. It was falling on Runtime error that the dictionary has changed during runtime. Problem is fixed by using copy
            quest_object.event_handler_ex(event)
            logger.info(f'Event "{event.event_type}" was passed to quest "{quest_name}" for handling.')

    def delete_quest(self, quest_name: str) -> None:
        '''Deletes quests from the game'''

        del self._quests[quest_name]
        logger.info(f'Quest "{quest_name}" was deleted.')

    def clear_quests(self) -> None:
        ''' Clears all the loaded quests.'''

        quests = list(self._quests.keys()).copy()

        for quest_name in quests:
            self.delete_quest(quest_name)

        logger.info(f'Quests cleared.')
