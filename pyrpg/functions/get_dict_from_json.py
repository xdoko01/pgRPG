import json, re
from pathlib import Path

def get_dict_from_json(filepath: Path) -> dict:
    ''' Returns dictionary based of json file with C-style 
    comments removed.

    Parameters:
        :param filepath: Path to the json file
        :type filepath: Path

        :returns: Dictionary of json data
    '''

    try:
        with open(filepath, 'r') as json_file:
            json_data = json_file.read()
            return json.loads(re.sub("[^:]//.*","", json_data, flags=re.MULTILINE)) # Remove C-style comments before processing JSON
    except FileNotFoundError:
        raise
