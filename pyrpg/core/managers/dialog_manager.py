# Create logger
import logging
logger = logging.getLogger(__name__)

from fnmatch import fnmatchcase # UNIX-like wildcards in load/clean functions

import pyrpg.utils.dialog as dialog

from pyrpg.core.config import FILEPATHS # DIALOG_PATH, IMAGE_PATH, FONT_PATH, Path # for DIALOG_PATH, IMAGE_PATH, FONT_PATH
from pyrpg.functions.get_dict_from_json import get_dict_from_json

from pathlib import Path

_dialogs = dict()

logger.info(f'DialogManager initiated.')


def load_dialog(dialog_def: dict) -> None:
    ''' Create dialog from dictionary definition contained in dictionary
    dialog_def and stores it in _dialogs dictionary

    - dialog_def - original data from the scene
    - new_dlg_data - data after taking into account all templates
    - new_dlg_obj - dictionary with surface objects generated from the data
    '''

    def prepare_dlg_data_from_template(dlg_template: str) -> dict:
        ''' Returns dictionary based of json file with dialog
        template specification.
        '''

        # Read the json file with dialog definition
        try:
            dlg_file = Path(FILEPATHS["DIALOG_PATH"] / Path(dlg_template + '.json'))
            dlg_data = get_dict_from_json(dlg_file)
        except FileNotFoundError:
            logger.error(f'Dialog file "{dlg_file}" not found.')
            raise

        # Final dlg data - empty at the start
        final_dlg_data = {}

        # Check if some template is used - first merge templates together - deeper and first go first
        for template in dlg_data.get('templates', []):
            
            # Get the json definition of the template and merge it
            final_dlg_data = { **prepare_dlg_data_from_template(template), **final_dlg_data }

        final_dlg_data = { **final_dlg_data, **dlg_data }

        return final_dlg_data

    # Prepare new empty dictionary that will hold the dialog's data
    new_dlg_data = {}

    # Decode dialog's id (name) - mandatory
    new_dlg_id = dialog_def.get('id')

    # Create the final dictionary definition using existing templates
    for template in dialog_def.get("templates", []):

        # Get the json definition of the template and merge it
        new_dlg_data = { **prepare_dlg_data_from_template(template), **new_dlg_data }

    # Now the final dialog description is stored here
    new_dlg_data = { **new_dlg_data, **dialog_def }

    # Now there is time to make surfaces and register the data object
    new_dlg_obj = dialog.prepare_dlg_obj_from_data(new_dlg_data, img_path=FILEPATHS["IMAGE_PATH"], font_path=FILEPATHS["FONT_PATH"])

    # Store the dialog
    _dialogs.update({new_dlg_id : new_dlg_obj})
    logger.info(f'Dialog added.')

def delete_dialog(dialog_name: str) -> None:
    ''' Unregister and delete the dialog object.'''

    if _dialogs.get(dialog_name, None):
        del _dialogs[dialog_name]
        logger.info(f'Dialog "{dialog_name}" successfully removed.')

def delete_dialogs_pattern(dialog_name_pattern: str) -> None:
    """Deletes all dialogs matching the dialog_name_pattern (UNIX-style wildcards).
    """

    logger.debug(f'About to delete dialogs with names matching pattern "{dialog_name_pattern}".')

    match = lambda k: fnmatchcase(k, dialog_name_pattern)

    for dialog_name in _dialogs.copy().keys():
        if match(dialog_name):
            delete_dialog(dialog_name)

def clear_dialogs() -> None:
    '''Dereference and delete all dialogs.'''

    dialogs = list(_dialogs.keys()).copy()

    # We need to use a copy in order not to delete parsed dictionary
    for dialog_name in dialogs:
        delete_dialog(dialog_name)
    logger.info(f'All dialogs cleared.')

"""
class DialogManager():

    def __init__(self) -> None:
        self._dialogs = {}
        logger.info(f'DialogManager initiated.')

    def load_dialog(self, dialog_def: dict) -> None:
        ''' Create dialog from dictionary definition contained in dictionary
        dialog_def and stores it in _dialogs dictionary

        - dialog_def - original data from the scene
        - new_dlg_data - data after taking into account all templates
        - new_dlg_obj - dictionary with surface objects generated from the data
        '''

        def prepare_dlg_data_from_template(dlg_template: str) -> dict:
            ''' Returns dictionary based of json file with dialog
            template specification.
            '''

            # Read the json file with dialog definition
            try:
                dlg_file = Path(DIALOG_PATH / Path(dlg_template + '.json'))
                dlg_data = get_dict_from_json(dlg_file)
            except FileNotFoundError:
                logger.error(f'Dialog file "{dlg_file}" not found.')
                raise

            # Final dlg data - empty at the start
            final_dlg_data = {}

            # Check if some template is used - first merge templates together - deeper and first go first
            for template in dlg_data.get('templates', []):
                
                # Get the json definition of the template and merge it
                final_dlg_data = { **prepare_dlg_data_from_template(template), **final_dlg_data }

            final_dlg_data = { **final_dlg_data, **dlg_data }

            return final_dlg_data

        # Prepare new empty dictionary that will hold the dialog's data
        new_dlg_data = {}

        # Decode dialog's id (name) - mandatory
        new_dlg_id = dialog_def.get('id')

        # Create the final dictionary definition using existing templates
        for template in dialog_def.get("templates", []):

            # Get the json definition of the template and merge it
            new_dlg_data = { **prepare_dlg_data_from_template(template), **new_dlg_data }

        # Now the final dialog description is stored here
        new_dlg_data = { **new_dlg_data, **dialog_def }

        # Now there is time to make surfaces and register the data object
        new_dlg_obj = dialog.prepare_dlg_obj_from_data(new_dlg_data, img_path=IMAGE_PATH, font_path=FONT_PATH)

        # Store the dialog
        self._dialogs.update({new_dlg_id : new_dlg_obj})
        logger.info(f'Dialog added.')

    def delete_dialog(self, dialog_name: str) -> None:
        ''' Unregister and delete the dialog object.'''

        if self._dialogs.get(dialog_name, None):
            del self._dialogs[dialog_name]
            logger.info(f'Dialog "{dialog_name}" successfully removed.')

    def clear_dialogs(self) -> None:
        '''Dereference and delete all dialogs.'''

        dialogs = list(self._dialogs.keys()).copy()

        # We need to use a copy in order not to delete parsed dictionary
        for dialog_name in dialogs:
            self.delete_dialog(dialog_name)
        logger.info(f'All dialogs cleared.')
"""