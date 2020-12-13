from .component import Component

class Pickable(Component):
    ''' Entity is pickable by HasInventory entity.

    Used by:
        - CollisionItemProcessor

    Examples of JSON definition:
        {"type" : "Pickable", "params" : {}}

    Tests:
        >>> c = Pickable()
    '''

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Just a tag marking the entity that it can
        be picked
        '''

        super().__init__()

