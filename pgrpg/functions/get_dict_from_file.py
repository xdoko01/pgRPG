"""Load a dictionary from a JSON, YAML, or TOML file.

Supports automatic file extension detection when the suffix is omitted,
trying TOML, YAML, JSON, and JSONC in order.
"""

from pathlib import Path
from .get_dict_from_json import get_dict_from_json
from .get_dict_from_yaml import get_dict_from_yaml
from .get_dict_from_toml import get_dict_from_toml


def get_dict_from_file(filepath: Path, dir: Path=Path('')) -> dict:
    """Load a dictionary from a file, guessing the format if needed.

    Supports absolute and relative paths. When no file extension is
    provided, tries ``.toml``, ``.yaml``, ``.json``, and ``.jsonc``
    in that order.

    Args:
        filepath: Path to the data file. Extension is optional.
        dir: Base directory for resolving relative paths.

    Returns:
        Dictionary parsed from the file.

    Raises:
        ValueError: If the file cannot be found or loaded.

    Examples:
        >>> d = get_dict_from_file(filepath=Path('C:/Users/otakar/OneDrive/Personal/Python/pgrpg/config.json'))
        >>> d = get_dict_from_file(filepath=Path('C:/Users/otakar/OneDrive/Personal/Python/pgrpg/config'))
        >>> d = get_dict_from_file(filepath=Path('config.json'), dir=Path('C:/Users/otakar/OneDrive/Personal/Python/pgrpg'))
        >>> d = get_dict_from_file(filepath=Path('config'), dir=Path('C:/Users/otakar/OneDrive/Personal/Python/pgrpg'))
        >>> d = get_dict_from_file(filepath=Path('C:/Users/otakar/OneDrive/Personal/Python/pgrpg/test.toml'))
    """

    # Check if the filepath has some file extension specified - if not we will try to guess json or yaml
    file_extension = filepath.suffix

    # Check if path to the dictionary is absolute or relative and construct the full path to the file
    filepath = filepath if filepath.is_absolute() else dir / filepath

    # Try to open the filepath - if suffix is not present, try to guess it
    try:
        if file_extension in ['.toml']:
            res = get_dict_from_toml(filepath)
        if file_extension in ['.yaml']:
            res = get_dict_from_yaml(filepath)
        elif file_extension in ['.json', '.jsonc']:
            res = get_dict_from_json(filepath)
        else:
            try:
                res = get_dict_from_toml(Path(str(filepath) + '.toml'))
            except FileNotFoundError:
                try:
                    res = get_dict_from_yaml(Path(str(filepath) + '.yaml'))
                except FileNotFoundError:
                    try:
                        res = get_dict_from_json(Path(str(filepath) + '.json'))
                    except FileNotFoundError:
                        res = get_dict_from_json(Path(str(filepath) + '.jsonc'))

    except FileNotFoundError:
        raise ValueError(f'Cannot load dict from file "{filepath}".')

    return res

if __name__ == '__main__':
    import doctest
    doctest.testmod()
