''' Module "example_game.core.components.has_inventory" contains
HasInventory component implemented as a HasInventory class.

Use 'python -m core.components.has_inventory -v' to run
module tests.
'''
# Logger init
import logging
logger = logging.getLogger(__name__)

from pgrpg.core.ecs import Component
from pgrpg.functions.dict_utils import add_dict_value, del_dict_value, get_all_dict_values

class HasInventory(Component):
    ''' Entity has inventory - can pick items and add it to the inventory.

    Used by:
        - PerformPickupProcessor

    Examples of JSON definition:
        {"type" : "HasInventory", "params" : {}},
        {"type" : "HasInventory", "params" : {"inventory" : ["key", "other_key", "money", 4]} }
        {"type" : "HasInventory", "params" : {"inventory" : ["key", "other_key", "money", 4], "categories" : {"keys" : ["key", "other_key"], "money" : ["money"], "weapons" : [4]}} }


    Tests:
        >>> c = HasInventory()
        >>> c = HasInventory(**{"inventory" : ["key", "other_key", "money", 4]})
        >>> c = HasInventory(**{"inventory" : ["key", "other_key", "money", 4], "categories" : {"keys" : ["key", "other_key"], "money" : ["money"], "weapons" : [5]}})
    '''

    __slots__ = ['inventory', 'categories', 'max_items', 'slots']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new HasInventory component.

        Parameters:
            :param inventory: List of entities that are in the inventory
            :type inventory: List of string or list of integers

            :param categories: Dictionary where the categorization of entities in inventory is stored
            :type categories: dict

            :param max_items: Max number of items that can be in the inventory
            :type max_items: int

        '''

        super().__init__()

        # Inventory is implemented as a set to enable easy adding and deletion of items
        # and prevent double membership.
        self.inventory = set(kwargs.get('inventory', []))
        self.categories = kwargs.get('categories', {})
        self.max_items = kwargs.get('max_items', 10)
        self.slots = [None for i in range(self.max_items)] # all the slots are empty at the start

        # Check that inventory is a set
        try:
            assert isinstance(self.inventory, set), f'Inventory must be a set of entities.'
            assert isinstance(self.categories, dict), f'Categories of inventory must be a dict.'
            assert len(self.inventory) <= self.max_items , f'Too many items in the inventory'

            # Add inventory to the slots - from start
            for slot_id, item in enumerate(self.inventory): self.slots[slot_id] = item

            # Every entity stored as a value in categories must be also in inventory
            assert set(get_all_dict_values(self.categories)).issubset(self.inventory), f'All items in categories must be also part of the inventory set.'

            # Every entity in the inventory must have some slot
            assert set(self.inventory).issubset(self.slots)
    
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


    def add(self, entity_id: int, category: str=None) -> int|None:
        '''Safely add entity_id to the inventory's data structures.

        :returns int: Entity Id of picked up item or None if pickup is not possible (full inventory)
        '''
        
        logger.debug(f'About to add {entity_id=} of {category=} to the inventory. Pre-add status: {self.max_items=}, {len(self.inventory)=}')
        
        # Check that there is still space in the inventory for the entity
        if self.max_items <= len(self.inventory):
            logger.debug(f'No more space in inventory')
            return None

        # Add the entity into the HasInventory inventory set
        self.inventory.add(entity_id)

        # Add the entity into the HasInventory categories dictionary, if category defined
        if category:
            add_dict_value(self.categories, category, entity_id)

        # Add the entity to the first empty slot
        for slot_id, item in enumerate(self.slots):
            if item is None:
                self.slots[slot_id] = entity_id
                break
        
        return entity_id

    def remove_by_entity_id(self, entity_id: int) -> None:
        '''Safely remove entity_id from the inventory's data structures.
        '''
        # Remove from set
        self.inventory.remove(entity_id) 
        
        # Remove from slots
        self.slots = [self.slots[slot_id] if self.slots[slot_id] != entity_id else None for slot_id in range(len(self.slots))]

        # Remove from categories
        del_dict_value(d=self.categories, value=entity_id)

    def remove_by_slot_id(self, slot_id: int) -> None:
        '''Safely remove entity_id stored in the slots[slot_id] from the inventory's data structures.
        '''
        # Remove from set
        self.inventory.remove(self.slots[slot_id]) 
        
        # Remove from slots
        self.slots[slot_id] = None

        # Remove from categories
        del_dict_value(d=self.categories, value=self.slots[slot_id])

if __name__ == '__main__':
    import doctest
    doctest.testmod()
