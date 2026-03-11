"""Load a dictionary from in-memory storage or from a file.

Provides a unified lookup that first checks a storage dictionary by
path, then falls back to loading from a JSON/YAML/TOML file.
"""

from pathlib import Path
from .get_dict_from_file import get_dict_from_file
from .dict_utils import get_dict_value

def get_dict(dictpath: str, storage: dict=None, dir: Path=Path('')) -> dict:
    """Load a dictionary by path from storage or from a file.

    First attempts to find the value at ``dictpath`` within ``storage``
    (using ``/`` as a key separator). If not found, loads from a
    JSON/YAML/TOML file using ``dictpath`` as a file path.

    Args:
        dictpath: Key path within storage (``/``-separated) or file path.
        storage: Dictionary to search first. Skipped if None.
        dir: Base directory for resolving relative file paths.

    Returns:
        The dictionary (or value) found at the specified path.

    Examples:
        >>> storage = { \
                'conf': "This is config", \
                'a': { \
                    'aa': {'aaa': 'AAA', 'aab': 'AAB', 'aac': 'AAC'}, \
                    'ab': {'aba': 'ABA', 'abb': 'ABB', 'abc': 'ABC'} \
                }, \
                'b': { \
                    'ba': 'BA', \
                    'bc': 'BC' \
                } \
            } \

        >>> get_dict(dictpath='a', storage=storage)
        {'aa': {'aaa': 'AAA', 'aab': 'AAB', 'aac': 'AAC'}, 'ab': {'aba': 'ABA', 'abb': 'ABB', 'abc': 'ABC'}}

        >>> get_dict(dictpath='a/aa', storage=storage)
        {'aaa': 'AAA', 'aab': 'AAB', 'aac': 'AAC'}

        >>> get_dict(dictpath='a/aa/aab', storage=storage)
        'AAB'

        >>> bool(get_dict(dictpath='C:/Users/otakar/OneDrive/Personal/Python/pgrpg/config.json'))
        True

        >>> bool(get_dict(dictpath='C:/Users/otakar/OneDrive/Personal/Python/pgrpg/config'))
        True

        >>> relative_path = Path('C:/Users/otakar/OneDrive/Personal/Python/pgrpg')
        >>> bool(get_dict(dictpath='config.json', dir=relative_path))
        True

        >>> get_dict(dictpath='conf', storage=storage, dir=relative_path)
        'This is config'

        >>> bool(get_dict(dictpath='config', storage=storage, dir=relative_path))
        True
    """

    # Try to look in the storage
    if storage:
        res = get_dict_value(d=storage, path=dictpath, sep='/')
        # If the key was successfully found in the storage, finish
        if res:
            return res

    # Continue looking in the files
    return get_dict_from_file(filepath=Path(dictpath), dir=dir)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
