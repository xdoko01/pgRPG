''' Module "example_game.core.components.flag_show_inventory" contains
FlagShowInventory component implemented as a FlagShowInventory class.

Use 'python -m example_game.core.components.flag_show_inventory -v' to run
module tests.
'''

from pygame import Rect
from pgrpg.core.ecs import Component
from pgrpg.core.config import DISPLAY, GAME

class FlagShowInventory(Component):
    ''' Entity has displayed inventory and can manipulate the inventory items.

    Used by:
        - PerformRenderInventoryProcessor

    Examples of JSON definition:
        {"type" : "FlagShowInventory", "params" : {}}

    Tests:
        >>> c = FlagShowInventory()
    '''

    __slots__ = ['camera_comp', 'inv_win_rect', 'inv_slot_rects', 'inv_slot_border_rects', 
                 'selected_slot_id', 'mouse_focused_slot_id', 'slots_per_row', 
                 'dragging', 'drag_item_id', 'drag_start_slot_id', 'drag_stop_slot_id', 'drag_item_model'
    ]

    def __init__(self, inventory_comp: Component, camera_comp: Component=None, slots_per_row: int=5):
        ''' Initiate values for the new FlagShowInventory component.

        Parameters:

            :param camera_comp: Optional reference to Camera component for calculation of inventory window
            :type camera_comp: Component
        '''

        super().__init__()

        self.inventory_comp: Component = inventory_comp
        self.camera_comp: Component = camera_comp
        self.inv_win_rect: Rect | None = None
        self.inv_slot_rect: Rect | None = None
        self.inv_slot_rects: list[Rect] = []
        self.inv_slot_border_rects: list[Rect] = []

        self.slots_per_row = slots_per_row # How many slots show in each row
        self.selected_slot_id: int = 0 # Inventory slot Id of the currently selected slot
        self.mouse_focused_slot_id: int|None = None # Remember on which slot mouse is focused

        self.dragging: bool = False # Keep information if dragging is in progress, to inform render processor to display dragged item
        self.drag_item_id = None
        self.drag_start_slot_id = None
        self.drag_stop_slot_id = None
        self.drag_item_model = None

        # Init the inventory window dimensions
        self.reinit()


    def reinit(self):
        '''Called when configuration is changed'''

        # Rectangle representing the inventory window
        _screen_width = self.camera_comp.screen_width if self.camera_comp is not None else DISPLAY["RESOLUTION"][0]
        _screen_height = self.camera_comp.screen_height if self.camera_comp is not None else DISPLAY["RESOLUTION"][1]

        # The dimensions should be to fit 5 tiles in one row + Header footer and some padding left and right and in between
        
        # Resolution of item pictures
        #_item_res_dim = (GAME["TILE_RES_PX"],GAME["TILE_RES_PX"]) # 64x64
        self.inv_slot_rect = Rect((0,0), (GAME["TILE_RES_PX"],GAME["TILE_RES_PX"]))

        # How many items on one row
        _max_number_of_slots = self.inventory_comp.max_items

        # Paddings
        _header_padding = 40
        _footer_padding = 40
        _left_padding = 2
        _right_padding = 2
        _slots_padding_x = 2
        _slots_padding_y = 2

        # Dimension of inventory window
        _inv_win_width = _left_padding + self.slots_per_row * (self.inv_slot_rect.width + 2*_slots_padding_x) + _right_padding
        _inv_win_height = _header_padding + (_max_number_of_slots // self.slots_per_row) * (self.inv_slot_rect.height + 2*_slots_padding_y) + _footer_padding

        # Assert that dimensions of the inventory are not greater than camera window
        try:
            assert _inv_win_width <= _screen_width, f'Inventory window width is greater than camera window width.'
            assert _inv_win_height <= _screen_height, f'Inventory window height is greater than camera window heignt.'
        except AssertionError:
            raise ValueError(f'Inventory window does not fit camera window.')

        # Position the inventory window in the centre of the camera
        _inv_win_pos_x = int((_screen_width - _inv_win_width) / 2)
        _inv_win_pos_y = int((_screen_height - _inv_win_height) / 2)

        # Store the inventory window rectangle
        self.inv_win_rect = Rect(
            # TL point
            (_inv_win_pos_x, _inv_win_pos_y),
            # Width/Height
            (_inv_win_width, _inv_win_height)
        )

        # List of Rectancles representing the individual slots for items
        for slot_id in range(_max_number_of_slots):
            
            slot_pos_x = _inv_win_pos_x + _left_padding + (slot_id % self.slots_per_row) * (_slots_padding_x + self.inv_slot_rect.width + _slots_padding_x) + _slots_padding_x
            slot_pos_y = _inv_win_pos_y + _header_padding + (slot_id // self.slots_per_row) * (_slots_padding_y + self.inv_slot_rect.height + _slots_padding_y) + _slots_padding_y
            
            self.inv_slot_rects.append(Rect((slot_pos_x, slot_pos_y), (self.inv_slot_rect.width, self.inv_slot_rect.height)))
            
            # Rectangles for selection boxes
            self.inv_slot_border_rects.append(
                Rect(
                    (slot_pos_x - _slots_padding_x, slot_pos_y - _slots_padding_y), 
                    (self.inv_slot_rect.width + 2*_slots_padding_x, self.inv_slot_rect.height + 2*_slots_padding_y)
                )
            )


    def pre_save(self):
        ''' Prepare component for saving - remove all references to
        non-serializable objects
        '''
        pass

    def post_load(self):
        ''' Regenerate all non-serializable objects for the component
        '''
        pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()
