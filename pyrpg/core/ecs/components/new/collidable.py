''' Module "pyrpg.core.ecs.components.new_collidable" contains
NewCollidable component implemented as a NewCollidable class.

Use 'python -m pyrpg.core.ecs.components.new_collidable -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class Collidable(Component):
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
        'apply_pos_fix_to_allowlist',
        'apply_pos_fix_to_denylist',
        'accept_pos_fix_from_allowlist',
        'accept_pos_fix_from_denylist',
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

            :param apply_pos_fix_to_allowlist: Allow fix position of others only in this allowlist upon hitting this entity
            :type apply_pos_fix_to_allowlist: set

            :param apply_pos_fix_to_denylist: Do not fix position of others in this denylist upon hitting this entity
            :type apply_pos_fix_to_denylist: set

            :param accept_pos_fix_from_allowlist: Should the entity adjust its position upon colliding into entity in the allowlist.
            :type accept_pos_fix_from_allowlist: set

            :param accept_pos_fix_from_denylist: Entity will not adjust its position upon colliding into entity in the denylist.
            :type accept_pos_fix_from_denylist: set

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
        self.apply_pos_fix_to_allowlist = set(kwargs.get('apply_pos_fix_to_allowlist', {}))

        # Do not fix position of others in this denylist upon hitting this entity
        self.apply_pos_fix_to_denylist = set(kwargs.get('apply_pos_fix_to_denylist', {}))

        # Should the entity adjust its position upon colliding into entity in the allowlist.
        self.accept_pos_fix_from_allowlist = set(kwargs.get('accept_pos_fix_from_allowlist', {}))

        # Entity will not adjust its position upon colliding into entity in the denylist.
        self.accept_pos_fix_from_denylist = set(kwargs.get('accept_pos_fix_from_denylist', {}))

        # Walkaround the colliding obstacle
        self.position_fix_walkaround_mode = kwargs.get('position_fix_walkaround_mode', True)

        try:
            assert isinstance(self.x, int) and self.x >= 0, f'Collision x-axis must be passed as a positive int.'
            assert isinstance(self.y, int) and self.x >= 0, f'Collision y-axis must be passed as a positive int.'
            assert isinstance(self.dx, int), f'Offset centre x-axis must be passed as an int.'
            assert isinstance(self.dy, int), f'Offset centre y-axis must be passed as an int.'
            assert isinstance(self.allowlist, set), f'Parameter "allowlist" must be a set.'
            assert isinstance(self.denylist, set), f'Parameter "denylist" must be a set.'
            assert isinstance(self.apply_pos_fix_to_allowlist, set), f'Parameter "apply_pos_fix_to_allowlist" must be a set.'
            assert isinstance(self.apply_pos_fix_to_denylist, set), f'Parameter "apply_pos_fix_to_denylist" must be a set.'
            assert isinstance(self.accept_pos_fix_from_allowlist, set), f'Parameter "accept_pos_fix_from_allowlist" must be a set.'
            assert isinstance(self.accept_pos_fix_from_denylist, set), f'Parameter "accept_pos_fix_from_denylist" must be a set.'
            assert isinstance(self.position_fix_walkaround_mode, bool), f'Parameter "position_fix_walkaround_mode" must be a boolean.'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

class CollidableObsolete(Component):
    ''' Entity collides with other collidable entities.

    Used by:
        - GenerateCollisionsProcessor

    Examples of JSON definition:
        {"type" : "Collidable", "params" : {"x" : 20, "y" : 20, "dx" : 0, "dy" : 0}}

    Tests:
        >>> c = Collidable()
        >>> c.x
        0
        >>> c = Collidable(**{"x" : 20, "y" : 20})
        >>> c.x
        20
    '''

    __slots__ = ['x', 'y', 'dx', 'dy', 'ignore_position_fix', 'ignore_collision_with', 'position_fix_walkaround_mode', 'position_fix_for_self']

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

            :param ignore_position_fix: Do not fix position of others upon hitting this entity - damage zones 
              need to be collidable in order to cause damage but at the same time can be stepped on by the player.
            :type ignore_position_fix: boolean

            :param ignore_collision_with: Do not register collision with specified entities.
            :type ignore_collision_with: list (entity names or ids)

            :param position_fix_walkaround_mode: Should the entity try to walk around the colliding entity or not.
            :type position_fix_walkaround_mode: boolean (default True)

            :param position_fix_for_self: Should the entity adjust its position upon colliding into other entity.
            :type position_fix_for_self: boolean (default True)

            :raise: ValueError - in case of incorrect collision borders
        '''

        super().__init__()

        # With and height of the collision zone - from the center +/-x and +/-y
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)

        # Correction of the centre from which the collision zone is calculated
        self.dx = kwargs.get('dx', 0)
        self.dy = kwargs.get('dy', 0)

        # Ignore fixing of position uppon collision with the entity - default False
        self.ignore_position_fix = kwargs.get('ignore_position_fix', False)

        # Ignore totally collision with given entity
        self.ignore_collision_with = set(kwargs.get('ignore_collision_with', []))

        # Walkaround the colliding obstacle
        self.position_fix_walkaround_mode = kwargs.get('position_fix_walkaround_mode', True)

        # Do not fix entity position when colliding into other entity
        self.position_fix_for_self = kwargs.get('position_fix_for_self', True)

        try:
            assert isinstance(self.x, int) and self.x >= 0, f'Collision x-axis must be passed as a positive int.'
            assert isinstance(self.y, int) and self.x >= 0, f'Collision y-axis must be passed as a positive int.'
            assert isinstance(self.dx, int), f'Offset centre x-axis must be passed as an int.'
            assert isinstance(self.dy, int), f'Offset centre y-axis must be passed as an int.'
            assert isinstance(self.ignore_position_fix, bool), f'Parameter "ignore_position_fix" must be a boolean.'
            assert isinstance(self.position_fix_walkaround_mode, bool), f'Parameter "position_fix_walkaround_mode" must be a boolean.'
            assert isinstance(self.position_fix_for_self, bool), f'Parameter "position_fix_for_self" must be a boolean.'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
