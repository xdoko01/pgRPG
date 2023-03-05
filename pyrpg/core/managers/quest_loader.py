import logging

from pyrpg.core.config.paths import QUEST_PATH
from pyrpg.functions import get_dict_from_file, get_dict_value
from pyrpg.core.menus.progress_bar2 import ProgressBar2

from pathlib import Path

# Create logger
logger = logging.getLogger(__name__)

class Quest:
    def __init__(self, alias: str, quest_def: dict):
        self.alias = alias
        dict_def = quest_def

class QuestLoader:
    '''Aim of the class is to translate definition of the quest from json/yaml file
    to game objects that represent the quest elements in the game - entities, maps,
    etc.
    '''

    def __init__(self, gui_manager, process_fncs: list) -> None:
        '''Init receives the references to functions that are necessary to
        load the quest successfully.
        
        Parameters:
            :param progress_fnc: Reference to function that updates the progress bar
            :type progress_fnc: fnc

            :param process_fncs: List of tuples specifying the source of data and the
                                 function that should be used for processing.
            :type process_fncs: list
        '''
        self.gui_manager = gui_manager
        self._process_fncs = process_fncs
        self._process_fncs[0][1] = self.load_quest_from_file

        logger.info(f'QuestLoader initiated.')

    def load_quest_from_file(self, filepath: str) -> Quest:
        '''Reads file with the quest, translates it to quest definition
        and processes quest definition into game world objects.
        
        Parameters:
            :param filepath: Absolute or relative path to the file containing
                             quest definition (JSON/YAML/other).
            :type filepath: str

            :returns: Quest object with basic quest information
        '''

        # Read the quest definition from a file
        quest_def = get_dict_from_file(filepath=Path(filepath), dir=QUEST_PATH)

        # Translate quest definition into the game objects
        quest = self.load_quest_from_def(quest_def)
        
        # Return the quest objects containing usefull information
        return quest

    def load_quest_from_def(self, quest_def: dict) -> Quest:
        '''Translates the quest definition into the objects representing the
        game world - entities, components, maps, dialogs, handlers, etc.

        Parameters:
            :param quest_def: Dictionary containing all information about the
                              quest.
            :type quest_def: dict

            :returns: Quest object with basic quest information
        '''

        quest = Quest(alias=quest_def["id"], quest_def=quest_def)

        logger.info(f'Loading objects for quest "{quest.alias}" has started.')

        # Search every defined location in the quest_def and try to process
        # it using the given functions for processing.
        for data_path, process_fnc in self._process_fncs:

            # Get the data on the path to be processed
            data_to_process = get_dict_value(quest_def, path=data_path, sep='/', not_found=[])

            logger.info(f'Start of processing of "{data_path}" for quest "{quest.alias}". Total "{len(data_to_process)} definitions".')

            # Cycle this data and process them using progress bar
            with ProgressBar2(gui_manager=self.gui_manager, header='Loading', text=data_path) as progress:
                for item in progress(data_to_process):
                    logger.debug(f'About to process following item "{item}" using function "{process_fnc}".')
                    process_fnc(item)

            logger.info(f'End of processing of "{data_path}" for quest "{quest.alias}".')
        
        logger.info(f'Loading objects for quest "{quest.alias}" has finished.')

        return quest
