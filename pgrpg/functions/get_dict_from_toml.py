"""Load a dictionary from a TOML file."""

import toml
from pathlib import Path

def get_dict_from_toml(filepath: Path) -> dict:
    """Parse a TOML file into a dictionary.

    Args:
        filepath: Path to the TOML file.

    Returns:
        Dictionary of parsed TOML data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """

    try:
        with open(filepath, 'r') as toml_file:
            return toml.load(toml_file)
    except FileNotFoundError as e:
        raise e
