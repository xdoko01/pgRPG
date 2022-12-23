import logging
from pyrpg.core.maps.map import Map

# Create logger
logger = logging.getLogger(__name__)

class MapManager:

    def __init__(self) -> None:
        self._maps = {}
        logger.info(f'MapManager initiated.')

    def get_map(self, map_name) -> Map:
        return self._maps.get(map_name, None)

    def add_map(self, map_name: str) -> None:
        ''' Register and create new map if not already created
        Called from Quest/Phase class
        '''

        # Create map, if not exists
        if not self._maps.get(map_name, None):
            self._maps.update({map_name : Map(map_name)})
            logger.info(f'Map "{map_name}" added.')

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