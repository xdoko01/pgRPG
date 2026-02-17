# Create logger
import logging
logger = logging.getLogger(__name__)

from fnmatch import fnmatchcase # UNIX-like wildcards in load/clean functions

from pgrpg.core.maps.map import Map

_maps = dict()
logger.info(f'MapManager initiated.')

def get_map(map_name) -> Map:
    return _maps.get(map_name, None)

def load_map(map_def: str) -> None:
    ''' Register and create new map if not already created
    '''

    # Create map, if not exists
    if not _maps.get(map_def, None):
        _maps.update({map_def: Map(map_def)})
        logger.info(f'Map "{map_def}" added.')

def delete_map(map_name: str) -> None:
    ''' Unregister and delete the map object.'''

    if _maps.get(map_name, None):
        del _maps[map_name]
        logger.info(f'Map "{map_name}" successfully removed.')

def delete_maps_pattern(map_name_pattern: str) -> None:
    '''Deletes all maps that match the map_name_pattern
    (UNIX-style expression).
    '''
    logger.debug(f'About to delete maps with names matching pattern "{map_name_pattern}".')

    match = lambda k: fnmatchcase(k, map_name_pattern)

    # Get all map_names matchint the pattern from _maps dictionary.
    # Perform delete_map on all those that match.
    for map_name in _maps.copy().keys():
        if match(map_name):
            delete_map(map_name)    

def clear_maps() -> None:
    '''Dereference and delete all maps.'''

    maps = list(_maps.keys()).copy()

    # We need to use a copy in order not to delete parsed dictionary
    for map_name in maps:
        delete_map(map_name)
    logger.info(f'All maps cleared.')

"""
class MapManager:

    def __init__(self) -> None:
        self._maps = {}
        logger.info(f'MapManager initiated.')

    def get_map(self, map_name) -> Map:
        return self._maps.get(map_name, None)

    def load_map(self, map_def: str) -> None:
        ''' Register and create new map if not already created
        '''

        # Create map, if not exists
        if not self._maps.get(map_def, None):
            self._maps.update({map_def : Map(map_def)})
            logger.info(f'Map "{map_def}" added.')

    def delete_map(self, map_name: str) -> None:
        ''' Unregister and delete the map object.'''

        if self._maps.get(map_name, None):
            del self._maps[map_name]
            logger.info(f'Map "{map_name}" successfully removed.')


    def clear_maps(self) -> None:
        '''Dereference and delete all maps.'''

        maps = list(self._maps.keys()).copy()

        # We need to use a copy in order not to delete parsed dictionary
        for map_name in maps:
            self.delete_map(map_name)
        logger.info(f'All maps cleared.')
"""

from dataclasses import dataclass

@dataclass
class MapManagerMock:

    def get_map(self, map_name):
        from pgrpg.core.maps.map import MapMock
        return MapMock()
