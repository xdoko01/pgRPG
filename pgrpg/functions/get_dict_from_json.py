"""Load a dictionary from a JSON file with C-style comment support."""

import json, re
from pathlib import Path

def get_dict_from_json(filepath: Path) -> dict:
    """Parse a JSON file into a dictionary, stripping C-style comments.

    Args:
        filepath: Path to the JSON or JSONC file.

    Returns:
        Dictionary of parsed JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """

    try:
        with open(filepath, 'r') as json_file:
            json_data = json_file.read()
            return json.loads(re.sub("[^:]//.*","", json_data, flags=re.MULTILINE)) # Remove C-style comments before processing JSON
    except FileNotFoundError:
        raise
