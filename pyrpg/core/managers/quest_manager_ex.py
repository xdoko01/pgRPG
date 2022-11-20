import logging

import pyrpg.core.events.event as event # for creation of QUEST_START, QUEST_FINISH, PHASE_START, PHASE_FINISH events
from pyrpg.core.config.paths import QUEST_PATH
from pyrpg.functions import get_dict_from_json, get_dict_from_yaml, get_dict_value


# Create logger
logger = logging.getLogger(__name__)

class QuestManager:
    '''New version that is ready to get rid of Quest as a class object and
    introduces event handlers as a dictionary property of Event manager.
    '''

    def __init__(self) -> None:
        self._quests = {}
        logger.info(f'QuestManager initiated.')

    def _get_quest_data(self, quest_filepath, quest_file_section=None) -> dict:
        '''Load quest data from the json/yaml file. One quest file can contain several quests. If this
        is the case, quest_id parameter defines the quest to load. Otherwise, it is assumed that the
        file contains only one quest.

        Parameters:
            :param quest_filepath: Relative or absolute filepath to YAML or JSON file with definition of one 
            or multiple quests.

            :param quest_file_section: Key within the quest file where the quest is stored. This way one file can contain.
            several quests, if convenient. If argument is not present, the whole quest file is considered as one big quest.

            :return: Dictionary containing the original quest data.
        '''

        # Check if quest is in yaml or json format
        quest_extension = quest_filepath.suffix

        # Check if path to the quest is absolute or relative and construct the full path to the file
        quest_filepath = quest_filepath if quest_filepath.is_absolute() else QUEST_PATH / quest_filepath

        # Open the quest file
        try:
            if quest_extension in ['.yml', '.yaml']:
                quest_data = get_dict_from_yaml(quest_filepath)
            elif quest_extension in ['.json']:
                quest_data = get_dict_from_json(quest_filepath)
            else:
                logger.error(f'Unsupported quest file format with extension "{quest_extension}". Only .json, .yml, .yaml files are supported.')
                raise ValueError(f'Unsupported quest file format with extension "{quest_extension}". Only .json, .yml, .yaml files are supported.')
        except:
            logger.error(f'Cannot load quest file "{quest_filepath}".')
            raise ValueError(f'Cannot load quest file "{quest_filepath}".')

        # If quest_id is present as a parameter, find it as a key in the data and return only data relevant to that key
        quest_data = get_dict_value(quest_data, path=quest_file_section, sep='/', not_found=None)
        if quest_data is None:
            logger.error(f'Section "{quest_file_section}" was not found in the quest file "{quest_filepath}".')
            raise ValueError(f'Section "{quest_file_section}" was not found in the quest file "{quest_filepath}".')
        else:
            return quest_data

    def _clean_processors(self, progress_fnc, processors_data: list, clean_processor_fnc):
        '''Deletes all processors from processors_data'''

        progress_fnc(text='Cleaning Processors', progress=0, total=len(processors_data))

        try:
            for n, processor in enumerate(processors_data):
                clean_processor_fnc(processor)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of processors "{processor}".')
            raise ValueError(f'Problem during cleaning of processors.')

    def _clean_templates(self, progress_fnc, templates_data: list, clean_template_fnc):
        '''Deletes all templates from templates_data'''

        progress_fnc(text='Cleaning Templates', progress=0, total=len(templates_data))

        try:
            for n, template in enumerate(templates_data):
                clean_template_fnc(template)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of templates "{template}".')
            raise ValueError(f'Problem during cleaning of templates.')

    def _clean_entities(self, progress_fnc, entities_data: list, clean_entity_fnc):
        '''Deletes all entities from entities_data'''

        progress_fnc(text='Cleaning Entities', progress=0, total=len(entities_data))

        try:
            for n, entity_name in enumerate(entities_data):
                clean_entity_fnc(alias=entity_name)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of entities "{entity}".')
            raise ValueError(f'Problem during cleaning of entities.')

    def _clean_maps(self, progress_fnc, maps_data: list, clean_map_fnc):
        '''Deletes all maps from maps_data'''

        progress_fnc(text='Cleaning Maps', progress=0, total=len(maps_data))

        try:
            for n, map in enumerate(maps_data):
                clean_map_fnc(map)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of maps "{map}".')
            raise ValueError(f'Problem during cleaning of maps.')

    def _clean_dialogs(self, progress_fnc, dialogs_data: list, clean_dialog_fnc):
        '''Deletes all dialogs from dialogs_data'''

        progress_fnc(text='Cleaning Dialogs', progress=0, total=len(dialogs_data))

        try:
            for n, dialog in enumerate(dialogs_data):
                clean_dialog_fnc(dialog)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of dialog "{dialog}".')
            raise ValueError(f'Problem during cleaning of dialogs.')

    def _clean_handlers(self, progress_fnc, handlers_data: list, clean_handler_fnc):
        '''Deletes all handlers from handlers_data'''

        progress_fnc(text='Cleaning Handlers', progress=0, total=len(handlers_data))

        try:
            for n, handler in enumerate(handlers_data):
                clean_handler_fnc(handler)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during cleaning of handler "{handler}".')
            raise ValueError(f'Problem during cleaning of handlers.')

    def _load_processors(self, progress_fnc, processors_data: list, load_processor_fnc):
        '''Loads all processors from processors_data'''

        progress_fnc(text='Loading Processors', progress=0, total=len(processors_data))

        try:
            for n, processor in enumerate(processors_data):
                load_processor_fnc(processor)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during loading of processor "{processor}".')
            raise ValueError(f'Problem during loading of processors.')

    def _load_maps(self, progress_fnc, maps_data: list, load_map_fnc):
        '''Loads all maps from maps_data'''

        progress_fnc(text='Loading Maps', progress=0, total=len(maps_data))

        try:
            for n, map in enumerate(maps_data):
                load_map_fnc(map)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during loading of map "{map}".')
            raise ValueError(f'Problem during loading of maps.')

    def _load_dialogs(self, progress_fnc, dialogs_data: list, load_dialog_fnc):
        '''Loads all dialogs from dialogs_data'''

        progress_fnc(text='Loading Dialogs', progress=0, total=len(dialogs_data))

        try:
            for n, dialog in enumerate(dialogs_data):
                load_dialog_fnc(dialog)
                progress_fnc(progress=n+1)
        except ValueError:
            logger.error(f'Problem during loading of dialog "{dialog}".')
            raise ValueError(f'Problem during loading of dialogs.')

    def _load_templates(self, progress_fnc, templates_data: list, load_template_fnc):
        '''Loads all templates from templates_data'''

        progress_fnc(text='Loading Entity Templates', progress=0, total=len(templates_data))

        try:
            for n, template in enumerate(templates_data):
                load_template_fnc(template, template['id'])
                progress_fnc(progress=n+1)
        except KeyError:
            raise ValueError(f'Template definition is missing required parameter "id".')
        except ValueError:
            logger.error(f'Problem during loading of templates.')
            raise ValueError(f'Problem during loading of templates.')

    def _create_empty_entities(progress_fnc, entities_data: list, create_empty_entity_fnc, entity_exists_fnc):
        '''Extract all aliases for the entities and create them as an empty and
        registered in lookup tables in ecs_manager.
        '''

        progress_fnc(text='Loading Entities - Registration', progress=0, total=len(entities_data))

        try:
            for n, entity in enumerate(entities_data):
                # Only create new empty entity if alias not yet exists.
                if not entity_exists_fnc(entity['id']):
                    create_empty_entity_fnc(entity_alias=entity['id'])
                progress_fnc(progress=n+1)
        except KeyError:
            raise ValueError(f'Entity definition is missing required parameter "id".')
        except ValueError:
            logger.error(f'Problem during creating of empty entities.')
            raise ValueError(f'Problem during creating of empty entities.')

    """OBSOLETE - delete"""
    def _store_entities_definitions(progress_fnc, entities_data: list, store_entity_definition_fnc, get_entity_id_fnc):
        '''Stores every entity definition in ecs_manager.
        '''

        progress_fnc(text='Loading Entities - Storing definitions', progress=0, total=len(entities_data))

        try:
            for n, entity in enumerate(entities_data):
                entity_id = get_entity_id_fnc(entity_alias=entity['id'])
                store_entity_definition_fnc(entity, entity_id)
                progress_fnc(progress=n+1)
        except KeyError:
            raise ValueError(f'Entity definition is missing required parameter "id".')
        except ValueError:
            logger.error(f'Problem during storing of entities definitions.')
            raise ValueError(f'Problem during storing of entities definitions.')

    def _update_entities(progress_fnc, entities_data: list, update_entity_fnc, get_entity_id_fnc):
        '''Stores every entity definition in ecs_manager.
        '''

        progress_fnc(text='Loading Entities - Components Update', progress=0, total=len(entities_data))

        try:
            for n, entity in enumerate(entities_data):
                entity_id = get_entity_id_fnc(entity_alias=entity['id'])
                update_entity_fnc(entity, entity_id)
                progress_fnc(progress=n+1)
        except KeyError:
            raise ValueError(f'Entity definition is missing required parameter "id".')
        except ValueError:
            logger.error(f'Problem during storing of components for entities.')
            raise ValueError(f'Problem during storing of components for entities.')

    def _load_entities(self, progress_fnc, entities_data: list, ecs_mng):
        '''Loads all entities from entities_data'''

        try:
            self._create_empty_entities(
                progress_fnc=progress_fnc,
                entities_data=entities_data,
                create_empty_entity_fnc=ecs_mng.create_empty_entity,
                entity_exists_fnc=ecs.mng.get_entity_id
            )

            """OBSoLETE - get rid of it """
            self._store_entities_definitions(
                progress_fnc=progress_fnc,
                entities_data=entities_data,
                store_entity_definition_fnc=ecs_mng.store_entity_definition,
                get_entity_id_fnc=ecs_mng.get_entity_id
            )

            self._update_entities(
                progress_fnc=progress_fnc,
                entities_data=entities_data,
                update_entity_fnc=ecs_mng.update_entity,
                get_entity_id_fnc=ecs_mng.get_entity_id
            )
        except ValueError:
            logger.error(f'Problem during loading of entities.')
            raise ValueError(f'Problem during loading of entities.')

    def _load_handlers(self, progress_fnc, handlers_data: list, load_handler_fnc):
        '''Loads all handlers from handlers_data'''

        progress_fnc(text='Loading Handlers', progress=0, total=len(handlers_data))

        pass


    def _load_quest(self, quest_data, progress_fnc, map_mng, dialog_mng, event_mng, ecs_mng):
        '''Loads the quest data into the game data structures of individual managers'''

        quest_id = quest_data["id"]

        #####
        # PRE-LOAD prerequisity quests
        #####

        # Load prerequisity quests
        for prereq_quest in quest_data.get("prereq", []):
            # If only the filename is defined without the
            if isinstance(prereq_quest, str):
                # Get the quest id from the file and decide if load or not
                if self._get_quest_data(prereq_quest)["id"] not in self._quests.keys():
                    self.add_quest(progress_fnc, prereq_quest, map_mng=map_mng, dialog_mng=dialog_mng, event_mng=event_mng, ecs_mng=ecs_mng)
            elif isinstance(prereq_quest, list or tuple) and len(prereq_quest) == 2:
                # Get the quest id from the file and decide if load or not
                if self._get_quest_data(prereq_quest[0], prereq_quest[1])["id"] not in self._quests.keys():
                    self.add_quest(progress_fnc, prereq_quest[0], prereq_quest[1], map_mng=map_mng, dialog_mng=dialog_mng, event_mng=event_mng, ecs_mng=ecs_mng)
            else:
                raise ValueError(f'Not supported format of quest prerequisity.')


        #####
        # PRE-LOAD cleanup
        #####

        # Clean processors
        self._clean_processors(
            progress_fnc=progress_fnc,
            processors_data=quest_data.get("cleanup", {}).get("processors", []),
            clean_processor_fnc=ecs_mng.delete_processor
        )

        # Clean templates
        self._clean_templates(
            progress_fnc=progress_fnc,
            templates_data=quest_data.get("cleanup", {}).get("templates", []),
            clean_template_fnc=ecs_mng.delete_template
        )

        # Clean entities
        self._clean_entities(
            progress_fnc=progress_fnc,
            entities_data=quest_data.get("cleanup", {}).get("entities", []),
            clean_entity_fnc=ecs_mng.delete_entity
        )

        # Clean maps
        self._clean_maps(
            progress_fnc=progress_fnc,
            maps_data=quest_data.get("cleanup", {}).get("maps", []),
            clean_map_fnc=map_mng.delete_map
        )

        # Clean dialogs
        self._clean_dialogs(
            progress_fnc=progress_fnc,
            dialogs_data=quest_data.get("cleanup", {}).get("dialogs", []),
            clean_dialog_fnc=dialog_mng.delete_dialog
        )

        # Clean handlers
        self._clean_handlers(
            progress_fnc=progress_fnc,
            handlers_data=quest_data.get("cleanup", {}).get("handlers", []),
            clean_handler_fnc=event_mng.delete_handler
        )

        #####
        # LOAD
        #####

        # Load processors
        self._load_processors(
            progress_fnc=progress_fnc,
            processors_data=quest_data.get("processors", []),
            load_processor_fnc=ecs_mng.load_processor
        )

        # Load maps
        self._load_maps(
            progress_fnc=progress_fnc,
            maps_data=quest_data.get("maps", []),
            load_map_fnc=map_mng.add_map
        )

        # Load dialogs
        self._load_dialogs(
            progress_fnc=progress_fnc,
            dialogs_data=quest_data.get("dialogs", []),
            load_dialog_fnc=dialog_mng.add_dialog
        )

        # Load templates
        self._load_templates(
            progress_fnc=progress_fnc,
            templates_data=quest_data.get("templates", []),
            load_template_fnc=ecs_mng.store_template_definition
        )

        # Load entities
        self._load_entities(
            progress_fnc=progress_fnc,
            entities_data=quest_data.get("entities", []),
            ecs_mng=ecs_mng
        )

        # Load handlers
        self._load_handlers(
            progress_fnc=progress_fnc,
            handlers_data=quest_data.get("event_handlers", {}),
            load_handler_fnc=event_mng.load_handler
        )


        # Report that quest was loaded - generate event
        event_mng.add_event(event.Event('QUEST_START', self, None, params={'quest_id' : quest_id}))

        return quest_id

    def add_quest(self, progress_fnc, quest_filepath, quest_file_section=None, map_mng=None, dialog_mng=None, event_mng=None, ecs_mng=None, script_mng=None) -> None:
        '''Adds new quest to the game'''
        quest_data = self._get_quest_data(quest_filepath, quest_file_section)
        logger.info(f'Quest data for quest succesfully extracted from the file: "{quest_filepath}", section "{quest_file_section}".')

        quest_id = self._load_quest(quest_data, progress_fnc, map_mng=map_mng, dialog_mng=dialog_mng, event_mng=event_mng, ecs_mng=ecs_mng)
        self._quests.update({quest_id : quest_data})
        logger.info(f'Quest "{quest_id}" was added to the game.')

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
