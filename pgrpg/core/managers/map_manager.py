"""Manage Tiled tile maps used by the game scenes.

Load, store, retrieve, and delete Map objects built from ``.tmx`` files.
Supports UNIX-wildcard pattern deletion for scene cleanup.

Module Globals:
    _maps: Dict mapping map name strings to Map instances.
"""

import logging
logger = logging.getLogger(__name__)

from fnmatch import fnmatchcase

from dataclasses import dataclass
from pgrpg.core.maps.map import Map

_maps = dict()
logger.info(f'MapManager initiated.')

def get_map(map_name) -> Map:
    """Return the Map instance for the given name, or None."""
    return _maps.get(map_name, None)

def load_map(map_def: str) -> None:
    """Create and register a Map from a .tmx file if not already loaded.

    Args:
        map_def: Map name (without extension) matching the .tmx filename.
    """

    # Create map, if not exists
    if not _maps.get(map_def, None):
        _maps.update({map_def: Map(map_def)})
        logger.info(f'Map "{map_def}" added.')

def delete_map(map_name: str) -> None:
    """Remove a map from the registry by name."""

    if _maps.get(map_name, None):
        del _maps[map_name]
        logger.info(f'Map "{map_name}" successfully removed.')

def delete_maps_pattern(map_name_pattern: str) -> None:
    """Delete all maps whose names match a UNIX-wildcard pattern.

    Args:
        map_name_pattern: fnmatch-style pattern (e.g. ``"arena_*"``).
    """
    logger.debug(f'About to delete maps with names matching pattern "{map_name_pattern}".')

    match = lambda k: fnmatchcase(k, map_name_pattern)

    # Get all map_names matchint the pattern from _maps dictionary.
    # Perform delete_map on all those that match.
    for map_name in _maps.copy().keys():
        if match(map_name):
            delete_map(map_name)    

def clear_maps() -> None:
    """Remove all maps from the registry."""

    maps = list(_maps.keys()).copy()

    # We need to use a copy in order not to delete parsed dictionary
    for map_name in maps:
        delete_map(map_name)
    logger.info(f'All maps cleared.')

# --- Test mock (used by example_game/ command doctests via ECSManagerMock) ---

@dataclass
class MapManagerMock:
    """Mock map manager returning a MapMock instance."""

    def get_map(self, map_name):
        from pgrpg.core.maps.map import MapMock
        return MapMock()

