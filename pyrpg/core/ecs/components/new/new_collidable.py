''' Module "pyrpg.core.ecs.components.new_collidable" contains
NewCollidable component implemented as a NewCollidable class.

Use 'python -m pyrpg.core.ecs.components.new_collidable -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class NewCollidable(Component):
    ''' Entity collides with other collidable entities.

    Used by:
        - GenerateCollisionsProcessor

    Examples of JSON definition:
        {"type" : "NewCollidable", "params" : {"x" : 20, "y" : 20, "dx" : 0, "dy" : 0}}

    Tests:
        >>> c = NewCollidable()
        >>> c.x
        0
        >>> c = NewCollidable(**{"x" : 20, "y" : 20})
        >>> c.x
        20
    '''

    __slots__ = [
        'x', 
        'y', 
        'dx', 
        'dy', 
        'allowlist', 
        'denylist', 
        'position_fix_others_allowlist',
        'position_fix_others_denylist',
        'position_fix_self_allowlist',
        'position_fix_self_denylist',
        'position_fix_walkaround_mode'
    ]

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the Collidable component.

        Parameters:
            :param x: X-axis collision zone +- from the x-centre of the entity in pixel coordinates
            :type x: int

            :param y: Y-axis collision zone +- from the y-centre of the entity in pixel coordinates
            :type y: int

            :param dx: X-axis set offset +- from the x-centre of the entity in pixel coordinates
            :type dx: int

            :param dy: Y-axis set offset +- from the y-centre of the entity in pixel coordinates
            :type dy: int

            :param dy: Y-axis set offset +- from the y-centre of the entity in pixel coordinates
            :type dy: int

            :param allowlist: Allow collision only with entities that are present in the allowlist
            :type allowlist: set

            :param denylist: Allow collision only with entities that are NOT present in the denylist
            :type denylist: set

            :param position_fix_others_allowlist: Allow fix position of others only in this allowlist upon hitting this entity
            :type position_fix_others_allowlist: set

            :param position_fix_others_denylist: Do not fix position of others in this denylist upon hitting this entity
            :type position_fix_others_denylist: set

            :param position_fix_self_allowlist: Should the entity adjust its position upon colliding into entity in the allowlist.
            :type position_fix_self_allowlist: set

            :param position_fix_self_denylist: Entity will not adjust its position upon colliding into entity in the denylist.
            :type position_fix_self_denylist: set

            :param position_fix_walkaround_mode: Should the entity try to walk around the colliding entity or not.
            :type position_fix_walkaround_mode: boolean (default True)

            :raise: ValueError - in case of incorrect collision borders
        '''

        super().__init__()

        # With and height of the collision zone - from the center +/-x and +/-y
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)

        # Correction of the centre from which the collision zone is calculated
        self.dx = kwargs.get('dx', 0)
        self.dy = kwargs.get('dy', 0)

        # Allow collision only on items from allowlist, if filled
        self.allowlist = set(kwargs.get('allowlist', {}))

        # Deny collision with items from denylist
        self.denylist = set(kwargs.get('denylist', {}))

        # Allow fix position of others only in this allowlist upon hitting this entity
        self.position_fix_others_allowlist = set(kwargs.get('position_fix_others_allowlist', {}))

        # Do not fix position of others in this denylist upon hitting this entity
        self.position_fix_others_denylist = set(kwargs.get('position_fix_others_denylist', {}))

        # Should the entity adjust its position upon colliding into entity in the allowlist.
        self.position_fix_self_allowlist = set(kwargs.get('position_fix_self_allowlist', {}))

        # Entity will not adjust its position upon colliding into entity in the denylist.
        self.position_fix_self_denylist = set(kwargs.get('position_fix_self_denylist', {}))

        # Walkaround the colliding obstacle
        self.position_fix_walkaround_mode = kwargs.get('position_fix_walkaround_mode', True)

        try:
            assert isinstance(self.x, int) and self.x >= 0, f'Collision x-axis must be passed as a positive int.'
            assert isinstance(self.y, int) and self.x >= 0, f'Collision y-axis must be passed as a positive int.'
            assert isinstance(self.dx, int), f'Offset centre x-axis must be passed as an int.'
            assert isinstance(self.dy, int), f'Offset centre y-axis must be passed as an int.'
            assert isinstance(self.allowlist, set), f'Parameter "allowlist" must be a set.'
            assert isinstance(self.denylist, set), f'Parameter "denylist" must be a set.'
            assert isinstance(self.position_fix_others_allowlist, set), f'Parameter "position_fix_others_allowlist" must be a set.'
            assert isinstance(self.position_fix_others_denylist, set), f'Parameter "position_fix_others_denylist" must be a set.'
            assert isinstance(self.position_fix_self_allowlist, set), f'Parameter "position_fix_self_allowlist" must be a set.'
            assert isinstance(self.position_fix_self_denylist, set), f'Parameter "position_fix_self_denylist" must be a set.'
            assert isinstance(self.position_fix_walkaround_mode, bool), f'Parameter "position_fix_walkaround_mode" must be a boolean.'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
