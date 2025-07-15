''' Module "pyrpg.core.ecs.components.render_data_from_parent" contains
RenderDataFromParent component implemented as a NewRenderPosition class.

Use 'python -m pyrpg.core.ecs.components.render_data_from_parent -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class RenderDataFromParent(Component):
    ''' Entity is rendered using this data in absence of Position
    component in case entity is in inventory (for example weapon in use).

    Used by:
        - PerformRenderArmedWeaponProcessor
        - GenerateRenderDataFromParentProcessor
    '''

    __slots__ = ['parent_pos_comp', 'x', 'y', 'dir_name', 'action', 'last_frame']

    def __init__(self, parent_pos_comp, x, y, dir_name, action, last_frame):
        ''' Initiation of NewRenderPosition component
        '''

        super().__init__()

        # For visual effect to follow the parent position
        self.parent_pos_comp = parent_pos_comp

        # Position parameters from parent necessary for rendering
        self.x = x
        self.y = y
        self.dir_name = dir_name

        # Animation parameters from parent necessary for rendering
        self.action = action
        self.last_frame = last_frame


if __name__ == '__main__':
    import doctest
    doctest.testmod()
